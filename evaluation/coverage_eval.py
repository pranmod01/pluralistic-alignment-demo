"""
Coverage Evaluation

Measures whether the system includes all relevant community perspectives.
Computes recall of ground truth communities in system selections.

Target: > 90% recall of major relevant perspectives
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.dataset import get_test_cases
from src.controversy import detect_controversy
from src.community_selection import select_communities, parse_selected_communities_string


def evaluate_coverage() -> dict:
    """
    Evaluate coverage of relevant community perspectives.

    For each test case where perspectives should be surfaced:
    - Parse expected communities from dataset
    - Get system's selected communities
    - Calculate recall: |intersection| / |expected|

    Returns:
    - mean_recall: Average recall across all cases
    - per_case_results: Detailed results per test case
    """
    test_cases = get_test_cases()

    recalls = []
    results = []

    for tc in test_cases:
        # Skip cases where no perspectives should be surfaced
        if not tc["should_surface_perspectives"]:
            continue

        query = tc["query_text"]
        user = tc["user_profile"]
        expected_communities = parse_selected_communities_string(tc["selected_communities"])

        if not expected_communities:
            continue

        # Get system's selection
        controversy_profile, topic_category = detect_controversy(query)
        selected = select_communities(
            user=user,
            controversy_profile=controversy_profile,
            topic_category=topic_category
        )
        predicted_communities = set(selected.all_communities())
        expected_set = set(expected_communities)

        # Calculate recall
        intersection = predicted_communities & expected_set
        recall = len(intersection) / len(expected_set) if expected_set else 1.0

        recalls.append(recall)

        results.append({
            "query_id": tc["query_id"],
            "query": query[:50] + "...",
            "expected": list(expected_set),
            "predicted": list(predicted_communities),
            "intersection": list(intersection),
            "missing": list(expected_set - predicted_communities),
            "extra": list(predicted_communities - expected_set),
            "recall": recall,
        })

    mean_recall = sum(recalls) / len(recalls) if recalls else 0

    return {
        "mean_recall": mean_recall,
        "total_cases": len(recalls),
        "perfect_coverage_cases": sum(1 for r in recalls if r == 1.0),
        "partial_coverage_cases": sum(1 for r in recalls if 0 < r < 1.0),
        "zero_coverage_cases": sum(1 for r in recalls if r == 0),
        "target_recall": 0.90,
        "meets_target": mean_recall >= 0.90,
        "detailed_results": results,
    }


def print_report(metrics: dict):
    """Print a formatted evaluation report."""
    print("=" * 60)
    print("COVERAGE EVALUATION REPORT")
    print("=" * 60)
    print(f"\nTotal test cases (with perspectives): {metrics['total_cases']}")
    print(f"\nCoverage Distribution:")
    print(f"  Perfect coverage (100%): {metrics['perfect_coverage_cases']}")
    print(f"  Partial coverage:        {metrics['partial_coverage_cases']}")
    print(f"  Zero coverage:           {metrics['zero_coverage_cases']}")
    print(f"\nMean Recall: {metrics['mean_recall']:.2%} (target: >{metrics['target_recall']:.0%}) {'PASS' if metrics['meets_target'] else 'FAIL'}")

    # Show cases with missing communities
    missing_cases = [r for r in metrics['detailed_results'] if r['missing']]
    if missing_cases:
        print(f"\n{'='*60}")
        print("CASES WITH MISSING COMMUNITIES:")
        print("=" * 60)
        for case in missing_cases[:10]:  # Limit to first 10
            print(f"\n{case['query_id']}: {case['query']}")
            print(f"  Expected:  {case['expected']}")
            print(f"  Got:       {case['predicted']}")
            print(f"  Missing:   {case['missing']}")
            print(f"  Recall:    {case['recall']:.2%}")


if __name__ == "__main__":
    metrics = evaluate_coverage()
    print_report(metrics)
