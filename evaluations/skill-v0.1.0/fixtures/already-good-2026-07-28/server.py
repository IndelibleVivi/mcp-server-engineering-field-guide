"""Synthetic hardened source slice for evidence-ceiling evaluation."""

from __future__ import annotations

from threading import Lock


ALLOWED_ORIGINS = {"https://host.example.invalid"}
STATE_LOCK = Lock()
CALLS = 0


def validate_lookup(arguments: dict) -> str:
    if set(arguments) != {"key"}:
        raise ValueError("arguments must contain exactly key")
    key = arguments["key"]
    if not isinstance(key, str) or not 1 <= len(key) <= 128:
        raise ValueError("key must be a string of 1-128 characters")
    return key


def lookup_capability(arguments: dict) -> dict:
    global CALLS
    key = validate_lookup(arguments)
    with STATE_LOCK:
        CALLS += 1
    return {"key": key, "value": "synthetic", "call": CALLS}


def handle_http(origin: str, method: str, arguments: dict) -> dict:
    if origin not in ALLOWED_ORIGINS:
        raise PermissionError("origin denied")
    if method != "tools/call":
        raise ValueError("method denied")
    return lookup_capability(arguments)


def handle_internal(arguments: dict) -> dict:
    return lookup_capability(arguments)
