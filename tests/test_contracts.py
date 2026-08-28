from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "rle-template"))
sys.path.insert(0, str(ROOT / "rubric-cookbook"))
sys.path.insert(0, str(ROOT / "eval-harness"))
sys.path.insert(0, str(ROOT / "3-worked-examples" / "support-ticket-triage"))

from composite import CompositeRubric  # noqa: E402
from dataset import EvalRecord  # noqa: E402
from foundry_client import StubFoundryClient  # noqa: E402
from reference_comparison import embedding_similarity  # noqa: E402
from ticket_env import TicketTriageEnv  # noqa: E402


class ContractTests(unittest.TestCase):
    def test_stub_completed_episode_has_completion_status(self) -> None:
        client = StubFoundryClient(terminal_after=1)
        session_id = client.start_session("stub-agent", {})

        response = client.send_message(session_id, {"content": "complete"})

        self.assertTrue(response["terminal"])
        self.assertEqual(response["status"], "completed")

    def test_triage_decision_ends_environment(self) -> None:
        env = TicketTriageEnv(client=StubFoundryClient(terminal_after=5))
        env.reset(
            task={
                "ticket": {
                    "subject": "Billing question",
                    "body": "Please review this invoice.",
                    "customer_tier": "standard",
                }
            }
        )

        result = env.step(
            {
                "type": "triage_decision",
                "content": {
                    "category": "billing",
                    "priority": "medium",
                    "disposition": "resolved",
                },
            }
        )

        self.assertTrue(result.done)
        self.assertTrue(env.state().done)
        with self.assertRaises(RuntimeError):
            env.step({"type": "message", "content": "another turn"})

    def test_embedding_similarity_rejects_mismatched_dimensions(self) -> None:
        def embed(text: str) -> list[float]:
            return [1.0, 0.0] if text == "reference" else [1.0, 0.0, 0.0]

        rubric = embedding_similarity("reference", embed)

        with self.assertRaisesRegex(ValueError, "same dimension"):
            rubric([{"role": "agent", "content": "answer"}])

    def test_scores_must_be_within_unit_interval(self) -> None:
        with self.assertRaises(ValueError):
            EvalRecord("episode", {}, [], 1.2, {})

        with self.assertRaises(ValueError):
            CompositeRubric([(lambda transcript: 1.2, 1.0)])([])


if __name__ == "__main__":
    unittest.main()