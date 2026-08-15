---
profile_id: json-rpc-2.0
profile_version: 1
assessed_at: 2026-08-15
status: normative-substrate
language: en
language_peer: json-rpc-2.0.zh-CN.md
---

# JSON-RPC 2.0 profile for MCP implementations

## Normative source

- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

MCP uses JSON-RPC 2.0 as a message substrate and then narrows or extends it by revision. Apply the selected MCP profile after basic JSON-RPC classification.

## Message classifier

Classify by structure before method dispatch:

| Kind | Required shape | Response behavior |
| --- | --- | --- |
| Request | object; `jsonrpc: "2.0"`; string `method`; `id` present | exactly one result or error with the same ID |
| Notification | object; `jsonrpc: "2.0"`; string `method`; `id` absent | no JSON-RPC response |
| Success response | object; `jsonrpc: "2.0"`; `id` present; `result` present; `error` absent | input to a client role, not a server method call |
| Error response | object; `jsonrpc: "2.0"`; `id` present; `error` present; `result` absent | input to a client role, not a server method call |
| Invalid | anything else | protocol error when a response is permitted |

An `id` may be a String, Number, or Null under base JSON-RPC. Fractional numeric IDs are discouraged for interoperability but are not made invalid merely by being fractional. Boolean is not a JSON Number for this purpose. Null IDs are discouraged because they collide with the conventional unknown-ID error response.

Do not use truthiness to detect an ID: `0`, `""`, and `null` require deliberate handling. Use field presence.

## Params and errors

- `params`, when present, is an Array or Object under base JSON-RPC. MCP methods ordinarily define object-shaped parameter schemas; apply the method schema after message classification.
- A response contains exactly one of `result` and `error`.
- The error object includes integer `code` and string `message`; optional `data` is application-defined.
- Preserve the request ID exactly in the response unless the ID is unknown because parsing or request classification failed.
- Distinguish parse error (`-32700`), invalid request (`-32600`), method not found (`-32601`), invalid params (`-32602`), internal error (`-32603`), and revision-allocated MCP errors.

## Notifications and side effects

“No response” does not mean “no validation.” A notification still passes transport, JSON, revision, method, authorization, argument, resource, and side-effect gates. Only methods that the selected MCP revision permits as notifications should execute without a response.

Unknown or malformed notifications do not receive a JSON-RPC error, but they should still be rejected internally, metered, and logged through a non-protocol channel.

## Batching boundary

Base JSON-RPC 2.0 defines arrays of requests as batches. MCP revision `2025-06-18` removed batching, and the later profiles in this guide continue to reject batch-shaped input. Therefore:

1. a generic JSON-RPC parser accepting a batch is not proof of MCP compliance;
2. reject a top-level array at the MCP envelope before any element executes;
3. do not partially execute a batch and then report a single error.

Bind the test to the declared MCP revision so historical behavior is explicit.

## Test obligations

- request IDs: positive, zero, negative, string, empty string, null, and fractional numeric value;
- explicitly reject Boolean IDs if the language runtime treats Boolean as numeric;
- notification is detected by absent `id`, not a falsy value;
- result/error exclusivity;
- response objects never enter server method dispatch;
- invalid version, non-string method, invalid params container, and extra batch wrapper;
- error IDs match the original when known and use null only when the ID cannot be established;
- malformed notification produces no protocol response and no side effect.

## Known unknowns

- A host or SDK may intentionally narrow the base ID domain. Record that as a compatibility constraint, not as a JSON-RPC normative claim.
- MCP revision-specific error allocation can change; load the corresponding MCP profile.
- A framework's pre-parser may erase duplicate keys or coerce numbers before application validation. Runtime probes are required to establish the actual accepted wire language.
