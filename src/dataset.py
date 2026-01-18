"""
Dataset loader for the synthetic evaluation dataset.

Loads user profiles and queries from the CSV file for testing
and evaluation purposes.
"""

import csv
from typing import Optional

from config import DATASET_PATH
from community_selection import UserProfile


def load_dataset() -> list[dict]:
    """Load the full synthetic dataset."""
    records = []
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    return records


def get_user_profile(user_id: str) -> Optional[UserProfile]:
    """Get a user profile by user_id from the dataset."""
    records = load_dataset()
    for record in records:
        if record["user_id"] == user_id:
            return UserProfile(
                user_id=record["user_id"],
                primary_community_type=record["primary_community_type"],
                primary_community=record["primary_community"],
                community_strength=record["community_strength"],
                secondary_community_type=record.get("secondary_community_type") or None,
                secondary_community=record.get("secondary_community") or None,
                secondary_strength=record.get("secondary_strength") or None,
                tertiary_community_type=record.get("tertiary_community_type") or None,
                tertiary_community=record.get("tertiary_community") or None,
                age_range=record.get("age_range") or None,
                education=record.get("education") or None,
                location=record.get("location") or None,
            )
    return None


def get_all_user_profiles() -> list[UserProfile]:
    """Get all unique user profiles from the dataset."""
    records = load_dataset()
    seen_users = set()
    profiles = []

    for record in records:
        user_id = record["user_id"]
        if user_id not in seen_users:
            seen_users.add(user_id)
            profiles.append(UserProfile(
                user_id=record["user_id"],
                primary_community_type=record["primary_community_type"],
                primary_community=record["primary_community"],
                community_strength=record["community_strength"],
                secondary_community_type=record.get("secondary_community_type") or None,
                secondary_community=record.get("secondary_community") or None,
                secondary_strength=record.get("secondary_strength") or None,
                tertiary_community_type=record.get("tertiary_community_type") or None,
                tertiary_community=record.get("tertiary_community") or None,
                age_range=record.get("age_range") or None,
                education=record.get("education") or None,
                location=record.get("location") or None,
            ))

    return profiles


def get_test_cases() -> list[dict]:
    """
    Get all test cases from the dataset.

    Each test case includes:
    - user profile
    - query
    - expected behavior (should_surface_perspectives, selected_communities)
    - consistency group for evaluation
    """
    records = load_dataset()
    test_cases = []

    for record in records:
        user_profile = UserProfile(
            user_id=record["user_id"],
            primary_community_type=record["primary_community_type"],
            primary_community=record["primary_community"],
            community_strength=record["community_strength"],
            secondary_community_type=record.get("secondary_community_type") or None,
            secondary_community=record.get("secondary_community") or None,
            secondary_strength=record.get("secondary_strength") or None,
            tertiary_community_type=record.get("tertiary_community_type") or None,
            tertiary_community=record.get("tertiary_community") or None,
            age_range=record.get("age_range") or None,
            education=record.get("education") or None,
            location=record.get("location") or None,
        )

        test_cases.append({
            "user_profile": user_profile,
            "query_id": record["query_id"],
            "query_text": record["query_text"],
            "topic_category": record["topic_category"],
            "controversy_religious": record["controversy_religious"],
            "controversy_political": record["controversy_political"],
            "controversy_regional": record["controversy_regional"],
            "should_surface_perspectives": record["should_surface_perspectives"] == "yes",
            "selected_communities": record["selected_communities"],
            "consistency_group": record["consistency_group"],
            "notes": record.get("notes", ""),
        })

    return test_cases


def get_test_cases_by_consistency_group() -> dict[str, list[dict]]:
    """Group test cases by their consistency group for consistency evaluation."""
    test_cases = get_test_cases()
    groups = {}

    for tc in test_cases:
        group = tc["consistency_group"]
        if group not in groups:
            groups[group] = []
        groups[group].append(tc)

    return groups
