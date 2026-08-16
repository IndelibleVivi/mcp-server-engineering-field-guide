# MCP Server Engineering Field Guide Agent Instructions

This repository publishes a revision-aware engineering method, pinned protocol
profiles, bilingual case-study evidence, and a thin distributable Codex Skill.
Its central contract is applicability: requirements, controls, and evidence must
stay bound to the server's declared MCP revision, transport, ownership, reachability,
and actual execution provenance.

Read `README.md`, `README.zh-CN.md`, `FIELD-GUIDE.md`, `VERSION-REGISTER.json`,
`MAINTENANCE.md`, `LICENSING.md`, and the relevant profile/case study before
editing. Global Faye/Cove collaboration style and private continuity live
outside this repository.

## Authority Layers

Keep these layers separate:

| Layer | Authority |
| --- | --- |
| `FIELD-GUIDE*.md` | stable capability ownership, trust-boundary, evidence, resource, egress, deployment, and verification method |
| `profiles/` | pinned normative protocol/revision reference and migration boundaries |
| dated moving profiles/integration guidance | host, SDK, deployment, or ecosystem behavior that can change independently of protocol |
| `case-studies/` | pinned public evidence applying the method to concrete code |
| `VERSION-REGISTER.json` | release/profile/document/receipt/version and publication registry |
| `skill/mcp-server-engineering/` | thin task router/controller plus selected references/templates |
| `evaluations/` | scoped evaluation fixtures, projected answers, rubrics, and receipts with explicit ownership/status |

A newer MCP profile does not rewrite an older profile. Historical tests and
servers remain bound to the revision they declare unless the task is an explicit
upgrade.

## Architecture Atlas Authority

The bilingual architecture atlas has three authority layers:

- `docs/architecture/architecture-model.json` is the renderer-neutral semantic
  authority for regions, nodes, canonical states, directed edges, declared
  unknowns/non-claims, selected views, layout variants, and the render contract.
- The twelve `.excalidraw` scenes own editable geometry and connector bindings
  for three semantic views across English/Simplified Chinese and native
  portrait/landscape layout families. Geometry is not a second semantic truth.
- The twelve `.svg` files are publication projections. Do not hand-edit them or
  treat rendered copy/coordinates as an independent model.

Preserve stable `R/N/S/E/U` identities, view IDs, versions, owners, edge
meanings, evidence status, and unknowns across both languages and both layout
families. English and Chinese are semantic peers; portrait and landscape are
native siblings, not crops, rotations, or splices of one another.

For a semantic atlas change, edit the model first and run the complete pipeline
from the repository root in this order:

```bash
python3 tools/architecture/prepare_bilingual_architecture_scenes.py
python3 tools/architecture/layout_portrait_architecture_scenes.py
python3 tools/architecture/render_architecture_svgs.py
```

A geometry-only change must preserve semantic IDs and update only the intended
scene geometry before rendering publication projections. These generators
rewrite tracked atlas files: do not run them for unrelated documentation-only
changes, and always inspect the generated diff plus both languages and both
layout families before publication.

## Revision Applicability

- Pin the audited source revision and identify the declared MCP revision before
  applying requirements.
- For a new design, select the latest supported official profile recorded in the
  register; for an existing design, use its declared/current target revision.
- Mark removed, added, changed, optional, and retained behavior explicitly during
  an upgrade.
- Do not retroactively require `2026-07-28` behavior from a correct
  `2025-06-18` server.
- A stateful `2025-11-25 -> 2026-07-28` upgrade must retire removed lifecycle,
  session, or protocol paths rather than leave both active without a documented
  compatibility owner.
- Preserve historical profile text. Add a new profile or versioned migration
  note instead of silently editing the past.
- Protocol keywords, method names, headers, status fields, claim IDs, and profile
  IDs are canonical and remain exact in translations.

## Transport And Ownership Applicability

- Identify transport before recommending controls.
- Host, Origin, CORS, HTTP framing, socket body timeout, reverse proxy, and URL
  derivation belong to reachable HTTP boundaries. Mark them `not applicable` for
  a parent-owned stdio server unless another HTTP surface actually exists.
- Parent/OS process possession can own reachability/caller possession without
  becoming an HTTP authentication protocol.
- Keep implementation invariants, host behavior, proxy configuration, deployment
  policy, and operator process as separate owners.
- For MCP Apps, separate model-visible, component-visible, operator-visible, and
  host-compatibility projections. Do not leak one projection into another or
  treat a host-specific bridge as the portable protocol.
- Apply a control only when it materially protects an identified asset/path at
  the layer that owns it.

## Evidence And Claim Status

- Source inspection, implementer-authored tests, same-owner reproduction,
  independent reproduction, external audit, and production observation are
  different evidence classes.
- Sanitization, projection, or publishing a receipt does not make evidence
  independent.
- Never label implementer-authored or same-owner evidence
  `independently-reproduced`.
- A read-only sandbox prevents mutation; it does not prove the evaluator could
  not read an oracle, answer key, hidden metadata, or prior result.
- Record selected fixture, source commit, tool/profile version, prompt/rubric,
  environment, result, residuals, and evidence owner needed to interpret a
  receipt.
- Never edit a prior receipt to represent a new execution. Create a new receipt
  ID/versioned set.
- Public projections state what was removed and preserve lineage to the private
  source where appropriate without exposing it.
- Unknown/unverified remains unknown/unverified. Do not convert missing evidence
  into a confident claim.

## Profile And Register Integrity

- `VERSION-REGISTER.json` is the machine-readable release authority.
- Update profile documents, register entries, skill references, README status,
  changelog, and bilingual peers coherently.
- Run profile mirror synchronization with `--write` only for an intentional
  canonical-to-mirror update; record hashes because they decide exact mirror
  identity here.
- Verify with `--check` afterward.
- Do not calculate or refresh hashes as ritual metadata when no identity decision
  uses them.
- Keep dated moving guidance out of stable normative profiles.
- Do not add a profile/reference that does not change agent behavior or review
  applicability.

## Bilingual Contract

English and Simplified Chinese files are semantic peers.

- Update both in one reviewable change.
- Keep versions, section IDs, profile IDs, claim IDs, receipt IDs, status,
  methods, headers, code, residuals, and normative strength aligned.
- Naturalize prose without strengthening `SHOULD` to `MUST`, narrowing or
  broadening scope, or changing `unknown` to `verified`.
- Maintain `BILINGUAL-MANIFEST.json` and coverage validation.
- Do not treat the Chinese file as a summary or delayed translation.

## Skill Package

- `SKILL.md` remains a thin revision-aware controller.
- Put detailed method in `references/` and reusable outputs in
  `assets/templates/`.
- Load only task-relevant profiles and references.
- Resolve installed-skill scripts relative to that Skill's `SKILL.md`; do not
  look up same-named scripts in the audited target repository.
- Validate the public package independently from private/local source context.
- Forward-test material workflow changes on pinned public or synthetic servers.
- Do not include private repos, local paths, raw model transcripts, unsanitized
  logs, or hidden answer keys in the package.

## Case Studies And Review Bundles

- Pin the source commit and retain attribution/license boundaries.
- Sanitize concrete private traces without erasing the provenance needed to
  understand the transformation.
- A case study documents one application of the method; it does not automatically
  generalize to every server.
- Prefer a public URL plus full commit hash for review.
- For archive transfer, run the bundle scanner and require strict UTF-8/U+FFFD,
  inventory, and manifest checks after ingestion.
- Byte-changing transfer breaks exact-code claims. Recover from the pinned public
  commit or verified strict-UTF-8 bundle.
- Keep damaged transfer artifacts only as transfer evidence, not canonical source.

## Licensing And Attribution

- Guide/profile/case-study/evidence prose follows the CC BY 4.0 boundary defined
  in `LICENSING.md`.
- Skill, scripts, templates, and machine-readable project files follow the
  Apache-2.0 boundary defined there.
- Do not apply one license to the other file class or inherit a license from a
  case-study repository.
- Preserve `AUTHORS.md`, `ATTRIBUTION.md`, `NOTICE`, and file-level provenance.
- Public reuse is encouraged with attribution; do not erase authorship or
  provenance.

## Release Checks

Run the canonical maintenance gate:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 skill/mcp-server-engineering/scripts/check_python_syntax.py skill/mcp-server-engineering/scripts tools tests
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v
python3 skill/mcp-server-engineering/scripts/validate_version_register.py VERSION-REGISTER.json
python3 skill/mcp-server-engineering/scripts/sync_profile_mirrors.py --check VERSION-REGISTER.json
python3 skill/mcp-server-engineering/scripts/check_bilingual_coverage.py .
python3 tools/validate_evaluation_corpus.py .
python3 skill/mcp-server-engineering/scripts/validate_skill_package.py skill/mcp-server-engineering
python3 skill/mcp-server-engineering/scripts/check_markdown_links.py .
python3 skill/mcp-server-engineering/scripts/scan_review_bundle.py .
git diff --check
```

- Use focused checks while iterating, then the full gate for a release/material
  authority change.
- Re-run forward evaluations only when the workflow/reference change can affect
  behavior; do not manufacture repeated receipts for typo-only edits.
- Report same-owner/dogfood receipts accurately and preserve residual limitations.
- A passing local gate is not a published release or independent assurance.

## Documentation Closure

- Update README peers for release status, supported profile set, validation
  status, publication, or entrypoint changes.
- Update Field Guide peers for stable method changes.
- Update profiles/register/skill references for revision changes.
- Update case studies/receipts for new evidence, without rewriting old runs.
- Update MAINTENANCE peers when release or synchronization procedure changes.
- Update CHANGELOG peers for released changes.
- Update this file when repository authority, applicability, evidence,
  bilingual, licensing, testing, or release behavior changes.

Private continuity lives outside Git in the external private-continuity root
governed by the user-level working contract.

## Git And Publication

- Inspect `git status --short`, stage explicit paths, review the staged diff, and
  run the release checks appropriate to the change.
- Never commit private continuity, raw private evaluations, local paths,
  unsanitized logs, credentials, or oracle material.
- Commit/push first, verify remote CI, then tag/publish the documented release
  only with explicit publication intent.
- Source commit, portable package, installed Skill, forward-test receipt, GitHub
  release, and independent assurance are separate facts.
