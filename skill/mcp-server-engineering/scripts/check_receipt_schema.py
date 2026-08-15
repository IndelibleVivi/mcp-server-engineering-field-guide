#!/usr/bin/env python3
"""Validate evidence receipts, provenance consistency, and public-safe text."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import sys


IDENTITY_PATTERNS = {
    "git-sha1": re.compile(r"^[0-9a-f]{40}$"),
    "git-sha256": re.compile(r"^[0-9a-f]{64}$"),
    "content-sha256": re.compile(r"^[0-9a-f]{64}$"),
}
PRIVATE_MARKERS = (
    "/" + "Users/",
    "\\" + "Users\\",
    ".codex/" + "private-continuity",
    ".codex/" + "attachments",
    "BEGIN " + "OPENSSH PRIVATE KEY",
    "BEGIN " + "PRIVATE KEY",
)
ALLOWED_STATUS = {"original-observation", "reproduced", "independently-reproduced"}
ALLOWED_REPRESENTATION = {"raw", "sanitized", "projected", "reconstructed"}
ALLOWED_OWNER_RELATIONSHIP = {"same-owner", "independent-owner", "not-assessed"}


def strings(value: object):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from strings(key)
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)


def non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def require_string(errors: list[str], data: dict, key: str, label: str = "") -> None:
    if not non_empty_string(data.get(key)):
        errors.append(f"{label}{key} must be a non-empty string")


def valid_timestamp(value: object) -> bool:
    if not non_empty_string(value):
        return False
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def validate_identity(errors: list[str], source: object) -> None:
    if not isinstance(source, dict):
        errors.append("source must be an object")
        return
    require_string(errors, source, "repository", "source.")
    identity = source.get("identity")
    if not isinstance(identity, dict):
        errors.append("source.identity must be an object")
        return
    identity_type = identity.get("type")
    identity_value = identity.get("value")
    pattern = IDENTITY_PATTERNS.get(identity_type)
    if pattern is None:
        errors.append(f"source.identity.type is unsupported: {identity_type!r}")
    elif not isinstance(identity_value, str) or not pattern.fullmatch(identity_value):
        errors.append(f"source.identity.value does not match {identity_type}")


def validate_probe(errors: list[str], probe: object, index: int, seen: set[str]) -> None:
    label = f"probes[{index}]."
    if not isinstance(probe, dict):
        errors.append(f"probes[{index}] must be an object")
        return
    probe_id = probe.get("receipt_id")
    if not non_empty_string(probe_id):
        errors.append(f"{label}receipt_id is required")
    elif probe_id in seen:
        errors.append(f"duplicate probe receipt ID: {probe_id}")
    else:
        seen.add(probe_id)
    for key in ("claim_id", "probe_method", "residual_boundary"):
        require_string(errors, probe, key, label)
    if not isinstance(probe.get("parameters"), dict):
        errors.append(f"{label}parameters must be an object")
    for key in ("expected", "observed"):
        value = probe.get(key)
        if not isinstance(value, dict) or not value:
            errors.append(f"{label}{key} must be a non-empty object")
def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="strict"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"cannot read strict JSON: {exc}"]
    if not isinstance(data, dict):
        return ["receipt root must be an object"]
    if data.get("schema_version") != 2:
        errors.append("schema_version must be 2")
    if not data.get("receipt_id") and not data.get("receipt_set_id"):
        errors.append("receipt_id or receipt_set_id is required")
    if data.get("receipt_id") and data.get("receipt_set_id"):
        errors.append("receipt_id and receipt_set_id are mutually exclusive")
    require_string(errors, data, "claim_id")
    if data.get("status") not in ALLOWED_STATUS:
        errors.append(f"unsupported status: {data.get('status')!r}")
    validate_identity(errors, data.get("source"))
    if not valid_timestamp(data.get("executed_at")):
        errors.append("executed_at must be an ISO 8601 timestamp with timezone")
    if "recorded_at" in data and not valid_timestamp(data.get("recorded_at")):
        errors.append("recorded_at must be an ISO 8601 timestamp with timezone when present")
    require_string(errors, data, "execution_owner_class")
    require_string(errors, data, "independence_basis")
    owner_relationship = data.get("owner_relationship")
    if owner_relationship not in ALLOWED_OWNER_RELATIONSHIP:
        errors.append(f"unsupported owner_relationship: {owner_relationship!r}")
    if not isinstance(data.get("independent_execution"), bool):
        errors.append("independent_execution must be a required boolean")
    independent_status = data.get("status") == "independently-reproduced"
    independent_flag = data.get("independent_execution") is True
    if independent_status != independent_flag:
        errors.append(
            "status independently-reproduced must be equivalent to independent_execution true"
        )
    if independent_flag and owner_relationship != "independent-owner":
        errors.append("independent execution requires owner_relationship independent-owner")
    if owner_relationship == "independent-owner" and not independent_flag:
        errors.append("owner_relationship independent-owner requires independent execution")
    if data.get("representation") not in ALLOWED_REPRESENTATION:
        errors.append(f"unsupported representation: {data.get('representation')!r}")
    if not isinstance(data.get("environment"), dict) or not data["environment"]:
        errors.append("environment must be a non-empty object")
    command = data.get("command_or_probe")
    if isinstance(command, list):
        if not command or not all(non_empty_string(item) for item in command):
            errors.append("command_or_probe list must contain non-empty strings")
    elif not non_empty_string(command):
        errors.append("command_or_probe must be a non-empty string or string array")
    if not isinstance(data.get("parameters"), dict):
        errors.append("parameters must be an object")
    for key in ("expected", "observed"):
        value = data.get(key)
        if not isinstance(value, dict) or not value:
            errors.append(f"{key} must be a non-empty object")
    exit_code = data.get("exit_code")
    if not isinstance(exit_code, int) or isinstance(exit_code, bool):
        errors.append("exit_code must be an integer")
    raw_material = data.get("raw_material")
    if not isinstance(raw_material, dict):
        errors.append("raw_material must be an object")
    else:
        if not isinstance(raw_material.get("included"), bool):
            errors.append("raw_material.included must be a boolean")
        if raw_material.get("included") is True and not non_empty_string(raw_material.get("location")):
            errors.append("raw_material.location is required when raw material is included")
        if raw_material.get("location") is not None and not non_empty_string(raw_material.get("location")):
            errors.append("raw_material.location must be null or a non-empty string")
        require_string(errors, raw_material, "omitted_material", "raw_material.")
    if not isinstance(data.get("residual_boundary"), str) or not data["residual_boundary"].strip():
        errors.append("residual_boundary must be a non-empty string")
    probe_ids: set[str] = set()
    if "probes" in data:
        if not isinstance(data["probes"], list) or not data["probes"]:
            errors.append("probes must be a non-empty array")
        else:
            for index, probe in enumerate(data["probes"]):
                validate_probe(errors, probe, index, probe_ids)
    for value in strings(data):
        if "\ufffd" in value:
            errors.append("contains U+FFFD replacement character")
            break
    for marker in PRIVATE_MARKERS:
        if any(marker in value for value in strings(data)):
            errors.append(f"contains private/sensitive marker: {marker}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipts", type=Path, nargs="+")
    args = parser.parse_args()
    failed = False
    for path in args.receipts:
        errors = validate(path)
        if errors:
            failed = True
            for error in errors:
                print(f"FAIL: {path}: {error}", file=sys.stderr)
        else:
            print(f"PASS: {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
