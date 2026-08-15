# Synthetic historical Streamable HTTP server

- Declared MCP revision: `2025-06-18`.
- Transport: Streamable HTTP on a loopback listener.
- The implementation intentionally uses an `Mcp-Session-Id` and a GET SSE stream as supported by its declared revision.
- `capture_thought` appends to an operator-selected capture log when capture is enabled.
- `/think` and `tools/call` are intended to expose the same capability contract.
- Evidence included here: source and documentation only; no handler, socket, process, or deployment execution is included.
