"""
Smoke test: exercises reset() -> step() x N -> state() against the stub
client, so you can confirm the OpenEnv contract round-trips correctly
before wiring in a real Foundry hosted agent or a real rubric.

Run:
    python run_smoke_test.py
"""

from env import FoundryAgentEnv
from foundry_client import StubFoundryClient


def toy_rubric(transcript: list[dict]) -> float:
    """
    Placeholder rubric: rewards longer engagement, purely to prove the
    reward field flows through step(). Replace with a real rubric from
    rubric-cookbook/ before using this for anything real.
    """
    return round(len(transcript) / 10, 2)


def main() -> None:
    client = StubFoundryClient(terminal_after=3)
    env = FoundryAgentEnv(client=client, rubric=toy_rubric, max_turns=10)

    print("=== reset() ===")
    obs = env.reset(task={"prompt": "Summarize the attached ticket."})
    print(obs)

    print("\n=== step() loop ===")
    done = False
    turn = 0
    while not done:
        turn += 1
        action = {"type": "message", "content": f"agent turn {turn}"}
        result = env.step(action)
        print(f"turn={turn} reward={result.reward} done={result.done} info={result.info}")
        done = result.done

    print("\n=== state() ===")
    print(env.state())

    print("\n=== full transcript ===")
    for entry in env.transcript():
        print(entry)

    print("\nSmoke test passed: reset/step/state contract round-tripped correctly.")


if __name__ == "__main__":
    main()
