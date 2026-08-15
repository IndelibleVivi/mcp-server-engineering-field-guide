# Installed-skill dogfood report — `mcp-server-engineering` 0.1.0

简体中文 · [English](REPORT.md)

## Verdict

**在声明的 same-owner boundary 内通过。** 经过 byte identity 固定的 installed skill，在 rubric `1.1.0` 下完成了一个 positive discovery canary 与八个 scored synthetic scenarios。九个 runs 全部为 `valid-completed`，每个 critical rubric item 都通过，且 observable command traces 没有显示任何 run 访问 evaluation oracle。

这是 installed end-to-end dogfood，不是 independent assurance，也不是 no-skill A/B comparison。Requested model 是 `gpt-5.6-sol`；runtime 没有报告更具体的 model identity，因此该字段保持 `unknown`。

## Evaluation identity

| Field | Value |
| --- | --- |
| Baseline guide commit | `3a322c5e99dcce5e09ca1e718eb58fa03fae92c8`（`v2.0.0`） |
| Skill version | `0.1.0` |
| Installed skill tree SHA-256 | `80c741e46ea5757721225468e6153c10966ae0f3f24da48679e957d365f4dede` |
| Installation shape | directory symlink |
| Runner SHA-256 | `46cce3fa9c776de2fc976025799f384c30fc94ab6d88fce153eb72b529f39f09` |
| Codex CLI | `0.147.0` |
| Codex binary SHA-256 | `134063e133f0b4244fa3b251acf973d4fe4b4aeeacbdc135211bf480f59f1477` |
| Requested model / effort | `gpt-5.6-sol` / `high` |
| Runtime-reported model | `unknown` |
| Sandbox / approval | read-only / never |
| Rubric | `1.1.0` |

Runner 使用 authenticated user Codex home，并传入 `--ignore-user-config`、`--ignore-rules` 与 `--ephemeral`。这些 flags 没有创造 context-free process：user-global instructions 与 45 个 installed skill descriptions 仍然是 ambient context，它们的 hashes 已写入每个 receipt。Discovery canary 产生了一条 nonfatal diagnostic，说明 skill descriptions 为适应 context budget 被缩短；但它仍直接加载了 installed `SKILL.md` entrypoint 与选中的 revision reference。

## Release matrix

| Scenario | Revision | Invocation | Observable loading | Rubric result | Public output |
| --- | ---: | --- | --- | --- | --- |
| `CANARY-DISCOVERY-001` | 1 | discovery | entrypoint + revision reference | pass | [answer](outputs/20260815T183509-CANARY-DISCOVERY-001.md) |
| `STDIO-ZH-001` | 2 | explicit | entrypoint + selected references | pass | [answer](outputs/20260815T183700-STDIO-ZH-001.md) |
| `HTTP-HIST-EN-001` | 2 | explicit | entrypoint + historical HTTP references | pass | [answer](outputs/20260815T184022-HTTP-HIST-EN-001.md) |
| `UPGRADE-ZH-001` | 2 | explicit | entrypoint + source/target profiles | pass | [answer](outputs/20260815T184417-UPGRADE-ZH-001.md) |
| `MCP-APP-EN-001` | 2 | explicit | entrypoint + MCP Apps/integration references | pass | [answer](outputs/20260815T184809-MCP-APP-EN-001.md) |
| `GOOD-ZH-001` | 2 | explicit | entrypoint + selected references | pass | [answer](outputs/20260815T185218-GOOD-ZH-001.md) |
| `SSE-LIGHT-EN-001` | 2 | explicit | selected references；no fresh entrypoint read | pass | [answer](outputs/20260815T185516-SSE-LIGHT-EN-001.md) |
| `WORDING-DISCOVERY-EN-001` | 2 | discovery | no skill material | pass | [answer](outputs/20260815T185541-WORDING-DISCOVERY-EN-001.md) |
| `STDIO-EN-PAIR-001` | 2 | explicit | selected references；no fresh entrypoint read | pass | [answer](outputs/20260815T185600-STDIO-EN-PAIR-001.md) |

Machine-readable adjudication 位于 [`results.json`](results.json)。每个 run 都有独立的 schema-v2 [same-owner receipt](receipts/)，记录 process/turn state、hashes、loading evidence、environment 与 residuals。Public outputs 保留完整 final agent messages，只把 temporary local paths 规范化为 checked-in synthetic fixtures。Private raw JSONL 与 tool traces 不公开。

## Runs 证明了什么

1. **Revision selection：** historical `2025-06-18` 的 session/SSE behavior 没有被 later rules 追溯判错；migration scenario 同时加载 source / target profiles，并检查 legacy-path absence。
2. **Applicability 与 owner precision：** stdio runs 把 HTTP controls 标为 `not applicable`，并把 parent/OS boundary 视为 reachability owner，而不是伪造出来的 network authentication protocol。
3. **Projection discipline：** MCP App run 分开了 model-visible content、component data、UI metadata、DOM input、host tool authority、CSP、cache/resource identity 与 current-host compatibility。
4. **Evidence ceiling：** source findings、function-level reproduction、runtime unknowns、named-host unknowns 与 independent assurance 始终分层表达。
5. **克制：** already-good fixture 没有获得任何制造出来的 finding；窄幅 SSE 回答保持简短；wording-only task 没有触发 skill，也没有膨胀成 audit。
6. **Bilingual semantics：** output language 成为显式 prompt control 后，中英文 stdio peers 对 revision、HTTP N/A controls、parent-owned authority 与 source-only evidence ceiling 保持同一技术语义。

## Protocol amendment provenance

Rubric `1.0.0` 只用于 non-release preflight。它暴露了 evaluation 自身的问题：observer 起初遗漏 installed symlink spelling 与 relative reference direct reads；English bilingual prompt 也没有显式要求 English output。这些 raw runs 被保留在 private archive，并在 `results.json` 中概括；它们没有被抹去、包装成 skill failure，或计入 release。

Rubric `1.1.0` 在 release runs 前冻结。它区分 direct entrypoint evidence 与 skill-material evidence，接受 installed/resolved/relative reference spellings，加入显式 output-language checks，并把每个被改动的 scored prompt 升级为 scenario revision `2`。

## Residual boundary

- Same-owner execution 与 same-owner、model-assisted assessment 可以确认可复现的 project behavior，但不能建立 independent assurance。
- Observable command traces 无法证明不存在任何隐藏 context influence。Evaluation 记录 ambient identities，而不声称完美隔离。
- Raw tool traces 保持 private。Public reader 可以检查完整 final answers、fixtures、prompts、hashes、receipts、rubric 与 adjudication，但不能重建每一步 internal reasoning。
- 本 corpus 测量 skill 能否选择正确 revision、适用性、owner、evidence ceiling 与工作力度；它不估计 skill 相对于 unassisted model 的 causal uplift。

由于 skill package bytes 没有变化，这组 evidence 支持 guide release `2.0.1`，同时保留 skill version `0.1.0`。
