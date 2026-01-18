"""
Community selection logic for perspective surfacing.

Implements the decision tree:
1. Always include user's own community perspective (baseline)
2. Select 1-2 additional communities based on:
   - Controversy profile (which dimensions are active)
   - Relevance to the specific topic
   - Significance of cleavage on this issue
"""

from dataclasses import dataclass
from typing import Optional

from controversy import ControversyProfile, ControversyLevel, get_controversy_dimensions
from communities import (
    Community, CommunityTier, get_community, get_community_name,
    TIER_1_COMMUNITIES, TIER_2_COMMUNITIES, TIER_5_COMMUNITIES
)


@dataclass
class UserProfile:
    """User profile with community affiliations from the dataset."""
    user_id: str
    primary_community_type: str
    primary_community: str
    community_strength: str
    secondary_community_type: Optional[str] = None
    secondary_community: Optional[str] = None
    secondary_strength: Optional[str] = None
    tertiary_community_type: Optional[str] = None
    tertiary_community: Optional[str] = None
    age_range: Optional[str] = None
    education: Optional[str] = None
    location: Optional[str] = None

    def get_communities(self) -> list[str]:
        """Get list of all user's communities."""
        communities = [self.primary_community]
        if self.secondary_community:
            communities.append(self.secondary_community)
        if self.tertiary_community:
            communities.append(self.tertiary_community)
        return communities

    def is_religious(self) -> bool:
        """Check if user has a religious primary affiliation."""
        return self.primary_community_type == "religious"

    def is_secular(self) -> bool:
        """Check if user has a secular primary affiliation."""
        return self.primary_community_type == "secular"

    def is_political(self) -> bool:
        """Check if user has a political primary affiliation."""
        return self.primary_community_type == "political"


@dataclass
class SelectedCommunities:
    """Result of community selection."""
    baseline: str  # User's primary community
    additional: list[str]  # 1-2 other communities to include
    rationale: str  # Why these were selected

    def all_communities(self) -> list[str]:
        """Get all selected communities including baseline."""
        return [self.baseline] + self.additional


# Topic to relevant community mappings
# These define which communities are most relevant for specific topics
TOPIC_COMMUNITY_MAPPINGS = {
    "reproductive_rights": {
        "religious": ["Catholic", "evangelical_protestant", "reform_jewish", "Muslim_Sunni"],
        "political": ["progressive", "conservative", "libertarian"],
        "identity": ["women", "feminist"],
    },
    "climate_environment": {
        "professional": ["climate_scientist", "environmental_scientist", "economist"],
        "political": ["progressive", "conservative", "libertarian", "environmentalist"],
        "regional": ["Global_South", "indigenous"],
    },
    "church_state_separation": {
        "religious": ["Muslim_Sunni", "Sikh", "evangelical_protestant", "Catholic"],
        "secular": ["atheist"],
        "political": ["progressive", "conservative", "libertarian"],
    },
    "food_ethics_animal_rights": {
        "religious": ["Hindu", "Buddhist", "Jain", "Muslim_Sunni", "Jewish_Orthodox"],
        "identity": ["vegetarian", "animal_rights_activist"],
        "professional": ["environmental_scientist"],
    },
    "economic_policy": {
        "political": ["progressive", "conservative", "libertarian", "socialist"],
        "professional": ["economist"],
        "identity": ["working_class", "labor_union"],
    },
    "LGBTQ_rights": {
        "religious": ["evangelical_protestant", "Catholic", "reform_jewish", "mainline_protestant"],
        "political": ["progressive", "conservative", "libertarian"],
        "identity": ["LGBTQ_gay"],
    },
    "gun_rights": {
        "political": ["progressive", "conservative", "libertarian"],
        "professional": ["law_enforcement"],
        "identity": ["gun_owner", "gun_violence_survivor", "parent"],
    },
    "indigenous_rights_environment": {
        "identity": ["indigenous", "local_community"],
        "political": ["progressive", "conservative", "libertarian", "environmentalist"],
        "professional": ["environmental_scientist"],
    },
    "immigration": {
        "political": ["progressive", "conservative", "libertarian"],
        "identity": ["immigrant", "second_generation"],
        "regional": ["border_community"],
        "professional": ["economist"],
    },
    "disability_rights": {
        "identity": ["neurodivergent", "parent_of_disabled", "disability_rights_advocate"],
        "professional": ["medical_researcher", "educator"],
    },
    "gender_religious_freedom": {
        "religious": ["Muslim_Sunni", "Sikh"],
        "political": ["progressive", "conservative", "libertarian"],
        "identity": ["feminist", "women"],
    },
    "religious_law": {
        "religious": ["Muslim_Sunni", "Catholic", "Jewish_Orthodox", "evangelical_protestant"],
        "secular": ["atheist"],
        "political": ["progressive", "conservative", "libertarian"],
    },
}


def select_communities(
    user: UserProfile,
    controversy_profile: ControversyProfile,
    topic_category: Optional[str],
    max_additional: int = 2
) -> SelectedCommunities:
    """
    Select which communities' perspectives to surface.

    Args:
        user: User's profile with community affiliations
        controversy_profile: Controversy profile from detection
        topic_category: Detected topic category (e.g., "reproductive_rights")
        max_additional: Maximum additional communities beyond baseline

    Returns:
        SelectedCommunities with baseline and additional perspectives
    """
    baseline = user.primary_community
    additional = []
    rationale_parts = []

    # If no perspectives should be surfaced, return only baseline
    if not controversy_profile.should_surface_perspectives():
        return SelectedCommunities(
            baseline=baseline,
            additional=[],
            rationale="Low controversy topic; standard response provided."
        )

    # Get active controversy dimensions
    active_dimensions = get_controversy_dimensions(controversy_profile)

    # Get relevant communities for this topic
    topic_communities = TOPIC_COMMUNITY_MAPPINGS.get(topic_category, {})

    # Determine which types of communities to include based on controversy
    candidates = []

    # Always consider opposing viewpoints based on user's primary type
    if controversy_profile.religious in {ControversyLevel.MEDIUM, ControversyLevel.HIGH}:
        if user.is_religious():
            # Add secular perspective
            if "atheist" not in user.get_communities():
                candidates.append(("secular_progressive", "secular counterpoint"))
        else:
            # Add religious perspectives
            religious_options = topic_communities.get("religious", ["Catholic", "evangelical_protestant"])
            for comm in religious_options:
                if comm not in user.get_communities():
                    candidates.append((comm, "religious perspective"))
                    break

    if controversy_profile.political in {ControversyLevel.MEDIUM, ControversyLevel.HIGH}:
        # Add opposing political perspective
        user_politics = None
        if user.primary_community_type == "political":
            user_politics = user.primary_community
        elif user.secondary_community_type == "political":
            user_politics = user.secondary_community

        if user_politics in ["progressive", "socialist"]:
            candidates.append(("conservative", "conservative political perspective"))
        elif user_politics in ["conservative"]:
            candidates.append(("progressive", "progressive political perspective"))
        elif user_politics == "libertarian":
            # Libertarians get both mainstream perspectives
            candidates.append(("progressive", "progressive perspective"))
            candidates.append(("conservative", "conservative perspective"))
        else:
            # Default: add progressive and conservative
            candidates.append(("progressive", "progressive perspective"))

    # Add identity communities if directly affected
    identity_communities = topic_communities.get("identity", [])
    for identity_comm in identity_communities:
        if identity_comm in user.get_communities():
            # User is directly affected - elevate their voice
            rationale_parts.append(f"User is directly affected as {get_community_name(identity_comm)}")
        else:
            # Consider adding affected community perspective
            community = get_community(identity_comm)
            if community and community.tier == CommunityTier.TIER_5_IDENTITY:
                candidates.append((identity_comm, f"{get_community_name(identity_comm)} perspective (affected community)"))

    # Add professional/expert perspective if relevant
    professional_communities = topic_communities.get("professional", [])
    for prof_comm in professional_communities:
        if prof_comm not in user.get_communities():
            candidates.append((prof_comm, f"{get_community_name(prof_comm)} expertise"))
            break

    # Select top candidates (avoiding duplicates with user's communities)
    seen = set(user.get_communities())
    for candidate, reason in candidates:
        if candidate not in seen and len(additional) < max_additional:
            additional.append(candidate)
            rationale_parts.append(f"Added {get_community_name(candidate)}: {reason}")
            seen.add(candidate)

    # Build rationale
    rationale = f"Topic has {', '.join(active_dimensions)} controversy. "
    if rationale_parts:
        rationale += " ".join(rationale_parts)

    return SelectedCommunities(
        baseline=baseline,
        additional=additional,
        rationale=rationale
    )


def parse_selected_communities_string(communities_str: str) -> list[str]:
    """Parse comma-separated community string from dataset."""
    if not communities_str or communities_str == "N/A":
        return []
    return [c.strip() for c in communities_str.split(",")]
