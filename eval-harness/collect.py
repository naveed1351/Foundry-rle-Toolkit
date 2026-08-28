"""
collect.py — run a batch of episodes against a FoundryAgentEnv, score each
with a rubric, and append results to an EvalDataset.

This is deliberately simple (a plain for-loop, no async/parallelism) so
it's easy to adapt. For large batches, parallelize the loop yourself —
each episode is independent.

Usage:
    python collect.py --episodes 50 --out runs/2026-08-28.jsonl

By default this uses the stub Foundry client and a toy rubric so it runs
out of the box. Swap in your real client/rubric per the TODOs below before
using this for anything real.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make rle-template/ and rubric-cookbook/ importable without packaging.
sys.path.insert(0, str(Path(__file__).parent.parent / "rle-template"))
sys.path.insert(0, str(Path(__file__).parent.parent / "rubric-cookbook"))

from dataset import EvalDataset, EvalRecord  # noqa: E402
from env import FoundryAgentEnv  # noqa: E402
from foundry_client import StubFoundryClient  # noqa: E402
from composite import CompositeRubric  # noqa: E402
from deterministic import task_completed_check, turn_count_penalty  # noqa: E402


def run_episode(env: FoundryAgentEnv, task: dict) -> EvalRecord:
    env.reset(task=task)
    done = False
    turn = 0
    while not done:
        turn += 1
        # TODO: replace this placeholder action with a real call to your
        # agent's policy / the actual Foundry hosted agent response loop.
        # In most setups the agent itself drives step() — this placeholder
        # exists purely so collect.py runs standalone against the stub.
        action = {"type": "message", "content": f"turn {turn}"}
        result = env.step(action)
        done = result.done

    state = env.state()
    transcript = env.transcript()

    rubric = CompositeRubric([
        (task_completed_check, 0.7),
        (turn_count_penalty, 0.3),
    ])
    score = rubric(transcript)
    breakdown = rubric.breakdown(transcript)

    return EvalRecord(
        episode_id=state.episode_id,
        task=task,
        transcript=transcript,
        score=score,
        breakdown=breakdown,
        trace_id=state.trace_id,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect and score a batch of episodes.")
    parser.add_argument("--episodes", type=int, default=10, help="Number of episodes to run.")
    parser.add_argument("--out", type=str, required=True, help="Output JSONL path.")
    args = parser.parse_args()

    # TODO: swap StubFoundryClient for RealFoundryClient once ready.
    client = StubFoundryClient(terminal_after=3)
    env = FoundryAgentEnv(client=client, rubric=None, max_turns=10)

    dataset = EvalDataset(args.out)

    for i in range(args.episodes):
        task = {"prompt": f"Sample task #{i}"}
        record = run_episode(env, task)
        dataset.append(record)
        print(f"episode {i+1}/{args.episodes}: score={record.score}")

    print(f"\nWrote {args.episodes} records to {args.out}")
    print(f"Mean score: {dataset.mean_score()}")


if __name__ == "__main__":
    main()
