#!/usr/bin/env python3
"""Validate evaluation identities, public result references, and release gates."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path, PurePosixPath
import sys


sys.dont_write_bytecode = True


ALLOWED_OUTCOMES = {"pass", "partial", "fail", "unknown"}
ALLOWED_VALIDITY = {
    "valid-completed",
    "invalid-fixture",
    "infrastructure-failed",
    "model-failed",
    "trace-incomplete",
    "timed-out",
}
FORBIDDEN_FIXTURE_NAMES = {
    "rubric.json",
    "results.json",
    "expected_decisions.json",
}
PRIVATE_OUTPUT_MARKERS = (
    "/" + "Users/",
    "/private/var/",
    "/var/folders/",
    ".codex/" + "private-continuity",
    ".codex/" + "attachments",
)


def load_json(path: Path, errors: list[str]) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="strict"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"{path}: cannot read strict JSON: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"{path}: root must be an object")
        return {}
    return data


def safe_path(root: Path, value: object, label: str, errors: list[str]) -> Path | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{label}: expected a non-empty relative path")
        return None
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts:
        errors.append(f"{label}: path must remain inside evaluation root")
        return None
    path = root.joinpath(*pure.parts)
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        errors.append(f"{label}: resolved path escapes evaluation root")
        return None
    return path


def load_tool(root: Path, name: str):
    path = root / "tools" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_receipt_validator(root: Path):
    path = root / "skill" / "mcp-server-engineering" / "scripts" / "check_receipt_schema.py"
    spec = importlib.util.spec_from_file_location("check_receipt_schema", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate(root: Path, allow_missing_results: bool = False) -> list[str]:
    errors: list[str] = []
    evaluation = root / "evaluations" / "skill-v0.1.0"
    scenarios_path = evaluation / "scenarios.json"
    rubric_path = evaluation / "rubric.json"
    results_path = evaluation / "results.json"
    scenarios_data = load_json(scenarios_path, errors)
    rubric_data = load_json(rubric_path, errors)
    runner = load_tool(root, "run_skill_dogfood")

    if scenarios_data.get("schema_version") != 1:
        errors.append("scenarios.json: schema_version must be 1")
    rubric_version = scenarios_data.get("rubric_version")
    if rubric_data.get("schema_version") != 1:
        errors.append("rubric.json: schema_version must be 1")
    if rubric_data.get("rubric_version") != rubric_version:
        errors.append("rubric version differs between scenarios.json and rubric.json")

    rubric_items = rubric_data.get("items")
    if not isinstance(rubric_items, dict) or not rubric_items:
        errors.append("rubric.json: items must be a non-empty object")
        rubric_items = {}
    critical_items = {
        item_id
        for item_id, item in rubric_items.items()
        if isinstance(item, dict) and item.get("critical") is True
    }
    scenario_rubrics = rubric_data.get("scenario_items")
    if not isinstance(scenario_rubrics, dict):
        errors.append("rubric.json: scenario_items must be an object")
        scenario_rubrics = {}

    scenarios = scenarios_data.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        errors.append("scenarios.json: scenarios must be a non-empty array")
        scenarios = []
    scenario_by_id: dict[str, dict] = {}
    seen_scenario_revisions: set[tuple[str, int]] = set()
    for index, scenario in enumerate(scenarios):
        label = f"scenarios[{index}]"
        if not isinstance(scenario, dict):
            errors.append(f"{label}: expected an object")
            continue
        scenario_id = scenario.get("scenario_id")
        revision = scenario.get("scenario_revision")
        if not isinstance(scenario_id, str) or not scenario_id:
            errors.append(f"{label}.scenario_id: expected a non-empty string")
            continue
        if not isinstance(revision, int) or isinstance(revision, bool) or revision <= 0:
            errors.append(f"{label}.scenario_revision: expected a positive integer")
            continue
        identity = (scenario_id, revision)
        if identity in seen_scenario_revisions:
            errors.append(f"duplicate scenario identity: {scenario_id}@{revision}")
        seen_scenario_revisions.add(identity)
        if scenario_id in scenario_by_id:
            errors.append(f"duplicate active scenario ID: {scenario_id}")
        scenario_by_id[scenario_id] = scenario
        if scenario.get("rubric_version") != rubric_version:
            errors.append(f"{label}: rubric_version mismatch")
        requires_skill_load = scenario.get("requires_skill_load")
        requires_entrypoint_load = scenario.get("requires_entrypoint_load", False)
        if not isinstance(requires_skill_load, bool):
            errors.append(f"{label}.requires_skill_load: expected boolean")
        if not isinstance(requires_entrypoint_load, bool):
            errors.append(f"{label}.requires_entrypoint_load: expected boolean")
        if requires_entrypoint_load is True and requires_skill_load is not True:
            errors.append(f"{label}: entrypoint loading implies skill-material loading")
        fixture = safe_path(evaluation, scenario.get("fixture_path"), f"{label}.fixture_path", errors)
        prompt = safe_path(evaluation, scenario.get("prompt_path"), f"{label}.prompt_path", errors)
        if fixture is not None:
            if not fixture.is_dir():
                errors.append(f"{label}.fixture_path: directory is absent")
            else:
                observed = runner.tree_sha256(fixture)
                if observed != scenario.get("fixture_content_sha256"):
                    errors.append(f"{label}: fixture_content_sha256 mismatch")
                for path in fixture.rglob("*"):
                    if path.is_file() and path.name in FORBIDDEN_FIXTURE_NAMES:
                        errors.append(f"{label}: fixture contains oracle file {path.name}")
        if prompt is not None:
            if not prompt.is_file():
                errors.append(f"{label}.prompt_path: file is absent")
            else:
                observed = runner.sha256_file(prompt)
                if observed != scenario.get("prompt_content_sha256"):
                    errors.append(f"{label}: prompt_content_sha256 mismatch")
                explicit = "$mcp-server-engineering" in prompt.read_text(
                    encoding="utf-8", errors="strict"
                )
                if scenario.get("invocation_mode") == "explicit" and not explicit:
                    errors.append(f"{label}: explicit invocation prompt lacks skill name")
                if scenario.get("invocation_mode") == "discovery" and explicit:
                    errors.append(f"{label}: discovery prompt explicitly names the skill")
        item_ids = scenario_rubrics.get(scenario_id)
        if not isinstance(item_ids, list) or not item_ids:
            errors.append(f"rubric.json: no rubric items for {scenario_id}")
        elif any(item_id not in rubric_items for item_id in item_ids):
            errors.append(f"rubric.json: {scenario_id} references an unknown rubric item")

    receipt_validator = load_receipt_validator(root)
    receipts = sorted(
        path
        for path in root.rglob("receipts/*.json")
        if ".git" not in path.parts
    )
    if not receipts:
        errors.append("repository contains zero discovered public receipts")
    receipt_paths: dict[str, Path] = {}
    for receipt in receipts:
        receipt_errors = receipt_validator.validate(receipt)
        errors.extend(f"{receipt.relative_to(root)}: {error}" for error in receipt_errors)
        data = load_json(receipt, errors)
        receipt_id = data.get("receipt_id") or data.get("receipt_set_id")
        if isinstance(receipt_id, str):
            if receipt_id in receipt_paths:
                errors.append(f"duplicate public receipt ID: {receipt_id}")
            receipt_paths[receipt_id] = receipt

    if not results_path.is_file():
        if not allow_missing_results:
            errors.append("results.json is required")
        return errors
    results = load_json(results_path, errors)
    if results.get("schema_version") != 1:
        errors.append("results.json: schema_version must be 1")
    if results.get("rubric_version") != rubric_version:
        errors.append("results.json: rubric_version mismatch")
    candidate_version = results.get("release_candidate_skill_version")
    if not isinstance(candidate_version, str) or not candidate_version:
        errors.append("results.json: release_candidate_skill_version is required")
    runs = results.get("runs")
    if not isinstance(runs, list) or not runs:
        errors.append("results.json: runs must be a non-empty array")
        runs = []
    seen_runs: set[str] = set()
    seen_result_receipts: set[str] = set()
    passing_candidate_scenarios: set[str] = set()
    for index, run in enumerate(runs):
        label = f"results.runs[{index}]"
        if not isinstance(run, dict):
            errors.append(f"{label}: expected an object")
            continue
        run_id = run.get("run_id")
        if not isinstance(run_id, str) or not run_id:
            errors.append(f"{label}.run_id is required")
        elif run_id in seen_runs:
            errors.append(f"duplicate run ID: {run_id}")
        else:
            seen_runs.add(run_id)
        scenario_id = run.get("scenario_id")
        scenario = scenario_by_id.get(scenario_id)
        if scenario is None:
            errors.append(f"{label}: unknown scenario_id {scenario_id!r}")
            continue
        if run.get("scenario_revision") != scenario.get("scenario_revision"):
            errors.append(f"{label}: scenario_revision does not match active corpus")
        validity = run.get("run_validity")
        if validity not in ALLOWED_VALIDITY:
            errors.append(f"{label}: unsupported run_validity {validity!r}")
        receipt_id = run.get("receipt_id")
        if not isinstance(receipt_id, str) or receipt_id not in receipt_paths:
            errors.append(f"{label}: referenced receipt is absent")
        elif receipt_id in seen_result_receipts:
            errors.append(f"{label}: receipt is referenced by more than one result")
        else:
            seen_result_receipts.add(receipt_id)
            receipt_data = load_json(receipt_paths[receipt_id], errors)
            if "recorded_at" not in receipt_data:
                errors.append(f"{label}: evaluation receipt requires recorded_at")
        output = safe_path(evaluation, run.get("output_projection_path"), f"{label}.output_projection_path", errors)
        if output is not None:
            if not output.is_file():
                errors.append(f"{label}: projected final output is absent")
            else:
                try:
                    output_text = output.read_text(encoding="utf-8", errors="strict")
                except (OSError, UnicodeError) as exc:
                    errors.append(f"{label}: cannot read projected output as strict UTF-8: {exc}")
                else:
                    if "\ufffd" in output_text:
                        errors.append(f"{label}: projected output contains U+FFFD")
                    for marker in PRIVATE_OUTPUT_MARKERS:
                        if marker in output_text:
                            errors.append(
                                f"{label}: projected output contains private path marker {marker}"
                            )
        outcomes = run.get("rubric_outcomes")
        expected_items = scenario_rubrics.get(scenario_id, [])
        if not isinstance(outcomes, dict):
            errors.append(f"{label}: rubric_outcomes must be an object")
            outcomes = {}
        if set(outcomes) != set(expected_items):
            errors.append(f"{label}: rubric_outcomes must cover exactly the scenario rubric")
        if any(value not in ALLOWED_OUTCOMES for value in outcomes.values()):
            errors.append(f"{label}: unsupported rubric outcome")
        if validity != "valid-completed" and run.get("counts_for_release") is True:
            errors.append(f"{label}: invalid run cannot count for release")
        critical_for_scenario = set(expected_items) & critical_items
        critical_pass = all(outcomes.get(item_id) == "pass" for item_id in critical_for_scenario)
        if (
            run.get("counts_for_release") is True
            and validity == "valid-completed"
            and run.get("skill_version") == candidate_version
            and critical_pass
        ):
            passing_candidate_scenarios.add(scenario_id)
        for key in ("assessment_owner", "assessment_method"):
            if not isinstance(run.get(key), str) or not run[key].strip():
                errors.append(f"{label}.{key} is required")
        if not isinstance(run.get("model_assisted_assessment"), bool):
            errors.append(f"{label}.model_assisted_assessment must be boolean")
        if not isinstance(run.get("evidence_references"), list):
            errors.append(f"{label}.evidence_references must be an array")
        if not isinstance(run.get("residuals"), list):
            errors.append(f"{label}.residuals must be an array")

    required_scenarios = {
        scenario_id
        for scenario_id, scenario in scenario_by_id.items()
        if scenario.get("required_for_release") is True
    }
    missing_passes = sorted(required_scenarios - passing_candidate_scenarios)
    if missing_passes:
        errors.append(
            "release candidate lacks a valid critical-pass run for: " + ", ".join(missing_passes)
        )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--allow-missing-results", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate(root, allow_missing_results=args.allow_missing_results)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    receipt_count = len(
        [path for path in root.rglob("receipts/*.json") if ".git" not in path.parts]
    )
    print(f"PASS: evaluation corpus and {receipt_count} discovered public receipts are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
