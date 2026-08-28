# Glossary

**Agent harness** — the runtime scaffolding around a model: the tool-calling loop, memory, guardrails, and orchestration code. The model is one component inside it.

**Hosted agent** — a Foundry Agent Service deployment where you supply your own orchestration code (e.g. Microsoft Agent Framework or LangChain) and Foundry runs it in a managed, per-session sandbox (Azure Container Apps) with state and filesystem access.

**RLE (Reinforcement Learning Environment)** — a codified practice space for an agent: the workflow steps, the tools it's allowed to use, the data it sees, and a rubric that scores outcomes. Built to the OpenEnv contract.

**OpenEnv** — a community standard (backed by Hugging Face, adopted by Microsoft) defining a minimal contract — `reset`, `step`, `state` — so any trainer, runtime, or model can talk to any environment without custom integration.

**Hill-climbing loop** — Microsoft's shorthand for practice → judge → learn, repeated: run the agent in an environment, score it against a rubric, improve it, repeat.

**Non-parametric learning** — improving an agent without touching model weights: tuning prompts, tool selection, and skills. Done via Agent Optimizer / SkillOpt. Cheap, fast, reversible.

**Parametric learning** — actually fine-tuning model weights (reinforcement fine-tuning / RFT) using Foundry post-training (Tinker + ECHO), grounded in an OpenEnv-compatible environment. Slower and more expensive, but can outperform prompt tuning once you've hit its ceiling.

**Rubric** — the function (deterministic code, an LLM judge, or a mix) that turns a completed agent run into a numeric or categorical score representing how well it achieved the desired outcome.

**Trace** — the OpenTelemetry record of everything that happened in one agent run: model calls, tool invocations, sub-agent hops, handoffs. The raw material an eval dataset and a rubric are built from.

**Agent Optimizer** — Foundry's closed-loop system that evaluates a hosted agent, generates candidate prompt/tool/model variations, ranks them against your rubric, and can deploy the winner.

**Frontier Tuning** — Foundry's managed on-ramp to parametric learning: reinforcement fine-tuning with better token efficiency, improved through real usage, without you having to build the RL infrastructure yourself.

**ECHO** — part of Foundry's post-training stack; reportedly reuses the majority of "discarded" trajectories from agent runs as a free world model input for training, rather than only training on winning runs.
