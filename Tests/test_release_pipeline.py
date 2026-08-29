"""Tests for release bootstrap, evidence, and publication ordering."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import copy
import importlib.util
import json
import re
import tarfile
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "Scripts/collect-release-evidence.py"
SPECIFICATION = importlib.util.spec_from_file_location("collect_release_evidence", SCRIPT)
assert SPECIFICATION and SPECIFICATION.loader
EVIDENCE = importlib.util.module_from_spec(SPECIFICATION)
SPECIFICATION.loader.exec_module(EVIDENCE)


class ReleaseEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(
            (ROOT / "catalog/release-manifest.json").read_text(encoding="utf-8")
        )
        cls.revision = "a" * 40

    def terminology_evidence(self) -> tuple[dict[str, object], dict[str, str]]:
        package_digests = {
            guide["packageId"]: f"{index:064x}"
            for index, guide in enumerate(self.manifest["guides"], start=1)
        }
        evidence = {
            "$schema": EVIDENCE.TERMINOLOGY_EVIDENCE_SCHEMA_URL,
            "schemaVersion": 0,
            "releaseVersion": self.manifest["releaseVersion"],
            "fhirVersion": self.manifest["fhirVersion"],
            "sourceRevision": self.revision,
            "validationDate": "2026-08-27",
            "endpoint": {
                "url": "https://terminology.example.org/fhir",
                "software": "Example terminology service",
                "version": "2026.08",
            },
            "terminologyEditions": [
                {
                    "system": "http://loinc.org",
                    "edition": "international",
                    "version": "2.81",
                    "authority": "Regenstrief Institute",
                }
            ],
            "policy": {
                "identifier": "https://example.org/policies/fhir-terminology-validation",
                "version": "1.0.0",
                "sha256": "b" * 64,
                "licensedContentAuthorized": True,
                "cacheMode": "cold",
                "warningDisposition": "reviewed",
            },
            "tool": {
                "name": "HL7 FHIR Validator",
                **self.manifest["toolchain"]["fhirValidator"],
                "arguments": ["-tx", "https://terminology.example.org/fhir"],
            },
            "packages": [
                {
                    "packageId": guide["packageId"],
                    "version": self.manifest["releaseVersion"],
                    "sha256": package_digests[guide["packageId"]],
                }
                for guide in self.manifest["guides"]
            ],
            "result": {
                "status": "passed",
                "validatedResourceCount": 100,
                "errorCount": 0,
                "warningCount": 2,
                "completedAt": "2026-08-27T20:15:00Z",
                "summary": "All errors failed; two warnings were reviewed under the policy.",
                "report": {
                    "file": "terminology-report.json",
                    "mediaType": "application/fhir+json",
                    "sha256": "c" * 64,
                },
            },
        }
        return evidence, package_digests

    def test_contract_archive_covers_every_declared_catalog_schema_and_corpus(self) -> None:
        paths = EVIDENCE.normative_contract_paths(ROOT, self.manifest)
        relative = {path.relative_to(ROOT).as_posix() for path in paths}

        expected = {
            "catalog/release-manifest.json",
            "catalog/schemas/release-manifest.schema.json",
            "catalog/schemas/release-evidence.schema.json",
            "catalog/schemas/terminology-evidence.schema.json",
        }
        expected.update(
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / "catalog").rglob("*.json")
        )
        for catalog in self.manifest["normativeCatalogs"]:
            expected.update((catalog["path"], catalog["schema"]))
        for corpus_root in EVIDENCE.NORMATIVE_CORPUS_ROOTS:
            expected.update(
                path.relative_to(ROOT).as_posix()
                for path in (ROOT / corpus_root).rglob("*.json")
            )
        self.assertEqual(relative, expected)
        self.assertTrue(
            {
                "Conformance/corpora/mobile-exchange/corpus.json",
                "Conformance/corpora/mobile-exchange/exchange-bundle.json",
                "Conformance/corpora/mobile-exchange/retraction-bundle.json",
                "Conformance/corpora/mobile-semantics/corpus.json",
            }.issubset(relative)
        )
        self.assertEqual(
            [path.relative_to(ROOT).as_posix() for path in paths], sorted(relative)
        )

    def test_contract_archive_is_byte_deterministic_and_self_indexed(self) -> None:
        index, paths = EVIDENCE.machine_contract_index(
            ROOT, self.manifest, self.revision
        )
        self.assertEqual(
            set(index["artifacts"]),
            {path.relative_to(ROOT).as_posix() for path in paths},
        )
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.tar.gz"
            second = Path(directory) / "second.tar.gz"
            EVIDENCE.write_machine_contract_archive(first, ROOT, index, paths)
            EVIDENCE.write_machine_contract_archive(second, ROOT, index, paths)
            self.assertEqual(first.read_bytes(), second.read_bytes())

            with tarfile.open(first, "r:gz") as archive:
                members = archive.getmembers()
                self.assertEqual(members[0].name, "machine-contract-index.json")
                self.assertEqual(
                    [member.name for member in members[1:]],
                    [path.relative_to(ROOT).as_posix() for path in paths],
                )
                self.assertTrue(
                    all(
                        member.mtime == 0
                        and member.uid == 0
                        and member.gid == 0
                        and member.mode == 0o644
                        for member in members
                    )
                )
                embedded = json.load(archive.extractfile(members[0]))
                self.assertEqual(embedded, index)

    def test_generated_contract_index_satisfies_its_closed_schema(self) -> None:
        index, _ = EVIDENCE.machine_contract_index(ROOT, self.manifest, self.revision)
        with tempfile.TemporaryDirectory() as directory:
            instance = Path(directory) / "index.json"
            instance.write_bytes(EVIDENCE.json_bytes(index))
            EVIDENCE.validate_json_schema(EVIDENCE.RELEASE_EVIDENCE_SCHEMA, instance)

            index["unexpected"] = True
            instance.write_bytes(EVIDENCE.json_bytes(index))
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "must NOT have"):
                EVIDENCE.validate_json_schema(EVIDENCE.RELEASE_EVIDENCE_SCHEMA, instance)

    def test_terminology_evidence_is_closed_and_bound_to_release_inputs(self) -> None:
        evidence, package_digests = self.terminology_evidence()
        with tempfile.TemporaryDirectory() as directory:
            instance = Path(directory) / "terminology.json"
            instance.write_bytes(EVIDENCE.json_bytes(evidence))
            EVIDENCE.validate_json_schema(EVIDENCE.TERMINOLOGY_EVIDENCE_SCHEMA, instance)

            EVIDENCE.validate_terminology_evidence(
                evidence,
                manifest=self.manifest,
                source_revision=self.revision,
                package_digests=package_digests,
            )

            unknown = copy.deepcopy(evidence)
            unknown["endpoint"]["unreviewed"] = True
            instance.write_bytes(EVIDENCE.json_bytes(unknown))
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "must NOT have"):
                EVIDENCE.validate_json_schema(
                    EVIDENCE.TERMINOLOGY_EVIDENCE_SCHEMA, instance
                )

            drifted = copy.deepcopy(evidence)
            drifted["packages"][0]["sha256"] = "f" * 64
            with self.assertRaisesRegex(
                EVIDENCE.EvidenceError, "package closure does not match"
            ):
                EVIDENCE.validate_terminology_evidence(
                    drifted,
                    manifest=self.manifest,
                    source_revision=self.revision,
                    package_digests=package_digests,
                )

    def test_terminology_validation_date_and_editions_are_unambiguous(self) -> None:
        evidence, package_digests = self.terminology_evidence()
        evidence["terminologyEditions"].append(
            copy.deepcopy(evidence["terminologyEditions"][0])
        )
        with self.assertRaisesRegex(EVIDENCE.EvidenceError, "repeats"):
            EVIDENCE.validate_terminology_evidence(
                evidence,
                manifest=self.manifest,
                source_revision=self.revision,
                package_digests=package_digests,
            )

        evidence, package_digests = self.terminology_evidence()
        evidence["result"]["completedAt"] = "2026-08-28T00:01:00Z"
        with self.assertRaisesRegex(EVIDENCE.EvidenceError, "validationDate"):
            EVIDENCE.validate_terminology_evidence(
                evidence,
                manifest=self.manifest,
                source_revision=self.revision,
                package_digests=package_digests,
            )

        evidence, package_digests = self.terminology_evidence()
        evidence["endpoint"]["url"] = "https://other.example.org/fhir"
        with self.assertRaisesRegex(EVIDENCE.EvidenceError, "arguments"):
            EVIDENCE.validate_terminology_evidence(
                evidence,
                manifest=self.manifest,
                source_revision=self.revision,
                package_digests=package_digests,
            )

        evidence, package_digests = self.terminology_evidence()
        evidence["policy"]["warningDisposition"] = "fail"
        with self.assertRaisesRegex(EVIDENCE.EvidenceError, "fails warnings"):
            EVIDENCE.validate_terminology_evidence(
                evidence,
                manifest=self.manifest,
                source_revision=self.revision,
                package_digests=package_digests,
            )

    def test_terminology_report_is_json_and_checksum_bound(self) -> None:
        evidence, _ = self.terminology_evidence()
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "terminology-report.json"
            report.write_text(
                json.dumps({"resourceType": "OperationOutcome", "issue": []}) + "\n",
                encoding="utf-8",
            )
            evidence["result"]["report"]["sha256"] = EVIDENCE.sha256(report)
            evidence_path = Path(directory) / "evidence.json"
            evidence_path.write_bytes(EVIDENCE.json_bytes(evidence))
            self.assertEqual(
                EVIDENCE.terminology_report_input(evidence_path, evidence), report
            )

            report.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "checksum"):
                EVIDENCE.terminology_report_input(evidence_path, evidence)


class ReleaseWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = (ROOT / ".github/workflows/deployment.yml").read_text(
            encoding="utf-8"
        )
        cls.build_guides = (ROOT / "Scripts/build-guides.sh").read_text(
            encoding="utf-8"
        )
        cls.build_release = (ROOT / "Scripts/build-release.sh").read_text(
            encoding="utf-8"
        )

    def test_release_is_created_only_after_verification(self) -> None:
        self.assertNotIn("types: [published]", self.workflow)
        self.assertNotIn("gh release upload", self.workflow)
        self.assertLess(
            self.workflow.index("npm test"), self.workflow.index("gh release create")
        )
        self.assertLess(
            self.workflow.index("collect-release-evidence.py"),
            self.workflow.index("gh release create"),
        )
        self.assertLess(
            self.workflow.index('"repos/$GITHUB_REPOSITORY/git/refs"'),
            self.workflow.index("gh release create"),
        )
        self.assertIn("--verify-tag", self.workflow)
        self.assertLess(
            self.workflow.index("gh release create"),
            self.workflow.index("gh release edit"),
        )
        self.assertIn("--draft=false", self.workflow)

    def test_release_candidates_run_both_official_validator_corpora(self) -> None:
        for label, script in (
            ("deployment workflow", self.workflow),
            ("local release script", self.build_release),
        ):
            with self.subTest(label=label):
                self.assertIn("Scripts/validate-questionnaire-fhir.py", script)
                self.assertIn("Scripts/validate-producer.py", script)
                self.assertIn("--allow-example-urls", script)
                self.assertLess(
                    script.index("Scripts/validate-questionnaire-fhir.py"),
                    script.index("Scripts/collect-release-evidence.py"),
                )
                self.assertLess(
                    script.index("Scripts/validate-producer.py"),
                    script.index("Scripts/collect-release-evidence.py"),
                )

    def test_write_token_is_isolated_from_repository_code(self) -> None:
        verify, publish = self.workflow.split("\n  publish:\n", maxsplit=1)
        self.assertNotIn("contents: write", verify)
        self.assertIn("contents: write", publish)
        self.assertNotIn("actions/checkout@", publish)
        self.assertNotIn("npm ", publish)
        self.assertLess(
            verify.index("collect-release-evidence.py"),
            verify.index("actions/upload-artifact@"),
        )
        self.assertIn("sha256sum --check SHA256SUMS", publish)

    def test_release_action_dependencies_use_reviewed_major_tags(self) -> None:
        action_references = [
            line.split("uses:", maxsplit=1)[1].strip()
            for line in self.workflow.splitlines()
            if "uses:" in line
        ]
        self.assertCountEqual(
            action_references,
            [
                "actions/checkout@v7",
                "actions/setup-node@v7",
                "actions/setup-python@v7",
                "actions/setup-java@v6",
                "ruby/setup-ruby@v1",
                "actions/cache@v6",
                "actions/upload-artifact@v7",
                "actions/download-artifact@v8",
            ],
        )
        self.assertTrue(all(re.search(r"@v[0-9]+$", ref) for ref in action_references))
        self.assertIn('node-version: "24.16.0"', self.workflow)
        self.assertNotIn("runs-on: ubuntu-latest", self.workflow)

    def test_artifact_boundary_uses_reviewed_major_tags_in_separate_jobs(self) -> None:
        verify, publish = self.workflow.split("\n  publish:\n", maxsplit=1)
        self.assertIn("uses: actions/upload-artifact@v7", verify)
        self.assertNotIn("actions/download-artifact@", verify)
        self.assertIn("uses: actions/download-artifact@v8", publish)
        self.assertNotIn("actions/upload-artifact@", publish)

    def test_online_bootstrap_precedes_and_is_replayed_offline(self) -> None:
        online = self.workflow.index("Bootstrap the checksum-pinned dependency closure online")
        offline = self.workflow.index("Replay the verified closure")
        self.assertLess(online, offline)
        for command in (
            "npm ci --offline",
            "bundle check",
            "download-fhir-tools.sh --offline",
            'GROVE_TX_OFFLINE: "1"',
        ):
            self.assertIn(command, self.workflow)
        for command in (
            "npm ci --offline",
            "bundle check",
            "download-fhir-tools.sh --offline",
            "export GROVE_TX_OFFLINE=1",
        ):
            self.assertIn(command, self.build_release)

    def test_offline_guide_build_cannot_fall_back_to_network(self) -> None:
        for command in (
            "export BUNDLE_FROZEN=true",
            "bundle install --local",
            "download-fhir-tools.sh --offline",
            "-tx n/a -no-network",
        ):
            self.assertIn(command, self.build_guides)
        self.assertIn(
            "GROVE_TX_SERVER is prohibited when GROVE_TX_OFFLINE=1",
            self.build_guides,
        )

if __name__ == "__main__":
    unittest.main()
