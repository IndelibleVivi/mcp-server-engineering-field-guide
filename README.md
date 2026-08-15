# MCP Server Engineering Field Guide

A revision-aware engineering reference for designing, auditing, testing, and maintaining MCP servers and MCP Apps.

[简体中文](README.zh-CN.md) · English

The project separates four things that age at different rates:

- the [stable engineering core](FIELD-GUIDE.md) ([简体中文](FIELD-GUIDE.zh-CN.md)): capability ownership, trust boundaries, evidence discipline, resource budgets, egress, deployment, and verification;
- [protocol profiles](profiles/) ([简体中文](profiles/README.zh-CN.md)): revision-specific normative requirements and migration consequences;
- [case studies](case-studies/): public, pinned evidence that keeps the general method grounded in real failures, with English and Simplified Chinese peers;
- a distributable [`mcp-server-engineering` skill](skill/mcp-server-engineering/SKILL.md): a thin workflow controller that loads only the relevant references.

## Start here

- Designing a server: read [Field Guide sections 1–4](FIELD-GUIDE.md#1-the-central-model-a-partially-ordered-capability-boundary), then select the intended profile in [VERSION-REGISTER.json](VERSION-REGISTER.json).
- Auditing an existing server: pin its source revision, identify its declared MCP revision and deployment reachability, then use the [claim and evidence method](FIELD-GUIDE.md#2-evidence-discipline).
- Upgrading protocol revisions: compare the applicable files in [profiles/](profiles/) and keep historical tests bound to the revision they were written for.
- Learning from the originating implementation: use the sanitized [thinking-block case study](case-studies/gpt-thinking-block-mcp/CASE-STUDY.md).
- Running an agent workflow: invoke the packaged skill in [skill/mcp-server-engineering](skill/mcp-server-engineering/SKILL.md).
- Maintaining or releasing the reference: follow the [maintenance workflow](MAINTENANCE.md) and [changelog](CHANGELOG.md).

## Version model

The guide and the protocols have independent versions.

```text
guide release
    ├── stable core model
    ├── pinned normative protocol profiles
    ├── dated moving-integration assessments
    └── case-study evidence receipts
```

Release `2.0.0` covers MCP `2025-06-18`, `2025-11-25`, and `2026-07-28`, plus JSON-RPC 2.0 and HTTP RFC 9110/9112. An older server is reviewed against the revision it declares; a new design should consult the latest supported official profile. See [VERSION-REGISTER.json](VERSION-REGISTER.json).

English and Simplified Chinese documents are maintained as semantic peers. They share the same version, section identifiers, profile IDs, claim IDs, receipt IDs, and evidence status. English protocol keywords and identifiers remain canonical in both languages.

## Publication status

Release `2.0.0` is published at [IndelibleVivi/mcp-server-engineering-field-guide](https://github.com/IndelibleVivi/mcp-server-engineering-field-guide). Publication state is recorded in [VERSION-REGISTER.json](VERSION-REGISTER.json).

The guide, profiles, case studies, and evidence prose are licensed under [CC BY 4.0](LICENSES/CC-BY-4.0.txt). The distributable skill, scripts, templates, and machine-readable project files are licensed under [Apache-2.0](LICENSES/Apache-2.0.txt). See [LICENSING.md](LICENSING.md) for the exact file boundary. No license is inherited from a case-study repository.

## Authorship and provenance

See [AUTHORS.md](AUTHORS.md) and [ATTRIBUTION.md](ATTRIBUTION.md). Private working continuity, raw model transcripts, local machine paths, and unsanitized execution logs are intentionally not part of this repository.
