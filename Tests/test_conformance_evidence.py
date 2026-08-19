"""Focused tests for the deterministic #8 evidence and publication lock."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import copy
import hashlib
import io
import json
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from Scripts.fhir_fixture_corpus import canonical_json_bytes
from Scripts import conformance_evidence as EVIDENCE


ROOT = Path(__file__).parents[1]
REVISION = "1" * 40
EPOCH = 1_700_000_000


class ConformanceEvidenceTests(unittest.TestCase):
    def test_downloaded_package_identity_ignores_non_fhir_json_but_rejects_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "dependency.tgz"
            manifest = canonical_json_bytes(
                {"name": "example.fhir.package", "version": "1.0.0"}
            )
            with tarfile.open(archive, "w:gz") as package:
                for name, data in {
                    "package/package.json": manifest,
                    "package/openapi/example.json": b"\xef\xbb\xbf{}\n",
                }.items():
                    member = tarfile.TarInfo(name)
                    member.size = len(data)
                    package.addfile(member, io.BytesIO(data))
            self.assertEqual(
                EVIDENCE._read_downloaded_package_manifest(archive, "package"),
                {"name": "example.fhir.package", "version": "1.0.0"},
            )

            with tarfile.open(archive, "w:gz") as package:
                member = tarfile.TarInfo("package/package.json")
                member.size = len(manifest)
                package.addfile(member, io.BytesIO(manifest))
                link = tarfile.TarInfo("package/unsafe.json")
                link.type = tarfile.SYMTYPE
                link.linkname = "package.json"
                package.addfile(link)
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "archive link"):
                EVIDENCE._read_downloaded_package_manifest(archive, "package")

    def test_schema_uses_ajv_and_rejects_missing_classification(self) -> None:
        valid = subprocess.run(
            [
                "node",
                "Scripts/validate-json-schema.cjs",
                "Conformance/evidence.schema.json",
                "Conformance/evidence.json",
                "Conformance/toolchain.json",
                "Conformance/semantic-baseline.json",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(valid.returncode, 0, valid.stderr)
        with tempfile.TemporaryDirectory() as directory:
            manifest = json.loads((ROOT / "Conformance/evidence.json").read_text())
            manifest["implementations"][0].pop("classification")
            invalid = Path(directory) / "invalid.json"
            invalid.write_text(json.dumps(manifest), encoding="utf-8")
            result = subprocess.run(
                [
                    "node",
                    str(ROOT / "Scripts/validate-json-schema.cjs"),
                    str(ROOT / "Conformance/evidence.schema.json"),
                    str(invalid),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("classification", result.stderr)

    def test_generator_identity_does_not_cover_same_source_implementation(self) -> None:
        proposals = {
            "writer-one": {
                "source": "shared-source",
                "dependsOn": [],
                "appliesAfter": [],
            },
            "writer-two": {
                "source": "shared-source",
                "dependsOn": [],
                "appliesAfter": [],
            },
        }
        implementations = {
            "first": {
                "id": "first",
                "source": "shared-source",
                "classification": "accepted-contract",
                "generator": {"proposal": "writer-one"},
            },
            "second": {
                "id": "second",
                "source": "shared-source",
                "classification": "accepted-contract",
                "generator": {"proposal": "writer-two"},
            },
        }
        artifacts = {
            "first-output": {
                "id": "first-output",
                "implementation": "first",
                "source": "shared-source",
                "classification": "accepted-contract",
                "proposals": ["writer-one"],
            }
        }
        with self.assertRaisesRegex(EVIDENCE.EvidenceError, "second.*no declared"):
            EVIDENCE.validate_external_evidence_coverage(
                artifacts, implementations, proposals
            )

    def test_language_toolchain_direct_dependencies_are_unique_and_exact(self) -> None:
        toolchain = json.loads((ROOT / "Conformance/toolchain.json").read_text())
        package_json = json.loads((ROOT / "package.json").read_text())
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            (repository / "Scripts").mkdir()
            for relative in (
                "Scripts/download-fhir-tools.sh",
                "Gemfile",
                "Gemfile.lock",
            ):
                target = repository / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, target)
            EVIDENCE.validate_toolchain(repository, toolchain, package_json)
            duplicate_npm = copy.deepcopy(toolchain)
            duplicate_npm["npmPackages"].append(
                copy.deepcopy(duplicate_npm["npmPackages"][0])
            )
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "unique package names"):
                EVIDENCE.validate_toolchain(repository, duplicate_npm, package_json)
            duplicate_ruby = copy.deepcopy(toolchain)
            duplicate_ruby["rubyPackages"].append(
                copy.deepcopy(duplicate_ruby["rubyPackages"][0])
            )
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "unique package names"):
                EVIDENCE.validate_toolchain(repository, duplicate_ruby, package_json)
            drifted_ruby = copy.deepcopy(toolchain)
            drifted_ruby["rubyPackages"][0]["version"] = "4.4.0"
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "exactly match"):
                EVIDENCE.validate_toolchain(repository, drifted_ruby, package_json)

        with patch.object(EVIDENCE, "_command_output", return_value="15.26.0"):
            locked = EVIDENCE.collect_language_packages(ROOT, toolchain)
        firebase = next(item for item in locked if item["name"] == "firebase-tools")
        self.assertEqual(firebase["resolvedVersion"], "15.26.0")
        self.assertEqual(firebase["executableVersion"], "15.26.0")
        self.assertEqual(
            firebase["lockfileSha256"], EVIDENCE.sha256_file(ROOT / "package-lock.json")
        )
        jekyll = next(item for item in locked if item["name"] == "jekyll")
        self.assertEqual(
            jekyll["lockfileSha256"], EVIDENCE.sha256_file(ROOT / "Gemfile.lock")
        )

    def test_archive_is_byte_deterministic_and_metadata_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root / "evidence"
            evidence.mkdir()
            (evidence / "z.txt").write_text("z\n", encoding="utf-8")
            (evidence / "a.txt").write_text("a\n", encoding="utf-8")
            first = root / "first.tgz"
            second = root / "second.tgz"
            EVIDENCE.create_deterministic_archive(evidence, first, EPOCH)
            EVIDENCE.create_deterministic_archive(evidence, second, EPOCH)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(first.read_bytes()[:10], EVIDENCE.canonical_gzip_header(EPOCH))
            with tarfile.open(first, "r:gz") as archive:
                members = archive.getmembers()
            self.assertEqual([item.name for item in members], sorted(item.name for item in members))
            for member in members:
                self.assertEqual(member.mode, 0o644)
                self.assertEqual(member.mtime, EPOCH)
                self.assertEqual(member.uid, 0)
                self.assertEqual(member.gid, 0)
                self.assertEqual(member.uname, "")
                self.assertEqual(member.gname, "")
                self.assertEqual(member.pax_headers, {})
                self.assertEqual(member.linkname, "")
                self.assertEqual(member.devmajor, 0)
                self.assertEqual(member.devminor, 0)
            for index, value in ((3, 4), (8, 0), (9, 3)):
                variant = root / f"header-{index}.tgz"
                EVIDENCE.create_deterministic_archive(evidence, variant, EPOCH)
                tampered = bytearray(variant.read_bytes())
                tampered[index] = value
                variant.write_bytes(tampered)
                Path(f"{variant}.sha256").write_text(
                    f"{hashlib.sha256(tampered).hexdigest()}  {variant.name}\n",
                    encoding="utf-8",
                )
                self.assertIn(
                    "evidence archive gzip header is not canonical",
                    EVIDENCE.verify_archive(evidence, variant, EPOCH),
                )

    def test_archive_rejects_pax_link_and_device_metadata(self) -> None:
        for variant in ("pax", "link", "devminor"):
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                evidence = root / "evidence"
                evidence.mkdir()
                data = b"exact\n"
                (evidence / "exact.txt").write_bytes(data)
                archive = root / f"{variant}.tgz"
                with archive.open("wb") as raw:
                    with EVIDENCE.gzip.GzipFile(
                        filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=EPOCH
                    ) as compressed:
                        with tarfile.open(
                            fileobj=compressed,
                            mode="w",
                            format=(
                                tarfile.PAX_FORMAT
                                if variant == "pax"
                                else tarfile.USTAR_FORMAT
                            ),
                        ) as package:
                            member = tarfile.TarInfo(
                                f"{EVIDENCE.ARCHIVE_PREFIX}/exact.txt"
                            )
                            member.size = len(data)
                            member.mode = 0o644
                            member.mtime = EPOCH
                            if variant == "pax":
                                member.pax_headers = {"comment": "not-canonical"}
                            elif variant == "link":
                                member.linkname = "ignored-link-target"
                            else:
                                member.type = tarfile.CHRTYPE
                                member.size = 0
                                member.devminor = 1
                            package.addfile(
                                member,
                                None if variant == "devminor" else io.BytesIO(data),
                            )
                Path(f"{archive}.sha256").write_text(
                    f"{EVIDENCE.sha256_file(archive)}  {archive.name}\n",
                    encoding="utf-8",
                )
                self.assertTrue(
                    any(
                        "metadata is not canonical" in failure
                        for failure in EVIDENCE.verify_archive(evidence, archive, EPOCH)
                    )
                )

    def test_portable_site_verifier_rejects_every_publication_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence, archive, site = self._site_fixture(root)
            self.assertEqual(EVIDENCE.verify_site_evidence(site, REVISION), [])

            semantic = site / "conformance/ci-build/semantic-diff.json"
            semantic.write_text("{}\n", encoding="utf-8")
            self.assertTrue(
                any("does not match bundled evidence" in item for item in EVIDENCE.verify_site_evidence(site, REVISION))
            )

            evidence, archive, site = self._site_fixture(root / "package")
            package = site / "fhir/mobile/ci-build/package.tgz"
            package.write_bytes(package.read_bytes() + b"tampered")
            self.assertTrue(
                any("package bytes do not match" in item for item in EVIDENCE.verify_site_evidence(site, REVISION))
            )

            evidence, archive, site = self._site_fixture(root / "member")
            report = evidence / "reports/semantic-diff.json"
            report.write_text('{"tampered":true}\n', encoding="utf-8")
            EVIDENCE.create_deterministic_archive(evidence, archive, EPOCH)
            EVIDENCE.inject_pages(evidence, archive, site)
            self.assertTrue(
                any("archive member does not match lock" in item for item in EVIDENCE.verify_site_evidence(site, REVISION))
            )

            evidence, archive, site = self._site_fixture(root / "extra")
            (evidence / "unexpected.txt").write_text("unexpected\n", encoding="utf-8")
            EVIDENCE.create_deterministic_archive(evidence, archive, EPOCH)
            EVIDENCE.inject_pages(evidence, archive, site)
            self.assertTrue(
                any("member set does not exactly match" in item for item in EVIDENCE.verify_site_evidence(site, REVISION))
            )

    def test_raw_validator_transcripts_are_not_external_evidence(self) -> None:
        declaration = {
            "path": "validation.txt",
            "format": "validator-transcript",
        }
        with self.assertRaisesRegex(EVIDENCE.EvidenceError, "unsupported"):
            EVIDENCE._validate_external_file(
                (
                    b"\x1b[31mSuccess: 0 errors, 0 warnings, 0 notes\x1b[0m\n"
                    b"Current: /Users/runner/work/repository/input.json\n"
                    b"Package Cache: C:\\Users\\runner\\.fhir\\packages\n"
                ),
                declaration,
                {"id": "example"},
                {},
                {},
            )

    def test_external_directory_allowlist_rejects_extra_and_symlink(self) -> None:
        declarations = {
            "example-set": {
                "id": "example-set",
                "kind": "directory",
                "implementation": "example",
                "files": [
                    {
                        "path": "resource.json",
                        "format": "fhir-json",
                        "mediaType": "application/fhir+json",
                    }
                ],
            }
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            (source / "resource.json").write_text(
                '{"resourceType":"Observation"}\n', encoding="utf-8"
            )
            (source / "extra.json").write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "allowlist mismatch"):
                EVIDENCE._external_source_files(
                    root / "evidence",
                    declarations,
                    {"example-set": source.resolve()},
                    copy_evidence=True,
                )
            (source / "extra.json").unlink()
            (source / "link.json").symlink_to(source / "resource.json")
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "symlink|non-regular"):
                EVIDENCE._external_source_files(
                    root / "evidence",
                    declarations,
                    {"example-set": source.resolve()},
                    copy_evidence=True,
                )

    def test_validation_report_is_exact_and_transitively_bound(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            evidence_root = repository / "evidence"
            evidence_root.mkdir()
            producer = repository / "Scripts/validate-domain-fhir.py"
            producer.parent.mkdir()
            producer.write_text("# deterministic producer\n", encoding="utf-8")
            corpus_root = repository / "Conformance/corpora"
            (corpus_root / "mobile").mkdir(parents=True)
            (corpus_root / "index.json").write_bytes(
                canonical_json_bytes(
                    {
                        "schemaVersion": 1,
                        "coverage": "Conformance/corpora/coverage.json",
                        "domainCorpora": [
                            {
                                "id": "mobile",
                                "manifest": "Conformance/corpora/mobile/corpus.json",
                                "validatorExpectations": "Conformance/corpora/mobile/validator-expectations.json",
                            }
                        ],
                        "referencedCorpora": [],
                    }
                )
            )
            (corpus_root / "mobile/corpus.json").write_bytes(
                canonical_json_bytes(
                    {
                        "schemaVersion": 1,
                        "bases": [{"id": "base"}],
                        "cases": [{"id": "case"}],
                    }
                )
            )
            (corpus_root / "coverage.json").write_bytes(
                canonical_json_bytes(
                    {
                        "schemaVersion": 2,
                        "guides": {
                            "mobile": {
                                "structureDefinitions": {"Profile": "profile"},
                                "invariants": {"inv": ["case"]},
                                "sourceRules": {"rule": "boundary"},
                                "caseBoundaries": {"case": "boundary"},
                                "nonInvalidBoundaries": {},
                                "validatorLimitations": {},
                            }
                        },
                    }
                )
            )
            external = [
                {
                    "id": "accepted-fhir",
                    "files": [
                        {
                            "path": "resource.json",
                            "format": "fhir-json",
                            "sha256": "a" * 64,
                            "size": 42,
                        }
                    ],
                    "transitiveSha256": "b" * 64,
                },
                {
                    "id": "test-result",
                    "files": [
                        {
                            "path": "result.json",
                            "format": "test-attestation-v1",
                            "sha256": "c" * 64,
                            "size": 24,
                        }
                    ],
                    "transitiveSha256": "d" * 64,
                },
            ]
            report = {
                "kind": "grove-domain-fhir-validation",
                "schemaVersion": 1,
                "validator": {
                    "id": "fhir-validator",
                    "version": "6.10.2",
                    "sha256": "e" * 64,
                },
                "fhirPackageClosure": [
                    {
                        "id": "hl7.fhir.r4.core",
                        "version": "4.0.1",
                        "sha256": "9" * 64,
                    }
                ],
                "guides": [
                    {
                        "id": "mobile",
                        "packageId": "org.example.mobile",
                        "version": "0.1.0",
                        "sha256": "f" * 64,
                        "baseCount": 1,
                        "caseCount": 1,
                        "additionalValidCount": 0,
                        "warningCount": 0,
                    }
                ],
                "coverage": [
                    {
                        "id": "mobile",
                        "structureDefinitionCount": 1,
                        "invariantCount": 1,
                        "computableRuleCount": 1,
                        "invalidBoundaryCount": 1,
                        "nonInvalidBoundaryCount": 0,
                        "validatorLimitationCount": 0,
                    }
                ],
                "externalEvidence": {
                    "setCount": 2,
                    "fhirInputCount": 1,
                    "resourceCount": 1,
                    "warningCount": 0,
                    "sets": [
                        {
                            "id": "accepted-fhir",
                            "files": [
                                {
                                    "path": "resource.json",
                                    "sha256": "a" * 64,
                                    "size": 42,
                                    "resourceCount": 1,
                                }
                            ],
                        },
                        {
                            "id": "test-result",
                            "files": [
                                {
                                    "path": "result.json",
                                    "sha256": "c" * 64,
                                    "size": 24,
                                }
                            ],
                        },
                    ],
                },
            }
            source = repository / "domain.json"
            source.write_bytes(canonical_json_bytes(report))
            manifest = {
                "validationReports": [
                    {
                        "id": "domain-fhir-validation",
                        "path": "domain-fhir-validation.json",
                        "mediaType": "application/json",
                        "format": "domain-fhir-validation-v1",
                        "producer": "Scripts/validate-domain-fhir.py",
                    }
                ]
            }
            inputs = [
                {
                    "path": "Scripts/validate-domain-fhir.py",
                    "sha256": EVIDENCE.sha256_file(producer),
                    "size": producer.stat().st_size,
                }
            ]
            tools = [
                {
                    "id": "fhir-validator",
                    "kind": "jar",
                    "version": "6.10.2",
                    "sha256": "e" * 64,
                    "transitiveSha256": "1" * 64,
                },
                {
                    "id": "hl7.fhir.r4.core",
                    "kind": "fhir-package",
                    "version": "4.0.1",
                    "sha256": "9" * 64,
                    "transitiveSha256": "2" * 64,
                },
            ]
            packages = [
                {
                    "id": "mobile",
                    "packageId": "org.example.mobile",
                    "version": "0.1.0",
                    "sha256": "f" * 64,
                    "transitiveSha256": "3" * 64,
                }
            ]
            locked = EVIDENCE.collect_validation_reports(
                repository,
                evidence_root,
                manifest,
                inputs,
                tools,
                packages,
                external,
                {"domain-fhir-validation": source.resolve()},
                copy_reports=True,
            )
            self.assertEqual(locked[0]["sha256"], EVIDENCE.sha256_file(source))
            self.assertTrue(
                (evidence_root / "reports/domain-fhir-validation.json").is_file()
            )
            report["externalEvidence"]["sets"][0]["files"][0]["sha256"] = "0" * 64
            source.write_bytes(canonical_json_bytes(report))
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "file bytes have drifted"):
                EVIDENCE.collect_validation_reports(
                    repository,
                    evidence_root,
                    manifest,
                    inputs,
                    tools,
                    packages,
                    external,
                    {"domain-fhir-validation": source.resolve()},
                    copy_reports=True,
                )
            report["externalEvidence"]["sets"][0]["files"][0]["sha256"] = "a" * 64
            report["validator"]["sha256"] = "0" * 64
            source.write_bytes(canonical_json_bytes(report))
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "Validator identity"):
                EVIDENCE.collect_validation_reports(
                    repository,
                    evidence_root,
                    manifest,
                    inputs,
                    tools,
                    packages,
                    external,
                    {"domain-fhir-validation": source.resolve()},
                    copy_reports=True,
                )

    def test_composed_attestation_uses_the_final_producer_proposal(self) -> None:
        evidence_set = {
            "id": "reader-result",
            "implementation": "current-reader",
            "proposals": ["questionnaire", "mobile", "reader"],
        }
        declaration = {
            "testGroup": "reader-evidence",
        }
        implementation = {"commit": "1" * 40}
        proposal = {
            "tests": [
                {
                    "group": "reader-evidence",
                    "cwd": ".",
                    "argv": ["./Scripts/run-reader.sh"],
                }
            ]
        }
        attestation = {
            "kind": "grove-fhir-test-attestation",
            "schemaVersion": 1,
            "artifactId": "reader-result",
            "implementation": "current-reader",
            "producerProposal": "reader",
            "sourceCommit": "1" * 40,
            "testGroup": "reader-evidence",
            "commands": [{"cwd": ".", "argv": ["./Scripts/run-reader.sh"]}],
            "result": "passed",
            "inputs": [],
        }
        EVIDENCE._validate_attestation(
            canonical_json_bytes(attestation),
            declaration,
            evidence_set,
            implementation,
            proposal,
            [],
        )
        attestation["producerProposal"] = "questionnaire"
        with self.assertRaisesRegex(EVIDENCE.EvidenceError, "provenance"):
            EVIDENCE._validate_attestation(
                canonical_json_bytes(attestation),
                declaration,
                evidence_set,
                implementation,
                proposal,
                [],
            )
    def test_baseline_update_is_explicit_and_ordinary_comparison_fails_stale(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            (repository / "Conformance").mkdir()
            manifest = {
                "toolchain": "Conformance/toolchain.json",
                "integrationSources": "Integration/sources.json",
                "semanticBaseline": "Conformance/semantic-baseline.json",
            }
            (repository / "Integration").mkdir()
            self._json(repository / "Conformance/evidence.json", manifest)
            self._json(repository / "Conformance/evidence.schema.json", {})
            self._json(repository / "Conformance/toolchain.json", {})
            self._json(repository / "Integration/sources.json", {})
            self._json(repository / "package.json", {})
            self._json(
                repository / "Conformance/semantic-baseline.json",
                {"kind": "grove-fhir-semantic-baseline", "schemaVersion": 1, "packages": []},
            )
            snapshot = self._minimal_snapshot()

            def fake_packages(
                _repository: Path,
                evidence_root: Path,
                _manifest: object,
                _toolchain: object,
                _overrides: object,
                copy_packages: bool,
            ) -> list[dict[str, object]]:
                self.assertTrue(copy_packages)
                target = evidence_root / "snapshots/mobile.json"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(canonical_json_bytes(snapshot))
                return [
                    {
                        "id": "mobile",
                        "packageId": "org.example.mobile",
                        "version": "0.1.0",
                        "semanticSnapshot": "snapshots/mobile.json",
                    }
                ]

            with (
                patch.object(EVIDENCE, "validate_json_schema"),
                patch.object(EVIDENCE, "validate_toolchain"),
                patch.object(EVIDENCE, "validate_semantic_baseline_inputs"),
                patch.object(EVIDENCE, "collect_packages", side_effect=fake_packages),
            ):
                updated = EVIDENCE.update_semantic_baseline(
                    repository,
                    repository / "Conformance/evidence.json",
                    repository / "Conformance/evidence.schema.json",
                )
            self.assertEqual(updated["packages"][0]["id"], "mobile")
            baseline = repository / "Conformance/semantic-baseline.json"
            self.assertEqual(baseline.read_bytes(), canonical_json_bytes(updated))
            baseline.write_bytes(
                canonical_json_bytes(
                    {"kind": "grove-fhir-semantic-baseline", "schemaVersion": 1, "packages": []}
                )
            )
            evidence_root = repository / "evidence"
            (evidence_root / "snapshots").mkdir(parents=True)
            (evidence_root / "snapshots/mobile.json").write_bytes(
                canonical_json_bytes(snapshot)
            )
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "does not byte-match"):
                EVIDENCE.collect_semantic_evidence(
                    repository,
                    evidence_root,
                    manifest,
                    fake_packages(repository, evidence_root, {}, {}, None, True),
                    EVIDENCE.ZERO_COMMIT,
                    REVISION,
                    write_reports=True,
                )

    @staticmethod
    def _json(path: Path, value: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(canonical_json_bytes(value))

    @staticmethod
    def _minimal_snapshot() -> dict[str, object]:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "package"
            package.mkdir()
            (package / "package.json").write_text(
                json.dumps(
                    {
                        "name": "org.example.mobile",
                        "version": "0.1.0",
                        "canonical": "https://example.org/mobile",
                        "fhirVersions": ["4.0.1"],
                        "dependencies": {},
                    }
                ),
                encoding="utf-8",
            )
            (package / ".index.json").write_text('{"index-version":2,"files":[]}\n')
            return EVIDENCE.create_snapshot(package)

    def _site_fixture(self, root: Path) -> tuple[Path, Path, Path]:
        root.mkdir(parents=True, exist_ok=True)
        evidence = root / "evidence"
        site = root / "site"
        evidence.mkdir()
        site.mkdir()
        for path, data in {
            "evidence.json": b"{}\n",
            "evidence.schema.json": b"{}\n",
            "toolchain.json": b"{}\n",
            "reports/semantic-diff.json": b'{"packages":[]}\n',
            "reports/semantic-diff.md": b"# No changes\n",
        }.items():
            target = evidence / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        package = evidence / "packages/mobile/package.tgz"
        package.parent.mkdir(parents=True)
        self._package(package)
        public_package = site / "fhir/mobile/ci-build/package.tgz"
        public_package.parent.mkdir(parents=True)
        shutil.copyfile(package, public_package)
        lock = {
            "kind": "grove-fhir-conformance-evidence-lock",
            "schemaVersion": 1,
            "sourceRevision": REVISION,
            "sourceDateEpoch": EPOCH,
            "files": EVIDENCE.output_file_records(evidence),
            "packages": [
                {
                    "id": "mobile",
                    "declaredPath": ".build/pages/fhir/mobile/ci-build/package.tgz",
                    "packageId": "org.example.mobile",
                    "version": "0.1.0",
                    "canonical": "https://example.org/mobile",
                    "fhirVersion": "4.0.1",
                    "dependencies": [],
                    "sha256": EVIDENCE.sha256_file(package),
                    "size": package.stat().st_size,
                }
            ],
        }
        lock["lockDigest"] = EVIDENCE.semantic_sha256(lock)
        EVIDENCE.write_json(evidence / EVIDENCE.LOCK_FILENAME, lock)
        archive = root / EVIDENCE.ARCHIVE_FILENAME
        EVIDENCE.create_deterministic_archive(evidence, archive, EPOCH)
        EVIDENCE.inject_pages(evidence, archive, site)
        return evidence, archive, site

    @staticmethod
    def _package(path: Path) -> None:
        metadata = canonical_json_bytes(
            {
                "name": "org.example.mobile",
                "version": "0.1.0",
                "canonical": "https://example.org/mobile",
                "fhirVersions": ["4.0.1"],
                "dependencies": {},
            }
        )
        with tarfile.open(path, "w:gz") as archive:
            member = tarfile.TarInfo("package/package.json")
            member.size = len(metadata)
            archive.addfile(member, io.BytesIO(metadata))


if __name__ == "__main__":
    unittest.main()
