#!/usr/bin/env python3
"""Write or verify byte-identical skill mirrors of registered profiles."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys


LOCALES = ("en", "zh-CN")


def safe_file(root: Path, value: object, label: str, must_exist: bool) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label}: expected a non-empty path string")
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts:
        raise ValueError(f"{label}: path must stay inside repository: {value!r}")
    result = root.joinpath(*pure.parts)
    if must_exist and not result.is_file():
        raise ValueError(f"{label}: missing file: {value}")
    return result


def profile_entries(data: dict):
    for group_name in ("normative_profiles", "moving_integration_guidance"):
        group = data.get(group_name)
        if not isinstance(group, list):
            raise ValueError(f"{group_name} must be an array")
        for index, entry in enumerate(group):
            if not isinstance(entry, dict):
                raise ValueError(f"{group_name}[{index}] must be an object")
            yield group_name, index, entry


def main() -> int:
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--check", action="store_true", help="verify mirrors and hashes")
    action.add_argument("--write", action="store_true", help="replace mirrors from canonical profiles")
    parser.add_argument("register", type=Path)
    args = parser.parse_args()
    write = args.write
    register_path = args.register.resolve()
    root = register_path.parent
    try:
        data = json.loads(register_path.read_text(encoding="utf-8", errors="strict"))
        entries = list(profile_entries(data))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL: cannot load profile bindings: {exc}", file=sys.stderr)
        return 1

    errors: list[str] = []
    reports: list[str] = []
    seen_targets: set[Path] = set()
    for group_name, index, entry in entries:
        profile_id = entry.get("id")
        label = f"{group_name}[{index}]"
        paths = entry.get("paths")
        skill_paths = entry.get("skill_paths")
        hashes = entry.get("content_sha256")
        if not isinstance(profile_id, str) or not profile_id:
            errors.append(f"{label}.id must be a non-empty string")
            continue
        if not isinstance(paths, dict) or set(paths) != set(LOCALES):
            errors.append(f"{label}.paths must contain exactly en and zh-CN")
            continue
        if not isinstance(skill_paths, dict) or set(skill_paths) != set(LOCALES):
            errors.append(f"{label}.skill_paths must contain exactly en and zh-CN")
            continue
        if not isinstance(hashes, dict) or set(hashes) != set(LOCALES):
            errors.append(f"{label}.content_sha256 must contain exactly en and zh-CN")
            continue
        for locale in LOCALES:
            item = f"{profile_id}:{locale}"
            try:
                canonical = safe_file(root, paths.get(locale), f"{label}.paths.{locale}", True)
                mirror = safe_file(root, skill_paths.get(locale), f"{label}.skill_paths.{locale}", not write)
            except ValueError as exc:
                errors.append(str(exc))
                continue
            if canonical == mirror:
                errors.append(f"{item}: canonical and skill mirror must be different paths")
                continue
            if mirror in seen_targets:
                errors.append(f"{item}: duplicate skill mirror path: {mirror.relative_to(root)}")
                continue
            seen_targets.add(mirror)
            canonical_bytes = canonical.read_bytes()
            if write:
                mirror.parent.mkdir(parents=True, exist_ok=True)
                mirror.write_bytes(canonical_bytes)
            try:
                mirror_bytes = mirror.read_bytes()
            except OSError as exc:
                errors.append(f"{item}: cannot read skill mirror: {exc}")
                continue
            digest = hashlib.sha256(canonical_bytes).hexdigest()
            reports.append(f"{item} sha256={digest}")
            if mirror_bytes != canonical_bytes:
                errors.append(f"{item}: skill mirror is not byte-identical to canonical profile")
            if not write and hashes.get(locale) != digest:
                errors.append(f"{item}: registered content_sha256 does not match canonical bytes")

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    for report in reports:
        print(report)
    action_name = "wrote" if write else "verified"
    print(f"PASS: {action_name} {len(reports)} profile mirrors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
