import streamlit as st
import os
import json
from datetime import datetime

import prompts
import database
import config

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


def get_client():
    if OpenAI is None:
        return None
    if not config.OPENAI_API_KEY:
        return None
    return OpenAI(api_key=config.OPENAI_API_KEY)


def generate_completion(client, prompt: str, max_tokens: int = 800):
    if client is None:
        return "[OpenAI client not configured: set OPENAI_API_KEY env var and install the `openai` package]"
    try:
        resp = client.chat.completions.create(
            model=config.GPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"[Error calling OpenAI API: {e}]"


def main():
    st.set_page_config(page_title="Pluralistic Alignment Demo", layout="wide")
    st.title("Pluralistic AI Alignment — Religious Perspectives Demo")

    st.markdown("Enter a question where worldview matters (e.g., 'Is it wrong to eat meat?').")

    with st.form("question_form"):
        question = st.text_area("Question", height=80)
        comparison_mode = st.checkbox("Show standard single-answer for comparison")
        submitted = st.form_submit_button("Generate responses")

    database.init_db()

    client = get_client()

    if submitted and question.strip():
        with st.spinner("Generating perspectives..."):
            perspectives = {}
            for tradition in prompts.TRADITIONS:
                prompt_text = prompts.PERSPECTIVE_PROMPT.format(tradition=tradition, question=question)
                out = generate_completion(client, prompt_text)
                perspectives[tradition] = out

            synthesis_prompt = prompts.SYNTHESIS_PROMPT.format(perspectives="\n\n".join([f"{t}: {p}" for t, p in perspectives.items()]))
            synthesis = generate_completion(client, synthesis_prompt)

            standard_response = None
            if comparison_mode:
                standard_prompt = prompts.STANDARD_PROMPT.format(question=question)
                standard_response = generate_completion(client, standard_prompt)

            # save to DB
            interaction_id = database.save_interaction(question, perspectives, synthesis, standard_response)

        # Display responses
        st.markdown("---")
        st.subheader("Perspectives")
        cols = st.columns(len(perspectives))
        for i, (tradition, text) in enumerate(perspectives.items()):
            with cols[i]:
                st.header(tradition)
                st.write(text)

        st.markdown("---")
        st.subheader("Synthesis")
        st.write(synthesis)

        if comparison_mode:
            st.markdown("---")
            st.subheader("Standard AI Answer (for comparison)")
            st.write(standard_response)

        # Feedback form
        st.markdown("---")
        st.subheader("Feedback")
        with st.form("feedback_form"):
            tradition_identify = st.selectbox("Which tradition do you identify with?", ["Hindu", "Buddhist", "Jain", "Sikh", "Other", "None"])
            accuracy = st.slider("How accurately does this represent your selected tradition?", 1, 5, 3)
            usefulness = st.slider("Was this useful to you?", 1, 5, 4)
            prefer_single = st.selectbox("Would you prefer this over a single AI answer?", ["Yes", "No", "Depends"])
            comments = st.text_area("What's missing or wrong?")
            fb_submitted = st.form_submit_button("Submit feedback")

        if fb_submitted:
            feedback = {
                "tradition_identify": tradition_identify,
                "accuracy": accuracy,
                "usefulness": usefulness,
                "prefer_single": prefer_single,
                "comments": comments,
            }
            database.save_feedback(interaction_id, feedback)
            st.success("Thanks — feedback saved.")

    # Sidebar: recent interactions
    st.sidebar.header("Recent interactions")
    all_inter = database.fetch_interactions(10)
    for it in all_inter:
        st.sidebar.markdown(f"**{it['question'][:60]}**")


if __name__ == "__main__":
    main()
