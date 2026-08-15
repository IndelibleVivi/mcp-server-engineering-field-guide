---
profile_id: mcp-apps-and-openai-hosts-2026-08-15
profile_version: 1
assessed_at: 2026-08-15
status: moving-guidance
language: zh-CN
language_peer: integration-guidance-2026-08-15.md
---

# Moving integration guidance：MCP Apps 与 OpenAI hosts

本 profile 记录 `2026-08-15` 观察到的 integration guidance。它刻意与 normative protocol profiles 分开，因为 host behavior、product names、metadata aliases、submission rules 与 documentation URLs 会按不同节奏变化。

## Sources assessed

- [MCP Apps overview](https://modelcontextprotocol.io/extensions/apps/overview)
- [MCP Apps specification and SDK documentation](https://apps.extensions.modelcontextprotocol.io/)
- [OpenAI: Add UI to an MCP server](https://developers.openai.com/plugins/build/chatgpt-ui)
- [OpenAI: Authenticate users](https://developers.openai.com/plugins/build/auth)
- [OpenAI: Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels)

在声称 current host support 或发布 integration 前重新检查这些 sources。

## 两个 consumers，分开的 views

MCP App result 至少服务两个 consumers：

1. assistant/model：需要简洁、有语义价值的 tool content 与 structured data；
2. human-facing component：需要可 render 的数据，也可能接收额外 UI-only metadata。

把投影到每个 view 的过程当作 security / correctness boundary。不能假定 model 看不到的 field 对 user 就是 secret，也不能假定 component 能看到的 field 就可安全当作 HTML render。

分别测试 model-visible content、component-visible `structuredContent`、UI-only metadata 与最终 DOM。

## Portable MCP Apps foundation

截至本 assessment date，共享 MCP Apps pattern 使用：

- Tool description 上的 `_meta.ui.resourceUri`，指向 `ui://` resource；
- 包含 HTML application 的 UI resource，通常也 bundle JavaScript 与 CSS；
- 通过 `postMessage` 运行的 `ui/*` JSON-RPC bridge，连接 host/app；
- 通过 host 发起的 `tools/call`，而不是让 sandbox 直接接触 server authority；
- `_meta.ui.csp`、permissions 及相关 UI resource metadata，定义 sandbox policy。

优先实现共享 MCP Apps fields。Host-specific aliases 或 globals 只是 optional compatibility extensions；需要 feature detection，并在可行时提供 fallback。

## Tool 与 resource contracts

- Workflow 能 portable 表达时，让 tool 在无 UI 环境里仍有用。
- 可以把 data tools 与 render tools 分开：data tool 返回可继续调用的 `structuredContent`；只有真正需要显示时，render tool 才附加最终 UI resource。
- Tool names、descriptions、schemas、annotations 与 output metadata 和 executable code 一样需要认真 review；它们影响 model routing 与 user consent。
- 把 UI resource URI 当作 cache/version identity。HTML、JavaScript 或 CSS 发生 breaking change 时发布新 URI，并更新所有引用 tool。
- CSP 只声明确切需要的 external origins；API connections、static resources 与 nested frames 使用不同 allowlists。

## Widget trust boundaries

- 假定所有 tool results 与 `postMessage` payloads 都是 widget 的 untrusted input。
- 使用前检查 `event.source`、message shape、JSON-RPC version、expected method、request correlation 与 payload schema。
- Dynamic text 使用安全 DOM API 或 framework escaping render；不要把 untrusted content 拼进 HTML。
- Durable business data 留在 server 或 authoritative service。UI-instance state 是 ephemeral；cross-session preferences 需要显式拥有的 durable storage。
- Host sandbox 限制 parent-page access，但不会代替 application data validation、阻止 unsafe tool call，或替你授权 external network request。

## OpenAI host compatibility

截至本 assessment date，OpenAI guidance 在可能时优先 shared MCP Apps fields 与 bridge methods，同时为现有 integrations 保留 ChatGPT compatibility aliases。新代码应 feature-detect `window.openai` extension，不能按 product name 分支。

Authenticated remote MCP server 的 documented model 是与 MCP authorization specification 对齐的 OAuth 2.1：

- MCP server 是 resource server，每个 request 都验证 token；
- protected-resource metadata 标识 canonical resource 与 authorization server；
- authorization server 发布 OAuth/OIDC discovery metadata；
- Resource Indicators 把 token 绑定到 intended resource；
- capability execution 前验证 issuer、audience、expiration 与 scopes；
- 支持时优先 Client ID Metadata Documents，其他 registration modes 保留为 compatibility choices。

不要发明一个 token header 或半成品“auth-like”机制，再把它描述为 MCP OAuth。

## Tunnels 与 deployment

Tunnel 改变 reachability，不会修复 implementation invariants。分开这些 owners：

| Layer | Typical owner | 能证明什么 |
| --- | --- | --- |
| local listener | server process | bind address、local admission、parsing |
| tunnel client | operator/infrastructure | authenticated private path 或 public reachability |
| edge/gateway | platform/operator | TLS、routing、selected auth 与 rate policy |
| MCP application | project | protocol classification、tool authority、arguments、state、effects、result contract |
| host | product | discovery、consent UI、sandbox behavior、compatibility |

Tunnel connected 不能证明 Origin policy、protocol validation、authorization scopes 或 tool side effects 正确。

## Integration test matrix

- Host 只 discover intended tools 与 UI resources；
- 在承诺 non-UI support 时，tool 在 non-UI client 中仍有用；
- Component 只 render intended result fields；
- Untrusted text 不能变成 active markup 或 script；
- Widget-to-host calls 只限 declared tools 与 validated arguments；
- CSP 只允许 observed required domains，并阻止 undeclared destinations；
- Resource URI version change 正确 invalidate cache surface；
- OAuth discovery、challenge、PKCE、resource、issuer、audience、scopes、expiry 与 reauthorization 端到端可用；
- 同一 build 经过实际 tunnel/edge/host route 验证，而不只是 localhost；
- Error、disconnect、retry 与 duplicate-effect behavior 可见且有边界。

## Known unknowns

- Host support matrices 与 review requirements 是 moving facts。
- Product-specific aliases 可能仍可用，但不一定是首选 portable contract。
- Sandbox 与 CSP enforcement details 会因 host 而异。
- Secure MCP Tunnel availability、permissions 与 supported flows 依赖 account 和 organization。
- Local rendering 成功不能证明 submission 或 production-host acceptance。
