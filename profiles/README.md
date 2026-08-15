# Protocol Profiles

[简体中文](README.zh-CN.md) · English

Profiles isolate revision-specific requirements from the stable engineering core. Select a profile by the protocol revision the implementation claims—not by the current calendar date or an SDK's default.

| Profile | Status in this guide | Purpose |
| --- | --- | --- |
| [MCP 2025-06-18](mcp-2025-06-18.md) | historical-supported | Stateful lifecycle, optional transport sessions, Streamable HTTP, no JSON-RPC batching |
| [MCP 2025-11-25](mcp-2025-11-25.md) | historical-supported | Stateful lifecycle plus clarified Origin failures, polling SSE, URL elicitation, experimental tasks |
| [MCP 2026-07-28](mcp-2026-07-28.md) | current as assessed 2026-08-15 | Stateless core, self-describing requests, discovery, MRTR, header routing, cacheable results |
| [JSON-RPC 2.0](json-rpc-2.0.md) | normative substrate | Message classification, IDs, notifications, errors, and MCP's batching override |
| [HTTP RFC 9110 / 9112](http-rfc9110-rfc9112.md) | normative substrate | Message framing, request-targets, connection behavior, and intermediary boundaries |
| [Integration guidance assessed 2026-08-15](integration-guidance-2026-08-15.md) | moving | MCP Apps and OpenAI-host integration guidance whose URLs and requirements may change independently |

Each profile records its source, assessment date, implementation consequences, migration boundary, test obligations, and known unknowns. A profile is not a substitute for the normative source.
