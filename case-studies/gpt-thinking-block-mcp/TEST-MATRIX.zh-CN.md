---
case_study_id: gpt-thinking-block-mcp
document: test-matrix
version: 1
language: zh-CN
language_peer: TEST-MATRIX.md
---

# Test matrix

简体中文 · [English](TEST-MATRIX.md)

Assessed source：`ec1379aa141a02a150ef7ce82ea4f5e92f55c72b`。

Status vocabulary：

- **executed** — behavior 在 named receipt 中实际运行；
- **statically checked** — 检查或 parse source/configuration，但未激活 runtime；
- **not verified** — 在所需 boundary 没有 evidence；
- **not applicable** — 超出 selected revision 或 declared product scope。

## Protocol 与 capability

| Surface | Evidence | Status | Residual |
| --- | --- | --- | --- |
| `2025-06-18` initialize negotiation | unit tests 与 real-process smoke | executed | 未测试 multi-host compatibility |
| request / notification / response classification | focused classifier tests | executed | accepted ID domain 刻意比 base JSON-RPC 更窄 |
| unsupported/malformed envelopes | classifier + HTTP tests | executed | framework pre-parser behavior 仍依赖 runtime |
| batch rejection | MCP HTTP test | executed | 只绑定 MCP `2025-06-18` |
| tool name 与 argument schema | protocol tests | executed | prompt-level token bands 未在 server enforce |
| MCP / REST parity | shared-validation / shared-limiter tests | executed | future transports 仍必须复用同一 core |
| notification side-effect boundary | protocol + HTTP tests | executed | 只覆盖当前 declared methods |
| resource URI validation / missing resource error | protocol tests | executed | 不含 host rendering |
| capture annotations 反映 write effect | runtime tests | executed | 未验证 host 如何显示 annotation |

## HTTP 与 trust boundaries

| Surface | Evidence | Status | Residual |
| --- | --- | --- | --- |
| exact route/method table | integration tests | executed | 未测试 upstream proxy method normalization |
| Origin allowlist / CORS echo | integration tests | executed | 未测试 browser-host production behavior |
| Host / absolute-form authority | raw HTTP integration tests | executed | 未测试 proxy chain normalization |
| forwarded metadata policy | configuration/integration tests | executed | immediate-peer identity 仍由 deployment 拥有 |
| optional bearer token / challenge | integration tests | executed | 不是 OAuth；不能发 custom header 的 client 无法使用 |
| content length/type/size | integration tests | executed | 未测试 HTTP/2-to-1 translation |
| huge decimal length | focused integration test | executed | alternative runtimes 可能不同 |
| transfer coding / duplicate length rejection | integration tests | executed | strict rejection 是 project policy |
| strict UTF-8、lone surrogates、non-finite/deep JSON | integration tests | executed | 未穷尽 parser complexity |
| incomplete-body idle failure | socket integration test | executed | 只证明 test timing/environment |
| absolute slow-body deadline | socket integration test | executed | header completion 仍在 deadline 外 |
| unread-body error closes connection | integration tests | executed | 未实现 framework drain behavior |
| transport error / JSON-RPC error 分离 | integration tests | executed | 未测试 host error rendering |
| preflight `204` framing | integration test | executed | 未测试 intermediary mutation |

## Concurrency、capture 与 failure paths

| Surface | Evidence | Status | Residual |
| --- | --- | --- | --- |
| server-wide rate limiter | deterministic clock + HTTP tests | executed | 不是 connection-admission limiter |
| shared capture lock | concurrent write test | executed | multi-process writers out of scope |
| owner-only capture mode | filesystem tests | executed | parent filesystem/backups 由 operator 负责 |
| capture failure non-fatal 且不 log raw content | forced-failure tests | executed | 未测试 external logging stack |
| response disconnect behavior | `WIRE-DISCONNECT-001` | executed | traceback noise 仍存在 |
| header slow-trickle | `WIRE-HDR-001` | executed | absolute header deadline 缺失 |
| pre-header worker admission | `WIRE-ADMISSION-001` | executed | application layer thread count 无界 |
| `Expect: 100-continue` ordering | `WIRE-EXPECT-001` | executed | inherited interim response 仍存在 |

## Deployment 与 host integration

| Surface | Evidence | Status | Residual |
| --- | --- | --- | --- |
| direct-run loopback default | configuration tests + real-process smoke | executed | operator 可明确 override |
| container process binds `0.0.0.0` | Dockerfile/Compose inspection | statically checked | 本机未运行 container |
| Compose host 侧只 publish loopback | Compose parsing/inspection | statically checked | 未观察 runtime port binding |
| Docker health check 支持 optional token | command/static inspection | statically checked | 未观察 image build / health transition |
| CI Python 3.9/3.12 | public GitHub Actions receipt | executed | CI 未运行 wire residual probes |
| local CPython 3.13.3 | sanitized local receipt | executed | 同一 development owner；不是 independent reproduction |
| reverse proxy/TLS/OAuth | 仅 documentation | not verified | 明确由 operator/deployment 拥有 |
| ChatGPT compatibility widget | 现有 project behavior/tests | partially executed | 本记录未捕获 actual current host session |
| standard MCP Apps bridge | source/docs | not applicable | 明确超出 assessed release |
| MCP `2026-07-28` behavior | source/docs | not applicable | 需要 migration，不是改 version string |

## Negative-space checks

以下 absence 也是结果：

- 没有无 state 的伪 session；
- 没有 fake SSE stream；
- 没有 catch-all wildcard CORS response；
- 没有默认 non-loopback host publication；
- 默认不 capture；
- 普通 logs 不含 raw captured thinking；
- 不把 static bearer token 声称为 OAuth；
- 不把 static Docker inspection 声称成 runtime proof；
- 不声称 standard MCP Apps portability。
