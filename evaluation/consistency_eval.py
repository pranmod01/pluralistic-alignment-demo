"""
Consistency Evaluation

Measures whether users from the same community asking similar queries
receive consistent perspective framings.

Uses semantic similarity (via embeddings) to compare perspective descriptions
across users in the same consistency group.

Target: > 85% similarity for same community-topic pairs
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from typing import Optional

from src.dataset import get_test_cases_by_consistency_group
from src.controversy import detect_controversy
from src.community_selection import select_communities


def evaluate_consistency_structure() -> dict:
    """
    Evaluate structural consistency of community selection.

    For users in the same consistency group:
    - Check if the same "other" communities are selected
    - Check if community selection is deterministic

    Note: Full semantic similarity evaluation requires running the model
    and computing embeddings, which is deferred to run_evaluation.py

    Returns:
    - group_results: Results per consistency group
    - structural_consistency: % of groups with identical community selection
    """
    groups = get_test_cases_by_consistency_group()

    group_results = []

    for group_name, cases in groups.items():
        if len(cases) < 2:
            # Need at least 2 cases to compare
            continue

        # Get community selections for each case
        selections = []
        for tc in cases:
            controversy_profile, topic_category = detect_controversy(tc["query_text"])
            selected = select_communities(
                user=tc["user_profile"],
                controversy_profile=controversy_profile,
                topic_category=topic_category
            )
            selections.append({
                "user_id": tc["user_profile"].user_id,
                "baseline": selected.baseline,
                "additional": sorted(selected.additional),
                "all": sorted(selected.all_communities()),
            })

        # Check if all users get the same "additional" communities
        # (baseline will differ as it's the user's own community)
        additional_sets = [tuple(s["additional"]) for s in selections]
        is_consistent = len(set(additional_sets)) == 1

        group_results.append({
            "group": group_name,
            "num_cases": len(cases),
            "is_structurally_consistent": is_consistent,
            "selections": selections,
            "unique_additional_patterns": len(set(additional_sets)),
        })

    consistent_groups = sum(1 for g in group_results if g["is_structurally_consistent"])
    total_groups = len(group_results)

    return {
        "total_consistency_groups": total_groups,
        "structurally_consistent_groups": consistent_groups,
        "structural_consistency_rate": consistent_groups / total_groups if total_groups > 0 else 0,
        "target_consistency": 0.85,
        "meets_target": (consistent_groups / total_groups if total_groups > 0 else 0) >= 0.85,
        "group_results": group_results,
    }


def print_report(metrics: dict):
    """Print a formatted evaluation report."""
    print("=" * 60)
    print("CONSISTENCY EVALUATION REPORT (Structural)")
    print("=" * 60)
    print(f"\nTotal consistency groups: {metrics['total_consistency_groups']}")
    print(f"Structurally consistent: {metrics['structurally_consistent_groups']}")
    print(f"\nStructural Consistency Rate: {metrics['structural_consistency_rate']:.2%} (target: >{metrics['target_consistency']:.0%}) {'PASS' if metrics['meets_target'] else 'FAIL'}")

    # Show inconsistent groups
    inconsistent = [g for g in metrics['group_results'] if not g['is_structurally_consistent']]
    if inconsistent:
        print(f"\n{'='*60}")
        print("INCONSISTENT GROUPS:")
        print("=" * 60)
        for group in inconsistent[:5]:  # Limit to first 5
            print(f"\nGroup: {group['group']}")
            print(f"  Cases: {group['num_cases']}")
            print(f"  Unique selection patterns: {group['unique_additional_patterns']}")
            for sel in group['selections']:
                print(f"    {sel['user_id']}: baseline={sel['baseline']}, additional={sel['additional']}")


if __name__ == "__main__":
    metrics = evaluate_consistency_structure()
    print_report(metrics)
