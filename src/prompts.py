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
