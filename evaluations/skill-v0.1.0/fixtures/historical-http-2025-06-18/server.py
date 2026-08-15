"""Synthetic historical audit slice; it is not a production HTTP server."""

from __future__ import annotations


CAPTURE_ENABLED = True
CAPTURE_LOG: list[str] = []
TOOL = {
    "name": "capture_thought",
    "description": "Render and optionally capture one thought.",
    "annotations": {"readOnlyHint": True},
}


def validate_thought(arguments: dict) -> str:
    thought = arguments.get("thought")
    if not isinstance(thought, str) or not thought.strip():
        raise ValueError("thought must be a non-empty string")
    if len(thought) > 2000:
        raise ValueError("thought exceeds 2000 characters")
    return thought


def rest_think(arguments: dict) -> dict:
    return invoke_capture(validate_thought(arguments))


def mcp_tools_call(arguments: dict) -> dict:
    # Intentional defect: this route bypasses the shared validator.
    return invoke_capture(arguments["thought"])


def invoke_capture(thought: str) -> dict:
    if CAPTURE_ENABLED:
        CAPTURE_LOG.append(thought)
    return {"content": [{"type": "text", "text": thought}]}


def historical_session_flow(session_id: str) -> str:
    return f"SSE stream for session {session_id}"
