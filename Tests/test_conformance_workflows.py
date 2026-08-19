"""Structural guards for the build-once evidence and deployment workflows."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
BUILD = ROOT / ".github/workflows/build-and-test.yml"
PAGES = ROOT / ".github/workflows/pages.yml"


class ConformanceWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.build = BUILD.read_text(encoding="utf-8")
        self.pages = PAGES.read_text(encoding="utf-8")
        self.toolchain = json.loads(
            (ROOT / "Conformance/toolchain.json").read_text(encoding="utf-8")
        )

    def test_exact_runtime_setup_matches_toolchain(self) -> None:
        runtimes = self.toolchain["runtimes"]
        for identifier in ("node", "python", "java", "ruby"):
            self.assertEqual(runtimes[identifier]["precision"], "exact")
            self.assertIn(runtimes[identifier]["version"], self.build)
        java_setup_version = runtimes["java"]["setupVersion"]
        self.assertEqual(
            self.build.count(f'java-version: "{java_setup_version}"'), 4
        )
        self.assertEqual(runtimes["bundler"]["precision"], "exact")
        self.assertIn(
            f"gem install bundler -v {runtimes['bundler']['version']}", self.build
        )
        self.assertIn(runtimes["python"]["version"], self.pages)
        self.assertIn("zlibVersion", (ROOT / "Conformance/evidence.schema.json").read_text())

    def test_required_pages_check_is_unique_and_always_present(self) -> None:
        combined = self.build + self.pages
        self.assertEqual(combined.count("name: Build GitHub Pages"), 1)
        build_pages = self.build.split("  build-pages:", 1)[1]
        self.assertIn("if: always()", build_pages)
        self.assertIn("needs.changes.result", build_pages)
        self.assertIn("pages-site-candidate", build_pages)
        self.assertIn("Scripts/check-evidence-lock.py site", build_pages)

    def test_dot_build_artifacts_explicitly_include_hidden_files(self) -> None:
        expected = {
            "implementation-guides": (".build/pages", ".build/fhir-tools"),
            "linux-evidence-fragments": (
                ".build/android-conformance",
                ".build/android-wire",
                ".build/firebase-lifecycle-result.json",
            ),
            "mac-evidence-fragments": ("grove-fhir/.build/mac-evidence",),
            "conformance-evidence": (
                ".build/conformance-evidence",
                ".build/corpus.tgz",
                ".build/corpus.tgz.sha256",
            ),
            "pages-site-candidate": (".build/pages",),
            "pages-site": (".build/pages",),
        }
        upload_blocks = [
            f"      - {block}"
            for block in self.build.split("\n      - ")[1:]
            if "uses: actions/upload-artifact@v4" in block
        ]
        actual: dict[str, str] = {}
        for block in upload_blocks:
            match = re.search(r"^          name: ([^\n]+)$", block, re.MULTILINE)
            self.assertIsNotNone(match, block)
            assert match is not None
            actual[match.group(1)] = block

        self.assertEqual(set(actual), set(expected))
        for artifact, paths in expected.items():
            with self.subTest(artifact=artifact):
                block = actual[artifact]
                self.assertIn("          include-hidden-files: true\n", block)
                for path in paths:
                    self.assertIn(path, block)

    def test_pages_deployment_preserves_nojekyll(self) -> None:
        self.assertIn("uses: actions/upload-pages-artifact@v5", self.pages)
        self.assertNotIn("uses: actions/upload-pages-artifact@v4", self.pages)
        pages_upload = self.pages.split(
            "uses: actions/upload-pages-artifact@v5", 1
        )[1].split("      - ", 1)[0]
        self.assertIn("include-hidden-files: true", pages_upload)

    def test_guides_build_once_and_consumers_only_download(self) -> None:
        guides, later = self.build.split("  integration-proposals:", 1)
        self.assertEqual(self.build.count("Build all implementation guides exactly once"), 1)
        self.assertIn("npm run build", guides)
        self.assertNotIn("build-guides.sh", later)
        self.assertNotIn("npm run pages:build", later)
        self.assertIn(".build/pages/fhir/mobile/ci-build/package.tgz", later)
        conformance = self.build.split("  conformance-evidence:", 1)[1].split(
            "  conformance-gates:", 1
        )[0]
        self.assertIn("name: conformance-evidence", conformance)
        self.assertIn(".build/conformance-evidence", conformance)
        self.assertIn(".build/corpus.tgz.sha256", conformance)
        for gate in (
            "validate-domain-fhir.py",
            "validate-receiver-evidence.cjs",
            "validate-heart-rate-equivalence.py",
            "validate-study-graph.py",
        ):
            self.assertIn(gate, conformance)
        self.assertEqual(
            conformance.count("--external-evidence grove-questionnaire-resources="),
            3,
        )

    def test_exact_head_and_base_guards_are_not_mutable_refs(self) -> None:
        self.assertIn("github.event.pull_request.head.sha || github.sha", self.build)
        self.assertIn("github.event.pull_request.base.sha || github.event.before", self.build)
        self.assertIn("git fetch --no-tags --depth=1 origin \"$EVENT_BASE\"", self.build)
        self.assertNotIn("origin/main", self.build)
        self.assertNotIn("ref: main", self.build)

    def test_partial_source_initialization_and_full_inventory_are_explicit(self) -> None:
        self.assertNotIn("submodules: true", self.build)
        workflow_environment = self.build.split("\nenv:\n", 1)[1].split(
            "\njobs:\n", 1
        )[0]
        self.assertIn('  GIT_LFS_SKIP_SMUDGE: "1"\n', workflow_environment)
        integration = self.build.split("  integration-sources:", 1)[1].split("  guides:", 1)[0]
        self.assertEqual(integration.count("Integration/Sources/"), 9)
        guides = self.build.split("  guides:", 1)[1].split("  integration-proposals:", 1)[0]
        self.assertNotIn("git submodule", guides)
        linux = self.build.split("  integration-proposals:", 1)[1].split("  vocabulary-is-current:", 1)[0]
        self.assertEqual(linux.count("Integration/Sources/"), 4)
        mac = self.build.split("  emitted-resource-conformance:", 1)[1].split("  conformance-evidence:", 1)[0]
        self.assertEqual(mac.count("Integration/Sources/"), 4)

    def test_documentation_is_hardened_workflow_run_consumer_only(self) -> None:
        self.assertIn("workflow_run:", self.pages)
        self.assertIn("branches: [main]", self.pages)
        self.assertIn(
            "github.event.workflow_run.head_repository.full_name == github.repository",
            self.pages,
        )
        self.assertIn("github.event.workflow_run.conclusion == 'success'", self.pages)
        self.assertIn("github.event.workflow_run.head_sha", self.pages)
        self.assertIn("run-id: ${{ github.event.workflow_run.id }}", self.pages)
        self.assertIn("Scripts/check-evidence-lock.py site", self.pages)
        self.assertNotIn("npm run build", self.pages)
        self.assertNotIn("npm run pages:build", self.pages)
        self.assertNotIn("Build GitHub Pages", self.pages)

    def test_publication_contract_routes_are_exact(self) -> None:
        source = (ROOT / "Scripts/conformance_evidence.py").read_text(encoding="utf-8")
        self.assertIn('LOCK_FILENAME = "evidence-lock.json"', source)
        self.assertIn('ARCHIVE_FILENAME = "corpus.tgz"', source)
        self.assertIn('"semantic-diff.json"', source)
        self.assertIn('"semantic-diff.md"', source)

    def test_equivalence_cli_uses_exact_manifest_evidence_set_ids(self) -> None:
        manifest = json.loads((ROOT / "Conformance/evidence.json").read_text())
        declared = {item["id"] for item in manifest["externalEvidence"]}
        specification = json.loads(
            (ROOT / "Conformance/semantic-equivalence/heart-rate.json").read_text()
        )
        expected = [item["id"] for item in specification["implementationInputs"]]
        self.assertEqual(
            expected,
            ["grove-current-resources", "my-heart-counts-android-conformance"],
        )
        self.assertTrue(set(expected).issubset(declared))
        for identifier in expected:
            self.assertIn(f"--external-evidence {identifier}=", self.build)

    def test_external_evidence_never_publishes_raw_validator_transcripts(self) -> None:
        manifest = json.loads((ROOT / "Conformance/evidence.json").read_text())
        files = [
            file
            for evidence_set in manifest["externalEvidence"]
            for file in evidence_set["files"]
        ]
        self.assertNotIn("validator-transcript", {file["format"] for file in files})
        self.assertNotIn("text/plain", {file["mediaType"] for file in files})
        self.assertNotIn("validation.txt", self.build)
        for identifier in (
            "grove-questionnaire-resources",
            "grove-current-resources",
            "my-heart-counts-android-conformance",
        ):
            declaration = next(
                item for item in manifest["externalEvidence"] if item["id"] == identifier
            )
            attestations = [
                file
                for file in declaration["files"]
                if file["format"] == "test-attestation-v1"
            ]
            self.assertEqual(len(attestations), 1)
            fhir_paths = {
                file["path"]
                for file in declaration["files"]
                if file["format"] == "fhir-json"
            }
            self.assertEqual(
                {item["path"] for item in attestations[0]["attestationInputs"]},
                fhir_paths,
            )


if __name__ == "__main__":
    unittest.main()
