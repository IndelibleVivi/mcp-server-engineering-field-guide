# Maintenance workflow

[简体中文](MAINTENANCE.zh-CN.md) · English

The guide, protocol profiles, moving integration guidance, case-study receipts, and skill have separate version pressures. Update the smallest authoritative surface and then synchronize its declared peers.

## When a new MCP revision appears

1. Verify the official specification index and changelog.
2. Add a new profile; do not rewrite historical requirements in an older profile.
3. Record migration boundaries in both the old and new profiles where useful.
4. Update `VERSION-REGISTER.json`, `profiles/README*`, and the skill's protocol selection/reference set.
5. Run `sync_profile_mirrors.py --write VERSION-REGISTER.json`, record the new canonical SHA-256 values in the register, then verify with `--check`. The hash is used here for a real canonical-to-mirror identity decision.
6. Add revision-bound tests or test guidance for removed, added, and changed behavior.
7. Keep host/product guidance in a dated moving profile unless it is normative protocol text.

## Bilingual synchronization

- English and `zh-CN` are semantic peers, not source/summary.
- Keep IDs, version values, normative keywords, code, methods, headers, claim status, receipts, and residuals identical.
- Naturalize prose, but do not strengthen a `SHOULD` into a `MUST` or convert `unknown` into `verified` during translation.
- Change both peer files in one reviewable commit.

## Evidence updates

- Never edit a prior receipt to represent a new execution.
- Give a new run a new receipt ID or explicitly versioned receipt set.
- Keep raw private output outside the public repository when it contains local paths or sensitive material.
- A public projection preserves provenance and says what was removed.
- Change `reproduced` to `independently-reproduced` only when execution ownership truly changed.

## Skill updates

- Keep `SKILL.md` as a thin controller; place detailed method in `references/` and reusable output files in `assets/templates/`.
- Load only the task-relevant profile.
- Add a reference only when it changes agent behavior.
- Run the official skill validator and the repository-local structural validator.
- Forward-test material workflow changes on a pinned public or synthetic server without exposing private source.

## Architecture atlas updates

- Treat `docs/architecture/architecture-model.json` as the semantic authority for regions, nodes, states, edges, unknowns, selected views, and the render contract.
- Preserve stable `R/N/S/E/U` identities across English and Simplified Chinese. Update the model first when ownership, version, evidence status, or a feedback route changes.
- Build a native layout for a new form factor, and a new semantic view only
  when the reader's question materially changes. Do not crop, rotate, or splice
  a landscape canvas into a portrait detail page.
- Keep landscape repository/full-screen and portrait document/print layouts as
  native siblings when both materially help. Share one semantic model and
  stable IDs; name the reader job of each geometry and never let layout variants
  drift into separate truths.
- Keep `.excalidraw` geometry editable and publication SVGs paired for the three deep views. Run `prepare_bilingual_architecture_scenes.py`, `layout_portrait_architecture_scenes.py`, and `render_architecture_svgs.py` in that order.
- Maintain `V-FRONT` as two self-contained native-SVG source/publication siblings. Change the model first when semantics move; then update both languages, validate XML and forbidden external dependencies, and inspect 1600×900 plus README-width browser renders.
- Inspect all twelve deep-atlas SVGs and both `V-FRONT` SVGs at their intended reading scales. A successful script or XML check does not establish legibility, correct connector routing, sibling alignment, or semantic completeness.

## External review handoff

- Prefer a public repository URL plus a full commit hash over a ZIP attachment.
- If an archive is necessary, run `scan_review_bundle.py` before transfer and ask the reviewer to rerun strict UTF-8, `U+FFFD`, inventory, and manifest checks after ingestion.
- A read-only sandbox prevents mutation; it does not prove that an evaluation agent could not read an oracle. Materialize only the selected fixture, prompt, and fixture-local metadata in a separate temporary repository.
- If transfer changes bytes, stop exact-code claims and recover from the pinned public commit or a verified strict-UTF-8 text bundle. Keep the damaged artifact only as transfer evidence.

## Release checks

Run:

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

The bundled script paths above are repository-maintenance paths. When invoking the installed skill against another repository, resolve scripts relative to that skill package's `SKILL.md`, not by same-name lookup in the target repository.

Then inspect the staged diff, confirm no private continuity or raw logs entered the repository, commit intentionally, push, verify GitHub Actions, and tag the documented release only after the remote commit is known.
