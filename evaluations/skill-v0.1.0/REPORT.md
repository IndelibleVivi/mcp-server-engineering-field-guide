# Installed-skill dogfood report — `mcp-server-engineering` 0.1.0

[简体中文](REPORT.zh-CN.md) · English

## Verdict

**Pass, within the declared same-owner boundary.** The byte-identified installed skill completed one positive discovery canary and eight scored synthetic scenarios under rubric `1.1.0`. All nine runs were `valid-completed`, every critical rubric item passed, and no run accessed the evaluation oracle according to observable command traces.

This is installed end-to-end dogfood, not independent assurance and not a no-skill A/B comparison. The requested model was `gpt-5.6-sol`; the runtime did not report a more specific model identity, so that value remains `unknown`.

## Evaluation identity

| Field | Value |
| --- | --- |
| Baseline guide commit | `3a322c5e99dcce5e09ca1e718eb58fa03fae92c8` (`v2.0.0`) |
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

The runner used the authenticated user Codex home with `--ignore-user-config`, `--ignore-rules`, and `--ephemeral`. Those flags did not create a context-free process: user-global instructions and 45 installed skill descriptions remained ambient, and their hashes are recorded in every receipt. The discovery canary emitted one nonfatal diagnostic that skill descriptions had been shortened to fit the context budget; it still directly loaded the installed `SKILL.md` entrypoint and the selected revision reference.

## Release matrix

| Scenario | Revision | Invocation | Observable loading | Rubric result | Public output |
| --- | ---: | --- | --- | --- | --- |
| `CANARY-DISCOVERY-001` | 1 | discovery | entrypoint + revision reference | pass | [answer](outputs/20260815T183509-CANARY-DISCOVERY-001.md) |
| `STDIO-ZH-001` | 2 | explicit | entrypoint + selected references | pass | [answer](outputs/20260815T183700-STDIO-ZH-001.md) |
| `HTTP-HIST-EN-001` | 2 | explicit | entrypoint + historical HTTP references | pass | [answer](outputs/20260815T184022-HTTP-HIST-EN-001.md) |
| `UPGRADE-ZH-001` | 2 | explicit | entrypoint + source/target profiles | pass | [answer](outputs/20260815T184417-UPGRADE-ZH-001.md) |
| `MCP-APP-EN-001` | 2 | explicit | entrypoint + MCP Apps/integration references | pass | [answer](outputs/20260815T184809-MCP-APP-EN-001.md) |
| `GOOD-ZH-001` | 2 | explicit | entrypoint + selected references | pass | [answer](outputs/20260815T185218-GOOD-ZH-001.md) |
| `SSE-LIGHT-EN-001` | 2 | explicit | selected references; no fresh entrypoint read | pass | [answer](outputs/20260815T185516-SSE-LIGHT-EN-001.md) |
| `WORDING-DISCOVERY-EN-001` | 2 | discovery | no skill material | pass | [answer](outputs/20260815T185541-WORDING-DISCOVERY-EN-001.md) |
| `STDIO-EN-PAIR-001` | 2 | explicit | selected references; no fresh entrypoint read | pass | [answer](outputs/20260815T185600-STDIO-EN-PAIR-001.md) |

Machine-readable adjudication is in [`results.json`](results.json). Each run has a separate schema-v2 [same-owner receipt](receipts/) containing process/turn state, hashes, loading evidence, environment, and residuals. Public outputs contain the complete final agent messages with temporary local paths normalized to checked-in synthetic fixtures. Private raw JSONL and tool traces are omitted.

## What the runs established

1. **Revision selection:** historical `2025-06-18` session/SSE behavior was not condemned by later rules; the migration scenario loaded both source and target profiles and checked legacy-path absence.
2. **Applicability and owner precision:** the stdio runs marked HTTP controls `not applicable` and treated the parent/OS boundary as reachability ownership, not a fabricated network authentication protocol.
3. **Projection discipline:** the MCP App run separated model-visible content, component data, UI metadata, DOM input, host tool authority, CSP, cache/resource identity, and current-host compatibility.
4. **Evidence ceiling:** source findings, function-level reproduction, runtime unknowns, named-host unknowns, and independent assurance remained distinct.
5. **Restraint:** the already-good fixture received zero manufactured findings; the narrow SSE answer remained short; the wording-only task did not trigger the skill or expand into an audit.
6. **Bilingual semantics:** the paired English and Chinese stdio reports preserved revision choice, HTTP N/A controls, parent-owned authority, and source-only evidence ceiling after output language became an explicit prompt control.

## Protocol amendment provenance

Rubric `1.0.0` was used only for non-release preflight. It exposed evaluation defects: the observer initially missed an installed symlink spelling and direct relative reference reads, while the English bilingual prompt did not explicitly require English output. Those raw runs were retained privately and summarized in `results.json`; they were not erased, converted into skill failures, or counted for release.

Rubric `1.1.0` was frozen before the release runs. It distinguishes direct entrypoint evidence from skill-material evidence, accepts installed/resolved/relative reference spellings, adds explicit output-language checks, and increments every changed scored prompt to scenario revision `2`.

## Residual boundary

- Same-owner execution and same-owner, model-assisted assessment can confirm reproducible project behavior but cannot establish independent assurance.
- Observable command traces cannot prove the absence of every hidden context influence. The evaluation records ambient identities instead of claiming perfect isolation.
- Raw tool traces remain private. Public readers can inspect the full final answers, fixtures, prompts, hashes, receipts, rubric, and adjudication, but not reconstruct every internal reasoning step.
- This corpus measures whether the skill chooses the right revision, applicability, owner, evidence ceiling, and level of effort. It does not estimate a causal uplift over an unassisted model.

Because the skill package bytes did not change, this evidence supports guide release `2.0.1` while retaining skill version `0.1.0`.
