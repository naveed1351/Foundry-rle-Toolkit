"""
Composite rubric pattern — combine multiple rubrics (deterministic,
reference-comparison, LLM-judge) into a single weighted score. Most real
workflows need this: a single check rarely captures "did a good job".
"""

from __future__ import annotations

from typing import Callable, Optional

RubricFn = Callable[[list], Optional[float]]


class CompositeRubric:
    """
    Combines several rubric functions into one weighted score.

    Parameters
    ----------
    components:
        List of (rubric_fn, weight) tuples. Weights don't need to sum to 1
        — they're normalized automatically over whichever components
        actually returned a score for a given transcript.
    require_all:
        If True, the composite returns None (unscored) when any component
        returns None. If False (default), missing components are simply
        excluded and remaining weights renormalized — use this for
        components that are legitimately not always applicable.
    """

    def __init__(self, components: list[tuple[RubricFn, float]], require_all: bool = False):
        self.components = components
        self.require_all = require_all

    def __call__(self, transcript: list[dict]) -> Optional[float]:
        scored = []
        for rubric_fn, weight in self.components:
            score = rubric_fn(transcript)
            if score is None:
                if self.require_all:
                    return None
                continue
            scored.append((score, weight))

        if not scored:
            return None

        total_weight = sum(w for _, w in scored)
        if total_weight == 0:
            return None

        return sum(s * w for s, w in scored) / total_weight

    def breakdown(self, transcript: list[dict]) -> dict:
        """
        Returns the per-component scores (not just the final number) —
        use this in eval-harness/ reports and when debugging why a
        transcript scored the way it did. Component functions without a
        __name__ (e.g. lambdas) are indexed by position instead.
        """
        result = {}
        for i, (rubric_fn, weight) in enumerate(self.components):
            name = getattr(rubric_fn, "__name__", f"component_{i}")
            result[name] = {"score": rubric_fn(transcript), "weight": weight}
        return result
