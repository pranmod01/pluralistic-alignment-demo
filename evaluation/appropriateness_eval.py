"""
Appropriateness Evaluation

Measures whether the system correctly decides when to surface perspectives.
Computes precision and recall on the should_surface_perspectives decision.

Targets:
- Precision > 85%
- Recall > 80%
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.dataset import get_test_cases
from src.controversy import detect_controversy


def evaluate_appropriateness() -> dict:
    """
    Evaluate appropriateness of perspective surfacing decisions.

    Returns metrics:
    - precision: TP / (TP + FP)
    - recall: TP / (TP + FN)
    - accuracy: (TP + TN) / total
    - confusion matrix details
    """
    test_cases = get_test_cases()

    true_positives = 0
    true_negatives = 0
    false_positives = 0
    false_negatives = 0

    results = []

    for tc in test_cases:
        query = tc["query_text"]
        expected_surface = tc["should_surface_perspectives"]

        # Get system decision
        controversy_profile, topic_category = detect_controversy(query)
        predicted_surface = controversy_profile.should_surface_perspectives()

        # Classify result
        if expected_surface and predicted_surface:
            true_positives += 1
            result = "TP"
        elif not expected_surface and not predicted_surface:
            true_negatives += 1
            result = "TN"
        elif not expected_surface and predicted_surface:
            false_positives += 1
            result = "FP"
        else:  # expected_surface and not predicted_surface
            false_negatives += 1
            result = "FN"

        results.append({
            "query_id": tc["query_id"],
            "query": query[:50] + "...",
            "expected": expected_surface,
            "predicted": predicted_surface,
            "result": result,
            "topic_category": topic_category,
        })

    # Calculate metrics
    total = len(test_cases)
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    accuracy = (true_positives + true_negatives) / total if total > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {
        "precision": precision,
        "recall": recall,
        "accuracy": accuracy,
        "f1_score": f1,
        "true_positives": true_positives,
        "true_negatives": true_negatives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "total_cases": total,
        "detailed_results": results,
        "target_precision": 0.85,
        "target_recall": 0.80,
        "meets_precision_target": precision >= 0.85,
        "meets_recall_target": recall >= 0.80,
    }


def print_report(metrics: dict):
    """Print a formatted evaluation report."""
    print("=" * 60)
    print("APPROPRIATENESS EVALUATION REPORT")
    print("=" * 60)
    print(f"\nTotal test cases: {metrics['total_cases']}")
    print(f"\nConfusion Matrix:")
    print(f"  True Positives:  {metrics['true_positives']}")
    print(f"  True Negatives:  {metrics['true_negatives']}")
    print(f"  False Positives: {metrics['false_positives']}")
    print(f"  False Negatives: {metrics['false_negatives']}")
    print(f"\nMetrics:")
    print(f"  Precision: {metrics['precision']:.2%} (target: >{metrics['target_precision']:.0%}) {'PASS' if metrics['meets_precision_target'] else 'FAIL'}")
    print(f"  Recall:    {metrics['recall']:.2%} (target: >{metrics['target_recall']:.0%}) {'PASS' if metrics['meets_recall_target'] else 'FAIL'}")
    print(f"  Accuracy:  {metrics['accuracy']:.2%}")
    print(f"  F1 Score:  {metrics['f1_score']:.2%}")

    # Show errors
    errors = [r for r in metrics['detailed_results'] if r['result'] in ['FP', 'FN']]
    if errors:
        print(f"\n{'='*60}")
        print("ERRORS (False Positives and False Negatives):")
        print("=" * 60)
        for err in errors:
            print(f"\n[{err['result']}] {err['query_id']}: {err['query']}")
            print(f"    Expected: {err['expected']}, Got: {err['predicted']}")
            print(f"    Detected topic: {err['topic_category']}")


if __name__ == "__main__":
    metrics = evaluate_appropriateness()
    print_report(metrics)
