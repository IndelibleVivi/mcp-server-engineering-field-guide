#!/usr/bin/env python3
"""Scan a text file, directory, or bounded ZIP for review-bundle hazards."""

from __future__ import annotations

import argparse
from pathlib import Path, PurePosixPath
import sys
import zipfile


PRIVATE_MARKERS = (
    "/" + "Users/",
    "\\" + "Users\\",
    ".codex/" + "private-continuity",
    ".codex/" + "attachments",
    "BEGIN " + "OPENSSH PRIVATE KEY",
    "BEGIN " + "PRIVATE KEY",
)
DEFAULT_MAX_FILES = 2048
DEFAULT_MAX_MEMBER_BYTES = 8 * 1024 * 1024
DEFAULT_MAX_TOTAL_BYTES = 64 * 1024 * 1024
DEFAULT_MAX_COMPRESSION_RATIO = 100.0


def inspect_bytes(
    label: str,
    raw: bytes,
    allow_private_paths: bool,
    allow_binary: bool = False,
) -> list[str]:
    if allow_binary:
        return []
    if b"\x00" in raw:
        return [f"{label}: unexpected NUL-bearing/binary member"]
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        return [f"{label}: not strict UTF-8 or unallowlisted binary: {exc}"]
    errors: list[str] = []
    if "\ufffd" in text:
        errors.append(f"{label}: contains U+FFFD replacement character")
    if not allow_private_paths:
        for marker in PRIVATE_MARKERS:
            if marker in text:
                errors.append(f"{label}: contains private/sensitive marker {marker!r}")
    return errors


def directory_items(root: Path):
    for path in sorted(root.rglob("*")):
        if path.is_file() and ".git" not in path.relative_to(root).parts:
            yield path.relative_to(root).as_posix(), path.read_bytes()


def preflight_zip(
    archive: zipfile.ZipFile,
    errors: list[str],
    max_files: int,
    max_member_bytes: int,
    max_total_bytes: int,
    max_compression_ratio: float,
) -> list[zipfile.ZipInfo]:
    infos = [info for info in archive.infolist() if not info.is_dir()]
    if len(infos) > max_files:
        errors.append(f"ZIP file count {len(infos)} exceeds limit {max_files}")
    total = 0
    seen: set[str] = set()
    accepted: list[zipfile.ZipInfo] = []
    for info in infos:
        member = PurePosixPath(info.filename)
        if member.is_absolute() or ".." in member.parts:
            errors.append(f"unsafe ZIP member path: {info.filename!r}")
            continue
        normalized = member.as_posix()
        if normalized in seen:
            errors.append(f"duplicate ZIP member path: {normalized!r}")
            continue
        seen.add(normalized)
        if info.flag_bits & 0x1:
            errors.append(f"encrypted ZIP member is not reviewable: {normalized!r}")
            continue
        if info.file_size > max_member_bytes:
            errors.append(
                f"ZIP member {normalized!r} size {info.file_size} exceeds limit {max_member_bytes}"
            )
        total += info.file_size
        if total > max_total_bytes:
            errors.append(
                f"ZIP total uncompressed size {total} exceeds limit {max_total_bytes}"
            )
        if info.file_size:
            ratio = (
                float("inf")
                if info.compress_size == 0
                else info.file_size / info.compress_size
            )
            if ratio > max_compression_ratio:
                errors.append(
                    f"ZIP member {normalized!r} compression ratio {ratio:.1f} exceeds limit {max_compression_ratio:.1f}"
                )
        accepted.append(info)
    return accepted


def zip_items(
    path: Path,
    errors: list[str],
    max_files: int,
    max_member_bytes: int,
    max_total_bytes: int,
    max_compression_ratio: float,
):
    try:
        with zipfile.ZipFile(path) as archive:
            infos = preflight_zip(
                archive,
                errors,
                max_files,
                max_member_bytes,
                max_total_bytes,
                max_compression_ratio,
            )
            if errors:
                return
            for info in infos:
                yield PurePosixPath(info.filename).as_posix(), archive.read(info)
    except (OSError, zipfile.BadZipFile, RuntimeError, NotImplementedError) as exc:
        errors.append(f"cannot read ZIP: {exc}")


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument(
        "--allow-private-paths",
        action="store_true",
        help="do not fail on local path markers (still checks text integrity)",
    )
    parser.add_argument(
        "--allow-binary",
        action="append",
        default=[],
        metavar="EXACT_MEMBER_PATH",
        help="explicitly skip text inspection for one exact member; repeat as needed",
    )
    parser.add_argument("--max-files", type=positive_int, default=DEFAULT_MAX_FILES)
    parser.add_argument(
        "--max-member-bytes", type=positive_int, default=DEFAULT_MAX_MEMBER_BYTES
    )
    parser.add_argument("--max-total-bytes", type=positive_int, default=DEFAULT_MAX_TOTAL_BYTES)
    parser.add_argument(
        "--max-compression-ratio",
        type=positive_float,
        default=DEFAULT_MAX_COMPRESSION_RATIO,
    )
    args = parser.parse_args()
    target = args.path.resolve()
    errors: list[str] = []
    file_count = 0
    byte_count = 0
    text_count = 0
    allowed_binary_count = 0
    allow_binary = set(args.allow_binary)
    seen_allowed: set[str] = set()

    if target.is_dir():
        items = directory_items(target)
    elif target.is_file() and zipfile.is_zipfile(target):
        items = zip_items(
            target,
            errors,
            args.max_files,
            args.max_member_bytes,
            args.max_total_bytes,
            args.max_compression_ratio,
        )
    elif target.is_file():
        if target.stat().st_size > args.max_member_bytes:
            errors.append(
                f"file size {target.stat().st_size} exceeds limit {args.max_member_bytes}"
            )
            items = []
        else:
            items = [(target.name, target.read_bytes())]
    else:
        print(f"FAIL: path does not exist: {target}", file=sys.stderr)
        return 1

    for label, raw in items:
        file_count += 1
        byte_count += len(raw)
        explicitly_allowed = label in allow_binary
        if explicitly_allowed:
            seen_allowed.add(label)
            allowed_binary_count += 1
        else:
            text_count += 1
        errors.extend(
            inspect_bytes(label, raw, args.allow_private_paths, explicitly_allowed)
        )
    if file_count > args.max_files:
        errors.append(f"file count {file_count} exceeds limit {args.max_files}")
    if byte_count > args.max_total_bytes:
        errors.append(f"total bytes {byte_count} exceeds limit {args.max_total_bytes}")
    for absent in sorted(allow_binary - seen_allowed):
        errors.append(f"allowlisted binary member not found: {absent!r}")
    if file_count == 0 and not errors:
        errors.append("bundle contains no files")
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        print(f"SUMMARY: {file_count} files, {byte_count} bytes", file=sys.stderr)
        return 1
    if allowed_binary_count:
        print(
            f"PASS: {file_count} files, {byte_count} bytes; {text_count} strict-text members checked; "
            f"{allowed_binary_count} explicitly allowlisted binary members not text-inspected"
        )
    else:
        print(
            f"PASS: {file_count} files, {byte_count} bytes; all members passed strict text integrity checks"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
