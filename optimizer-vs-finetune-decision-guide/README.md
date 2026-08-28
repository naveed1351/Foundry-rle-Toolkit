# Optimizer vs. fine-tune: a decision guide

Once you have a scored eval dataset (see `eval-harness/`), you have two branches available on Foundry: **non-parametric** tuning (Agent Optimizer / SkillOpt) or **parametric** tuning (Frontier Tuning / reinforcement fine-tuning, via Tinker + ECHO on your OpenEnv environment). This guide is for deciding between them — most teams should default to the left branch and only move right when they've actually hit its ceiling.

## The short version

**Start with Agent Optimizer. Move to fine-tuning only when you've exhausted it and the economics justify the jump.**

## Decision flow

```
Do you have a scored eval dataset with 30+ examples?
  NO  -> Stop. Build the dataset first (eval-harness/). Neither
         branch works without real signal.
  YES -> continue

Have you run Agent Optimizer / SkillOpt yet?
  NO  -> Run it first. It's cheap, fast, reversible, and often
         closes most of the gap on its own.
  YES -> continue

After optimization, is quality still below your bar?
  NO  -> Ship it. You're done — no need to fine-tune.
  YES -> continue

Is the gap caused by something a prompt/tool/model swap
structurally cannot fix (e.g. the task requires internalized
judgment or domain knowledge no amount of instruction conveys)?
  NO  -> Go back to Agent Optimizer with a revised rubric or
         tool set. You likely have a rubric problem, not a
         model-capability problem.
  YES -> continue

Do the unit economics justify it? (see cost model below)
  NO  -> Stay on Agent Optimizer's output; accept the quality
         ceiling or reduce scope.
  YES -> Move to Frontier Tuning (RFT) using your RLE.
```

## Why default to non-parametric

- **Cost**: Agent Optimizer iterations are prompt/tool/model changes — no training run, no GPU cost, results in minutes to hours.
- **Reversibility**: a bad optimizer output is just... don't deploy it. A bad fine-tune is a model you now own and have to manage the lifecycle of.
- **Model independence**: staying non-parametric keeps you free to swap the underlying model as better ones become available — the "loop is the asset, not the model" principle from `docs/architecture.md`.
- **Diagnostic value**: if Agent Optimizer can't improve your score, that's often a sign your rubric is measuring the wrong thing, not that you need a bigger hammer. Check the rubric before you check the model.

## When fine-tuning earns its cost

Fine-tuning tends to pay off when:

- You've already run several Agent Optimizer cycles and quality has plateaued below your bar.
- The task requires implicit judgment that's hard to spell out in a prompt (e.g. "does this response match our house style" after many edge cases), rather than a fact a prompt can just state.
- You run this workflow at high enough volume that **token cost per request** matters — reported real-world numbers put a fine-tuned agent's cost at roughly a third of the equivalent prompted approach for the same task (Microsoft's own case study reported a drop from about $0.0998 to $0.0310 per scenario). At low volume this saving won't offset the fine-tuning investment; at high volume it can be the deciding factor.
- Your OpenEnv environment (from `rle-template/`) is stable — if you're still actively changing what a "step" means or what `done` looks like, wait. Fine-tuning against a moving environment wastes runs.

## What you need before starting a fine-tune

1. A stable, versioned rubric (see `rubric-cookbook/README.md`'s "version your rubrics" rule) — changing it mid-training invalidates progress.
2. An eval dataset large enough to detect regressions, not just improvements (a few hundred scored episodes is a reasonable floor for most workflows; scale with task complexity).
3. A held-out test split your training loop never sees, so you can tell real improvement from overfitting to the training distribution.
4. Sign-off on the cost — Frontier Tuning runs are a real spend commitment even with Foundry's managed tooling; don't start one you can't finish evaluating.

## Common mistake to avoid

Jumping to fine-tuning because Agent Optimizer's first pass didn't help. Agent Optimizer usually needs 2-3 iterations with rubric refinement between them before you've actually exhausted what prompt/tool tuning can do. Treat "optimizer didn't help" as a prompt to revisit the rubric, not as evidence you need to fine-tune.
