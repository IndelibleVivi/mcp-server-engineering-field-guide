# Licensing

Copyright 2026 Faye (IndelibleVivi).

This repository uses two licenses because its human-readable engineering reference and its executable/distributable skill have different reuse patterns.

## CC BY 4.0 — documentation and evidence prose

The following are licensed under the [Creative Commons Attribution 4.0 International License](LICENSES/CC-BY-4.0.txt):

- `README.md` and `README.zh-CN.md`;
- `FIELD-GUIDE.md` and `FIELD-GUIDE.zh-CN.md`;
- `CHANGELOG.md`, `CHANGELOG.zh-CN.md`, `MAINTENANCE.md`, and `MAINTENANCE.zh-CN.md`;
- `AUTHORS.md`, `ATTRIBUTION.md`, and this licensing explanation;
- `ARCHITECTURE.md`, `ARCHITECTURE.zh-CN.md`, and everything under `docs/architecture/`, including the renderer-neutral model, editable Excalidraw sources, and publication SVGs;
- all Markdown under `profiles/`;
- all Markdown and public evidence receipts under `case-studies/`.
- all Markdown prompts, reports, projected outputs, and JSON evidence receipts under `evaluations/**/receipts/`.

A recommended attribution is:

> *MCP Server Engineering Field Guide*, Faye (IndelibleVivi), version identified in `VERSION-REGISTER.json`, licensed CC BY 4.0.

Link to the public repository and indicate modifications when reasonably practicable.

## Apache-2.0 — skill, scripts, templates, and machine-readable project files

The following are licensed under the [Apache License 2.0](LICENSES/Apache-2.0.txt):

- everything under `skill/`;
- `VERSION-REGISTER.json` and `BILINGUAL-MANIFEST.json`;
- everything under `tests/` and `.github/`;
- everything under `tools/`, including the architecture rebuild pipeline;
- `evaluations/**/scenarios.json`, `evaluations/**/rubric.json`, `evaluations/**/results.json`, JSON schemas, and synthetic fixture source files under `evaluations/**/fixtures/`;
- validation or build scripts added at repository root in future;
- `.gitignore`, `NOTICE`, and other machine-oriented configuration created for this repository.

## Boundaries

- External specifications, RFCs, documentation, repositories, commits, and CI runs are linked as sources; this repository does not relicense them.
- The case study describes public source and observed behavior. It does not copy or relicense the case-study project's implementation.
- Facts and receipt measurements may not be copyrightable in some jurisdictions; the license statement still clarifies permission for the authored selection, arrangement, and explanatory text.
- Model-assisted drafting does not alter the named maintainer's publication decision or the source-specific attribution recorded in `ATTRIBUTION.md`.
- If a future file carries its own SPDX identifier or license notice, that file-specific notice controls.
