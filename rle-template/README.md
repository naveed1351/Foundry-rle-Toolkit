# rle-template

A minimal OpenEnv-compatible wrapper around a Microsoft Foundry hosted agent. Copy this folder as the starting point for turning your own agent harness into a Reinforcement Learning Environment.

## What "OpenEnv-compatible" means here

OpenEnv's contract is three calls:

- **`reset()`** — start a fresh episode/task instance, return the initial observation.
- **`step(action)`** — send the agent's action into the environment, return `(observation, reward, done, info)`.
- **`state()`** — return the environment's current status without advancing it (useful for debugging and for external monitors).

This template implements that contract around a Foundry hosted agent. It does **not** reimplement the agent itself — your existing harness (Microsoft Agent Framework, LangChain, or custom) keeps running inside Foundry's managed sandbox exactly as it does today. This file is the adapter layer, not a replacement for your agent.

## Files

- `env.py` — the `FoundryAgentEnv` class implementing `reset/step/state`.
- `foundry_client.py` — thin wrapper over the Foundry Agent Service SDK calls this template needs (session create, send message, fetch trace). Swap this out for your actual SDK calls.
- `run_smoke_test.py` — runs one full episode against a stub agent so you can validate the contract before wiring in something real.
- `.env.example` — required environment variables.
- `requirements.txt` — Python dependencies.

## How to adapt this to your workflow

1. **Define what an "episode" is.** For a single-turn workflow (classify this document) an episode is one exchange. For a multi-turn workflow (resolve this support ticket) an episode may be an entire conversation. Set this in `env.py::reset()`.
2. **Define what a "step" is.** Usually one agent turn: the agent takes an action (tool call or message), the environment returns the next observation. If your workflow doesn't naturally decompose into steps, treat the whole episode as a single step — that's fine and still OpenEnv-compatible.
3. **Decide what `done` means.** Task completion, a max-turn limit, or an explicit terminal tool call are all valid. Be explicit — an ambiguous `done` condition is the most common source of broken environments.
4. **Wire in your rubric.** `step()`'s `reward` field should call into a rubric from `rubric-cookbook/`. Start with `reward=None` and a placeholder until you've picked a rubric pattern — don't invent scoring logic here.
5. **Point `info` at the trace.** Always include a trace ID or link in `info` so the eval harness can pull the full OpenTelemetry trace for offline analysis later, even if you don't score every field online.

## Running the smoke test

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in FOUNDRY_PROJECT_ENDPOINT, FOUNDRY_AGENT_ID, etc.
python run_smoke_test.py
```

Expected output: a `reset()` call, three `step()` calls against a stub echo agent, and a final `state()` dump — confirming the contract round-trips correctly before you plug in a real agent or rubric.
