# Installed skill dogfood — `mcp-server-engineering` 0.1.0

[简体中文](README.zh-CN.md) · English

## Scope and claim boundary

This corpus tests whether the installed skill selects the declared revision, marks inapplicable controls, identifies the enforcement owner, respects the evidence ceiling, and stops when a task is already narrow. It does not compare against a no-skill baseline and does not provide independent assurance.

The baseline skill is the package published with guide tag `v2.0.0`. Runs use fresh Codex CLI tasks against newly authored synthetic fixtures. A separate discovery canary must prove that the installed entrypoint can be found before scored runs are accepted.

## Evidence authority

| Artifact | Authority |
| --- | --- |
| Receipt | Records process, turn, installed-skill identity, loading evidence, and the observable execution result. |
| Projected final output | Shows the complete final agent message without private tool traces or local paths. |
| `results.json` | Records maintainer-authorized adjudication against the preregistered rubric; it references rather than duplicates receipt observations. |

All executions and assessments are same-owner. A projected or sanitized representation does not change that provenance.

The completed evidence and adjudication are summarized in the bilingual [dogfood report](REPORT.md) ([简体中文](REPORT.zh-CN.md)).

## Oracle isolation and invocation

Each run materializes only one fixture, its prompt, and fixture-local identity metadata in a new temporary Git repository. The rubric, expected decisions, other scenarios, prior outputs, receipts, and this repository are not copied into that workspace. Read-only sandboxing prevents mutation but is not treated as proof that the process could not read other filesystem locations; command traces are checked for observed oracle access.

Core scenarios and the internal-proportionality probe explicitly invoke `$mcp-server-engineering`. The wording-only probe relies on description-based discovery. A separate positive discovery canary makes a non-trigger in that wording probe interpretable.

Loading evidence distinguishes the installed `SKILL.md` entrypoint from bundled reference material. The discovery canary requires direct entrypoint evidence. Explicit core runs require command-trace evidence for either the entrypoint or a bundled reference, because a correctly routed task may reuse already-loaded instructions and read only the task-relevant reference.

## Scenarios

| ID | Purpose | Invocation |
| --- | --- | --- |
| `CANARY-DISCOVERY-001` | Prove description-based discovery can load the symlinked installed skill. | discovery |
| `STDIO-ZH-001` | Parent-owned stdio applicability, ownership, and evidence ceiling in Chinese. | explicit |
| `HTTP-HIST-EN-001` | Historical `2025-06-18` audit with one revision-independent defect. | explicit |
| `UPGRADE-ZH-001` | `2025-11-25` to `2026-07-28` migration and legacy-path absence. | explicit |
| `MCP-APP-EN-001` | MCP App projections, widget authority, and dated host guidance. | explicit |
| `GOOD-ZH-001` | Already-good server with source-verifiable, runtime-unknown, and N/A claims. | explicit |
| `SSE-LIGHT-EN-001` | Internal proportionality on a small SSE explanation. | explicit |
| `WORDING-DISCOVERY-EN-001` | Description-trigger precision for a wording-only task. | discovery |
| `STDIO-EN-PAIR-001` | Semantic peer of `STDIO-ZH-001` for bilingual comparison. | explicit |

Scenario identities, prompt/fixture hashes, and revisions are preregistered in [`scenarios.json`](scenarios.json). Expected decisions live separately in [`rubric.json`](rubric.json) and are never copied into the run workspace. Changing a fixture or prompt requires a new `scenario_revision`; an old run remains bound to the old revision.

## Run and rubric success

The runner distinguishes process exit, thread/turn events, trace completeness, final-message availability, and rubric adjudication. Only `valid-completed` runs enter the rubric. Allowed validity values are `valid-completed`, `invalid-fixture`, `infrastructure-failed`, `model-failed`, `trace-incomplete`, and `timed-out`.

An invalid fixture is not a skill failure. A valid run that exposes a skill defect remains a public fail; a later fixed run is appended rather than replacing it. Every critical rubric item must pass for the release-candidate skill version.

## Protocol preflight and amendment

Non-release preflight runs against rubric `1.0.0` exposed two evaluation defects before publication. The trace observer initially recognized only the resolved skill path and missed the installed symlink spelling; it also treated direct reads of relative `references/*.md` paths as if no skill material had loaded. Separately, the English member of the bilingual pair did not explicitly require English output, so ambient user-global language guidance made that comparison ambiguous.

Those runs remain in the private raw evidence archive and are not counted as skill failures or release evidence. Rubric `1.1.0` separates entrypoint loading from skill-material loading, recognizes installed, resolved, and relative reference spellings, and adds an explicit output-language check. All scored prompts changed by that language control are scenario revision `2`; official release runs occur only after this amendment is frozen.

## Reproduction

Run corpus validation before execution:

```bash
python3 tools/validate_evaluation_corpus.py . --allow-missing-results
```

Run the canary first, then the scored scenarios, with an operator-controlled output directory outside the public repository:

```bash
python3 tools/run_skill_dogfood.py \
  --scenario CANARY-DISCOVERY-001 \
  --output-dir "$PRIVATE_OUTPUT_DIR" \
  --model gpt-5.6-sol \
  --reasoning-effort high
```

The runner uses the authenticated Codex home with `--ignore-user-config`, `--ignore-rules`, `--ephemeral`, a read-only sandbox, approval policy `never`, a fixed locale, and a wall-clock timeout. These flags do not erase user-global instructions or other installed skill descriptions; their hashed ambient identity and the residual are recorded.

## Publication status

Rubric `1.1.0` produced nine `valid-completed` release runs: one positive discovery canary and eight scored scenarios. All critical items passed same-owner adjudication. The machine-readable [results](results.json), complete [projected final answers](outputs/), and schema-v2 [receipts](receipts/) are public; private raw JSONL and tool traces remain outside the repository.

This supports a same-owner installed end-to-end dogfood claim for skill `0.1.0`. It does not support independent assurance, a causal no-skill comparison, or a more specific runtime model identity than `unknown`. Repository tests and local corpus validation have passed; remote CI and the release object remain separate publication gates until the release workflow completes.
