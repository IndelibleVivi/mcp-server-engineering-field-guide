---
case_study_id: gpt-thinking-block-mcp
document: test-matrix
version: 1
language: en
language_peer: TEST-MATRIX.zh-CN.md
---

# Test matrix

[简体中文](TEST-MATRIX.zh-CN.md) · English

Assessed source: `ec1379aa141a02a150ef7ce82ea4f5e92f55c72b`.

Status vocabulary:

- **executed** — the behavior ran in the named receipt;
- **statically checked** — source/configuration was inspected or parsed, without activating the runtime;
- **not verified** — no evidence at the required boundary;
- **not applicable** — outside the selected revision or declared product scope.

## Protocol and capability

| Surface | Evidence | Status | Residual |
| --- | --- | --- | --- |
| `2025-06-18` initialize negotiation | unit tests and real-process smoke | executed | multi-host compatibility not exercised |
| request / notification / response classification | focused classifier tests | executed | accepted ID domain is intentionally narrower than base JSON-RPC |
| unsupported/malformed envelopes | classifier + HTTP tests | executed | framework pre-parser behavior remains runtime-specific |
| batch rejection | MCP HTTP test | executed | bound specifically to MCP `2025-06-18` |
| tool name and argument schema | protocol tests | executed | prompt-level token bands are not server-enforced |
| MCP and REST parity | shared-validation and shared-limiter tests | executed | other future transports must reuse the same core |
| notification side-effect boundary | protocol + HTTP tests | executed | only currently declared methods covered |
| resource URI validation and missing resource error | protocol tests | executed | host rendering not part of this test |
| capture annotations reflect write effect | runtime tests | executed | host display of annotation not verified |

## HTTP and trust boundaries

| Surface | Evidence | Status | Residual |
| --- | --- | --- | --- |
| exact route/method table | integration tests | executed | upstream proxy method normalization untested |
| Origin allowlist and CORS echo | integration tests | executed | browser-host production behavior untested |
| Host and absolute-form authority | raw HTTP integration tests | executed | proxy chain normalization untested |
| forwarded metadata policy | configuration/integration tests | executed | immediate-peer identity remains deployment-owned |
| optional bearer token and challenge | integration tests | executed | not OAuth; unsupported by clients unable to send custom header |
| content length/type/size | integration tests | executed | HTTP/2-to-1 translation untested |
| huge decimal length | focused integration test | executed | alternative runtimes may parse differently |
| transfer coding and duplicate length rejection | integration tests | executed | strict rejection is project policy |
| strict UTF-8, lone surrogates, non-finite/deep JSON | integration tests | executed | parser complexity beyond tested bounds not exhaustively proven |
| incomplete-body idle failure | socket integration test | executed | only test timing/environment proven |
| absolute slow-body deadline | socket integration test | executed | header completion remains outside deadline |
| unread-body error closes connection | integration tests | executed | framework drain behavior not implemented |
| transport error versus JSON-RPC error | integration tests | executed | host error rendering untested |
| preflight `204` framing | integration test | executed | intermediary mutation untested |

## Concurrency, capture, and failure paths

| Surface | Evidence | Status | Residual |
| --- | --- | --- | --- |
| server-wide rate limiter | deterministic clock + HTTP tests | executed | not a connection-admission limiter |
| shared capture lock | concurrent write test | executed | multi-process writers out of scope |
| owner-only capture mode | filesystem tests | executed | parent filesystem/backups operator-owned |
| capture failure is non-fatal and does not log raw content | forced-failure tests | executed | external logging stack untested |
| response disconnect behavior | `WIRE-DISCONNECT-001` | executed | traceback noise remains |
| header slow-trickle | `WIRE-HDR-001` | executed | absolute header deadline absent |
| pre-header worker admission | `WIRE-ADMISSION-001` | executed | thread count unbounded at application layer |
| `Expect: 100-continue` ordering | `WIRE-EXPECT-001` | executed | inherited interim response remains |

## Deployment and host integration

| Surface | Evidence | Status | Residual |
| --- | --- | --- | --- |
| direct-run loopback default | configuration tests + real-process smoke | executed | operator can intentionally override |
| container process binds `0.0.0.0` | Dockerfile/Compose inspection | statically checked | container not run locally |
| Compose publishes host loopback only | Compose parsing/inspection | statically checked | runtime port binding not observed |
| Docker health check with optional token | command/static inspection | statically checked | image build and health transition not observed |
| CI Python 3.9/3.12 | public GitHub Actions receipt | executed | CI did not run wire residual probes |
| local CPython 3.13.3 | sanitized local receipt | executed | same development owner; not independent reproduction |
| reverse proxy/TLS/OAuth | documentation only | not verified | deliberately operator/deployment-owned |
| ChatGPT compatibility widget | existing project behavior/tests | partially executed | actual current host session not captured here |
| standard MCP Apps bridge | source/docs | not applicable | explicitly outside assessed release |
| MCP `2026-07-28` behavior | source/docs | not applicable | requires migration, not a version-string edit |

## Negative-space checks

These absences are part of the result:

- no claimed session without session state;
- no fake SSE stream;
- no catch-all wildcard CORS response;
- no default non-loopback host publication;
- no capture by default;
- no raw captured thinking in ordinary logs;
- no OAuth claim for a static bearer token;
- no claim that static Docker inspection is runtime proof;
- no claim of standard MCP Apps portability.
