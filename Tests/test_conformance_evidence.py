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
    def test_documented_local_build_disables_python_bytecode_first(self) -> None:
        documentation = (ROOT / "Conformance/README.md").read_text(encoding="utf-8")
        command_block = documentation.split("```console", 1)[1].split("```", 1)[0]
        commands = [line for line in command_block.splitlines() if line.strip()]
        self.assertEqual(commands[0], "export PYTHONDONTWRITEBYTECODE=1")
        self.assertTrue(any(line.startswith("python3 ") for line in commands[1:]))

    def test_input_inventory_is_exactly_bound_to_git_head_and_gitlinks(self) -> None:
        def git(repository: Path, *arguments: str) -> str:
            result = subprocess.run(
                ["git", *arguments],
                cwd=repository,
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip()

        def write(path: Path, value: str) -> None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value, encoding="utf-8")

        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            upstream = fixture / "source-upstream"
            upstream.mkdir()
            git(upstream, "init", "--quiet")
            git(upstream, "config", "user.name", "Conformance Test")
            git(upstream, "config", "user.email", "test@example.org")
            git(upstream, "config", "commit.gpgsign", "false")
            package_manifest = upstream / "Project/Package.resolved"
            write(package_manifest, '{"version":1}\n')
            git(upstream, "add", "Project/Package.resolved")
            git(upstream, "commit", "--quiet", "-m", "Pin package")
            source_commit = git(upstream, "rev-parse", "HEAD")

            repository = fixture / "repository"
            repository.mkdir()
            repository = repository.resolve()
            git(repository, "init", "--quiet")
            git(repository, "config", "user.name", "Conformance Test")
            git(repository, "config", "user.email", "test@example.org")
            git(repository, "config", "commit.gpgsign", "false")
            git(
                repository,
                "-c",
                "protocol.file.allow=always",
                "submodule",
                "add",
                "--quiet",
                str(upstream),
                "Integration/Sources/External",
            )
            write(
                repository / ".gitignore",
                "__pycache__/\n*.ignored\n**/ignored.fsh\n",
            )
            tracked_script = repository / "Scripts/tracked.py"
            write(tracked_script, "VALUE = 1\n")
            write(repository / "Conformance/corpora/case.json", "{}\n")
            write(repository / "guide/ig.ini", "[IG]\n")
            write(repository / "guide/sushi-config.yaml", "id: example\n")
            write(repository / "guide/input/fsh/profile.fsh", "Profile: Example\n")
            git(repository, "add", ".")
            git(repository, "commit", "--quiet", "-m", "Fixture")

            manifest = {
                "trackedInputs": [
                    ".gitignore",
                    ".gitmodules",
                    "Scripts/tracked.py",
                ],
                "trackedInputRoots": ["Scripts"],
                "guides": [{"id": "guide", "source": "guide"}],
                "corpora": [
                    {
                        "id": "corpus",
                        "root": "Conformance/corpora",
                    }
                ],
                "implementations": [
                    {
                        "id": "implementation",
                        "source": "external",
                        "provenance": {
                            "resolvedPackages": [
                                {"manifest": "Project/Package.resolved"}
                            ]
                        },
                    }
                ],
            }
            integration = {
                "schemaVersion": 3,
                "sources": [
                    {
                        "id": "external",
                        "path": "Integration/Sources/External",
                        "commit": source_commit,
                    }
                ],
                "proposals": [],
            }

            expected = {
                ".gitignore",
                ".gitmodules",
                "Conformance/corpora/case.json",
                "Integration/Sources/External/Project/Package.resolved",
                "Scripts/tracked.py",
                "guide/ig.ini",
                "guide/input/fsh/profile.fsh",
                "guide/sushi-config.yaml",
            }
            actual = {
                path.relative_to(repository).as_posix()
                for path in EVIDENCE.collect_input_paths(
                    repository, manifest, integration
                )
            }
            self.assertEqual(actual, expected)

            python_cache = repository / "Scripts/__pycache__/tracked.cpython-313.pyc"
            write(python_cache, "derived cache bytes")
            with self.assertRaisesRegex(
                EVIDENCE.EvidenceError, "untracked-or-ignored"
            ):
                EVIDENCE.collect_input_paths(repository, manifest, integration)
            python_cache.unlink()

            extras = (
                ("Scripts/untracked.py", "untracked script"),
                ("Scripts/local.ignored", "ignored script input"),
                ("Conformance/corpora/untracked.json", "untracked corpus"),
                ("Conformance/corpora/local.ignored", "ignored corpus"),
                ("guide/input/fsh/untracked.fsh", "untracked guide FSH"),
                ("guide/input/fsh/ignored.fsh", "ignored guide FSH"),
            )
            for relative, label in extras:
                extra = repository / relative
                write(extra, "unexpected\n")
                with self.subTest(label=label), self.assertRaisesRegex(
                    EVIDENCE.EvidenceError, "untracked-or-ignored"
                ):
                    EVIDENCE.collect_input_paths(repository, manifest, integration)
                extra.unlink()

            guide_link = repository / "guide/input/fsh/linked.fsh"
            guide_link.symlink_to("profile.fsh")
            with self.assertRaisesRegex(
                EVIDENCE.EvidenceError, "symlink|non-regular"
            ):
                EVIDENCE.collect_input_paths(repository, manifest, integration)
            guide_link.unlink()

            checked_out_manifest = (
                repository
                / "Integration/Sources/External/Project/Package.resolved"
            )
            checked_out_manifest.write_text('{"version":2}\n', encoding="utf-8")
            with self.assertRaisesRegex(
                EVIDENCE.EvidenceError, "resolved package manifest working-tree bytes"
            ):
                EVIDENCE.collect_input_paths(repository, manifest, integration)
            checked_out_manifest.write_text('{"version":1}\n', encoding="utf-8")

            checked_out_manifest.write_text('{"version":2}\n', encoding="utf-8")
            git(
                repository / "Integration/Sources/External",
                "add",
                "Project/Package.resolved",
            )
            with self.assertRaisesRegex(
                EVIDENCE.EvidenceError, "not exact in the pinned source index"
            ):
                EVIDENCE.collect_input_paths(repository, manifest, integration)
            git(
                repository / "Integration/Sources/External",
                "reset",
                "--quiet",
                "HEAD",
                "--",
                "Project/Package.resolved",
            )
            checked_out_manifest.write_text('{"version":1}\n', encoding="utf-8")

            source_checkout = repository / "Integration/Sources/External"
            checked_out_manifest.write_text('{"version":2}\n', encoding="utf-8")
            git(source_checkout, "add", "Project/Package.resolved")
            git(source_checkout, "config", "user.name", "Conformance Test")
            git(source_checkout, "config", "user.email", "test@example.org")
            git(source_checkout, "config", "commit.gpgsign", "false")
            git(source_checkout, "commit", "--quiet", "-m", "Wrong checkout")
            with self.assertRaisesRegex(
                EVIDENCE.EvidenceError, "checkout HEAD does not match"
            ):
                EVIDENCE.collect_input_paths(repository, manifest, integration)
            git(source_checkout, "checkout", "--quiet", "--detach", source_commit)

            tracked_script.write_text("VALUE = 2\n", encoding="utf-8")
            with self.assertRaisesRegex(
                EVIDENCE.EvidenceError, "working-tree bytes"
            ):
                EVIDENCE.collect_input_paths(repository, manifest, integration)
            tracked_script.write_text("VALUE = 1\n", encoding="utf-8")

            tracked_script.chmod(0o755)
            with self.assertRaisesRegex(
                EVIDENCE.EvidenceError, "working-tree mode"
            ):
                EVIDENCE.collect_input_paths(repository, manifest, integration)
            tracked_script.chmod(0o644)

            tracked_script.write_text("VALUE = 3\n", encoding="utf-8")
            git(repository, "add", "Scripts/tracked.py")
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "Git index"):
                EVIDENCE.collect_input_paths(repository, manifest, integration)

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

        with tempfile.TemporaryDirectory() as directory:
            toolchain = json.loads((ROOT / "Conformance/toolchain.json").read_text())
            toolchain["runtimes"]["java"].pop("setupVersion")
            invalid = Path(directory) / "invalid-toolchain.json"
            invalid.write_text(json.dumps(toolchain), encoding="utf-8")
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
        self.assertIn("setupVersion", result.stderr)

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

    def test_bundler_runtime_version_accepts_only_exact_cli_forms(self) -> None:
        toolchain = json.loads((ROOT / "Conformance/toolchain.json").read_text())

        def collect(bundler_output: str) -> list[dict[str, object]]:
            runtimes = toolchain["runtimes"]
            outputs = {
                "node": f"v{runtimes['node']['version']}",
                "npm": runtimes["npm"]["version"],
                "python": f"Python {runtimes['python']['version']}",
                "ruby": f"ruby {runtimes['ruby']['version']} (revision exact)",
                "bundler": bundler_output,
                "java": (
                    f"    java.runtime.version = {runtimes['java']['version']}\n"
                    "    java.vendor = Eclipse Adoptium"
                ),
            }

            def command_output(
                _command: list[str], label: str, **_kwargs: object
            ) -> str:
                return outputs[label]

            with patch.object(EVIDENCE, "_command_output", side_effect=command_output):
                return EVIDENCE.collect_runtime_environment(toolchain)

        for output in ("4.0.16", "Bundler version 4.0.16"):
            with self.subTest(output=output):
                bundler = next(
                    item for item in collect(output) if item["id"] == "bundler"
                )
                self.assertEqual(bundler["version"], "4.0.16")

        rejected = (
            "v4.0.16",
            "bundler 4.0.16",
            "Bundler version 4.0.16 extra",
            "4.0.16-beta",
            "4",
            "4.0.16.",
            " 4.0.16",
            "4.0.16 ",
            "\x1b[32m4.0.16\x1b[0m",
            "4.0.16\nBundler version 4.0.16",
            "Bundler version 4.0.16\n4.0.16",
        )
        for output in rejected:
            with self.subTest(output=output):
                with self.assertRaisesRegex(
                    EVIDENCE.EvidenceError,
                    "unable to parse bundler runtime version",
                ):
                    collect(output)

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

    def test_archive_sidecar_symlink_never_overwrites_its_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root / "evidence"
            evidence.mkdir()
            (evidence / "exact.txt").write_text("exact\n", encoding="utf-8")
            archive = root / EVIDENCE.ARCHIVE_FILENAME
            victim = root / "victim.txt"
            victim.write_text("sentinel\n", encoding="utf-8")
            sidecar = Path(f"{archive}.sha256")
            sidecar.symlink_to(victim)

            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "checksum path is unsafe"):
                EVIDENCE.create_deterministic_archive(evidence, archive, EPOCH)
            self.assertEqual(victim.read_text(encoding="utf-8"), "sentinel\n")
            self.assertFalse(archive.exists())

            sidecar.unlink()
            sidecar.write_text("stale\n", encoding="utf-8")
            EVIDENCE.create_deterministic_archive(evidence, archive, EPOCH)
            self.assertFalse(sidecar.is_symlink())
            self.assertEqual(
                sidecar.read_text(encoding="utf-8"),
                f"{EVIDENCE.sha256_file(archive)}  {archive.name}\n",
            )

    def test_archive_and_external_evidence_reject_nonportable_text(self) -> None:
        declaration = {"path": "resource.json", "format": "fhir-json"}
        evidence_set = {"id": "example"}
        for text, expected in (
            ("Current: /Users/runner/secret", "machine-local"),
            (r"Cache: C:\Users\runner\.fhir", "machine-local"),
            ("\x1b[31mSuccess\x1b[0m", "ANSI"),
        ):
            with self.subTest(text=text), self.assertRaisesRegex(
                EVIDENCE.EvidenceError, expected
            ):
                EVIDENCE._validate_external_file(
                    canonical_json_bytes(
                        {"resourceType": "Observation", "note": [{"text": text}]}
                    ),
                    declaration,
                    evidence_set,
                    {},
                    {},
                )
        EVIDENCE._validate_external_file(
            canonical_json_bytes(
                {
                    "resourceType": "Observation",
                    "note": [
                        {"text": "https://example.org/home/runner/reference"}
                    ],
                }
            ),
            declaration,
            evidence_set,
            {},
            {},
        )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root / "evidence"
            evidence.mkdir()
            payload = b'{"path":"/private/tmp/validator-output"}\n'
            (evidence / "report.json").write_bytes(payload)
            archive = root / EVIDENCE.ARCHIVE_FILENAME
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "machine-local"):
                EVIDENCE.create_deterministic_archive(evidence, archive, EPOCH)

            with archive.open("wb") as raw:
                with EVIDENCE.gzip.GzipFile(
                    filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=EPOCH
                ) as compressed:
                    with tarfile.open(
                        fileobj=compressed, mode="w", format=tarfile.USTAR_FORMAT
                    ) as bundle:
                        member = tarfile.TarInfo(
                            f"{EVIDENCE.ARCHIVE_PREFIX}/report.json"
                        )
                        member.size = len(payload)
                        member.mode = 0o644
                        member.mtime = EPOCH
                        bundle.addfile(member, io.BytesIO(payload))
            Path(f"{archive}.sha256").write_text(
                f"{EVIDENCE.sha256_file(archive)}  {archive.name}\n",
                encoding="utf-8",
            )
            self.assertTrue(
                any(
                    "machine-local" in failure
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

    def test_pages_parent_symlink_is_rejected_without_external_deletion(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence, archive, site = self._site_fixture(root / "fixture")
            external = root / "external"
            external.mkdir()
            shutil.move(str(site / "conformance"), str(external / "conformance"))
            (site / "conformance").symlink_to(
                external / "conformance", target_is_directory=True
            )
            sentinel = external / "conformance/ci-build/sentinel.txt"
            sentinel.write_text("do not delete\n", encoding="utf-8")

            failures = EVIDENCE.verify_site_evidence(site, REVISION)
            self.assertTrue(any("symlink" in failure for failure in failures))
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "symlink"):
                EVIDENCE.inject_pages(evidence, archive, site)
            self.assertEqual(
                sentinel.read_text(encoding="utf-8"), "do not delete\n"
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
                    "classification": "accepted-contract",
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
                    "id": "legacy-fhir",
                    "classification": "legacy-candidate",
                    "files": [
                        {
                            "path": "legacy.json",
                            "format": "fhir-json",
                            "sha256": "1" * 64,
                            "size": 84,
                        }
                    ],
                    "expectedUnknownExtensions": [
                        {
                            "path": "legacy.json",
                            "expression": "Observation.extension[0]",
                            "url": "https://legacy.example/fhir/extension",
                            "valueField": "valueString",
                        }
                    ],
                    "transitiveSha256": "2" * 64,
                },
                {
                    "id": "test-result",
                    "classification": "accepted-contract",
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
                    "setCount": 3,
                    "fhirInputCount": 2,
                    "resourceCount": 2,
                    "warningCount": 0,
                    "expectedErrorCount": 1,
                    "sets": [
                        {
                            "id": "accepted-fhir",
                            "validationScope": "accepted-package-closure",
                            "expectedErrorCount": 0,
                            "files": [
                                {
                                    "path": "resource.json",
                                    "sha256": "a" * 64,
                                    "size": 42,
                                    "resourceCount": 1,
                                    "expectedErrorCount": 0,
                                }
                            ],
                        },
                        {
                            "id": "legacy-fhir",
                            "validationScope": "r4-core",
                            "expectedErrorCount": 1,
                            "files": [
                                {
                                    "path": "legacy.json",
                                    "sha256": "1" * 64,
                                    "size": 84,
                                    "resourceCount": 1,
                                    "expectedErrorCount": 1,
                                }
                            ],
                        },
                        {
                            "id": "test-result",
                            "validationScope": "none",
                            "expectedErrorCount": 0,
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
            base_input_closure = locked[0]["inputClosureSha256"]
            questionnaire_inputs = (
                "questionnaire/input/fsh/profiles.fsh",
                "questionnaire/fixtures/validator/cases.json",
                "questionnaire/fixtures/pairs/cases.json",
            )
            for index, path in enumerate(questionnaire_inputs, start=4):
                first_inputs = inputs + [
                    {
                        "path": path,
                        "sha256": str(index) * 64,
                        "size": index,
                    }
                ]
                first = EVIDENCE.collect_validation_reports(
                    repository,
                    evidence_root,
                    manifest,
                    first_inputs,
                    tools,
                    packages,
                    external,
                    {"domain-fhir-validation": source.resolve()},
                    copy_reports=True,
                )
                self.assertNotEqual(
                    first[0]["inputClosureSha256"], base_input_closure
                )
                changed_inputs = copy.deepcopy(first_inputs)
                changed_inputs[-1]["sha256"] = "f" * 64
                changed = EVIDENCE.collect_validation_reports(
                    repository,
                    evidence_root,
                    manifest,
                    changed_inputs,
                    tools,
                    packages,
                    external,
                    {"domain-fhir-validation": source.resolve()},
                    copy_reports=True,
                )
                self.assertNotEqual(
                    changed[0]["inputClosureSha256"],
                    first[0]["inputClosureSha256"],
                )
            report["externalEvidence"]["sets"][1]["expectedErrorCount"] = True
            source.write_bytes(canonical_json_bytes(report))
            with self.assertRaisesRegex(
                EVIDENCE.EvidenceError, "external validation contract has drifted"
            ):
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
            report["externalEvidence"]["sets"][1]["expectedErrorCount"] = 1
            report["externalEvidence"]["sets"][1]["files"][0][
                "expectedErrorCount"
            ] = True
            source.write_bytes(canonical_json_bytes(report))
            with self.assertRaisesRegex(
                EVIDENCE.EvidenceError, "resource or expected error count is invalid"
            ):
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
            report["externalEvidence"]["sets"][1]["files"][0][
                "expectedErrorCount"
            ] = 1
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

    def test_implementation_profile_claims_are_owned_and_producer_only(self) -> None:
        manifest = json.loads((ROOT / "Conformance/evidence.json").read_text())
        EVIDENCE.validate_implementation_profile_claims(manifest)

        consumer_claim = copy.deepcopy(manifest)
        firebase = next(
            item
            for item in consumer_claim["implementations"]
            if item["id"] == "my-heart-counts-firebase"
        )
        firebase["packages"] = ["mobile"]
        with self.assertRaisesRegex(EVIDENCE.EvidenceError, "non-producer"):
            EVIDENCE.validate_implementation_profile_claims(consumer_claim)

        unowned_claim = copy.deepcopy(manifest)
        android = next(
            item
            for item in unowned_claim["implementations"]
            if item["id"] == "my-heart-counts-android"
        )
        android["profiles"].append("https://example.org/StructureDefinition/unowned")
        with self.assertRaisesRegex(EVIDENCE.EvidenceError, "unowned"):
            EVIDENCE.validate_implementation_profile_claims(unowned_claim)

        missing_owner = copy.deepcopy(manifest)
        grove = next(
            item
            for item in missing_owner["implementations"]
            if item["id"] == "grove-healthkit"
        )
        grove["packages"].remove("healthkit")
        with self.assertRaisesRegex(EVIDENCE.EvidenceError, "owners are not exact"):
            EVIDENCE.validate_implementation_profile_claims(missing_owner)

    def test_manifest_has_the_reviewed_producer_profile_closures(self) -> None:
        manifest = json.loads((ROOT / "Conformance/evidence.json").read_text())
        implementations = {
            item["id"]: item for item in manifest["implementations"]
        }
        mobile = [
            "https://schmiedmayerlab.github.io/grove-fhir/fhir/mobile/StructureDefinition/grove-application-device",
            "https://schmiedmayerlab.github.io/grove-fhir/fhir/mobile/StructureDefinition/grove-mobile-conversion-provenance",
            "https://schmiedmayerlab.github.io/grove-fhir/fhir/mobile/StructureDefinition/grove-mobile-observation",
            "https://schmiedmayerlab.github.io/grove-fhir/fhir/mobile/StructureDefinition/grove-mobile-step-count",
            "https://schmiedmayerlab.github.io/grove-fhir/fhir/mobile/StructureDefinition/grove-recording-device",
            "https://schmiedmayerlab.github.io/grove-fhir/fhir/mobile/StructureDefinition/grove-recording-method",
        ]
        grove = implementations["grove-healthkit"]
        self.assertEqual(grove["direction"], "produce")
        self.assertEqual(grove["packages"], ["mobile", "healthkit"])
        self.assertEqual(
            grove["profiles"],
            mobile
            + [
                "https://schmiedmayerlab.github.io/grove-fhir/fhir/healthkit/StructureDefinition/healthkit-observation"
            ],
        )
        self.assertIn("historical decoding is evidenced separately", grove["purpose"])
        android = implementations["my-heart-counts-android"]
        self.assertEqual(android["packages"], ["mobile", "health-connect"])
        self.assertEqual(
            android["profiles"],
            mobile
            + [
                "https://schmiedmayerlab.github.io/grove-fhir/fhir/health-connect/StructureDefinition/health-connect-conversion-provenance",
                "https://schmiedmayerlab.github.io/grove-fhir/fhir/health-connect/StructureDefinition/health-connect-observation",
            ],
        )
        firebase = implementations["my-heart-counts-firebase"]
        self.assertEqual(firebase["direction"], "consume")
        self.assertEqual(firebase["packages"], [])
        self.assertEqual(firebase["profiles"], [])

    def test_generated_fhir_profile_coverage_is_exact_and_inherited(self) -> None:
        mobile_canonical = "https://example.org/fhir/mobile"
        adapter_canonical = "https://example.org/fhir/adapter"
        base = f"{mobile_canonical}/StructureDefinition/mobile-observation"
        extension = f"{mobile_canonical}/StructureDefinition/recording-method"
        child = f"{adapter_canonical}/StructureDefinition/adapter-observation"

        def definition(
            canonical: str, resource_type: str, base_definition: str
        ) -> dict[str, object]:
            return {
                "resourceType": "StructureDefinition",
                "url": canonical,
                "version": "1.0.0",
                "type": resource_type,
                "baseDefinition": base_definition,
            }

        manifest = {
            "guides": [
                {
                    "id": "mobile",
                    "packageId": "org.example.mobile",
                    "version": "1.0.0",
                    "canonical": mobile_canonical,
                    "structureDefinitions": [base, extension],
                },
                {
                    "id": "adapter",
                    "packageId": "org.example.adapter",
                    "version": "1.0.0",
                    "canonical": adapter_canonical,
                    "structureDefinitions": [child],
                },
            ],
            "implementations": [
                {
                    "id": "producer",
                    "direction": "produce",
                    "packages": ["mobile", "adapter"],
                    "profiles": [base, extension, child],
                },
                {
                    "id": "consumer",
                    "direction": "consume",
                    "packages": [],
                    "profiles": [],
                },
            ],
        }
        packages = [
            {"id": "mobile", "semanticSnapshot": "snapshots/mobile.json"},
            {"id": "adapter", "semanticSnapshot": "snapshots/adapter.json"},
        ]
        external = [
            {
                "id": "producer-resources",
                "implementation": "producer",
                "path": "implementations/producer/producer-resources",
                "files": [{"path": "observation.json", "format": "fhir-json"}],
            }
        ]
        resource = {
            "resourceType": "Observation",
            "meta": {"profile": [f"{child}|1.0.0"]},
            "extension": [{"url": extension, "valueString": "automatic"}],
        }

        def snapshot(
            package_id: str,
            canonical: str,
            definitions: dict[str, dict[str, object]],
        ) -> dict[str, object]:
            return {
                "package": {
                    "name": package_id,
                    "version": "1.0.0",
                    "canonical": canonical,
                },
                "structureDefinitions": {
                    url: {"resource": value} for url, value in definitions.items()
                },
            }

        with tempfile.TemporaryDirectory() as directory:
            evidence_root = Path(directory)
            mobile_snapshot = snapshot(
                "org.example.mobile",
                mobile_canonical,
                {
                    base: definition(
                        base,
                        "Observation",
                        "http://hl7.org/fhir/StructureDefinition/Observation",
                    ),
                    extension: definition(
                        extension,
                        "Extension",
                        "http://hl7.org/fhir/StructureDefinition/Extension",
                    ),
                },
            )
            adapter_snapshot = snapshot(
                "org.example.adapter",
                adapter_canonical,
                {child: definition(child, "Observation", f"{base}|1.0.0")},
            )
            self._json(evidence_root / "snapshots/mobile.json", mobile_snapshot)
            self._json(evidence_root / "snapshots/adapter.json", adapter_snapshot)
            resource_path = (
                evidence_root
                / "implementations/producer/producer-resources/observation.json"
            )
            self._json(resource_path, resource)

            EVIDENCE.validate_implementation_profile_coverage(
                evidence_root, manifest, packages, external
            )

            missing_base = copy.deepcopy(manifest)
            missing_base["implementations"][0]["profiles"].remove(base)
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "undeclared"):
                EVIDENCE.validate_implementation_profile_coverage(
                    evidence_root, missing_base, packages, external
                )

            missing_extension_claim = copy.deepcopy(manifest)
            missing_extension_claim["implementations"][0]["profiles"].remove(extension)
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "undeclared"):
                EVIDENCE.validate_implementation_profile_coverage(
                    evidence_root, missing_extension_claim, packages, external
                )

            no_extension_resource = copy.deepcopy(resource)
            no_extension_resource.pop("extension")
            self._json(resource_path, no_extension_resource)
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "unexercised"):
                EVIDENCE.validate_implementation_profile_coverage(
                    evidence_root, manifest, packages, external
                )

            wrong_resource_type = copy.deepcopy(resource)
            wrong_resource_type["resourceType"] = "Patient"
            self._json(resource_path, wrong_resource_type)
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "expected 'Observation'"):
                EVIDENCE.validate_implementation_profile_coverage(
                    evidence_root, manifest, packages, external
                )

            wrong_profile_version = copy.deepcopy(resource)
            wrong_profile_version["meta"]["profile"] = [f"{child}|9.9.9"]
            self._json(resource_path, wrong_profile_version)
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "version '9.9.9'"):
                EVIDENCE.validate_implementation_profile_coverage(
                    evidence_root, manifest, packages, external
                )

            profile_fragment = copy.deepcopy(resource)
            profile_fragment["meta"]["profile"] = [f"{child}#other"]
            self._json(resource_path, profile_fragment)
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "undefined owned"):
                EVIDENCE.validate_implementation_profile_coverage(
                    evidence_root, manifest, packages, external
                )

            altered_extension = copy.deepcopy(resource)
            altered_extension["extension"][0]["url"] = f"{extension}|1.0.0"
            self._json(resource_path, altered_extension)
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "undefined owned"):
                EVIDENCE.validate_implementation_profile_coverage(
                    evidence_root, manifest, packages, external
                )

            undefined_profile = copy.deepcopy(resource)
            undefined_profile["meta"]["profile"].append(
                f"{mobile_canonical}/StructureDefinition/not-declared"
            )
            self._json(resource_path, undefined_profile)
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "undefined owned"):
                EVIDENCE.validate_implementation_profile_coverage(
                    evidence_root, manifest, packages, external
                )

            self._json(resource_path, resource)
            missing_owned_base = copy.deepcopy(adapter_snapshot)
            missing_owned_base["structureDefinitions"][child]["resource"][
                "baseDefinition"
            ] = f"{mobile_canonical}/StructureDefinition/not-declared"
            self._json(
                evidence_root / "snapshots/adapter.json", missing_owned_base
            )
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "unresolved owned"):
                EVIDENCE.validate_implementation_profile_coverage(
                    evidence_root, manifest, packages, external
                )

            wrong_base_version = copy.deepcopy(adapter_snapshot)
            wrong_base_version["structureDefinitions"][child]["resource"][
                "baseDefinition"
            ] = f"{base}|9.9.9"
            self._json(
                evidence_root / "snapshots/adapter.json", wrong_base_version
            )
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "version '9.9.9'"):
                EVIDENCE.validate_implementation_profile_coverage(
                    evidence_root, manifest, packages, external
                )

            self._json(evidence_root / "snapshots/adapter.json", adapter_snapshot)
            cyclic_mobile = copy.deepcopy(mobile_snapshot)
            cyclic_mobile["structureDefinitions"][base]["resource"][
                "baseDefinition"
            ] = child
            self._json(evidence_root / "snapshots/mobile.json", cyclic_mobile)
            with self.assertRaisesRegex(EVIDENCE.EvidenceError, "cycle"):
                EVIDENCE.validate_implementation_profile_coverage(
                    evidence_root, manifest, packages, external
                )

    def test_profile_coverage_gate_runs_during_build_and_replay(self) -> None:
        manifest = {
            "toolchain": "Conformance/toolchain.json",
            "semanticBaseline": "Conformance/semantic-baseline.json",
            "integrationSources": "Integration/sources.json",
            "pathMatrix": [],
            "pathMatrixIgnored": [],
        }
        packages = [{"id": "mobile", "inputMode": "declared"}]
        external = [{"id": "producer-resources"}]
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory) / "repository"
            evidence_root = Path(directory) / "evidence"
            repository.mkdir()
            evidence_root.mkdir()
            with (
                patch.object(EVIDENCE, "collect_inputs", return_value=[]),
                patch.object(EVIDENCE, "collect_runtime_environment", return_value=[]),
                patch.object(EVIDENCE, "collect_language_packages", return_value=[]),
                patch.object(EVIDENCE, "collect_tool_artifacts", return_value=[]),
                patch.object(EVIDENCE, "collect_proposals", return_value=[]),
                patch.object(EVIDENCE, "collect_gitlinks", return_value=[]),
                patch.object(EVIDENCE, "collect_resolved_packages", return_value=[]),
                patch.object(EVIDENCE, "_write_supporting_evidence"),
                patch.object(EVIDENCE, "collect_packages", return_value=packages),
                patch.object(EVIDENCE, "collect_semantic_evidence", return_value={}),
                patch.object(EVIDENCE, "collect_external_evidence", return_value=external),
                patch.object(EVIDENCE, "collect_validation_reports", return_value=[]),
                patch.object(EVIDENCE, "collect_corpora", return_value=[]),
                patch.object(EVIDENCE, "output_file_records", return_value=[]),
                patch.object(EVIDENCE, "_toolchain_transitive_hash", return_value="hash"),
                patch.object(EVIDENCE, "validate_implementation_profile_coverage") as gate,
            ):
                EVIDENCE.build_lock(
                    repository,
                    evidence_root,
                    manifest,
                    {},
                    {},
                    REVISION,
                    EPOCH,
                    EVIDENCE.ZERO_COMMIT,
                )
            gate.assert_called_once_with(
                evidence_root, manifest, packages, external
            )

            self._json(repository / "Conformance/evidence.json", manifest)
            self._json(repository / "Conformance/toolchain.json", {})
            self._json(repository / "Conformance/semantic-baseline.json", {})
            self._json(repository / "Integration/sources.json", {})
            self._json(repository / "package.json", {})
            lock = {
                "sourceRevision": REVISION,
                "sourceDateEpoch": EPOCH,
                "inputs": [],
                "runtimes": [],
                "runtimeTransitiveSha256": EVIDENCE.semantic_sha256([]),
                "languagePackages": [],
                "languagePackagesTransitiveSha256": EVIDENCE.semantic_sha256([]),
                "toolArtifacts": [],
                "toolArtifactsTransitiveSha256": EVIDENCE.semantic_sha256([]),
                "toolchainTransitiveSha256": "hash",
                "pathMatrixSha256": EVIDENCE.semantic_sha256(
                    {"pathMatrix": [], "pathMatrixIgnored": []}
                ),
                "proposals": [],
                "gitlinks": [],
                "resolvedPackages": [],
                "externalEvidence": external,
                "packages": packages,
            }
            lock["lockDigest"] = EVIDENCE.semantic_sha256(lock)
            self._json(evidence_root / EVIDENCE.LOCK_FILENAME, lock)
            with (
                patch.object(EVIDENCE, "validate_toolchain"),
                patch.object(EVIDENCE, "validate_manifest_semantics"),
                patch.object(EVIDENCE, "git_revision", return_value=REVISION),
                patch.object(EVIDENCE, "git_commit_epoch", return_value=EPOCH),
                patch.object(EVIDENCE, "collect_inputs", return_value=[]),
                patch.object(EVIDENCE, "collect_runtime_environment", return_value=[]),
                patch.object(EVIDENCE, "collect_language_packages", return_value=[]),
                patch.object(EVIDENCE, "collect_tool_artifacts", return_value=[]),
                patch.object(EVIDENCE, "_toolchain_transitive_hash", return_value="hash"),
                patch.object(EVIDENCE, "collect_proposals", return_value=[]),
                patch.object(EVIDENCE, "collect_gitlinks", return_value=[]),
                patch.object(EVIDENCE, "collect_resolved_packages", return_value=[]),
                patch.object(EVIDENCE, "collect_external_evidence", return_value=external),
                patch.object(EVIDENCE, "collect_packages", return_value=copy.deepcopy(packages)),
                patch.object(
                    EVIDENCE,
                    "validate_implementation_profile_coverage",
                    side_effect=EVIDENCE.EvidenceError("profile replay gate reached"),
                ) as replay_gate,
            ):
                failures = EVIDENCE.verify_evidence(
                    repository,
                    repository / "Conformance/evidence.json",
                    repository / "Conformance/evidence.schema.json",
                    evidence_root,
                    validate_schema=False,
                )
            self.assertEqual(failures, ["profile replay gate reached"])
            replay_gate.assert_called_once()

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
