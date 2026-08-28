"""
FoundryClient — thin wrapper over the Foundry Agent Service calls env.py
needs. Swap StubFoundryClient for a real client backed by the Foundry SDK
once you're ready to point this at an actual hosted agent.

Keep this wrapper narrow on purpose: env.py should never import the Foundry
SDK directly, so you can test the OpenEnv contract against the stub without
any Azure credentials, and swap in the real client with a one-line change.
"""

from __future__ import annotations

import os
import uuid
from typing import Optional, Protocol


class FoundryClient(Protocol):
    """Interface env.py depends on. Implement this against the real SDK."""

    agent_id: str

    def start_session(self, agent_id: str, metadata: dict) -> str:
        ...

    def send_message(self, session_id: str, action: dict) -> dict:
        ...

    def get_trace_id(self, session_id: str) -> Optional[str]:
        ...


class StubFoundryClient:
    """
    In-memory fake client for local development and the smoke test.

    Echoes the action back with a trivial transformation and marks the
    episode terminal after a fixed number of turns, so you can validate
    env.py's reset/step/state contract without any network calls or
    Foundry credentials.
    """

    def __init__(self, agent_id: str = "stub-agent", terminal_after: int = 3):
        self.agent_id = agent_id
        self.terminal_after = terminal_after
        self._sessions: dict[str, dict] = {}

    def start_session(self, agent_id: str, metadata: dict) -> str:
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = {"metadata": metadata, "turns": 0}
        return session_id

    def send_message(self, session_id: str, action: dict) -> dict:
        session = self._sessions[session_id]
        session["turns"] += 1
        content = action.get("content", "")
        terminal = session["turns"] >= self.terminal_after
        return {
            "content": f"stub response to: {content!r}",
            "terminal": terminal,
            "status": "completed" if terminal else "in_progress",
        }

    def get_trace_id(self, session_id: str) -> Optional[str]:
        return f"stub-trace-{session_id[:8]}"


class RealFoundryClient:
    """
    Skeleton for a real client backed by the Foundry Agent Service SDK.

    TODO: fill in with actual azure-ai-projects / Agent Service calls.
    The exact SDK surface has been moving fast (hosted agents + Toolboxes
    went beta -> stable in the SDKs around July 2026) — check the current
    docs at https://learn.microsoft.com/en-us/azure/foundry/agents/
    before wiring this up, rather than trusting example code you find
    elsewhere, including in this repo.
    """

    def __init__(self, agent_id: Optional[str] = None):
        self.agent_id = agent_id or os.environ["FOUNDRY_AGENT_ID"]
        self.project_endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
        # TODO: instantiate the real SDK client here, e.g.
        # from azure.ai.projects import AIProjectClient
        # from azure.identity import DefaultAzureCredential
        # self._client = AIProjectClient(endpoint=self.project_endpoint,
        #                                 credential=DefaultAzureCredential())

    def start_session(self, agent_id: str, metadata: dict) -> str:
        raise NotImplementedError(
            "Wire this up to a real Foundry hosted-agent session create call."
        )

    def send_message(self, session_id: str, action: dict) -> dict:
        raise NotImplementedError(
            "Wire this up to a real Foundry hosted-agent message/run call."
        )

    def get_trace_id(self, session_id: str) -> Optional[str]:
        raise NotImplementedError(
            "Wire this up to a real Foundry trace lookup call."
        )
