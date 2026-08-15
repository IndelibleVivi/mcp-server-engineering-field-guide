#!/usr/bin/env python3
"""Run oracle-isolated, installed-skill dogfood scenarios through Codex CLI."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = ROOT / "evaluations" / "skill-v0.1.0"
SCENARIOS_PATH = EVALUATION_ROOT / "scenarios.json"
ALLOWED_VALIDITY = {
    "valid-completed",
    "invalid-fixture",
    "infrastructure-failed",
    "model-failed",
    "trace-incomplete",
    "timed-out",
}


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def tree_sha256(root: Path) -> str:
    """Hash sorted relative paths and bytes; directory metadata is excluded."""
    digest = hashlib.sha256()
    files = [path for path in root.rglob("*") if path.is_file()]
    for path in sorted(files, key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8", errors="strict"))
    if not isinstance(data, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return data


def run_text(arguments: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(
        arguments,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {arguments!r}: {result.stderr.strip()}"
        )
    return result.stdout.strip()


def installed_kind(path: Path, realpath: Path) -> str:
    if path.is_symlink():
        return "directory-symlink"
    try:
        run_text(["git", "-C", str(realpath), "rev-parse", "--show-toplevel"])
    except RuntimeError:
        return "copied"
    return "directory"


def skill_identity(installed: Path, expected_commit: str, expected_tree_hash: str) -> dict:
    if not installed.exists() or not installed.is_dir():
        raise ValueError(f"installed skill directory is absent: {installed}")
    realpath = installed.resolve()
    entrypoint = realpath / "SKILL.md"
    if not entrypoint.is_file():
        raise ValueError(f"installed skill entrypoint is absent: {entrypoint}")
    observed_tree_hash = tree_sha256(realpath)
    if observed_tree_hash != expected_tree_hash:
        raise ValueError(
            "installed skill tree does not match the preregistered baseline: "
            f"expected {expected_tree_hash}, observed {observed_tree_hash}"
        )
    repository_root = Path(
        run_text(["git", "-C", str(realpath), "rev-parse", "--show-toplevel"])
    ).resolve()
    source_commit = run_text(["git", "-C", str(realpath), "rev-parse", "HEAD"])
    relative_skill = realpath.relative_to(repository_root).as_posix()
    status = run_text(
        ["git", "-C", str(repository_root), "status", "--porcelain", "--", relative_skill]
    )
    if status:
        raise ValueError("installed skill source has tracked or untracked changes")
    tag_diff = subprocess.run(
        ["git", "-C", str(repository_root), "diff", "--quiet", expected_commit, "--", relative_skill],
        check=False,
    )
    if tag_diff.returncode != 0:
        raise ValueError("installed skill bytes differ from the preregistered source commit")
    return {
        "version": None,
        "source_commit": source_commit,
        "baseline_source_commit": expected_commit,
        "tree_sha256": observed_tree_hash,
        "installed_realpath_kind": installed_kind(installed, realpath),
        "installed_path": installed.absolute(),
        "installed_entrypoint": installed.absolute() / "SKILL.md",
        "entrypoint": entrypoint,
        "realpath": realpath,
    }


def ambient_context() -> dict:
    home = Path.home()
    agents = home / ".codex" / "AGENTS.md"
    skills_root = home / ".codex" / "skills"
    catalog = hashlib.sha256()
    count = 0
    if skills_root.is_dir():
        for entrypoint in sorted(skills_root.glob("*/SKILL.md"), key=lambda item: item.parent.name):
            if not entrypoint.is_file():
                continue
            count += 1
            catalog.update(entrypoint.parent.name.encode("utf-8"))
            catalog.update(b"\0")
            catalog.update(entrypoint.read_bytes())
            catalog.update(b"\0")
    return {
        "global_agents_present": agents.is_file(),
        "global_agents_sha256": sha256_file(agents) if agents.is_file() else None,
        "ambient_skill_count": count,
        "ambient_skill_catalog_sha256": catalog.hexdigest(),
        "residual": (
            "User-global instructions and other installed skill descriptions may remain ambient; "
            "ignore-user-config, ignore-rules, and ephemeral do not prove a context-free process."
        ),
    }


def init_fixture_repository(workspace: Path, fixture: Path, prompt: Path, scenario: dict) -> None:
    for source in sorted(fixture.rglob("*")):
        relative = source.relative_to(fixture)
        destination = workspace / relative
        if source.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        elif source.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
    shutil.copyfile(prompt, workspace / "TASK.md")
    context = {
        "scenario_id": scenario["scenario_id"],
        "scenario_revision": scenario["scenario_revision"],
        "fixture_content_sha256": scenario["fixture_content_sha256"],
        "prompt_content_sha256": scenario["prompt_content_sha256"],
        "rubric_version": scenario["rubric_version"],
    }
    (workspace / "EVALUATION-CONTEXT.json").write_text(
        json.dumps(context, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    run_text(["git", "init", "-q"], cwd=workspace)
    run_text(["git", "config", "user.name", "Synthetic Evaluation"], cwd=workspace)
    run_text(["git", "config", "user.email", "evaluation@example.invalid"], cwd=workspace)
    run_text(["git", "add", "--all"], cwd=workspace)
    run_text(["git", "commit", "-q", "-m", "materialize isolated evaluation fixture"], cwd=workspace)


def parse_events(stdout: str, skill: dict) -> dict:
    events: list[dict] = []
    parse_errors: list[str] = []
    for index, line in enumerate(stdout.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            parse_errors.append(f"line {index}: {exc}")
            continue
        if isinstance(event, dict):
            events.append(event)
        else:
            parse_errors.append(f"line {index}: event is not an object")

    thread_started = any(event.get("type") == "thread.started" for event in events)
    turn_completed = any(event.get("type") == "turn.completed" for event in events)
    turn_failed = any(event.get("type") == "turn.failed" for event in events)
    top_level_errors = [event for event in events if event.get("type") == "error"]
    item_errors: list[dict] = []
    final_messages: list[str] = []
    commands: list[tuple[str, str]] = []
    runtime_reported_model = None
    for event in events:
        if runtime_reported_model is None and isinstance(event.get("model"), str):
            runtime_reported_model = event["model"]
        item = event.get("item")
        if not isinstance(item, dict):
            continue
        if item.get("type") == "error":
            item_errors.append(item)
        if event.get("type") == "item.completed" and item.get("type") == "agent_message":
            text = item.get("text")
            if isinstance(text, str) and text.strip():
                final_messages.append(text)
        if item.get("type") == "command_execution" and isinstance(item.get("command"), str):
            commands.append((str(item.get("id", "unknown")), item["command"]))

    entrypoints = {str(skill["entrypoint"]), str(skill["installed_entrypoint"])}
    reference_roots = {
        skill["realpath"] / "references",
        skill["installed_path"] / "references",
    }
    reference_names = {
        reference.name
        for reference_root in reference_roots
        for reference in reference_root.glob("*.md")
    }
    invocation_evidence: list[dict] = []
    loaded_references: set[str] = set()
    seen_commands: set[str] = set()
    for item_id, command in commands:
        if command in seen_commands:
            continue
        seen_commands.add(command)
        normalized: list[str] = []
        if any(entrypoint in command for entrypoint in entrypoints):
            normalized.append("SKILL.md")
        for reference_name in sorted(reference_names):
            relative_reference = f"references/{reference_name}"
            absolute_references = {
                str(reference_root / reference_name)
                for reference_root in reference_roots
            }
            if relative_reference in command or any(
                reference in command for reference in absolute_references
            ):
                loaded_references.add(Path(reference_name).stem)
                normalized.append(relative_reference)
        if normalized:
            invocation_evidence.append({"item_id": item_id, "reads": sorted(set(normalized))})

    forbidden_oracle_names = ("rubric.json", "results.json", "expected_decisions", "/receipts/")
    oracle_access_commands = [
        item_id
        for item_id, command in commands
        if any(marker in command for marker in forbidden_oracle_names)
    ]
    entrypoint_loaded = any(
        "SKILL.md" in evidence["reads"] for evidence in invocation_evidence
    )
    skill_material_loaded = entrypoint_loaded or bool(loaded_references)
    return {
        "event_count": len(events),
        "jsonl_parse_errors": parse_errors,
        "thread_started": thread_started,
        "turn_completed": turn_completed,
        "turn_failed": turn_failed,
        "top_level_errors": top_level_errors,
        "item_level_errors": item_errors,
        "final_agent_message": final_messages[-1] if final_messages else None,
        "runtime_reported_model": runtime_reported_model or "unknown",
        "entrypoint_loaded": entrypoint_loaded,
        "skill_material_loaded": skill_material_loaded,
        "skill_loaded": skill_material_loaded,
        "loaded_reference_ids": sorted(loaded_references),
        "skill_invocation_evidence": invocation_evidence,
        "oracle_access_observed": bool(oracle_access_commands),
        "oracle_access_item_ids": oracle_access_commands,
    }


def classify_validity(
    process_exit_code: int | None,
    timed_out: bool,
    trace: dict,
    scenario: dict,
) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if timed_out:
        return "timed-out", ["wall-clock timeout expired"]
    if process_exit_code != 0:
        return "infrastructure-failed", [f"codex process exited {process_exit_code}"]
    if trace["oracle_access_observed"]:
        return "invalid-fixture", ["trace shows access to evaluation oracle material"]
    if trace["turn_failed"] or trace["top_level_errors"]:
        return "model-failed", ["trace contains turn.failed or a top-level error event"]
    if not trace["thread_started"]:
        return "infrastructure-failed", ["trace lacks thread.started"]
    if trace["jsonl_parse_errors"]:
        reasons.append("one or more stdout lines were not parseable JSONL events")
    if not trace["turn_completed"] or not trace["final_agent_message"]:
        reasons.append("trace lacks turn.completed or a complete final agent message")
    if scenario.get("requires_entrypoint_load") is True and not trace["entrypoint_loaded"]:
        reasons.append("trace does not prove the installed skill entrypoint was loaded")
    elif scenario.get("requires_skill_load") is True and not trace["skill_material_loaded"]:
        reasons.append(
            "trace does not prove the installed skill entrypoint or a bundled reference was loaded"
        )
    if reasons:
        return "trace-incomplete", reasons
    return "valid-completed", []


def execute_scenario(
    scenario: dict,
    skill: dict,
    codex: Path,
    output_root: Path,
    model: str,
    reasoning_effort: str,
    timeout_seconds: int,
    locale: str,
    ambient: dict,
) -> dict:
    fixture = (EVALUATION_ROOT / scenario["fixture_path"]).resolve()
    prompt = (EVALUATION_ROOT / scenario["prompt_path"]).resolve()
    observed_fixture_hash = tree_sha256(fixture)
    observed_prompt_hash = sha256_file(prompt)
    executed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    run_id = f"{executed_at[:19].replace('-', '').replace(':', '')}-{scenario['scenario_id']}"
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    invalid_reasons: list[str] = []
    if observed_fixture_hash != scenario["fixture_content_sha256"]:
        invalid_reasons.append("fixture_content_sha256 mismatch")
    if observed_prompt_hash != scenario["prompt_content_sha256"]:
        invalid_reasons.append("prompt_content_sha256 mismatch")
    if invalid_reasons:
        summary = {
            "run_id": run_id,
            "scenario_id": scenario["scenario_id"],
            "scenario_revision": scenario["scenario_revision"],
            "run_validity": "invalid-fixture",
            "validity_reasons": invalid_reasons,
            "executed_at": executed_at,
        }
        (run_dir / "run-summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        return summary

    with tempfile.TemporaryDirectory(prefix="mcp-skill-eval-") as directory:
        workspace = Path(directory) / "fixture-repository"
        workspace.mkdir()
        init_fixture_repository(workspace, fixture, prompt, scenario)
        prompt_text = prompt.read_text(encoding="utf-8", errors="strict")
        command = [
            str(codex),
            "--ask-for-approval",
            "never",
            "exec",
            "--json",
            "--ephemeral",
            "--ignore-user-config",
            "--ignore-rules",
            "--sandbox",
            "read-only",
            "--model",
            model,
            "-c",
            f'model_reasoning_effort="{reasoning_effort}"',
            "-C",
            str(workspace),
            prompt_text,
        ]
        environment = {
            **os.environ,
            "LANG": locale,
            "LC_ALL": locale,
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        started = time.monotonic()
        timed_out = False
        process_exit_code: int | None = None
        stdout = ""
        stderr = ""
        try:
            result = subprocess.run(
                command,
                cwd=workspace,
                env=environment,
                stdin=subprocess.DEVNULL,
                text=True,
                capture_output=True,
                check=False,
                timeout=timeout_seconds,
            )
            process_exit_code = result.returncode
            stdout = result.stdout
            stderr = result.stderr
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            if isinstance(stdout, bytes):
                stdout = stdout.decode("utf-8", errors="replace")
            if isinstance(stderr, bytes):
                stderr = stderr.decode("utf-8", errors="replace")
        duration = time.monotonic() - started

    (run_dir / "stdout.jsonl").write_text(stdout, encoding="utf-8")
    (run_dir / "stderr.log").write_text(stderr, encoding="utf-8")
    trace = parse_events(stdout, skill)
    validity, validity_reasons = classify_validity(
        process_exit_code, timed_out, trace, scenario
    )
    if validity not in ALLOWED_VALIDITY:
        raise AssertionError(f"unexpected run validity: {validity}")
    final_message = trace.pop("final_agent_message")
    if final_message:
        (run_dir / "final.md").write_text(final_message.rstrip() + "\n", encoding="utf-8")
    recorded_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    summary = {
        "run_id": run_id,
        "scenario_id": scenario["scenario_id"],
        "scenario_revision": scenario["scenario_revision"],
        "rubric_version": scenario["rubric_version"],
        "executed_at": executed_at,
        "recorded_at": recorded_at,
        "duration_seconds": round(duration, 3),
        "invocation_mode": scenario["invocation_mode"],
        "requested_model": model,
        "runtime_reported_model": trace.pop("runtime_reported_model"),
        "requested_reasoning_effort": reasoning_effort,
        "codex_cli_version": run_text([str(codex), "--version"]),
        "codex_binary_sha256": sha256_file(codex),
        "sandbox": "read-only",
        "approval_policy": "never",
        "locale": locale,
        "feature_config_overrides": [
            "ignore-user-config",
            "ignore-rules",
            "ephemeral",
        ],
        "wall_clock_timeout_seconds": timeout_seconds,
        "process_exit_code": process_exit_code,
        "timed_out": timed_out,
        "run_validity": validity,
        "validity_reasons": validity_reasons,
        "fixture_content_sha256": observed_fixture_hash,
        "prompt_content_sha256": observed_prompt_hash,
        "skill_version": skill["version"],
        "skill_source_commit": skill["source_commit"],
        "skill_baseline_source_commit": skill["baseline_source_commit"],
        "skill_tree_sha256": skill["tree_sha256"],
        "installed_realpath_kind": skill["installed_realpath_kind"],
        "ambient_context": ambient,
        "trace": trace,
        "raw_material": {
            "included_in_public_repository": False,
            "files": ["stdout.jsonl", "stderr.log", "run-summary.json", "final.md"],
        },
    }
    (run_dir / "run-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", action="append", default=[])
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument("--reasoning-effort", default="high")
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument("--locale", default="en_US.UTF-8")
    parser.add_argument("--codex-binary", type=Path, default=Path(shutil.which("codex") or ""))
    parser.add_argument(
        "--installed-skill",
        type=Path,
        default=Path.home() / ".codex" / "skills" / "mcp-server-engineering",
    )
    args = parser.parse_args()
    if args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be positive")
    if not args.codex_binary.is_file():
        parser.error("Codex binary is absent; pass --codex-binary")
    output_root = args.output_dir.resolve()
    try:
        output_root.relative_to(ROOT.resolve())
    except ValueError:
        pass
    else:
        parser.error("--output-dir must be outside the public repository")
    output_root.mkdir(parents=True, exist_ok=True)

    corpus = load_json(SCENARIOS_PATH)
    scenarios = corpus.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        parser.error("scenarios.json has no scenarios")
    by_id = {scenario["scenario_id"]: scenario for scenario in scenarios}
    selected_ids = list(by_id) if args.all else args.scenario
    if not selected_ids:
        parser.error("select --all or at least one --scenario")
    unknown = [scenario_id for scenario_id in selected_ids if scenario_id not in by_id]
    if unknown:
        parser.error(f"unknown scenario IDs: {', '.join(unknown)}")

    baseline = corpus.get("skill_baseline", {})
    skill = skill_identity(
        args.installed_skill,
        str(baseline.get("source_commit", "")),
        str(baseline.get("skill_tree_sha256", "")),
    )
    skill["version"] = baseline.get("skill_version")
    ambient = ambient_context()
    failed = False
    for scenario_id in selected_ids:
        summary = execute_scenario(
            by_id[scenario_id],
            skill,
            args.codex_binary.resolve(),
            output_root,
            args.model,
            args.reasoning_effort,
            args.timeout_seconds,
            args.locale,
            ambient,
        )
        print(
            json.dumps(
                {
                    "run_id": summary["run_id"],
                    "scenario_id": scenario_id,
                    "run_validity": summary["run_validity"],
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        if summary["run_validity"] != "valid-completed":
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
