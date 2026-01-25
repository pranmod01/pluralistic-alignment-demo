"""
Pluralistic Alignment Demo - V1 MVP

A Streamlit app that generates multiple community perspectives on
controversial topics based on user's community affiliations.
"""

import streamlit as st

import sys
from pathlib import Path

# Add src directory to path for imports when running directly
sys.path.insert(0, str(Path(__file__).parent))

import config
import database
from controversy import detect_controversy, detect_controversy_llm, ControversyLevel
from community_selection import select_communities, UserProfile
from communities import get_community_name
from prompts import get_perspective_prompt, get_composite_identity_prompt, format_synthesis_prompt, STANDARD_PROMPT
from cache import get_cached_perspective, store_cached_perspective, init_cache_table
from dataset import get_all_user_profiles

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


def get_client():
    """Get OpenAI client if configured."""
    if OpenAI is None:
        return None
    if not config.OPENAI_API_KEY:
        return None
    return OpenAI(api_key=config.OPENAI_API_KEY)


def generate_completion(client, prompt: str, max_tokens: int = 800) -> str:
    """Generate a completion from OpenAI."""
    if client is None:
        return "[OpenAI client not configured: set OPENAI_API_KEY env var]"
    try:
        resp = client.chat.completions.create(
            model=config.GPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"[Error calling OpenAI API: {e}]"


def generate_perspective(
    client,
    community: str,
    topic_category: str,
    question: str,
    use_cache: bool = True,
    composite_communities: list[str] = None
) -> str:
    """
    Generate a perspective for a community, using cache if available.

    Args:
        client: OpenAI client
        community: Community ID (used for cache key)
        topic_category: Topic category for caching
        question: The user's question
        use_cache: Whether to use caching
        composite_communities: If provided, generate a composite identity perspective
    """
    # Build cache key - include all communities for composite
    cache_key = community
    if composite_communities and len(composite_communities) > 1:
        cache_key = "_".join(composite_communities)

    # Check cache first
    if use_cache and topic_category:
        cached = get_cached_perspective(cache_key, topic_category, question)
        if cached:
            return cached

    # Generate new perspective
    if composite_communities and len(composite_communities) > 1:
        prompt = get_composite_identity_prompt(composite_communities, question)
    else:
        prompt = get_perspective_prompt(community, question)

    perspective = generate_completion(client, prompt)

    # Store in cache
    if use_cache and topic_category and not perspective.startswith("["):
        store_cached_perspective(cache_key, topic_category, question, perspective)

    return perspective


def main():
    st.set_page_config(page_title="Pluralistic Alignment Demo", layout="wide")
    st.title("Pluralistic AI Alignment Demo - V1")

    st.markdown("""
    This demo surfaces multiple community perspectives on controversial topics
    based on your community affiliations. Select a user profile to see how
    different communities view the same question.
    """)

    # Initialize database
    database.init_db()
    init_cache_table()

    # Load user profiles from dataset
    user_profiles = get_all_user_profiles()

    # Sidebar: User profile selection
    st.sidebar.header("User Profile")

    # Create a mapping for the dropdown
    profile_options = {
        f"{p.user_id}: {p.primary_community} ({p.primary_community_type})": p
        for p in user_profiles
    }

    selected_profile_key = st.sidebar.selectbox(
        "Select a user profile",
        options=list(profile_options.keys()),
        index=0
    )

    user = profile_options[selected_profile_key]

    # Display user info
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Primary:** {get_community_name(user.primary_community)}")
    if user.secondary_community:
        st.sidebar.markdown(f"**Secondary:** {get_community_name(user.secondary_community)}")
    if user.tertiary_community:
        st.sidebar.markdown(f"**Tertiary:** {get_community_name(user.tertiary_community)}")
    if user.location:
        st.sidebar.markdown(f"**Location:** {user.location}")

    # Main form
    with st.form("question_form"):
        question = st.text_area(
            "Enter your question",
            height=80,
            placeholder="e.g., Is it ethical to eat meat? Should abortion be legal?"
        )
        show_debug = st.checkbox("Show debug info", value=False)
        submitted = st.form_submit_button("Get Perspectives")

    client = get_client()

    if submitted and question.strip():
        # Get user's full community list for context
        user_communities = user.get_communities()

        # Step 1: Detect controversy using LLM-based detection (with user context)
        controversy_profile, topic_category = detect_controversy_llm(
            question, client, config.GPT_MODEL, user_communities=user_communities
        )

        if show_debug:
            st.markdown("### Debug Info")
            st.markdown(f"**User Communities:** {', '.join(user_communities)}")
            st.markdown(f"**Topic Category:** {topic_category or 'Not detected'}")
            st.markdown(f"**Controversy Profile:**")
            st.markdown(f"- Religious: {controversy_profile.religious.value}")
            st.markdown(f"- Political: {controversy_profile.political.value}")
            st.markdown(f"- Regional: {controversy_profile.regional.value}")
            st.markdown(f"**Should Surface:** {controversy_profile.should_surface_perspectives()}")
            if controversy_profile.divergent_communities:
                st.markdown(f"**LLM-Identified Divergent Communities:** {', '.join(controversy_profile.divergent_communities)}")
            if controversy_profile.intra_community_contrast:
                st.markdown(f"**Intra-Community Contrast:** {controversy_profile.intra_community_contrast}")
            if controversy_profile.reasoning:
                st.markdown(f"**LLM Reasoning:** {controversy_profile.reasoning}")

        # Step 2: Decide whether to surface perspectives
        if controversy_profile.should_surface_perspectives():
            # Step 3: Select communities
            selected = select_communities(
                user=user,
                controversy_profile=controversy_profile,
                topic_category=topic_category,
                max_additional=config.MAX_ADDITIONAL_COMMUNITIES
            )

            if show_debug:
                st.markdown(f"**Selected Communities:** {selected.all_communities()}")
                st.markdown(f"**Rationale:** {selected.rationale}")

            # Step 4: Generate perspectives
            with st.spinner("Generating perspectives..."):
                perspectives = {}

                # For baseline (user's community), use composite identity
                baseline_communities = user_communities  # All user communities
                perspectives[selected.baseline] = generate_perspective(
                    client,
                    selected.baseline,
                    topic_category,
                    question,
                    composite_communities=baseline_communities
                )

                # For other perspectives, use single community
                for community in selected.additional:
                    perspectives[community] = generate_perspective(
                        client,
                        community,
                        topic_category,
                        question
                    )

                # Generate synthesis
                synthesis_prompt = format_synthesis_prompt(perspectives)
                synthesis = generate_completion(client, synthesis_prompt)

            # Save to database
            interaction_id = database.save_interaction(
                question=question,
                perspectives=perspectives,
                synthesis=synthesis,
                user_id=user.user_id,
                topic_category=topic_category,
                controversy_profile={
                    "religious": controversy_profile.religious.value,
                    "political": controversy_profile.political.value,
                    "regional": controversy_profile.regional.value,
                },
                selected_communities=selected.all_communities(),
                surfaced_perspectives=True
            )

            # Display perspectives
            st.markdown("---")
            st.subheader("Community Perspectives")

            # Show baseline (user's composite identity) first
            composite_name = " + ".join([get_community_name(c) for c in user_communities if c])
            st.markdown(f"### Your Perspective: {composite_name}")
            st.markdown(perspectives[selected.baseline])

            # Show other perspectives
            if selected.additional:
                st.markdown("### Other Perspectives")
                cols = st.columns(len(selected.additional))
                for i, community in enumerate(selected.additional):
                    with cols[i]:
                        st.markdown(f"**{get_community_name(community)}**")
                        st.markdown(perspectives[community])

            # Show synthesis
            st.markdown("---")
            st.subheader("Synthesis")
            st.markdown(synthesis)

        else:
            # Standard response - no perspectives needed
            with st.spinner("Generating response..."):
                standard_prompt = STANDARD_PROMPT.format(question=question)
                standard_response = generate_completion(client, standard_prompt)

            # Save to database
            interaction_id = database.save_interaction(
                question=question,
                perspectives={},
                synthesis=None,
                user_id=user.user_id,
                topic_category=topic_category,
                standard_response=standard_response,
                surfaced_perspectives=False
            )

            st.markdown("---")
            st.subheader("Response")
            st.markdown(standard_response)
            st.info("This topic doesn't have significant controversy across communities, so a standard response was provided.")

        # Feedback form
        st.markdown("---")
        st.subheader("Feedback")
        with st.form("feedback_form"):
            if controversy_profile.should_surface_perspectives():
                accuracy_own = st.slider(
                    "How accurately does this represent your community's view?",
                    1, 5, 3
                )
                accuracy_other = st.slider(
                    "How accurately does this represent other communities?",
                    1, 5, 3
                )
            else:
                accuracy_own = None
                accuracy_other = None

            usefulness = st.slider("How useful was this response?", 1, 5, 3)
            prefer_multiple = st.selectbox(
                "Do you prefer seeing multiple perspectives?",
                ["Yes", "No", "Depends on topic"]
            )
            missing = st.text_input("Any perspectives missing?")
            comments = st.text_area("Additional comments")
            fb_submitted = st.form_submit_button("Submit Feedback")

        if fb_submitted:
            feedback = {
                "user_community": user.primary_community,
                "accuracy_own_community": accuracy_own,
                "accuracy_other_communities": accuracy_other,
                "usefulness": usefulness,
                "prefer_multiple_perspectives": prefer_multiple,
                "missing_perspectives": missing,
                "comments": comments,
            }
            database.save_feedback(interaction_id, feedback)
            st.success("Thank you for your feedback!")

    # Sidebar: Recent interactions
    st.sidebar.markdown("---")
    st.sidebar.header("Recent Queries")
    recent = database.fetch_interactions(5, user_id=user.user_id)
    if recent:
        for it in recent:
            st.sidebar.markdown(f"- {it['question'][:50]}...")
    else:
        st.sidebar.markdown("*No recent queries*")


if __name__ == "__main__":
    main()
