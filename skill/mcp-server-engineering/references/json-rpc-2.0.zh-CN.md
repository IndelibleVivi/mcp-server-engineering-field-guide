---
profile_id: json-rpc-2.0
profile_version: 1
assessed_at: 2026-08-15
status: normative-substrate
language: zh-CN
language_peer: json-rpc-2.0.md
---

# MCP implementation 的 JSON-RPC 2.0 profile

## Normative source

- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

MCP 使用 JSON-RPC 2.0 作为 message substrate，再由各 revision 收窄或扩展。先完成基本 JSON-RPC classification，再应用所选 MCP profile。

## Message classifier

在 method dispatch 前按 structure 分类：

| Kind | Required shape | Response behavior |
| --- | --- | --- |
| Request | object；`jsonrpc: "2.0"`；string `method`；`id` present | 返回且只返回一个带相同 ID 的 result 或 error |
| Notification | object；`jsonrpc: "2.0"`；string `method`；`id` absent | 不发送 JSON-RPC response |
| Success response | object；`jsonrpc: "2.0"`；`id` present；`result` present；`error` absent | 属于 client role 的输入，不是 server method call |
| Error response | object；`jsonrpc: "2.0"`；`id` present；`error` present；`result` absent | 属于 client role 的输入，不是 server method call |
| Invalid | 其他任何 shape | 在允许 response 时返回 protocol error |

Base JSON-RPC 允许 `id` 为 String、Number 或 Null。Fractional numeric IDs 因 interoperability 而不推荐，但不能仅因存在小数就判 invalid。Boolean 在这里不是 JSON Number。Null ID 也不推荐，因为会与 unknown-ID error response 的常见表示冲突。

不要用 truthiness 判断 ID：`0`、`""` 与 `null` 都需要显式处理。检查 field presence。

## Params 与 errors

- Base JSON-RPC 中，若存在 `params`，它是 Array 或 Object。MCP methods 通常定义 object-shaped parameter schemas；message classification 后再应用 method schema。
- Response 必须且只能包含 `result` 或 `error` 之一。
- Error object 包含 integer `code` 与 string `message`；optional `data` 由 application 定义。
- 除非 parsing 或 request classification 失败而无法得知 ID，否则 response 应原样保留 request ID。
- 区分 parse error（`-32700`）、invalid request（`-32600`）、method not found（`-32601`）、invalid params（`-32602`）、internal error（`-32603`）及 revision-allocated MCP errors。

## Notifications 与 side effects

“没有 response”不等于“不做 validation”。Notification 仍要经过 transport、JSON、revision、method、authorization、argument、resource 与 side-effect gates。只有所选 MCP revision 允许成为 notification 的 methods 才能无响应执行。

Unknown 或 malformed notification 不会收到 JSON-RPC error，但仍应在内部被拒绝、metered，并通过 non-protocol channel 记录。

## Batching boundary

Base JSON-RPC 2.0 把 request arrays 定义为 batches；MCP revision `2025-06-18` 删除 batching，本 guide 后续 profiles 也继续拒绝 batch-shaped input。因此：

1. Generic JSON-RPC parser 接受 batch，不能证明 MCP compliance；
2. 在任何 element 执行前，于 MCP envelope 拒绝 top-level array；
3. 不要先 partial execute batch，再返回一个总 error。

Test 必须绑定 declared MCP revision，让 historical behavior 保持显式。

## Test obligations

- Request IDs：positive、zero、negative、string、empty string、null 与 fractional numeric value；
- 若 language runtime 把 Boolean 当作 numeric，显式拒绝 Boolean ID；
- Notification 依据 `id` absent 识别，而不是 falsy value；
- Result/error exclusivity；
- Response objects 永不进入 server method dispatch；
- Invalid version、non-string method、invalid params container 与额外 batch wrapper；
- Error ID 在已知时匹配 original，只在无法确定 ID 时使用 null；
- Malformed notification 不产生 protocol response，也不产生 side effect。

## Known unknowns

- Host 或 SDK 可能有意收窄 base ID domain。应把它记录为 compatibility constraint，而不是 JSON-RPC normative claim。
- MCP revision-specific error allocation 会变化；加载对应 MCP profile。
- Framework pre-parser 可能在 application validation 前丢失 duplicate keys 或 coerce numbers。必须用 runtime probe 确定实际 accepted wire language。
