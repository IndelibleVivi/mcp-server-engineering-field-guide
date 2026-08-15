#!/usr/bin/env python3
"""Compile Python source in memory without creating bytecode artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


def python_files(paths: list[Path]):
    seen: set[Path] = set()
    for supplied in paths:
        path = supplied.resolve()
        candidates = sorted(path.rglob("*.py")) if path.is_dir() else [path]
        for candidate in candidates:
            if candidate.suffix == ".py" and candidate not in seen:
                seen.add(candidate)
                yield candidate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", type=Path, nargs="+")
    args = parser.parse_args()
    errors: list[str] = []
    count = 0
    for path in python_files(args.paths):
        count += 1
        try:
            source = path.read_text(encoding="utf-8", errors="strict")
            compile(source, str(path), "exec")
        except (OSError, UnicodeError, SyntaxError) as exc:
            errors.append(f"{path}: {exc}")
    if count == 0:
        errors.append("no Python source files found")
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {count} Python source files compile in memory")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
