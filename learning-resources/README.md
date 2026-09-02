# Foundry RLE Learning Resources

This collection is a practical reading companion to the toolkit. It focuses on choices that determine whether an agent-learning loop produces trustworthy evidence: task boundaries, datasets, rewards, traces, evaluation, optimization, and escalation to fine-tuning.

## Start here

Read the notes in this order:

1. Establish the task and environment contract.
2. Build a small, representative dataset and a measurable rubric.
3. Instrument traces before optimizing anything.
4. Compare candidates against a fixed baseline and held-out cases.
5. Use the decision guides to determine whether prompt and tool optimization is sufficient.

## Primary references

- [Microsoft Foundry documentation](https://learn.microsoft.com/azure/foundry/)
- [Microsoft Foundry blog](https://devblogs.microsoft.com/foundry/)
- [OpenTelemetry documentation](https://opentelemetry.io/docs/)
- [OpenEnv](https://github.com/meta-pytorch/OpenEnv)

Each topic note states a concrete question to answer, the evidence to collect, and a failure mode to avoid. They complement the runnable template and worked examples rather than replacing them.