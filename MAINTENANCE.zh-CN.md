# Maintenance workflow

简体中文 · [English](MAINTENANCE.md)

Guide、protocol profiles、moving integration guidance、case-study receipts 与 skill 的 version pressure 不同。只更新最小 authoritative surface，再同步其 declared peers。

## 出现新 MCP revision 时

1. 核验 official specification index 与 changelog。
2. 新建 profile，不要在旧 profile 中重写 historical requirements。
3. 在有必要时，于新旧 profiles 同时记录 migration boundary。
4. 更新 `VERSION-REGISTER.json`、`profiles/README*` 与 skill protocol selection/reference set。
5. 运行 `sync_profile_mirrors.py --write VERSION-REGISTER.json`，把新的 canonical SHA-256 values 记录进 register，再用 `--check` 验证。这里的 hash 服务于真实 canonical-to-mirror identity decision，不是仪式性 checksum。
6. 为 removed、added、changed behavior 加入 revision-bound tests 或 test guidance。
7. 除非属于 normative protocol text，否则 host/product guidance 留在带日期的 moving profile。

## Bilingual synchronization

- English 与 `zh-CN` 是 semantic peers，不是 source/summary 关系。
- IDs、version values、normative keywords、code、methods、headers、claim status、receipts 与 residuals 保持一致。
- Prose 可以自然化，但 translation 不能把 `SHOULD` 强化成 `MUST`，也不能把 `unknown` 变成 `verified`。
- 两份 peer files 在同一个可 review commit 中修改。

## Evidence updates

- 不能修改旧 receipt 来代表新 execution。
- New run 使用新 receipt ID 或显式 versioned receipt set。
- Raw private output 若含 local paths 或 sensitive material，应留在 public repository 外。
- Public projection 保留 provenance，并说明删除了什么。
- 只有 execution ownership 真实变化时，才能把 `reproduced` 改成 `independently-reproduced`。

## Skill updates

- `SKILL.md` 保持 thin controller；详细 method 放在 `references/`，可复用 output files 放在 `assets/templates/`。
- 只加载 task-relevant profile。
- Reference 只有在会改变 agent behavior 时才加入。
- 同时运行 official skill validator 与 repository-local structural validator。
- Material workflow change 应在 pinned public 或 synthetic server 上 forward-test，不能暴露 private source。

## Release checks

运行：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 skill/mcp-server-engineering/scripts/check_python_syntax.py skill/mcp-server-engineering/scripts tests
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v
python3 skill/mcp-server-engineering/scripts/validate_version_register.py VERSION-REGISTER.json
python3 skill/mcp-server-engineering/scripts/sync_profile_mirrors.py --check VERSION-REGISTER.json
python3 skill/mcp-server-engineering/scripts/check_bilingual_coverage.py .
python3 skill/mcp-server-engineering/scripts/check_receipt_schema.py case-studies/gpt-thinking-block-mcp/receipts/*.json
python3 skill/mcp-server-engineering/scripts/validate_skill_package.py skill/mcp-server-engineering
python3 skill/mcp-server-engineering/scripts/check_markdown_links.py .
python3 skill/mcp-server-engineering/scripts/scan_review_bundle.py .
git diff --check
```

上面的 bundled script paths 属于 repository maintenance。若 installed skill 正在检查另一个 repository，应相对该 skill package 的 `SKILL.md` 解析 scripts，不能在 target repository 中按同名文件碰运气。

随后 inspect staged diff，确认没有 private continuity 或 raw logs 进入 repo，intentional commit、push、verify GitHub Actions；只有 remote commit 确定后再为 documented release 打 tag。
