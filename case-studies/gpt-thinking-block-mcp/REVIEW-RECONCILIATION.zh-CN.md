---
case_study_id: gpt-thinking-block-mcp
document: review-reconciliation
version: 1
language: zh-CN
language_peer: REVIEW-RECONCILIATION.md
---

# Review reconciliation

本记录比较 independent review lanes，但不把 model rank、elapsed thinking time 或 confident prose 当作 assurance。

简体中文 · [English](REVIEW-RECONCILIATION.md)

## Review shape

| Lane | Input boundary | Primary attack surface |
| --- | --- | --- |
| Implementation lane | upstream baseline、initial threat model、与 patch 同时编写的 tests | capability authority、JSON-RPC shapes、request bounds、capture、deployment docs |
| Review lane A | actual hardened source/diff 与 tests | low-level parser/runtime behavior、Unicode/numeric edges、error exits、response framing |
| Review lane B | fresh public pinned commits 与 independent brief | wire-level composition、effective authority、auth metadata、review-bundle integrity、residual deployment claims |
| Runtime-probe lane | real local process 中的 pinned fork revision | handler dispatch 前或 unit-test seams 外的 inherited behavior |

两个 review lanes 有部分相同 context，但 prompts 与 execution histories 不同。它们是 orthogonal instruments，不是 statistically independent samples。

## Finding ledger

| ID | Finding | First strong signal | Reproduction | Disposition |
| --- | --- | --- | --- | --- |
| R-001 | Equivalent MCP / REST actions 需要同一 validator 与 limiter | implementation | focused unit/integration tests | adopted |
| R-002 | Notifications 与 client responses 不得执行 request-only tool methods | implementation + lane A | classifier tests | adopted |
| R-003 | Huge decimal `Content-Length` 会在普通 size comparison 前消耗 parser work | lane A | direct handler test | adopted with bounded decimal policy |
| R-004 | Malformed/lone-surrogate/non-finite JSON 需要显式 accepted-language boundary | lane A | HTTP / classifier tests | adopted |
| R-005 | Framing errors 被错误折叠成 JSON-RPC parse errors | lane B | transport-error tests | adopted；HTTP / JSON-RPC domains 分开 |
| R-006 | Absolute-form authority 与 `Host` 在 route / policy layers 之间可能不一致 | lane B | raw request-target tests | adopted |
| R-007 | 只按 path cache parsed authority 会复用前一 Host decision | R-006 后的 implementation regression test | two-request keep-alive test | adopted；cache key 包含 target / Host values |
| R-008 | Configured bearer mode 与 `WWW-Authenticate`、tool metadata 或 OpenAPI 不一致 | lane B | runtime-mode metadata tests | adopted |
| R-009 | Invalid forwarded authority 与 generated public base 需要统一 trust model | lane A + lane B | configuration/request tests | 可执行部分进入 code；deployment ownership 被澄清 |
| R-010 | Renewable body idle timeout 不能保证 whole-body deadline | lane A | slow-trickle body test | adopted as absolute body deadline |
| R-011 | Header parsing 仍在 absolute body deadline 之外 | lane B / runtime probe | `WIRE-HDR-001` | recorded residual |
| R-012 | Thread-per-connection admission 发生在 tool limiter 前 | lane B / runtime probe | `WIRE-ADMISSION-001` | recorded residual；仍要求 deployment perimeter |
| R-013 | Application Origin denial 前已发出 `Expect: 100-continue` | runtime probe | `WIRE-EXPECT-001` | recorded residual |
| R-014 | Remote disconnect 会产生完整 `BrokenPipeError` traceback | runtime probe | `WIRE-DISCONNECT-001` | recorded residual |
| R-015 | Capture failure 可能通过 diagnostics 泄漏 raw thinking | lane A | forced-failure tests | adopted；只 log bounded metadata |
| R-016 | Capture-on annotations 仍声称 read-only behavior | implementation | schema/runtime-mode tests | adopted |
| R-017 | `204 No Content` response framing 需要 wire-correct path | lane A | preflight test | adopted |
| R-018 | Widget 是 ChatGPT-bridge-specific，并非 standard portable MCP Apps bridge | lane B | source/docs inspection | documentation corrected；portable bridge deferred |
| R-019 | Docker runtime 与 non-root behavior 未在本机执行 | lane B | tool/runtime inventory | 保持 `unverified`；不伪造 receipt |
| R-020 | Fractional numeric IDs 被 JSON-RPC discourage，但并非普遍 invalid | later protocol reconciliation | normative-source check | 记录为 deliberate compatibility narrowing，而非 spec claim |

## Reviews 在哪里 disagreement 或 overreach

### Proxy identity

一条 review 推断启用 trusted forwarded headers 就意味着验证 immediate network peer。Application 没有可执行的 peer identity signal。我们没有用 cosmetic check 假装“修好”，而是修改 documentation：operator 必须保证 untrusted clients 无法 bypass proxy，并由 proxy overwrite forwarded headers。

当 application layer 缺少实现 proposed control 所需 authority 时，这才是正确处理。

### `Expect: 100-continue`

只看 source 容易以为 handler policy 会在 body transfer 前 reject；raw socket transcript 证明 inherited framework 先发 `100 Continue`。Observed wire sequence 推翻 source-level assumption。

### Protocol IDs

Review 正确要求 JSON-RPC error code 必须 integer。Request ID 不同：base JSON-RPC 允许 Number，只 discourage fractional parts。Fork 选择 string/integer-only interoperability。General guide 必须保留 normative distinction，不能把单一项目的 accepted-language policy 变成 universal rule。

### Portable widget work

Standard MCP Apps `postMessage` bridge 会改善 portability，但它改变 product / host-compatibility scope，也需要 real host tests。它不应偷偷进入 transport-hardening patch；现有 compatibility boundary 被精确记录。

## Review-bundle integrity incident

某次 ZIP upload 到 reviewer 后出现不可逆 `U+FFFD` replacement characters，尽管 local manifest 与 strict-UTF-8 source set 完整。Review 改为直接读取 public pinned commit，而不是把 corrupted attachment text 当作 authority。

Reusable handling：

1. 在 upload transformation 外保留 original source identity 与 manifest；
2. Ingestion 后检查 strict UTF-8、replacement-character count、file count 与 pinned revision；
3. Binary archive path 被 transcoded 后，不要从 damaged text 重构 exact code；
4. Manual model upload 若 archive handling 不确定，优先用 delimited strict-UTF-8 text bundle；
5. Disclosure policy 允许时，让 reviewer fetch public pinned commit；
6. 记录实际被 review 的 source。

## 这里的 “independent” 是什么

- Review prompts 与 analysis lanes 分开。
- Implementation tests 仍由同一 development effort 编写，因此不是 independent assurance。
- Local wire receipts 重新执行并记录，但并非 unrelated owner 执行；status 是 `reproduced`，不是 `independently-reproduced`。
- Public CI 在额外 runtimes 执行 test suite，但没有运行 local raw-socket probe suite。

Combined evidence 更强，是因为各 lane 的 failure pattern 不同，而不是因为某一 lane 被宣布“更高级”。
