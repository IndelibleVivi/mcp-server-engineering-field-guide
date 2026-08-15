from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile


sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skill" / "mcp-server-engineering" / "scripts"
TOOLS = ROOT / "tools"


def load_script(name: str):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_tool(name: str):
    path = TOOLS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valid_receipt() -> dict:
    return {
        "schema_version": 2,
        "receipt_id": "TEST-001",
        "claim_id": "CLM-TEST-001",
        "status": "reproduced",
        "executed_at": "2026-08-16T00:00:00+08:00",
        "execution_owner_class": "project-local test execution",
        "owner_relationship": "same-owner",
        "independence_basis": "The same project owner repeated the execution.",
        "independent_execution": False,
        "representation": "projected",
        "source": {
            "repository": "https://example.invalid/repository",
            "identity": {"type": "git-sha1", "value": "a" * 40},
        },
        "environment": {"runtime": "CPython 3"},
        "command_or_probe": ["python3", "probe.py"],
        "parameters": {},
        "expected": {"exit_code": 0},
        "observed": {"exit_code": 0},
        "exit_code": 0,
        "raw_material": {
            "included": False,
            "location": None,
            "omitted_material": "Raw output omitted from this projection.",
        },
        "residual_boundary": "Bounded synthetic receipt.",
    }


class ScriptRunnerMixin:
    def run_script(self, name: str, *arguments: str):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / f"{name}.py"), *arguments],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )


class ReceiptValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipts = load_script("check_receipt_schema")

    def validate_payload(self, payload: dict) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            return self.receipts.validate(path)

    def test_published_receipts_validate(self):
        paths = sorted(ROOT.rglob("receipts/*.json"))
        self.assertGreaterEqual(len(paths), 2)
        for path in paths:
            with self.subTest(path=path.name):
                self.assertEqual(self.receipts.validate(path), [])

    def test_private_path_and_replacement_character_are_rejected(self):
        payload = valid_receipt()
        payload["residual_boundary"] = "/" + "Users/example/\ufffd"
        errors = self.validate_payload(payload)
        self.assertTrue(any("private/sensitive marker" in error for error in errors))
        self.assertTrue(any("U+FFFD" in error for error in errors))

    def test_independent_status_and_flag_are_biconditional(self):
        cases = [
            ("independently-reproduced", False, "same-owner"),
            ("reproduced", True, "independent-owner"),
            ("independently-reproduced", True, "same-owner"),
            ("reproduced", False, "independent-owner"),
        ]
        for status, flag, relationship in cases:
            with self.subTest(status=status, flag=flag, relationship=relationship):
                payload = valid_receipt()
                payload["status"] = status
                payload["independent_execution"] = flag
                payload["owner_relationship"] = relationship
                errors = self.validate_payload(payload)
                self.assertTrue(any("independent" in error for error in errors), errors)

        valid = valid_receipt()
        valid["status"] = "independently-reproduced"
        valid["independent_execution"] = True
        valid["owner_relationship"] = "independent-owner"
        valid["execution_owner_class"] = "external reviewer execution"
        valid["independence_basis"] = "A separate reviewer reran the defined probe."
        self.assertEqual(self.validate_payload(valid), [])

    def test_false_minimal_independent_receipt_is_rejected(self):
        payload = {
            "schema_version": 2,
            "receipt_id": "BAD-MINIMAL",
            "status": "independently-reproduced",
            "source": {
                "identity": {"type": "git-sha1", "value": "b" * 40}
            },
            "environment": {"runtime": "test"},
            "residual_boundary": "bounded",
        }
        errors = self.validate_payload(payload)
        for required in (
            "claim_id",
            "executed_at",
            "execution_owner_class",
            "independence_basis",
            "independent_execution",
            "command_or_probe",
            "parameters",
            "expected",
            "observed",
            "exit_code",
            "raw_material",
        ):
            self.assertTrue(any(required in error for error in errors), (required, errors))

    def test_typed_sha256_identities_are_accepted(self):
        for identity_type in ("git-sha256", "content-sha256"):
            with self.subTest(identity_type=identity_type):
                payload = valid_receipt()
                payload["source"]["identity"] = {
                    "type": identity_type,
                    "value": "c" * 64,
                }
                self.assertEqual(self.validate_payload(payload), [])

    def test_identity_length_must_match_type(self):
        payload = valid_receipt()
        payload["source"]["identity"] = {
            "type": "content-sha256",
            "value": "d" * 40,
        }
        errors = self.validate_payload(payload)
        self.assertTrue(any("does not match content-sha256" in error for error in errors))


class BundleValidationTests(ScriptRunnerMixin, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load_script("scan_review_bundle")

    def test_clean_utf8_passes(self):
        self.assertEqual(self.bundle.inspect_bytes("clean.md", "猫 MCP".encode(), False), [])

    def test_corruption_private_markers_and_binary_fail(self):
        replacement_errors = self.bundle.inspect_bytes(
            "damaged.md", "damaged \ufffd".encode("utf-8"), False
        )
        private_errors = self.bundle.inspect_bytes(
            "private.md", ("/" + "Users/example/source.py").encode(), False
        )
        binary_errors = self.bundle.inspect_bytes("compiled.pyc", b"abc\x00def", False)
        self.assertTrue(any("U+FFFD" in error for error in replacement_errors))
        self.assertTrue(any("private/sensitive marker" in error for error in private_errors))
        self.assertTrue(any("binary" in error for error in binary_errors))
        self.assertEqual(
            self.bundle.inspect_bytes("declared.bin", b"abc\x00def", False, True), []
        )

    def test_binary_single_file_cannot_report_strict_text_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "attachment.bin"
            path.write_bytes(b"prefix\x00payload")
            result = self.run_script("scan_review_bundle", str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unexpected NUL-bearing/binary", result.stderr)

    def test_explicit_binary_allowlist_reports_partial_text_inspection(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "attachment.bin"
            path.write_bytes(b"prefix\x00payload")
            result = self.run_script(
                "scan_review_bundle",
                str(path),
                "--allow-binary",
                "attachment.bin",
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("explicitly allowlisted binary", result.stdout)
        self.assertNotIn("all members passed strict text", result.stdout)

    def test_zip_file_count_and_member_size_budgets_fail_before_scan(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "bundle.zip"
            with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as handle:
                handle.writestr("one.txt", "one")
                handle.writestr("two.txt", "two" * 100)
            count = self.run_script("scan_review_bundle", str(archive), "--max-files", "1")
            size = self.run_script(
                "scan_review_bundle", str(archive), "--max-member-bytes", "10"
            )
            total = self.run_script(
                "scan_review_bundle", str(archive), "--max-total-bytes", "5"
            )
        self.assertNotEqual(count.returncode, 0)
        self.assertIn("file count", count.stderr)
        self.assertNotEqual(size.returncode, 0)
        self.assertIn("size", size.stderr)
        self.assertNotEqual(total.returncode, 0)
        self.assertIn("total uncompressed size", total.stderr)

    def test_zip_compression_ratio_budget_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "ratio.zip"
            with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as handle:
                handle.writestr("repeat.txt", "A" * 100_000)
            result = self.run_script(
                "scan_review_bundle", str(archive), "--max-compression-ratio", "2"
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("compression ratio", result.stderr)


class EvaluationCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_tool("validate_evaluation_corpus")
        cls.runner = load_tool("run_skill_dogfood")

    def copy_repository(self, directory: str) -> Path:
        destination = Path(directory) / "repository"
        shutil.copytree(
            ROOT,
            destination,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"),
        )
        return destination

    def test_preregistered_corpus_validates_before_results(self):
        self.assertEqual(self.validator.validate(ROOT, allow_missing_results=True), [])

    def test_fixture_hash_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = self.copy_repository(directory)
            fixture = (
                repository
                / "evaluations"
                / "skill-v0.1.0"
                / "fixtures"
                / "parent-owned-stdio"
                / "server.py"
            )
            fixture.write_text(fixture.read_text(encoding="utf-8") + "\n# drift\n", encoding="utf-8")
            errors = self.validator.validate(repository, allow_missing_results=True)
        self.assertTrue(any("fixture_content_sha256 mismatch" in error for error in errors), errors)

    def test_zero_discovered_receipts_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = self.copy_repository(directory)
            for receipt in repository.rglob("receipts/*.json"):
                receipt.unlink()
            errors = self.validator.validate(repository, allow_missing_results=True)
        self.assertTrue(any("zero discovered public receipts" in error for error in errors), errors)

    def test_private_path_in_projected_output_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = self.copy_repository(directory)
            evaluation = repository / "evaluations" / "skill-v0.1.0"
            results = json.loads((evaluation / "results.json").read_text(encoding="utf-8"))
            output = evaluation / results["runs"][0]["output_projection_path"]
            output.write_text("Private path: /" + "Users/example/fixture.py\n", encoding="utf-8")
            errors = self.validator.validate(repository)
        self.assertTrue(
            any("projected output contains private path marker" in error for error in errors),
            errors,
        )

    def test_invalid_completed_shape_cannot_count_for_release(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = self.copy_repository(directory)
            evaluation = repository / "evaluations" / "skill-v0.1.0"
            receipts = evaluation / "receipts"
            outputs = evaluation / "outputs"
            receipts.mkdir(exist_ok=True)
            outputs.mkdir(exist_ok=True)
            receipt = valid_receipt()
            receipt["receipt_id"] = "EVAL-INVALID-001"
            receipt["recorded_at"] = "2026-08-16T00:01:00+08:00"
            (receipts / "EVAL-INVALID-001.json").write_text(
                json.dumps(receipt), encoding="utf-8"
            )
            (outputs / "RUN-INVALID.md").write_text("Projected output.\n", encoding="utf-8")
            rubric = json.loads((evaluation / "rubric.json").read_text(encoding="utf-8"))
            item_ids = rubric["scenario_items"]["CANARY-DISCOVERY-001"]
            results = {
                "schema_version": 1,
                "rubric_version": rubric["rubric_version"],
                "release_candidate_skill_version": "0.1.0",
                "runs": [
                    {
                        "run_id": "RUN-INVALID",
                        "scenario_id": "CANARY-DISCOVERY-001",
                        "scenario_revision": 1,
                        "skill_version": "0.1.0",
                        "receipt_id": "EVAL-INVALID-001",
                        "output_projection_path": "outputs/RUN-INVALID.md",
                        "run_validity": "trace-incomplete",
                        "counts_for_release": True,
                        "rubric_outcomes": {item_id: "pass" for item_id in item_ids},
                        "evidence_references": ["EVAL-INVALID-001"],
                        "assessment_owner": "test assessor",
                        "assessment_method": "synthetic unit test",
                        "model_assisted_assessment": False,
                        "residuals": [],
                    }
                ],
            }
            (evaluation / "results.json").write_text(json.dumps(results), encoding="utf-8")
            errors = self.validator.validate(repository)
        self.assertTrue(any("invalid run cannot count for release" in error for error in errors), errors)

    def test_completed_turn_with_item_diagnostic_can_be_valid(self):
        trace = {
            "oracle_access_observed": False,
            "turn_failed": False,
            "top_level_errors": [],
            "thread_started": True,
            "jsonl_parse_errors": [],
            "turn_completed": True,
            "final_agent_message": "done",
            "entrypoint_loaded": True,
            "skill_material_loaded": True,
            "skill_loaded": True,
            "item_level_errors": [{"message": "nonfatal diagnostic"}],
        }
        validity, reasons = self.runner.classify_validity(
            0, False, trace, {"requires_skill_load": True}
        )
        self.assertEqual((validity, reasons), ("valid-completed", []))

    def test_trace_parser_accepts_installed_symlink_spelling(self):
        skill = {
            "entrypoint": Path("/canonical/mcp-server-engineering/SKILL.md"),
            "installed_entrypoint": Path("/installed/mcp-server-engineering/SKILL.md"),
            "realpath": Path("/canonical/mcp-server-engineering"),
            "installed_path": Path("/installed/mcp-server-engineering"),
        }
        events = [
            {"type": "thread.started", "thread_id": "test"},
            {
                "type": "item.completed",
                "item": {
                    "id": "item_1",
                    "type": "command_execution",
                    "command": "sed -n 1,200p /installed/mcp-server-engineering/SKILL.md",
                },
            },
            {
                "type": "item.completed",
                "item": {"id": "item_2", "type": "agent_message", "text": "done"},
            },
            {"type": "turn.completed"},
        ]
        trace = self.runner.parse_events(
            "\n".join(json.dumps(event) for event in events), skill
        )
        self.assertTrue(trace["skill_loaded"])
        self.assertTrue(trace["entrypoint_loaded"])
        self.assertTrue(trace["skill_material_loaded"])
        self.assertEqual(trace["skill_invocation_evidence"][0]["reads"], ["SKILL.md"])

    def test_trace_parser_accepts_relative_reference_spelling(self):
        skill = {
            "entrypoint": Path("/canonical/mcp-server-engineering/SKILL.md"),
            "installed_entrypoint": Path("/installed/mcp-server-engineering/SKILL.md"),
            "realpath": ROOT / "skill" / "mcp-server-engineering",
            "installed_path": ROOT / "skill" / "mcp-server-engineering",
        }
        events = [
            {"type": "thread.started", "thread_id": "test"},
            {
                "type": "item.completed",
                "item": {
                    "id": "item_1",
                    "type": "command_execution",
                    "command": "sed -n 1,200p references/protocol-selection.md",
                },
            },
            {
                "type": "item.completed",
                "item": {"id": "item_2", "type": "agent_message", "text": "done"},
            },
            {"type": "turn.completed"},
        ]
        trace = self.runner.parse_events(
            "\n".join(json.dumps(event) for event in events), skill
        )
        self.assertFalse(trace["entrypoint_loaded"])
        self.assertTrue(trace["skill_material_loaded"])
        self.assertEqual(trace["loaded_reference_ids"], ["protocol-selection"])

    def test_process_exit_zero_without_completed_turn_is_trace_incomplete(self):
        trace = {
            "oracle_access_observed": False,
            "turn_failed": False,
            "top_level_errors": [],
            "thread_started": True,
            "jsonl_parse_errors": [],
            "turn_completed": False,
            "final_agent_message": None,
            "entrypoint_loaded": True,
            "skill_material_loaded": True,
            "skill_loaded": True,
        }
        validity, reasons = self.runner.classify_validity(
            0, False, trace, {"requires_skill_load": True}
        )
        self.assertEqual(validity, "trace-incomplete")
        self.assertTrue(reasons)


class RepositoryContractTests(ScriptRunnerMixin, unittest.TestCase):
    def copy_repository(self, directory: str) -> Path:
        destination = Path(directory) / "repository"
        shutil.copytree(
            ROOT,
            destination,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"),
        )
        return destination

    def test_version_register(self):
        result = self.run_script("validate_version_register", "VERSION-REGISTER.json")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_profile_mirrors(self):
        result = self.run_script(
            "sync_profile_mirrors", "--check", "VERSION-REGISTER.json"
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_register_rejects_missing_or_mistyped_release_identity_fields(self):
        mutations = {
            "missing-skill-version": lambda data: data.pop("skill_version"),
            "missing-skill-package": lambda data: data.pop("skill_package"),
            "object-profile-set-version": lambda data: data.__setitem__(
                "profile_set_version", {"value": 1}
            ),
            "invalid-recorded-at": lambda data: data.__setitem__("recorded_at", "not-a-date"),
            "unbound-profile-hash": lambda data: data["normative_profiles"][0][
                "content_sha256"
            ].__setitem__("en", "0" * 64),
            "missing-documentation-license": lambda data: data["publication"].pop(
                "documentation_license"
            ),
            "missing-code-license": lambda data: data["publication"].pop(
                "skill_and_code_license"
            ),
        }
        source = json.loads((ROOT / "VERSION-REGISTER.json").read_text(encoding="utf-8"))
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                repository = self.copy_repository(directory)
                data = copy.deepcopy(source)
                mutate(data)
                register = repository / "VERSION-REGISTER.json"
                register.write_text(json.dumps(data), encoding="utf-8")
                result = self.run_script("validate_version_register", str(register))
                self.assertNotEqual(result.returncode, 0, result.stdout)

    def test_register_rejects_missing_profile_front_matter(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = self.copy_repository(directory)
            profile = repository / "profiles" / "mcp-2025-06-18.md"
            text = profile.read_text(encoding="utf-8")
            profile.write_text(text.split("\n---\n", 1)[1], encoding="utf-8")
            result = self.run_script(
                "validate_version_register", str(repository / "VERSION-REGISTER.json")
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("require front matter", result.stderr)

    def test_register_rejects_skill_profile_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = self.copy_repository(directory)
            mirror = (
                repository
                / "skill"
                / "mcp-server-engineering"
                / "references"
                / "mcp-2025-11-25.md"
            )
            mirror.write_text(mirror.read_text(encoding="utf-8") + "\ndrift\n", encoding="utf-8")
            result = self.run_script(
                "validate_version_register", str(repository / "VERSION-REGISTER.json")
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("mirror differs", result.stderr)

    def test_bilingual_structure(self):
        result = self.run_script("check_bilingual_coverage", ".")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_bilingual_check_is_bidirectional_via_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = self.copy_repository(directory)
            missing = (
                repository
                / "skill"
                / "mcp-server-engineering"
                / "assets"
                / "templates"
                / "finding.zh-CN.md"
            )
            missing.unlink()
            result = self.run_script("check_bilingual_coverage", str(repository))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing zh-CN peer", result.stderr)

    def test_skill_package(self):
        result = self.run_script(
            "validate_skill_package", "skill/mcp-server-engineering"
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_skill_package_rejects_compiled_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "mcp-server-engineering"
            shutil.copytree(ROOT / "skill" / "mcp-server-engineering", copied)
            cache = copied / "scripts" / "__pycache__"
            cache.mkdir(exist_ok=True)
            (cache / "validator.cpython-313.pyc").write_bytes(b"\x00compiled")
            result = self.run_script("validate_skill_package", str(copied))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("generated/cache", result.stderr)

    def test_local_markdown_links(self):
        result = self.run_script("check_markdown_links", ".")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_controller_encodes_upgrade_and_stdio_branches(self):
        controller = (
            ROOT / "skill" / "mcp-server-engineering" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("For **spec-upgrade**, load both", controller)
        self.assertIn("base [JSON-RPC 2.0 profile]", controller)
        self.assertIn("For pure stdio owned by a parent process", controller)
        self.assertIn("upgrade-retirement-inventory.md", controller)


if __name__ == "__main__":
    unittest.main()
