"""
Prompt templates for perspective generation.

V1 MVP: Community-specific perspective prompts with explicit framing.
"""

from communities import get_community_name, CommunityTier, get_community


# Template for generating a perspective from a specific community
COMMUNITY_PERSPECTIVE_PROMPT = """You are providing the perspective of {community_name} on a question.

Guidelines:
- Present views commonly held within the {community_name} community
- Acknowledge internal diversity where it exists (not all members think alike)
- Reference relevant sources, values, or reasoning typical of this community
- Be respectful and accurate - do not caricature or stereotype
- Focus on how this community typically approaches this issue
- 2-3 paragraphs

Question: {question}

Perspective from {community_name}:"""


# Template for composite identity (user's full identity with multiple communities)
# NOTE: This is kept for "intersectional mode" but the default is now "communal navigation mode"
COMPOSITE_IDENTITY_PROMPT = """You are providing the perspective of someone who identifies as {identity_description} on a question.

Guidelines:
- Present views that reflect this specific intersection of identities
- Show how these different aspects of identity might interact or create nuance on this issue
- Acknowledge that not everyone with these identities agrees, but focus on common threads
- Be respectful and accurate - do not caricature or stereotype
- Focus on the reasoning and values that emerge from this particular combination
- 2-3 paragraphs

Question: {question}

Perspective from a {identity_description} viewpoint:"""


# =============================================================================
# COMMUNAL NAVIGATION MODE PROMPTS
# These prompts speak FROM communities the user belongs to, not AS the user
# =============================================================================

# Template for speaking as an external community the user belongs to
COMMUNAL_VOICE_PROMPT = """You are representing the voice of the {community_name} community on a question.

IMPORTANT: You are speaking AS the community itself - as an external social group - NOT as an individual member or as the user personally. Present how this community collectively tends to view this issue.

Guidelines:
- Speak in the voice of the community: "Within {community_name}, the prevailing view is..." or "The {community_name} community generally holds that..."
- Present the mainstream or dominant perspective within this community
- Acknowledge internal diversity briefly, but focus on the core communal stance
- Reference shared values, traditions, texts, or reasoning that shape this community's view
- Be respectful and accurate - represent the community fairly
- 2-3 paragraphs

Question: {question}

The {community_name} community's perspective:"""


# Template for identifying tensions between a user's multiple communities
TENSIONS_PROMPT = """A person belongs to the following communities: {communities_list}

Given their question below, identify any tensions or conflicts that might arise between these communities' perspectives on this issue.

Guidelines:
- Focus ONLY on tensions between the communities listed above (the user's actual communities)
- Be specific about which communities are in tension and why
- Explain the nature of the disagreement (values, priorities, interpretations, etc.)
- Help the user understand how to navigate between these communal expectations
- If there are no significant tensions on this particular issue, say so briefly
- Be concise: 1-2 paragraphs

Question: {question}

Communities: {communities_list}

Tensions between your communities on this issue:"""


# Template for the lead/primary community perspective (most relevant to the question)
LEAD_COMMUNITY_PROMPT = """You are representing the voice of the {community_name} community on a question. This is the user's primary relevant community for this particular question.

IMPORTANT: You are speaking AS the community itself - as an external social group - NOT as an individual member. Present how this community collectively tends to view this issue.

Guidelines:
- Speak in the voice of the community: "Within {community_name}..." or "The {community_name} tradition holds that..."
- Present the mainstream or dominant perspective within this community
- This is the PRIMARY perspective for this user on this question, so be thorough
- Reference shared values, traditions, texts, or reasoning that shape this community's view
- Acknowledge internal diversity briefly where relevant
- Be respectful and accurate - represent the community fairly
- 2-3 paragraphs

Question: {question}

The {community_name} community's perspective:"""


# Template for religious community perspectives
RELIGIOUS_PERSPECTIVE_PROMPT = """You are providing the perspective of {community_name} traditions on a question.

Guidelines:
- Present views commonly held within {community_name} traditions
- Acknowledge internal diversity (different denominations, schools of thought, reform vs traditional)
- Reference relevant religious texts, teachings, or philosophical frameworks where appropriate
- Be respectful and accurate - do not flatten to a single "official" position
- Focus on the ethical and moral reasoning typical of this tradition
- 2-3 paragraphs

Question: {question}

Perspective from {community_name}:"""


# Template for political/ideological perspectives
POLITICAL_PERSPECTIVE_PROMPT = """You are providing the perspective commonly held by those with {community_name} political views on a question.

Guidelines:
- Present views commonly held within {community_name} political philosophy
- Acknowledge internal diversity (moderates vs. more committed adherents)
- Reference relevant political values, principles, or policy frameworks
- Be respectful and accurate - avoid partisan caricatures
- Focus on the reasoning and values behind this political perspective
- 2-3 paragraphs

Question: {question}

Perspective from {community_name}:"""


# Template for identity/experience-based perspectives
IDENTITY_PERSPECTIVE_PROMPT = """You are providing the perspective commonly held within the {community_name} community on a question.

Guidelines:
- Present views informed by the lived experience of {community_name}
- Acknowledge diversity within this community (not all members share identical views)
- Focus on how this community's experience shapes their perspective on this issue
- Be respectful and center the voices and concerns of this community
- Avoid speaking over or stereotyping the community
- 2-3 paragraphs

Question: {question}

Perspective from {community_name}:"""


# Template for professional/expert perspectives
PROFESSIONAL_PERSPECTIVE_PROMPT = """You are providing the perspective of {community_name} on a question based on their professional expertise.

Guidelines:
- Present the evidence-based or professional consensus view where one exists
- Acknowledge areas of ongoing debate or uncertainty within the field
- Reference relevant research, professional standards, or methodological approaches
- Distinguish between scientific/professional consensus and policy recommendations
- Be accurate and grounded in the actual state of knowledge in this field
- 2-3 paragraphs

Question: {question}

Perspective from {community_name}:"""


# Synthesis prompt for combining perspectives
SYNTHESIS_PROMPT = """Given the following perspectives from different communities on a question, write a brief synthesis (1 paragraph) noting:
- Key areas where these perspectives converge or share common ground
- Key areas of divergence and the reasoning behind different positions
- Any nuances or complexities worth highlighting
- Avoid taking sides; present the landscape of views fairly

{perspectives}

Synthesis:"""


# Standard response prompt (when perspectives not needed)
STANDARD_PROMPT = """Answer the following question in a helpful, accurate, and balanced way.

Question: {question}"""


def get_perspective_prompt(community_id: str, question: str) -> str:
    """
    Get the appropriate prompt template for a community.

    Args:
        community_id: The community identifier
        question: The user's question

    Returns:
        Formatted prompt string
    """
    community = get_community(community_id)
    community_name = get_community_name(community_id)

    # Select template based on community tier
    if community:
        if community.tier == CommunityTier.TIER_1_RELIGIOUS:
            template = RELIGIOUS_PERSPECTIVE_PROMPT
        elif community.tier == CommunityTier.TIER_2_POLITICAL:
            template = POLITICAL_PERSPECTIVE_PROMPT
        elif community.tier == CommunityTier.TIER_4_PROFESSIONAL:
            template = PROFESSIONAL_PERSPECTIVE_PROMPT
        elif community.tier == CommunityTier.TIER_5_IDENTITY:
            template = IDENTITY_PERSPECTIVE_PROMPT
        else:
            template = COMMUNITY_PERSPECTIVE_PROMPT
    else:
        # Fallback for unknown communities
        template = COMMUNITY_PERSPECTIVE_PROMPT

    return template.format(community_name=community_name, question=question)


def get_composite_identity_prompt(communities: list[str], question: str) -> str:
    """
    Get a prompt for a composite identity combining multiple communities.
    NOTE: This is for "intersectional mode" - kept as alternative to communal navigation.

    Args:
        communities: List of community IDs representing the user's identity
        question: The user's question

    Returns:
        Formatted prompt string for composite identity
    """
    if not communities:
        return STANDARD_PROMPT.format(question=question)

    if len(communities) == 1:
        return get_perspective_prompt(communities[0], question)

    # Build identity description from communities
    community_names = [get_community_name(c) for c in communities if c]
    identity_description = " ".join(community_names)

    return COMPOSITE_IDENTITY_PROMPT.format(
        identity_description=identity_description,
        question=question
    )


# =============================================================================
# COMMUNAL NAVIGATION MODE FUNCTIONS
# =============================================================================

def get_communal_voice_prompt(community_id: str, question: str, is_lead: bool = False) -> str:
    """
    Get a prompt that speaks AS a community (external voice), not as an individual.

    Args:
        community_id: The community identifier
        question: The user's question
        is_lead: Whether this is the primary/most relevant community for this question

    Returns:
        Formatted prompt string for communal voice
    """
    community_name = get_community_name(community_id)

    if is_lead:
        return LEAD_COMMUNITY_PROMPT.format(
            community_name=community_name,
            question=question
        )
    else:
        return COMMUNAL_VOICE_PROMPT.format(
            community_name=community_name,
            question=question
        )


def get_tensions_prompt(communities: list[str], question: str) -> str:
    """
    Get a prompt to identify tensions between a user's communities on an issue.

    Args:
        communities: List of community IDs the user belongs to
        question: The user's question

    Returns:
        Formatted prompt string for tensions analysis
    """
    if len(communities) < 2:
        return None  # No tensions possible with single community

    community_names = [get_community_name(c) for c in communities if c]
    communities_list = ", ".join(community_names)

    return TENSIONS_PROMPT.format(
        communities_list=communities_list,
        question=question
    )


def format_synthesis_prompt(perspectives: dict[str, str]) -> str:
    """
    Format the synthesis prompt with all perspectives.

    Args:
        perspectives: Dict mapping community_id to perspective text

    Returns:
        Formatted synthesis prompt
    """
    perspective_texts = []
    for community_id, text in perspectives.items():
        community_name = get_community_name(community_id)
        perspective_texts.append(f"**{community_name}**: {text}")

    return SYNTHESIS_PROMPT.format(perspectives="\n\n".join(perspective_texts))
