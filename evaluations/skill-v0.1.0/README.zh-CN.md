# Installed skill dogfood — `mcp-server-engineering` 0.1.0

简体中文 · [English](README.md)

## Scope 与 claim boundary

本 corpus 检查 installed skill 能否选择 declared revision、标记不适用 controls、识别 enforcement owner、守住 evidence ceiling，并在任务已经足够窄时停下来。它不与 no-skill baseline 比较，也不提供 independent assurance。

Baseline skill 是 guide tag `v2.0.0` 发布的 package。每个 run 使用 fresh Codex CLI task 与 newly authored synthetic fixture。所有计分 run 被接纳前，必须先由独立 discovery canary 证明 installed entrypoint 可以被发现。

## Evidence authority

| Artifact | Authority |
| --- | --- |
| Receipt | 记录 process、turn、installed-skill identity、loading evidence 与可观察 execution result。 |
| Projected final output | 展示完整 final agent message，不包含 private tool traces 或 local paths。 |
| `results.json` | 记录 maintainer-authorized、依据 preregistered rubric 作出的 adjudication；它引用而不重复 receipt observations。 |

全部 executions 与 assessments 都是 same-owner。Projected 或 sanitized representation 不会改变 provenance。

已完成的 evidence 与 adjudication 汇总在双语 [dogfood report](REPORT.zh-CN.md)（[English](REPORT.md)）中。

## Oracle isolation 与 invocation

每次 run 只把一个 fixture、对应 prompt 与 fixture-local identity metadata 物化到新的 temporary Git repository。Rubric、expected decisions、其他 scenarios、既有 outputs、receipts 与本仓库都不会复制到该 workspace。Read-only sandbox 能阻止 mutation，但不被当作 process 无法读取其他 filesystem locations 的证明；command traces 会检查可观察到的 oracle access。

Core scenarios 与 internal-proportionality probe 显式调用 `$mcp-server-engineering`。Wording-only probe 依赖 description-based discovery；另一个 positive discovery canary 让 wording probe 中的 non-trigger 具有可解释性。

Loading evidence 会区分 installed `SKILL.md` entrypoint 与 bundled reference material。Discovery canary 必须留下直接 entrypoint evidence；显式 core runs 则必须由 command trace 证明 entrypoint 或至少一个 bundled reference 被读取，因为正确 routed 的 task 可能复用已加载的 instructions，只读取与当前任务相关的 reference。

## Scenarios

| ID | Purpose | Invocation |
| --- | --- | --- |
| `CANARY-DISCOVERY-001` | 证明 description-based discovery 能加载 symlinked installed skill。 | discovery |
| `STDIO-ZH-001` | 用中文测试 parent-owned stdio 的 applicability、ownership 与 evidence ceiling。 | explicit |
| `HTTP-HIST-EN-001` | 审查 historical `2025-06-18`，同时包含一个与 revision 演进无关的真实 defect。 | explicit |
| `UPGRADE-ZH-001` | 测试 `2025-11-25` 到 `2026-07-28` migration 与 legacy-path absence。 | explicit |
| `MCP-APP-EN-001` | 测试 MCP App projections、widget authority 与 dated host guidance。 | explicit |
| `GOOD-ZH-001` | 测试 already-good server 中 source-verifiable、runtime-unknown 与 N/A claims。 | explicit |
| `SSE-LIGHT-EN-001` | 用小型 SSE explanation 测试 internal proportionality。 | explicit |
| `WORDING-DISCOVERY-EN-001` | 用 wording-only task 测试 description-trigger precision。 | discovery |
| `STDIO-EN-PAIR-001` | `STDIO-ZH-001` 的 semantic peer，用于 bilingual comparison。 | explicit |

Scenario identities、prompt/fixture hashes 与 revisions 预注册在 [`scenarios.json`](scenarios.json)。Expected decisions 单独保存在 [`rubric.json`](rubric.json)，永远不会复制到 run workspace。Fixture 或 prompt 发生变化时必须创建新的 `scenario_revision`；旧 run 继续绑定旧 revision。

## Run 与 rubric success

Runner 区分 process exit、thread/turn events、trace completeness、final-message availability 与 rubric adjudication。只有 `valid-completed` run 才进入 rubric。允许的 validity values 为 `valid-completed`、`invalid-fixture`、`infrastructure-failed`、`model-failed`、`trace-incomplete` 与 `timed-out`。

Invalid fixture 不是 skill failure。有效 run 若暴露 skill defect，应作为 public fail 保留；后续 fixed run 只能追加，不能替换。Release-candidate skill version 的每个 critical rubric item 都必须通过。

## Protocol preflight 与 amendment

在公开发布前，针对 rubric `1.0.0` 的 non-release preflight runs 暴露了两处 evaluation defect。Trace observer 起初只识别 resolved skill path，遗漏了 installed symlink spelling；它也把通过 relative `references/*.md` 路径直接读取 bundled references 的行为误判成没有加载任何 skill material。与此同时，bilingual pair 的 English member 没有显式要求 English output，导致 ambient user-global language guidance 让这组比较变得含混。

这些 runs 会保留在 private raw evidence archive 中，但不计作 skill failure，也不作为 release evidence。Rubric `1.1.0` 区分 entrypoint loading 与 skill-material loading，识别 installed、resolved 与 relative reference spellings，并加入显式 output-language check。所有被该 language control 改动的 scored prompts 都升级为 scenario revision `2`；只有 amendment 冻结后的 official runs 才参与 release 判定。

## Reproduction

Execution 前先运行 corpus validation：

```bash
python3 tools/validate_evaluation_corpus.py . --allow-missing-results
```

先运行 canary，再运行计分 scenarios；output directory 由 operator 控制，并位于 public repository 之外：

```bash
python3 tools/run_skill_dogfood.py \
  --scenario CANARY-DISCOVERY-001 \
  --output-dir "$PRIVATE_OUTPUT_DIR" \
  --model gpt-5.6-sol \
  --reasoning-effort high
```

Runner 使用 authenticated Codex home，并固定 `--ignore-user-config`、`--ignore-rules`、`--ephemeral`、read-only sandbox、approval policy `never`、locale 与 wall-clock timeout。这些 flags 不会抹除 user-global instructions 或其他 installed skill descriptions；runner 会记录它们的 hashed ambient identity 与 residual。

## Publication status

Rubric `1.1.0` 产生了九个 `valid-completed` release runs：一个 positive discovery canary 与八个 scored scenarios。Same-owner adjudication 下的全部 critical items 都通过。Machine-readable [results](results.json)、完整 [projected final answers](outputs/) 与 schema-v2 [receipts](receipts/) 已公开；private raw JSONL 与 tool traces 继续保留在 repository 之外。

这支持对 skill `0.1.0` 作出 same-owner installed end-to-end dogfood claim；它不支持 independent assurance、causal no-skill comparison，也不能把 runtime model identity 从 `unknown` 抬高。Repository tests 与 local corpus validation 已通过；remote CI 与 release object 在 release workflow 完成前仍是独立 publication gates。
