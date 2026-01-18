#!/usr/bin/env python3
"""
Run all evaluations for the Pluralistic Alignment Demo.

This script runs:
1. Appropriateness evaluation (should perspectives be surfaced?)
2. Coverage evaluation (are all relevant communities included?)
3. Consistency evaluation (do same community-topic pairs get same framing?)

Usage:
    python evaluation/run_evaluation.py [--verbose]
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory and src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from evaluation.appropriateness_eval import evaluate_appropriateness, print_report as print_appropriateness
from evaluation.coverage_eval import evaluate_coverage, print_report as print_coverage
from evaluation.consistency_eval import evaluate_consistency_structure, print_report as print_consistency


def run_all_evaluations(verbose: bool = False) -> dict:
    """Run all evaluation suites and return combined results."""
    print("\n" + "=" * 70)
    print(" PLURALISTIC ALIGNMENT DEMO - EVALUATION SUITE")
    print("=" * 70)
    print(f"\nTimestamp: {datetime.now().isoformat()}")

    results = {
        "timestamp": datetime.now().isoformat(),
        "evaluations": {},
        "summary": {},
    }

    # 1. Appropriateness Evaluation
    print("\n" + "-" * 70)
    print(" 1. APPROPRIATENESS EVALUATION")
    print("-" * 70)
    appropriateness = evaluate_appropriateness()
    results["evaluations"]["appropriateness"] = {
        "precision": appropriateness["precision"],
        "recall": appropriateness["recall"],
        "accuracy": appropriateness["accuracy"],
        "f1_score": appropriateness["f1_score"],
        "meets_precision_target": appropriateness["meets_precision_target"],
        "meets_recall_target": appropriateness["meets_recall_target"],
    }
    if verbose:
        print_appropriateness(appropriateness)
    else:
        status = "PASS" if appropriateness["meets_precision_target"] and appropriateness["meets_recall_target"] else "FAIL"
        print(f"  Precision: {appropriateness['precision']:.2%} (target >85%) {'PASS' if appropriateness['meets_precision_target'] else 'FAIL'}")
        print(f"  Recall:    {appropriateness['recall']:.2%} (target >80%) {'PASS' if appropriateness['meets_recall_target'] else 'FAIL'}")

    # 2. Coverage Evaluation
    print("\n" + "-" * 70)
    print(" 2. COVERAGE EVALUATION")
    print("-" * 70)
    coverage = evaluate_coverage()
    results["evaluations"]["coverage"] = {
        "mean_recall": coverage["mean_recall"],
        "total_cases": coverage["total_cases"],
        "meets_target": coverage["meets_target"],
    }
    if verbose:
        print_coverage(coverage)
    else:
        print(f"  Mean Recall: {coverage['mean_recall']:.2%} (target >90%) {'PASS' if coverage['meets_target'] else 'FAIL'}")
        print(f"  Cases evaluated: {coverage['total_cases']}")

    # 3. Consistency Evaluation
    print("\n" + "-" * 70)
    print(" 3. CONSISTENCY EVALUATION (Structural)")
    print("-" * 70)
    consistency = evaluate_consistency_structure()
    results["evaluations"]["consistency"] = {
        "structural_consistency_rate": consistency["structural_consistency_rate"],
        "total_groups": consistency["total_consistency_groups"],
        "consistent_groups": consistency["structurally_consistent_groups"],
        "meets_target": consistency["meets_target"],
    }
    if verbose:
        print_consistency(consistency)
    else:
        print(f"  Structural Consistency: {consistency['structural_consistency_rate']:.2%} (target >85%) {'PASS' if consistency['meets_target'] else 'FAIL'}")
        print(f"  Groups evaluated: {consistency['total_consistency_groups']}")

    # Summary
    print("\n" + "=" * 70)
    print(" SUMMARY")
    print("=" * 70)

    all_pass = (
        appropriateness["meets_precision_target"] and
        appropriateness["meets_recall_target"] and
        coverage["meets_target"] and
        consistency["meets_target"]
    )

    results["summary"] = {
        "all_targets_met": all_pass,
        "appropriateness_pass": appropriateness["meets_precision_target"] and appropriateness["meets_recall_target"],
        "coverage_pass": coverage["meets_target"],
        "consistency_pass": consistency["meets_target"],
    }

    print(f"\n  Appropriateness: {'PASS' if results['summary']['appropriateness_pass'] else 'FAIL'}")
    print(f"  Coverage:        {'PASS' if results['summary']['coverage_pass'] else 'FAIL'}")
    print(f"  Consistency:     {'PASS' if results['summary']['consistency_pass'] else 'FAIL'}")
    print(f"\n  Overall: {'ALL TARGETS MET' if all_pass else 'SOME TARGETS NOT MET'}")
    print("=" * 70 + "\n")

    return results


def save_results(results: dict, output_path: str):
    """Save evaluation results to JSON file."""
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Run evaluation suite for Pluralistic Alignment Demo")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser.add_argument("--output", "-o", type=str, help="Save results to JSON file")
    args = parser.parse_args()

    results = run_all_evaluations(verbose=args.verbose)

    if args.output:
        save_results(results, args.output)


if __name__ == "__main__":
    main()
