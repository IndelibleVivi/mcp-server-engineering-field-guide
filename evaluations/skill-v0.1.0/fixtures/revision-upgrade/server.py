"""Synthetic mixed-era implementation used to test migration review."""

from __future__ import annotations


legacy_sessions: dict[str, list[str]] = {}


def target_dispatch(request: dict) -> dict:
    """Target 2026-07-28 path: each request is self-describing and stateless."""
    revision = request["headers"]["MCP-Protocol-Version"]
    route = request["headers"]["MCP-Route"]
    return {"revision": revision, "route": route, "result": "ok"}


def legacy_dispatch(method: str, session_id: str | None) -> dict:
    """Still-reachable 2025-11-25 session/SSE path that should be retired."""
    if method == "GET":
        return {"content_type": "text/event-stream", "session": session_id}
    if session_id:
        legacy_sessions.setdefault(session_id, []).append("request")
    return {"session": session_id, "result": "legacy-ok"}
