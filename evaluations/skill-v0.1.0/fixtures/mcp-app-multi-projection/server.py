"""Synthetic MCP App response projection."""

from __future__ import annotations


def render_card(arguments: dict) -> dict:
    title = str(arguments.get("title", "Untitled"))
    return {
        "content": [{"type": "text", "text": f"Rendered card: {title}"}],
        "structuredContent": {"title": title, "theme": "mist"},
        "_meta": {
            "ui/resourceUri": "ui://thinking-card/v1",
            "ui/csp": {"connect_domains": [], "resource_domains": []},
            "operator/debugToken": "ui-only-synthetic-value",
        },
    }
