"""
TicketTriageEnv — a concrete example of subclassing FoundryAgentEnv for a
real workflow. See rle-template/env.py for the base class and contract.

Named ticket_env.py (not env.py) so it doesn't collide on sys.path with
rle-template/env.py when both are imported by run_example.py.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "rle-template"))

from env import FoundryAgentEnv  # noqa: E402
from foundry_client import FoundryClient  # noqa: E402

CATEGORIES = {"billing", "technical", "account", "other"}
PRIORITIES = {"low", "medium", "high", "urgent"}


class TicketTriageEnv(FoundryAgentEnv):
    """
    Episode = one ticket, from arrival to the agent's terminal decision
    (resolve or escalate). Overrides reset() to validate the ticket shape
    and step() to interpret triage-specific terminal signals.
    """

    def reset(self, task: Optional[dict] = None) -> dict:
        if task is None or "ticket" not in task:
            raise ValueError("TicketTriageEnv.reset() requires task={'ticket': {...}}")

        ticket = task["ticket"]
        required_fields = {"subject", "body", "customer_tier"}
        missing = required_fields - set(ticket.keys())
        if missing:
            raise ValueError(f"Ticket missing required fields: {missing}")

        return super().reset(task=task)

    def step(self, action: dict):
        """
        A ticket-triage action is terminal once the agent has both
        classified the ticket AND either resolved it or escalated it.
        This overrides the base class's generic terminal detection
        (which just trusts response.get("terminal")) with a stricter
        check specific to this workflow's action shape.
        """
        result = super().step(action)

        content = action.get("content", {})
        if isinstance(content, dict):
            has_category = content.get("category") in CATEGORIES
            has_priority = content.get("priority") in PRIORITIES
            has_disposition = content.get("disposition") in {"resolved", "escalated"}
            if has_category and has_priority and has_disposition:
                result.done = True

        return result
