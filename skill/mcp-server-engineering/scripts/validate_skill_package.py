#!/usr/bin/env python3
"""Validate the complete, text-only portable mcp-server-engineering skill package."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
from urllib.parse import unquote


LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
FORBIDDEN_DIR_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
FORBIDDEN_FILE_NAMES = {".DS_Store"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".swp", ".swo"}
REQUIRED_FILES = {
    "SKILL.md",
    "agents/openai.yaml",
    "references/json-rpc-2.0.md",
    "references/http-rfc9110-rfc9112.md",
    "references/mcp-2025-06-18.md",
    "references/mcp-2025-11-25.md",
    "references/mcp-2026-07-28.md",
    "scripts/check_bilingual_coverage.py",
    "scripts/check_markdown_links.py",
    "scripts/check_python_syntax.py",
    "scripts/check_receipt_schema.py",
    "scripts/scan_review_bundle.py",
    "scripts/sync_profile_mirrors.py",
    "scripts/validate_skill_package.py",
    "scripts/validate_version_register.py",
}


def front_matter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip().strip('"\'')
    return values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skill", type=Path)
    args = parser.parse_args()
    root = args.skill.resolve()
    errors: list[str] = []
    if not root.is_dir():
        print(f"FAIL: skill directory does not exist: {root}", file=sys.stderr)
        return 1

    text_files: dict[Path, str] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if path.is_symlink():
            errors.append(f"portable package contains symlink: {relative}")
            continue
        if any(part in FORBIDDEN_DIR_NAMES for part in relative.parts):
            errors.append(f"portable package contains generated/cache path: {relative}")
            continue
        if not path.is_file():
            continue
        if (
            path.name in FORBIDDEN_FILE_NAMES
            or path.suffix in FORBIDDEN_SUFFIXES
            or path.name.endswith("~")
        ):
            errors.append(f"portable package contains forbidden generated file: {relative}")
            continue
        try:
            raw = path.read_bytes()
            if b"\x00" in raw:
                raise UnicodeError("NUL-bearing/binary file")
            text = raw.decode("utf-8", errors="strict")
        except (OSError, UnicodeError) as exc:
            errors.append(f"portable package must contain strict UTF-8 text only: {relative}: {exc}")
            continue
        if "\ufffd" in text:
            errors.append(f"portable package contains U+FFFD: {relative}")
        text_files[path] = text

    observed = {path.relative_to(root).as_posix() for path in text_files}
    for required in sorted(REQUIRED_FILES - observed):
        errors.append(f"required package file missing: {required}")

    skill_file = root / "SKILL.md"
    text = text_files.get(skill_file, "")
    metadata = front_matter(text)
    if metadata.get("name") != root.name:
        errors.append(f"front matter name must equal directory name {root.name!r}")
    description = metadata.get("description", "")
    if len(description) < 40 or len(description) > 1024:
        errors.append("description must be informative and 40-1024 characters")
    if "TODO" in text:
        errors.append("SKILL.md contains TODO")
    if len(text.splitlines()) > 500:
        errors.append("SKILL.md exceeds 500 lines")

    agent_file = root / "agents" / "openai.yaml"
    agent_text = text_files.get(agent_file, "")
    for key in ("display_name", "short_description", "default_prompt"):
        if not re.search(rf"^\s+{key}:\s+\"[^\"]+\"\s*$", agent_text, re.MULTILINE):
            errors.append(f"agents/openai.yaml missing quoted {key}")
    if "$mcp-server-engineering" not in agent_text:
        errors.append("default_prompt must mention $mcp-server-engineering")

    for source, markdown in text_files.items():
        if source.suffix != ".md":
            continue
        for raw_target in LINK.findall(markdown):
            target = raw_target.split("#", 1)[0].strip().strip("<>")
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            resolved = (source.parent / unquote(target)).resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                errors.append(f"{source.relative_to(root)}: link escapes package: {raw_target}")
                continue
            if not resolved.exists():
                errors.append(f"{source.relative_to(root)}: link target missing: {target}")

    expected_dirs = ("references", "scripts", "assets/templates")
    for relative in expected_dirs:
        directory = root / relative
        if not directory.is_dir() or not any(directory.iterdir()):
            errors.append(f"required non-empty resource directory missing: {relative}")

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {root} is a complete text-only portable skill package")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
