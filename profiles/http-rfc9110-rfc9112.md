---
profile_id: http-rfc9110-rfc9112
profile_version: 1
assessed_at: 2026-08-15
status: normative-substrate
language: en
language_peer: http-rfc9110-rfc9112.zh-CN.md
---

# HTTP/1.1 profile for low-level MCP servers

## Normative sources

- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html)
- [RFC 9112: HTTP/1.1](https://www.rfc-editor.org/rfc/rfc9112.html)

This profile focuses on server implementations that directly own HTTP parsing or use a thin standard-library handler. A mature framework may own these duties, but the review must identify and test the actual owner.

## Enforcement order is a partial order

No single universal linear pipeline fits every framework, but these dependencies matter:

```text
complete header section
    ├── request-target + effective authority
    ├── framing metadata
    ├── Origin / authentication material
    └── forwarding eligibility
             │
             └── bounded body consumption
                       └── strict decode + JSON
                                └── MCP classification
                                         └── capability execution
```

A control cannot retroactively protect bytes, threads, memory, state, or authority already consumed before its enforcement point.

## Message framing

- Parse the complete header section before deciding message body framing.
- A request containing both `Transfer-Encoding` and `Content-Length` is a smuggling risk. RFC 9112 treats it as an error condition; reject it and close the connection rather than guessing.
- Multiple `Content-Length` field values require deliberate RFC handling. A deliberately stricter application policy may reject all duplicates, but document that as a policy, not as an RFC quotation.
- If chunked request bodies are unsupported, reject them explicitly before application dispatch. Do not read until EOF on a persistent connection.
- Enforce a configured maximum body length before allocation and before capability admission.
- For an incomplete declared body, use an actual whole-body or absolute deadline. A per-read idle timeout alone can be defeated by a slow trickle.
- Decode required UTF-8 strictly. Replacement decoding changes the accepted protocol language and can hide malformed input.

If a rejection leaves request-body bytes unread, close the connection unless the server framework has a proven drain-and-resynchronize mechanism.

## Request-target and authority

HTTP/1.1 supports origin-form, absolute-form, authority-form, and asterisk-form request targets in defined contexts. An MCP endpoint normally expects origin-form. Validate:

- exact normalized path intended for the MCP endpoint;
- whether query parameters are allowed and how they affect routing or caches;
- `Host` and effective authority consistency;
- absolute-form targets received through or outside a proxy;
- percent encoding and path normalization before authorization decisions.

Do not compare a raw target string in one layer and an independently decoded path in another without tests for disagreement.

## `Expect: 100-continue`

Some handlers automatically send `100 Continue` before application code examines Origin, authentication, content type, or body budget. This is observable wire behavior and can invite a client to transmit a body that policy intended to reject cheaply.

Inspect the framework's pre-dispatch hook. If early rejection is required, override or configure the expectation handler and test the actual socket exchange—not merely the final status code.

## Time and admission budgets

Name separate budgets:

- header completion deadline;
- body completion deadline;
- per-read idle timeout, if useful in addition to an absolute deadline;
- admission queue or concurrent-connection budget;
- capability execution deadline;
- response write deadline and output-size limit.

A capability semaphore acquired after the body is read does not limit incomplete-body sockets. A thread-per-connection server needs an admission boundary before each connection consumes an unbounded thread.

## Origin, CORS, and authentication

Origin validation prevents a browser-origin trust confusion such as DNS rebinding. CORS response headers tell a browser whether script may read a response. Authentication establishes a caller identity or possession claim. They are separate controls.

- Compare origins as parsed scheme/host/port tuples or exact canonical allowlist entries.
- Never reflect an arbitrary Origin merely because a request supplied it.
- Attach CORS headers only to the intended responses, with exact allowed values and correct `Vary: Origin` behavior where applicable.
- Validate authentication before capability execution, but do not claim it limits header/body resource consumption unless it runs before those resources are consumed.

## Response and disconnect behavior

- Serialize a bounded response before committing headers when practical, so serialization failure does not produce a misleading success status.
- Treat write failure after a side effect separately from execution failure. The client may retry after receiving no result.
- Catch expected disconnect exceptions at the response boundary and record them without an uncontrolled traceback storm.
- Define whether an interrupted response cancels work, merely abandons delivery, or requires explicit cancellation according to the selected MCP revision.

## Test obligations

- duplicate and conflicting `Content-Length`;
- `Transfer-Encoding` plus `Content-Length`;
- unsupported chunked body;
- missing length where the endpoint requires it;
- oversized declared body without reading the body;
- incomplete body with no bytes and with a periodic trickle;
- strict UTF-8 and malformed JSON;
- absolute-form target, query-bearing endpoint, invalid `Host`, and normalization edge cases;
- `Expect: 100-continue` early-rejection transcript;
- disallowed Origin with and without unread body, followed by a second request attempt;
- connection admission saturation before body parsing;
- client disconnect during response write and retry after a committed side effect.

Record raw wire receipts with environment, source revision, timing parameters, observed result, and provenance status.

## Known unknowns

- Reverse proxies may normalize, combine, reject, or rewrite requests before the application sees them.
- HTTP/2 and HTTP/3 have different framing but can be translated into HTTP/1.1 at an intermediary; test both public edge and application hop when relevant.
- Standard-library handler behavior changes across runtime versions. Pin the runtime in receipts.
- Static source review cannot prove kernel backlog, proxy timeouts, TLS behavior, or the deployed admission ceiling.
