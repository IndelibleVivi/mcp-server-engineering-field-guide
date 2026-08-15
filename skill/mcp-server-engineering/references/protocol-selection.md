# Protocol selection

Protocol rules are time-scoped. Begin every audit or design with an explicit revision decision.

## Selection table

| Declared/target revision | Load | Lifecycle shape |
| --- | --- | --- |
| `2025-06-18` | `mcp-2025-06-18.md` | initialize handshake; optional HTTP session/SSE; no batching |
| `2025-11-25` | `mcp-2025-11-25.md` | initialize/session era plus clarified Origin failure, polling SSE, URL elicitation, experimental tasks |
| `2026-07-28` | `mcp-2026-07-28.md` | stateless, self-describing requests; discovery; MRTR; routing headers; cacheable results |

If another revision is declared, retrieve its official specification and create a task-local profile before making normative findings.

## Decision rules

1. An existing implementation is judged against the revision it publicly claims and negotiates.
2. A new design uses the current official revision unless a named host/SDK compatibility requirement justifies another.
3. A multi-revision server needs an explicit compatibility architecture and tests for each active era.
4. A feature removed later is not a historical defect; an unsupported feature falsely advertised in its own era is.
5. Host integration guidance is not a protocol revision. Date it separately.
6. JSON-RPC and HTTP remain separate normative substrates; MCP may narrow them.

## Load branches

- For an audit or design, load the one MCP profile matching the declared or selected revision.
- For a spec upgrade, load both the declared source profile and target profile. Identify behavior to preserve, replace, and retire; do not apply target requirements retroactively to the historical baseline.
- Always load `json-rpc-2.0.md` as the base message substrate.
- Load `http-rfc9110-rfc9112.md` only when HTTP is in scope. For pure parent-owned stdio, mark HTTP controls not applicable unless a separate HTTP wrapper exists.
- Load the dated integration-guidance profile separately when an MCP App or named host is in scope; recheck moving sources before making current compatibility claims.

## Current-profile freshness

The bundled current profile was assessed on `2026-08-15`. If a user asks for “latest,” browse the official MCP specification index and changelog. Record the newly observed revision and date. Do not silently rewrite historical test expectations.

Official index: <https://modelcontextprotocol.io/specification/>
