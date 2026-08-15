from server import target_dispatch


def test_target_dispatch() -> None:
    request = {
        "headers": {
            "MCP-Protocol-Version": "2026-07-28",
            "MCP-Route": "notes.lookup",
        }
    }
    assert target_dispatch(request)["result"] == "ok"


# Intentional gap: no test proves legacy_dispatch or legacy_sessions are absent.
