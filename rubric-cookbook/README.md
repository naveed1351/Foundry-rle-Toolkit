# Rubric cookbook

The hardest part of turning a workflow into an RLE isn't the `reset/step/state` wrapper — it's writing a rubric that actually captures the outcome you care about. This folder collects reusable patterns, in increasing order of difficulty and cost.

A rubric is just a function: `(transcript) -> score`. Nothing here is Foundry-specific — you can unit-test rubrics entirely offline before ever pointing them at a real agent run.

## Pick a pattern

| Pattern | File | Use when | Cost | Reliability |
|---|---|---|---|---|
| Deterministic check | [`deterministic.py`](./deterministic.py) | Outcome is verifiable by code: did the SQL query run, does the output match a schema, is the number correct | Near-zero | Very high |
| Reference comparison | [`reference_comparison.py`](./reference_comparison.py) | You have a known-good answer to compare against (exact match, fuzzy match, embedding similarity) | Low | High |
| LLM-judge | [`llm_judge.py`](./llm_judge.py) | Outcome is qualitative (helpfulness, tone, correctness of free-form reasoning) and no reference answer exists | Medium (extra model call per score) | Medium — needs calibration |
| Composite / weighted | [`composite.py`](./composite.py) | Real workflows usually need more than one signal (e.g. "resolved the ticket" AND "stayed within 5 turns" AND "didn't use a disallowed tool") | Sum of parts | As good as its weakest component |

## Rules of thumb

1. **Prefer deterministic checks wherever the outcome allows it.** If you can verify correctness with code (a regex, a schema check, a database query result), do that before reaching for an LLM judge. Deterministic rubrics are cheap, reproducible, and don't drift.
2. **Never let the rubric and the agent share a prompt or a model instance.** An LLM judge should be a clean, separate call — otherwise you risk the agent's own reasoning "convincing" the judge.
3. **Calibrate LLM judges against a small human-labeled set before trusting them.** Run the judge against 20-50 transcripts you've scored by hand; if the judge disagrees with you more than ~15-20% of the time, tighten the judge's prompt before using it to drive optimization.
4. **Rubrics should be able to return "unscored", not just a number.** Some transcripts are genuinely ambiguous or out of scope — returning `None` and excluding them from training/optimization is better than forcing a guess that adds noise.
4. **Version your rubrics.** A rubric change invalidates comparisons against prior optimizer runs. Treat rubric files like model config — check them into source control and reference the version in your eval dataset metadata.
5. **Watch for reward hacking.** If Agent Optimizer starts producing suspiciously high scores, check whether the agent found a shortcut that satisfies the rubric's letter but not its spirit (e.g. an agent that learns to just claim "task complete" if that's what the rubric checks for, rather than actually completing the task).

## Composite rubric example

Most real workflows need a composite, not a single check:

```python
from composite import CompositeRubric
from deterministic import task_completed_check
from llm_judge import helpfulness_judge

rubric = CompositeRubric(components=[
    (task_completed_check, 0.6),   # did it actually finish the job — weighted highest
    (helpfulness_judge, 0.3),      # was the interaction pleasant / clear
    (turn_count_penalty, 0.1),     # small penalty for excessive back-and-forth
])
```

See `3-worked-examples/` for full composite rubrics built for real workflows.
