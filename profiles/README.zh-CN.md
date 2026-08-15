# Protocol Profiles

简体中文 · [English](README.md)

Profiles 把 revision-specific requirements 与稳定工程核心分开。选择 profile 时依据 implementation 声明的 protocol revision，而不是当前日期或某个 SDK 的默认值。

| Profile | 本 guide 中的状态 | 用途 |
| --- | --- | --- |
| [MCP 2025-06-18](mcp-2025-06-18.zh-CN.md) | historical-supported | Stateful lifecycle、optional transport sessions、Streamable HTTP、禁止 JSON-RPC batching |
| [MCP 2025-11-25](mcp-2025-11-25.zh-CN.md) | historical-supported | Stateful lifecycle，加上明确的 Origin failure、polling SSE、URL elicitation、experimental tasks |
| [MCP 2026-07-28](mcp-2026-07-28.zh-CN.md) | current as assessed 2026-08-15 | Stateless core、self-describing requests、discovery、MRTR、header routing、cacheable results |
| [JSON-RPC 2.0](json-rpc-2.0.zh-CN.md) | normative substrate | Message classification、IDs、notifications、errors，以及 MCP 对 batching 的覆盖 |
| [HTTP RFC 9110 / 9112](http-rfc9110-rfc9112.zh-CN.md) | normative substrate | Message framing、request-targets、connection behavior 与 intermediary boundaries |
| [Integration guidance assessed 2026-08-15](integration-guidance-2026-08-15.zh-CN.md) | moving | MCP Apps 与 OpenAI host integration guidance；其 URLs 和 requirements 可独立变化 |

每个 profile 都记录 source、assessment date、implementation consequences、migration boundary、test obligations 与 known unknowns。Profile 不能替代 normative source。
