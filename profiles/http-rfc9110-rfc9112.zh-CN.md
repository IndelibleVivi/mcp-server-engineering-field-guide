---
profile_id: http-rfc9110-rfc9112
profile_version: 1
assessed_at: 2026-08-15
status: normative-substrate
language: zh-CN
language_peer: http-rfc9110-rfc9112.md
---

# Low-level MCP server 的 HTTP/1.1 profile

## Normative sources

- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html)
- [RFC 9112: HTTP/1.1](https://www.rfc-editor.org/rfc/rfc9112.html)

本 profile 聚焦直接拥有 HTTP parsing 或使用较薄 standard-library handler 的 server implementation。成熟 framework 可能已经承担这些责任，但 review 必须识别并测试真实 owner。

## Enforcement order 是 partial order

不存在适合所有 framework 的单一线性 pipeline，但以下 dependencies 很重要：

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

Control 无法 retroactively 保护在其 enforcement point 之前已经消耗的 bytes、threads、memory、state 或 authority。

## Message framing

- 在决定 message body framing 前，先完整 parse header section。
- 同时含 `Transfer-Encoding` 与 `Content-Length` 的 request 存在 smuggling risk。RFC 9112 将其视为 error condition；应拒绝并关闭 connection，不要猜测。
- Multiple `Content-Length` field values 需要按 RFC 明确处理。Application 可以采用更严格的“拒绝所有 duplicates”policy，但必须把它写成 policy，不能伪称 RFC 原文。
- 若不支持 chunked request body，应在 application dispatch 前显式拒绝；不要在 persistent connection 上一直读到 EOF。
- Allocation 与 capability admission 前执行 configured maximum body length。
- 对 incomplete declared body 使用真实 whole-body 或 absolute deadline。只有 per-read idle timeout 会被缓慢 trickle 绕过。
- Required UTF-8 必须 strict decode。Replacement decoding 会改变 accepted protocol language，也可能隐藏 malformed input。

若 rejection 后仍有 unread request-body bytes，除非 framework 已被证明能够 drain 并重新同步，否则关闭 connection。

## Request-target 与 authority

HTTP/1.1 在特定 context 下支持 origin-form、absolute-form、authority-form 与 asterisk-form request targets。MCP endpoint 通常只预期 origin-form。验证：

- MCP endpoint 预期的 exact normalized path；
- 是否允许 query parameters，以及它们如何影响 routing/cache；
- `Host` 与 effective authority consistency；
- 通过或绕过 proxy 收到的 absolute-form target；
- Authorization decision 前的 percent encoding 与 path normalization。

不要让一层比较 raw target string、另一层比较独立 decoded path，却不测试二者 disagreement。

## `Expect: 100-continue`

某些 handler 会在 application code 检查 Origin、authentication、content type 或 body budget 前自动发送 `100 Continue`。这是 observable wire behavior，会邀请 client 发送本应被 policy 廉价拒绝的 body。

检查 framework pre-dispatch hook。若必须 early reject，override 或配置 expectation handler，并测试真实 socket exchange，不能只检查 final status code。

## Time 与 admission budgets

分别命名：

- header completion deadline；
- body completion deadline；
- 若有需要，作为 absolute deadline 补充的 per-read idle timeout；
- admission queue 或 concurrent-connection budget；
- capability execution deadline；
- response write deadline 与 output-size limit。

Body 读完后才 acquire 的 capability semaphore 无法限制 incomplete-body sockets。Thread-per-connection server 需要在每条 connection 消耗一个无界 thread 前设置 admission boundary。

## Origin、CORS 与 authentication

Origin validation 防止 DNS rebinding 等 browser-origin trust confusion；CORS response headers 告诉 browser 某个 script 能否读取 response；authentication 建立 caller identity 或 possession claim。它们是不同 controls。

- 按 parsed scheme/host/port tuple 或 exact canonical allowlist entry 比较 origins。
- 不能只因 request 提供 Origin 就任意 reflect。
- 只给预期 responses 附加 CORS headers，精确返回 allowed value；适用时正确设置 `Vary: Origin`。
- Capability execution 前验证 authentication；若 authentication 发生在资源已经消耗后，就不要声称它限制了 header/body resource consumption。

## Response 与 disconnect behavior

- 在可行时先 serialize bounded response，再 commit headers，防止 serialization failure 产生误导性 success status。
- Side effect 后的 write failure 与 execution failure 分开处理；client 可能因没收到 result 而 retry。
- 在 response boundary 捕获 expected disconnect exceptions，避免 uncontrolled traceback storm。
- 按所选 MCP revision 定义 interrupted response 是 cancel work、只 abandon delivery，还是需要 explicit cancellation。

## Test obligations

- duplicate 与 conflicting `Content-Length`；
- `Transfer-Encoding` 加 `Content-Length`；
- unsupported chunked body；
- endpoint 要求 length 时的 missing length；
- 不读取 body 就拒绝 oversized declared body；
- zero-byte 与 periodic trickle 两种 incomplete body；
- strict UTF-8 与 malformed JSON；
- absolute-form target、带 query 的 endpoint、invalid `Host` 与 normalization edge cases；
- `Expect: 100-continue` early-rejection transcript；
- 有无 unread body 的 disallowed Origin，并在之后尝试第二个 request；
- body parsing 前的 connection admission saturation；
- response write 时 client disconnect，以及 committed side effect 后的 retry。

Raw wire receipt 记录 environment、source revision、timing parameters、observed result 与 provenance status。

## Known unknowns

- Reverse proxies 可能在 application 看到 request 前对其 normalize、combine、reject 或 rewrite。
- HTTP/2 与 HTTP/3 framing 不同，但 intermediary 可能把它们转换为 HTTP/1.1；需要时同时测试 public edge 与 application hop。
- Standard-library handler behavior 会随 runtime version 改变；receipt 必须 pin runtime。
- Static source review 不能证明 kernel backlog、proxy timeouts、TLS behavior 或 deployed admission ceiling。
