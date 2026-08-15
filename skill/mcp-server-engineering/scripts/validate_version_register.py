#!/usr/bin/env python3
"""Validate release identity, bilingual peers, and canonical profile mirrors."""

from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import urlparse


LOCALES = ("en", "zh-CN")
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def positive_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def valid_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def valid_url(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def safe_relative_path(
    errors: list[str],
    root: Path,
    value: object,
    label: str,
    expected: str = "file",
) -> Path | None:
    if not isinstance(value, str) or not value:
        fail(errors, f"{label}: expected a non-empty path string")
        return None
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts:
        fail(errors, f"{label}: path must stay inside the repository: {value!r}")
        return None
    candidate = root.joinpath(*pure.parts)
    try:
        candidate.resolve().relative_to(root.resolve())
    except ValueError:
        fail(errors, f"{label}: resolved path escapes repository: {value!r}")
        return None
    exists = candidate.is_file() if expected == "file" else candidate.is_dir()
    if not exists:
        fail(errors, f"{label}: missing {expected}: {value}")
        return None
    return candidate


def parse_front_matter(path: Path) -> dict[str, str] | None:
    text = path.read_text(encoding="utf-8", errors="strict")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    result: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"\'')
    return result


def validate_peer_pair(
    errors: list[str],
    root: Path,
    paths: object,
    label: str,
    expected_id: str | None = None,
    require_profile_front_matter: bool = False,
) -> dict[str, Path]:
    result: dict[str, Path] = {}
    if not isinstance(paths, dict):
        fail(errors, f"{label}: expected an object")
        return result
    if set(paths) != set(LOCALES):
        fail(errors, f"{label}: expected exactly en and zh-CN")
        return result
    for locale in LOCALES:
        path = safe_relative_path(errors, root, paths.get(locale), f"{label}.{locale}")
        if path is not None:
            result[locale] = path
    if set(result) != set(LOCALES):
        return result
    en = result["en"]
    zh = result["zh-CN"]
    try:
        en_meta = parse_front_matter(en)
        zh_meta = parse_front_matter(zh)
    except (OSError, UnicodeError) as exc:
        fail(errors, f"{label}: cannot read strict UTF-8/front matter: {exc}")
        return result
    if require_profile_front_matter and (en_meta is None or zh_meta is None):
        fail(errors, f"{label}: both profile peers require front matter")
        return result
    if en_meta is not None or zh_meta is not None:
        en_meta = en_meta or {}
        zh_meta = zh_meta or {}
        if en_meta.get("language") != "en":
            fail(errors, f"{label}.en: front matter language must be en")
        if zh_meta.get("language") != "zh-CN":
            fail(errors, f"{label}.zh-CN: front matter language must be zh-CN")
        if en_meta.get("language_peer") != zh.name:
            fail(errors, f"{label}.en: language_peer must be {zh.name}")
        if zh_meta.get("language_peer") != en.name:
            fail(errors, f"{label}.zh-CN: language_peer must be {en.name}")
        if expected_id:
            if en_meta.get("profile_id") != expected_id or zh_meta.get("profile_id") != expected_id:
                fail(errors, f"{label}: profile_id must equal {expected_id} in both peers")
        for locale, metadata in (("en", en_meta), ("zh-CN", zh_meta)):
            if require_profile_front_matter:
                if not positive_integer_string(metadata.get("profile_version")):
                    fail(errors, f"{label}.{locale}: profile_version must be a positive integer")
                if not valid_date(metadata.get("assessed_at")):
                    fail(errors, f"{label}.{locale}: assessed_at must be an ISO date")
    return result


def positive_integer_string(value: object) -> bool:
    return isinstance(value, str) and value.isdigit() and int(value) > 0


def validate_profile_binding(
    errors: list[str],
    root: Path,
    skill_root: Path | None,
    entry: dict,
    label: str,
) -> None:
    profile_id = entry.get("id")
    if not isinstance(profile_id, str) or not profile_id:
        fail(errors, f"{label}.id: expected a non-empty string")
        return
    canonical = validate_peer_pair(
        errors,
        root,
        entry.get("paths"),
        f"{label}.paths",
        profile_id,
        require_profile_front_matter=True,
    )
    mirrors = validate_peer_pair(
        errors,
        root,
        entry.get("skill_paths"),
        f"{label}.skill_paths",
        profile_id,
        require_profile_front_matter=True,
    )
    hashes = entry.get("content_sha256")
    if not isinstance(hashes, dict) or set(hashes) != set(LOCALES):
        fail(errors, f"{label}.content_sha256: expected exactly en and zh-CN")
        return
    for locale in LOCALES:
        expected_hash = hashes.get(locale)
        if not isinstance(expected_hash, str) or not SHA256.fullmatch(expected_hash):
            fail(errors, f"{label}.content_sha256.{locale}: expected lowercase SHA-256")
        source = canonical.get(locale)
        mirror = mirrors.get(locale)
        if source is None or mirror is None:
            continue
        if skill_root is not None:
            try:
                mirror.resolve().relative_to(skill_root.resolve())
            except ValueError:
                fail(errors, f"{label}.skill_paths.{locale}: mirror must be inside skill package")
        source_bytes = source.read_bytes()
        mirror_bytes = mirror.read_bytes()
        if source_bytes != mirror_bytes:
            fail(errors, f"{label}.{locale}: skill mirror differs from canonical profile")
        observed_hash = hashlib.sha256(source_bytes).hexdigest()
        if expected_hash != observed_hash:
            fail(errors, f"{label}.content_sha256.{locale}: hash does not bind canonical bytes")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("register", type=Path)
    args = parser.parse_args()
    register_path = args.register.resolve()
    root = register_path.parent
    errors: list[str] = []
    try:
        data = json.loads(register_path.read_text(encoding="utf-8", errors="strict"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"FAIL: cannot read register: {exc}", file=sys.stderr)
        return 1
    if not isinstance(data, dict):
        print("FAIL: register root must be an object", file=sys.stderr)
        return 1

    if data.get("schema_version") != 1:
        fail(errors, "schema_version must be 1")
    for key in ("guide_version", "skill_version"):
        value = data.get(key)
        if not isinstance(value, str) or not SEMVER.fullmatch(value):
            fail(errors, f"{key} must be a semantic version string")
    for key in ("stable_core_version", "profile_set_version"):
        if not positive_integer(data.get(key)):
            fail(errors, f"{key} must be a positive integer")
    if not valid_date(data.get("recorded_at")):
        fail(errors, "recorded_at must be an ISO date")
    if data.get("locales") != list(LOCALES):
        fail(errors, "locales must be ['en', 'zh-CN'] in canonical order")

    skill_root: Path | None = None
    skill_package = data.get("skill_package")
    if not isinstance(skill_package, dict):
        fail(errors, "skill_package must be an object")
    else:
        skill_root = safe_relative_path(
            errors, root, skill_package.get("path"), "skill_package.path", expected="directory"
        )
        entrypoint = safe_relative_path(
            errors, root, skill_package.get("entrypoint"), "skill_package.entrypoint"
        )
        if skill_root is not None and entrypoint is not None:
            try:
                entrypoint.resolve().relative_to(skill_root.resolve())
            except ValueError:
                fail(errors, "skill_package.entrypoint must be inside skill_package.path")
            if entrypoint.name != "SKILL.md":
                fail(errors, "skill_package.entrypoint must name SKILL.md")
    safe_relative_path(errors, root, data.get("bilingual_manifest"), "bilingual_manifest")

    peers = data.get("language_peers")
    if not isinstance(peers, dict) or not peers:
        fail(errors, "language_peers must be a non-empty object")
    else:
        for key, pair in peers.items():
            validate_peer_pair(errors, root, pair, f"language_peers.{key}")

    seen_ids: set[str] = set()
    for group_name in ("normative_profiles", "moving_integration_guidance"):
        group = data.get(group_name)
        if not isinstance(group, list) or not group:
            fail(errors, f"{group_name} must be a non-empty array")
            continue
        for index, entry in enumerate(group):
            label = f"{group_name}[{index}]"
            if not isinstance(entry, dict):
                fail(errors, f"{label}: expected an object")
                continue
            item_id = entry.get("id")
            if not isinstance(item_id, str) or not item_id:
                fail(errors, f"{label}.id: expected a non-empty string")
                continue
            if item_id in seen_ids:
                fail(errors, f"duplicate profile ID: {item_id}")
            seen_ids.add(item_id)
            for key in ("status",):
                if not isinstance(entry.get(key), str) or not entry[key]:
                    fail(errors, f"{label}.{key}: expected a non-empty string")
            if group_name == "normative_profiles":
                for key in ("kind", "version"):
                    if not isinstance(entry.get(key), str) or not entry[key]:
                        fail(errors, f"{label}.{key}: expected a non-empty string")
                if not valid_url(entry.get("source")):
                    fail(errors, f"{label}.source: expected an http(s) URL")
            else:
                if not valid_date(entry.get("assessed_at")):
                    fail(errors, f"{label}.assessed_at: expected an ISO date")
                sources = entry.get("sources")
                if not isinstance(sources, list) or not sources or not all(valid_url(url) for url in sources):
                    fail(errors, f"{label}.sources: expected a non-empty array of http(s) URLs")
            validate_profile_binding(errors, root, skill_root, entry, label)

    studies = data.get("case_studies")
    if not isinstance(studies, list):
        fail(errors, "case_studies must be an array")
    else:
        for index, study in enumerate(studies):
            label = f"case_studies[{index}]"
            if not isinstance(study, dict) or not isinstance(study.get("id"), str):
                fail(errors, f"{label}: missing string id")
                continue
            validate_peer_pair(errors, root, study.get("paths"), f"{label}.paths")
            validate_peer_pair(
                errors, root, study.get("evidence_indexes"), f"{label}.evidence_indexes"
            )

    publication = data.get("publication")
    required_publication = {
        "remote_configured": bool,
        "published": bool,
        "license_selected": bool,
        "documentation_license": str,
        "skill_and_code_license": str,
        "bilingual_sync_status": str,
    }
    if not isinstance(publication, dict):
        fail(errors, "publication must be an object")
    else:
        for key, expected_type in required_publication.items():
            value = publication.get(key)
            if not isinstance(value, expected_type) or (
                expected_type is str and not value.strip()
            ):
                fail(errors, f"publication.{key}: expected non-empty {expected_type.__name__}")
        if publication.get("documentation_license") != "CC-BY-4.0":
            fail(errors, "publication.documentation_license must be CC-BY-4.0")
        if publication.get("skill_and_code_license") != "Apache-2.0":
            fail(errors, "publication.skill_and_code_license must be Apache-2.0")
        if publication.get("published") is True:
            if publication.get("remote_configured") is not True:
                fail(errors, "published release requires remote_configured true")
            if not valid_url(publication.get("repository_url")):
                fail(errors, "published release requires publication.repository_url")
            if not valid_date(publication.get("published_at")):
                fail(errors, "published release requires publication.published_at ISO date")

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(
        f"PASS: {register_path} ({len(seen_ids)} bound profiles, bilingual peers present)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
