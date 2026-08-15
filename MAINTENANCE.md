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

## Release checks

Run:

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

The bundled script paths above are repository-maintenance paths. When invoking the installed skill against another repository, resolve scripts relative to that skill package's `SKILL.md`, not by same-name lookup in the target repository.

Then inspect the staged diff, confirm no private continuity or raw logs entered the repository, commit intentionally, push, verify GitHub Actions, and tag the documented release only after the remote commit is known.
