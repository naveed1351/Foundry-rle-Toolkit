"""
report.py — summarize an EvalDataset, and optionally compare two datasets
(e.g. before/after an Agent Optimizer run) to check whether a change
actually helped.

Usage:
    python report.py runs/2026-08-28.jsonl
    python report.py runs/2026-08-28.jsonl --compare runs/2026-08-29-post-optimize.jsonl
"""

from __future__ import annotations

import argparse

from dataset import EvalDataset


def print_report(path: str) -> None:
    ds = EvalDataset(path)
    records = ds.load()
    print(f"\n=== {path} ===")
    print(f"records: {len(records)}")
    print(f"unscored: {len(ds.unscored())}")
    mean = ds.mean_score()
    print(f"mean score: {mean:.3f}" if mean is not None else "mean score: n/a")
    print("score distribution:")
    for bucket, count in ds.score_distribution().items():
        bar = "#" * count
        print(f"  {bucket}: {bar} ({count})")

    print("\nworst 3 episodes:")
    for r in ds.worst(3):
        print(f"  episode={r.episode_id} score={r.score} trace_id={r.trace_id}")


def compare(path_a: str, path_b: str) -> None:
    ds_a, ds_b = EvalDataset(path_a), EvalDataset(path_b)
    mean_a, mean_b = ds_a.mean_score(), ds_b.mean_score()
    print(f"\n=== comparison ===")
    print(f"{path_a}: mean={mean_a}")
    print(f"{path_b}: mean={mean_b}")
    if mean_a is not None and mean_b is not None:
        delta = mean_b - mean_a
        direction = "improved" if delta > 0 else "regressed" if delta < 0 else "unchanged"
        print(f"delta: {delta:+.3f} ({direction})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Report on an EvalDataset.")
    parser.add_argument("path", type=str, help="Path to the JSONL dataset.")
    parser.add_argument("--compare", type=str, default=None, help="Second dataset to compare against.")
    args = parser.parse_args()

    print_report(args.path)
    if args.compare:
        print_report(args.compare)
        compare(args.path, args.compare)


if __name__ == "__main__":
    main()
