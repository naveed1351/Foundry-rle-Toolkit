"""
EvalDataset — append-only store of scored episodes, backed by a local
JSONL file by default. Each record captures everything you'd need to
debug a low score, regenerate a rubric breakdown, or hand a batch off to
Agent Optimizer / a fine-tuning job later.
"""

from __future__ import annotations

import dataclasses
import json
import math
import statistics
from pathlib import Path
from typing import Any, Optional


@dataclasses.dataclass
class EvalRecord:
    episode_id: str
    task: dict
    transcript: list[dict]
    score: Optional[float]
    breakdown: dict
    trace_id: Optional[str] = None
    metadata: dict = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.score is None:
            return
        if (
            not isinstance(self.score, (int, float))
            or isinstance(self.score, bool)
            or not math.isfinite(self.score)
            or not 0.0 <= self.score <= 1.0
        ):
            raise ValueError("score must be a finite number between 0.0 and 1.0, or None.")

    def to_json(self) -> str:
        return json.dumps(dataclasses.asdict(self))

    @classmethod
    def from_json(cls, line: str) -> "EvalRecord":
        return cls(**json.loads(line))


class EvalDataset:
    """
    Append-only JSONL-backed dataset of EvalRecords.

    Usage:
        ds = EvalDataset("runs/2026-08-28.jsonl")
        ds.append(record)
        ds.load()                 # read all records back
        ds.mean_score()
        ds.worst(n=5)
        ds.filter(lambda r: r.score is not None and r.score < 0.5)
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, record: EvalRecord) -> None:
        with self.path.open("a") as f:
            f.write(record.to_json() + "\n")

    def load(self) -> list[EvalRecord]:
        if not self.path.exists():
            return []
        with self.path.open() as f:
            return [EvalRecord.from_json(line) for line in f if line.strip()]

    def mean_score(self) -> Optional[float]:
        scores = [r.score for r in self.load() if r.score is not None]
        if not scores:
            return None
        return statistics.mean(scores)

    def score_distribution(self, buckets: int = 5) -> dict[str, int]:
        scores = [r.score for r in self.load() if r.score is not None]
        counts = {f"{i/buckets:.1f}-{(i+1)/buckets:.1f}": 0 for i in range(buckets)}
        for s in scores:
            idx = min(int(s * buckets), buckets - 1)
            key = f"{idx/buckets:.1f}-{(idx+1)/buckets:.1f}"
            counts[key] += 1
        return counts

    def worst(self, n: int = 5) -> list[EvalRecord]:
        scored = [r for r in self.load() if r.score is not None]
        return sorted(scored, key=lambda r: r.score)[:n]

    def unscored(self) -> list[EvalRecord]:
        return [r for r in self.load() if r.score is None]

    def filter(self, predicate) -> list[EvalRecord]:
        return [r for r in self.load() if predicate(r)]

    def __len__(self) -> int:
        return len(self.load())
