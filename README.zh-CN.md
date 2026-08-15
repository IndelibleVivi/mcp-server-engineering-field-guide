# MCP Server Engineering Field Guide

一份 revision-aware 的工程参考，用于设计、审查、测试和维护 MCP servers 与 MCP Apps。

简体中文 · [English](README.md)

本项目把老化速度不同的四层内容分开：

- [稳定工程核心](FIELD-GUIDE.zh-CN.md)（[English](FIELD-GUIDE.md)）：capability ownership、trust boundaries、evidence discipline、resource budgets、egress、deployment 与 verification；
- [protocol profiles](profiles/README.zh-CN.md)（[English](profiles/README.md)）：特定 revision 的 normative requirements 与 migration consequences；
- [case studies](case-studies/)：以 public、pinned evidence 把通用方法锚定在真实 failure modes 上，并维护中英 semantic peers；
- 可分发的 [`mcp-server-engineering` skill](skill/mcp-server-engineering/SKILL.md)：只加载当前任务真正需要的 reference 的轻量 workflow controller。

## 从哪里开始

- 设计新 server：先读 [Field Guide 第 1–4 节](FIELD-GUIDE.zh-CN.md#1-中央模型partially-ordered-capability-boundary)，再从 [VERSION-REGISTER.json](VERSION-REGISTER.json) 选择目标 profile。
- 审查现有 server：pin source revision，识别它声明的 MCP revision 与 deployment reachability，再使用 [claim / evidence 方法](FIELD-GUIDE.zh-CN.md#2-evidence-discipline)。
- 升级 protocol revision：对比 [profiles/](profiles/README.zh-CN.md) 中适用的文件，并让 historical tests 继续绑定其原始 revision。
- 阅读起源实现：使用已去除私人工作痕迹的 [thinking-block case study](case-studies/gpt-thinking-block-mcp/CASE-STUDY.zh-CN.md)。
- 运行 agent workflow：调用 [skill/mcp-server-engineering](skill/mcp-server-engineering/SKILL.md) 中打包的 skill。
- 维护或发布 reference：遵循 [maintenance workflow](MAINTENANCE.zh-CN.md) 与 [changelog](CHANGELOG.zh-CN.md)。

## Version model

Guide 与 protocols 独立 versioning：

```text
guide release
    ├── stable core model
    ├── pinned normative protocol profiles
    ├── dated moving-integration assessments
    └── case-study evidence receipts
```

Release `2.0.0` 覆盖 MCP `2025-06-18`、`2025-11-25`、`2026-07-28`，以及 JSON-RPC 2.0 与 HTTP RFC 9110/9112。审查旧 server 时，依据它声明的 revision；设计新 server 时，查询当前支持的最新 official profile。详见 [VERSION-REGISTER.json](VERSION-REGISTER.json)。

English 与简体中文文档作为 semantic peers 维护：version、section identifiers、profile IDs、claim IDs、receipt IDs 与 evidence status 一致；English protocol keywords 与 identifiers 在两种语言中都保持 canonical。

## Publication status

Release `2.0.0` 已发布到 [IndelibleVivi/mcp-server-engineering-field-guide](https://github.com/IndelibleVivi/mcp-server-engineering-field-guide)；publication state 记录在 [VERSION-REGISTER.json](VERSION-REGISTER.json)。

Guide、profiles、case studies 与 evidence prose 使用 [CC BY 4.0](LICENSES/CC-BY-4.0.txt)；可分发 skill、scripts、templates 与 machine-readable project files 使用 [Apache-2.0](LICENSES/Apache-2.0.txt)。确切 file boundary 见 [LICENSING.md](LICENSING.md)。任何 license 都不是从 case-study repository 继承而来。

## Authorship 与 provenance

见 [AUTHORS.md](AUTHORS.md) 与 [ATTRIBUTION.md](ATTRIBUTION.md)。私人 working continuity、raw model transcripts、本机路径和未清理的 execution logs 均不属于这个 repo。
