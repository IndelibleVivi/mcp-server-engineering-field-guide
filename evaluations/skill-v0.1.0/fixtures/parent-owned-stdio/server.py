"""Synthetic source slice for a parent-owned stdio MCP server."""

from __future__ import annotations

import json
import sys


NOTES = {"alpha": "first note", "beta": "second note"}


def handle(message: dict) -> dict | None:
    if message.get("method") != "tools/call":
        return None
    parameters = message.get("params") or {}
    if parameters.get("name") != "notes.lookup":
        raise ValueError("unknown tool")
    arguments = parameters.get("arguments") or {}
    key = arguments.get("key")
    if not isinstance(key, str) or not key:
        raise ValueError("key must be a non-empty string")
    return {"jsonrpc": "2.0", "id": message.get("id"), "result": NOTES.get(key)}


def main() -> None:
    for line in sys.stdin:
        request = json.loads(line)
        response = handle(request)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
