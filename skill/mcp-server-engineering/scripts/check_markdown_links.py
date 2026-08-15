#!/usr/bin/env python3
"""Check local Markdown link targets without fetching external URLs."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
from urllib.parse import unquote


LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []
    checked = 0

    for source in sorted(root.rglob("*.md")):
        if ".git" in source.parts:
            continue
        try:
            text = source.read_text(encoding="utf-8", errors="strict")
        except UnicodeError as exc:
            errors.append(f"{source.relative_to(root)}: UTF-8 error: {exc}")
            continue
        for raw in LINK.findall(text):
            target = raw.strip().strip("<>")
            if not target or target.startswith("#") or "://" in target or target.startswith("mailto:"):
                continue
            target = unquote(target.split("#", 1)[0])
            if not target:
                continue
            checked += 1
            resolved = (source.parent / target).resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                errors.append(f"{source.relative_to(root)}: link escapes repository: {raw}")
                continue
            if not resolved.exists():
                errors.append(f"{source.relative_to(root)}: missing link target: {target}")

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {checked} local Markdown links resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
