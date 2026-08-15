#!/usr/bin/env python3
"""Check manifest-driven structural parity for English and zh-CN Markdown peers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys


HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$", re.MULTILINE)
NUMBER = re.compile(r"^(\d+(?:\.\d+)*)\.?\s")


def safe_path(root: Path, value: object, label: str, errors: list[str]) -> Path | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{label}: expected a non-empty path string")
        return None
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts:
        errors.append(f"{label}: path must stay inside repository: {value!r}")
        return None
    return root.joinpath(*pure.parts)


def structure(path: Path) -> tuple[list[int], list[str], int, int]:
    text = path.read_text(encoding="utf-8", errors="strict")
    headings = HEADING.findall(text)
    levels = [len(markers) for markers, _ in headings]
    numbers = []
    for _, title in headings:
        match = NUMBER.match(title)
        if match:
            numbers.append(match.group(1))
    return levels, numbers, text.count("```"), text.count("\n| ---")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument(
        "--manifest",
        default="BILINGUAL-MANIFEST.json",
        help="manifest path relative to root (default: BILINGUAL-MANIFEST.json)",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []
    manifest_path = safe_path(root, args.manifest, "manifest", errors)
    if manifest_path is None:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8", errors="strict"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"FAIL: cannot read bilingual manifest: {exc}", file=sys.stderr)
        return 1
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        errors.append("bilingual manifest schema_version must be 1")
        entries: object = None
    else:
        entries = manifest.get("pairs")
    if not isinstance(entries, list) or not entries:
        errors.append("bilingual manifest pairs must be a non-empty array")
        entries = []

    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    expected_zh: set[str] = set()
    pairs = 0
    for index, entry in enumerate(entries):
        label = f"pairs[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label}: expected an object")
            continue
        pair_id = entry.get("id")
        if not isinstance(pair_id, str) or not pair_id:
            errors.append(f"{label}.id: expected a non-empty string")
        elif pair_id in seen_ids:
            errors.append(f"duplicate pair id: {pair_id}")
        else:
            seen_ids.add(pair_id)
        en = safe_path(root, entry.get("en"), f"{label}.en", errors)
        zh = safe_path(root, entry.get("zh-CN"), f"{label}.zh-CN", errors)
        if en is None or zh is None:
            continue
        en_rel = en.relative_to(root).as_posix()
        zh_rel = zh.relative_to(root).as_posix()
        for relative in (en_rel, zh_rel):
            if relative in seen_paths:
                errors.append(f"duplicate bilingual path: {relative}")
            seen_paths.add(relative)
        expected_zh.add(zh_rel)
        if not en_rel.endswith(".md") or en_rel.endswith(".zh-CN.md"):
            errors.append(f"{label}.en must name an English .md file")
        expected_peer = en.with_name(en.name.removesuffix(".md") + ".zh-CN.md")
        if zh != expected_peer:
            errors.append(f"{label}: zh-CN path must be the conventional peer of en")
        if not en.is_file():
            errors.append(f"missing English peer: {en_rel}")
        if not zh.is_file():
            errors.append(f"missing zh-CN peer: {zh_rel}")
        if not en.is_file() or not zh.is_file():
            continue
        pairs += 1
        try:
            en_structure = structure(en)
            zh_structure = structure(zh)
        except UnicodeError as exc:
            errors.append(f"UTF-8 error in pair {en_rel}/{zh_rel}: {exc}")
            continue
        if en_structure[0] != zh_structure[0]:
            errors.append(f"heading-level mismatch: {en_rel} <> {zh_rel}")
        if en_structure[1] != zh_structure[1]:
            errors.append(f"numbered-section mismatch: {en_rel} <> {zh_rel}")
        if en_structure[2] != zh_structure[2]:
            errors.append(f"code-fence mismatch: {en_rel} <> {zh_rel}")
        if en_structure[3] != zh_structure[3]:
            errors.append(f"table-header mismatch: {en_rel} <> {zh_rel}")

    actual_zh = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*.zh-CN.md")
        if ".git" not in path.parts
    }
    for unregistered in sorted(actual_zh - expected_zh):
        errors.append(f"unregistered zh-CN peer: {unregistered}")
    for absent in sorted(expected_zh - actual_zh):
        if not any(absent in error for error in errors):
            errors.append(f"manifested zh-CN peer is absent: {absent}")

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {pairs} manifested bilingual Markdown pairs have matching structure")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
