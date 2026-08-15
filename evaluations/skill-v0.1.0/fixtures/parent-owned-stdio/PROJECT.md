# Synthetic parent-owned stdio server

- Declared MCP revision: `2026-07-28`.
- Transport: stdio only, one JSON-RPC message per input line.
- Reachability: a local desktop host launches the executable as a child process and owns executable selection plus environment delivery.
- There is no TCP listener, HTTP wrapper, proxy, tunnel, browser, or network authentication protocol.
- Capability: `notes.lookup` reads a fixed in-memory mapping and has no durable side effect.
- Evidence included here: source and documentation only. No process, host, integration, or independent execution receipt is included.
