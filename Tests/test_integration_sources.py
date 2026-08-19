"""Tests for immutable external integration-source manifests."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "Scripts/check-integration-sources.py"
SPECIFICATION = importlib.util.spec_from_file_location(
    "check_integration_sources", SCRIPT
)
assert SPECIFICATION and SPECIFICATION.loader
CHECK = importlib.util.module_from_spec(SPECIFICATION)
SPECIFICATION.loader.exec_module(CHECK)


class IntegrationSourceManifestTests(unittest.TestCase):
    manifest = {
        "schemaVersion": 3,
        "sources": [
            {
                "id": "example",
                "repository": "https://github.com/SchmiedmayerLab/example.git",
                "path": "Integration/Sources/Example",
                "commit": "a" * 40,
                "purpose": "Exact example revision used by the proposal fixture.",
            }
        ],
        "proposals": [],
    }

    @staticmethod
    def proposal(
        identifier: str,
        dependencies: list[str],
        *,
        source: str = "example",
    ) -> dict[str, object]:
        return {
            "id": identifier,
            "source": source,
            "patch": f"Integration/Patches/{identifier}.patch",
            "sha256": "b" * 64,
            "dependsOn": dependencies,
            "appliesAfter": [],
            "tests": [
                {
                    "group": "portable",
                    "platforms": ["linux", "macos"],
                    "cwd": ".",
                    "argv": ["git", "diff", "--check"],
                }
            ],
            "claims": ["The example preserves the declared contract."],
        }

    def test_accepts_an_exact_physical_source_manifest(self) -> None:
        self.assertEqual(CHECK.validate_manifest(deepcopy(self.manifest)), [])

    def test_repository_manifest_has_the_reviewed_schema_v3_layout(self) -> None:
        manifest = json.loads(
            (ROOT / "Integration/sources.json").read_text(encoding="utf-8")
        )
        self.assertEqual(CHECK.validate_manifest(manifest), [])
        self.assertEqual(manifest["schemaVersion"], 3)
        expected = {
            "grove-questionnaire": (
                "Integration/Sources/GroveQuestionnaire",
                "5e5bcfae39caed46e9ce12a70d84c1546aa76aea",
            ),
            "grove-healthkit": (
                "Integration/Sources/GroveHealthKit",
                "fb78db4c5343c234825b433706f7ee62f111c5cc",
            ),
            "grove-legacy-021": (
                "Integration/Sources/GroveLegacy021",
                "7fbc89d590ee29d9e73b9d700f91aa1e3d905883",
            ),
            "grove-sensorkit-reference": (
                "Integration/Sources/GroveSensorKit",
                "2c2a7c61004fd6c56bfb4b67f1e967b4bee98d06",
            ),
            "my-heart-counts-ios": (
                "Integration/Sources/MyHeartCountsIOS",
                "e7ae70ebbbfb335eea274cd35eacd5d3c5c93d33",
            ),
            "my-heart-counts-android": (
                "Integration/Sources/MyHeartCountsAndroid",
                "5d9fc561ba2b30f93a2334a1678ea5f4103263c6",
            ),
            "my-heart-counts-firebase": (
                "Integration/Sources/MyHeartCountsFirebase",
                "8bad2e814ad60763ddf810750e503488719f55f5",
            ),
            "my-heart-counts-study-definitions-024": (
                "Integration/Sources/MyHeartCountsStudyDefinitions024",
                "44a658790d03b74a570e40eadba06ae5fa435b60",
            ),
            "my-heart-counts-study-definitions-025": (
                "Integration/Sources/MyHeartCountsStudyDefinitions025",
                "06e410c9ded3727296961dc39526aa1c49905538",
            ),
        }
        actual = {
            source["id"]: (source["path"], source["commit"])
            for source in manifest["sources"]
        }
        self.assertEqual(actual, expected)
        proposal_sources = {
            proposal["source"] for proposal in manifest["proposals"]
        }
        self.assertNotIn("grove-sensorkit-reference", proposal_sources)
        for source in manifest["sources"]:
            self.assertEqual(
                set(source), {"id", "repository", "path", "commit", "purpose"}
            )
            self.assertTrue(source["purpose"].strip())
        for proposal in manifest["proposals"]:
            self.assertNotIn("target", proposal)

    def test_empty_submodule_directory_is_not_the_parent_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Integration/Sources/Example").mkdir(parents=True)
            with mock.patch.object(CHECK, "gitlink", return_value="a" * 40):
                failures = CHECK.verify_repository(
                    root=root,
                    source=deepcopy(self.manifest["sources"][0]),
                )
        self.assertEqual(
            failures,
            [
                "example submodule is not initialized: "
                "Integration/Sources/Example"
            ],
        )

    def test_source_verification_never_fetches_or_resolves_a_ref(self) -> None:
        source = deepcopy(self.manifest["sources"][0])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            checkout = root / "Integration/Sources/Example"
            (checkout / ".git").mkdir(parents=True)

            def fake_run(*arguments: str, cwd: Path) -> str:
                expected = {
                    ("git", "rev-parse", "HEAD"): source["commit"],
                    (
                        "git",
                        "status",
                        "--porcelain=v1",
                        "--untracked-files=all",
                    ): "",
                    ("git", "rev-parse", "--abbrev-ref", "HEAD"): "HEAD",
                    (
                        "git",
                        "remote",
                        "get-url",
                        "origin",
                    ): source["repository"],
                }
                self.assertIn(arguments, expected)
                return expected[arguments]

            with (
                mock.patch.object(CHECK, "gitlink", return_value=source["commit"]),
                mock.patch.object(CHECK, "run", side_effect=fake_run),
            ):
                failures = CHECK.verify_repository(root=root, source=source)
        self.assertEqual(failures, [])

    def test_duplicate_repository_urls_are_allowed_for_distinct_checkouts(self) -> None:
        manifest = deepcopy(self.manifest)
        second = deepcopy(manifest["sources"][0])
        second.update(
            {
                "id": "second",
                "path": "Integration/Sources/Second",
                "commit": "b" * 40,
                "purpose": "A second exact revision of the same repository.",
            }
        )
        manifest["sources"].append(second)
        self.assertEqual(CHECK.validate_manifest(manifest), [])

        duplicate = deepcopy(manifest)
        duplicate["sources"].append(deepcopy(duplicate["sources"][0]))
        failures = CHECK.validate_manifest(duplicate)
        self.assertIn("duplicate integration source id: example", failures)
        self.assertIn(
            "duplicate integration source path: Integration/Sources/Example",
            failures,
        )

    def test_repository_comparison_normalizes_git_suffix_and_case(self) -> None:
        self.assertEqual(
            CHECK.normalize_repository(
                "https://github.com/SchmiedmayerLab/Example.git"
            ),
            "https://github.com/schmiedmayerlab/example",
        )

    def test_rejects_unsafe_or_legacy_source_metadata(self) -> None:
        manifest = deepcopy(self.manifest)
        source = manifest["sources"][0]
        source["path"] = "Integration/Other/Example"
        source["repository"] = (
            "https://github.com/SchmiedmayerLab/../another-owner/example.git"
        )
        source["commit"] = "abc123"
        source["purpose"] = "  "
        source["targets"] = []
        failures = CHECK.validate_manifest(manifest)
        self.assertIn(
            "example path must be one directory under Integration/Sources", failures
        )
        self.assertIn(
            "example repository must be an HTTPS SchmiedmayerLab .git URL", failures
        )
        self.assertIn("example commit must be a full lowercase SHA", failures)
        self.assertIn("example purpose must be a nonempty string", failures)
        self.assertIn(
            "integration source contains unsupported fields: targets", failures
        )

    def test_requires_structured_test_commands_and_claims(self) -> None:
        manifest = deepcopy(self.manifest)
        proposal = self.proposal("proposal", [])
        proposal["tests"] = ["swift test"]
        proposal["claims"] = [""]
        manifest["proposals"] = [proposal]
        failures = CHECK.validate_manifest(manifest)
        self.assertIn(
            "proposal test 1 must be an object with group, platforms, cwd, and argv",
            failures,
        )
        self.assertIn(
            "proposal must declare at least one nonempty contract claim", failures
        )

    def test_rejects_patch_paths_outside_the_proposal_directory(self) -> None:
        manifest = deepcopy(self.manifest)
        proposal = self.proposal("proposal", [])
        proposal["patch"] = "README.md"
        manifest["proposals"] = [proposal]
        self.assertIn(
            "proposal patch must be under Integration/Patches and end in .patch",
            CHECK.validate_manifest(manifest),
        )

    def test_rejects_unknown_schema_fields_and_reused_patch_files(self) -> None:
        manifest = deepcopy(self.manifest)
        first = self.proposal("first", [])
        second = self.proposal("second", [])
        second["patch"] = first["patch"]
        first["target"] = "main"
        manifest["proposals"] = [first, second]
        failures = CHECK.validate_manifest(manifest)
        self.assertIn(
            "integration proposal contains unsupported fields: target", failures
        )
        self.assertIn(
            "duplicate integration proposal patch: Integration/Patches/first.patch",
            failures,
        )

    def test_rejects_unknown_and_cyclic_proposal_dependencies(self) -> None:
        unknown = deepcopy(self.manifest)
        unknown["proposals"] = [self.proposal("proposal", ["missing"])]
        self.assertIn(
            "proposal references unknown proposal dependency: missing",
            CHECK.validate_manifest(unknown),
        )

        cyclic = deepcopy(self.manifest)
        cyclic["proposals"] = [
            self.proposal("proposal-a", ["proposal-b"]),
            self.proposal("proposal-b", ["proposal-a"]),
        ]
        self.assertIn(
            "proposal dependency cycle: proposal-a -> proposal-b -> proposal-a",
            CHECK.validate_manifest(cyclic),
        )

    def test_rejects_invalid_and_unknown_proposal_source_ids(self) -> None:
        invalid = deepcopy(self.manifest)
        invalid_proposal = self.proposal("proposal", [])
        invalid_proposal["source"] = ["example"]
        invalid["proposals"] = [invalid_proposal]
        self.assertIn(
            "proposal source must be a lowercase source identifier",
            CHECK.validate_manifest(invalid),
        )

        unknown = deepcopy(self.manifest)
        unknown["proposals"] = [
            self.proposal("proposal", [], source="missing")
        ]
        self.assertIn(
            "proposal references unknown source: missing",
            CHECK.validate_manifest(unknown),
        )

    def test_tests_are_optional_and_never_inferred(self) -> None:
        manifest = deepcopy(self.manifest)
        proposal = self.proposal("proposal", [])
        proposal.pop("tests")
        manifest["proposals"] = [proposal]
        self.assertEqual(CHECK.validate_manifest(manifest), [])

    def test_test_groups_require_explicit_consistent_platforms(self) -> None:
        manifest = deepcopy(self.manifest)
        proposal = self.proposal("proposal", [])
        proposal["tests"] = [
            {
                "group": "macos-contract",
                "platforms": ["macos"],
                "cwd": ".",
                "argv": ["swift", "test"],
            },
            {
                "group": "macos-contract",
                "platforms": ["linux"],
                "cwd": ".",
                "argv": ["git", "diff", "--check"],
            },
        ]
        manifest["proposals"] = [proposal]
        self.assertIn(
            "proposal test group macos-contract must use one consistent platform set",
            CHECK.validate_manifest(manifest),
        )

        proposal["tests"][1]["platforms"] = ["macos", "macos"]
        self.assertIn(
            "proposal test 2 contains duplicate platform: macos",
            CHECK.validate_manifest(manifest),
        )
        proposal["tests"][1]["platforms"] = ["windows"]
        self.assertIn(
            "proposal test 2 contains unsupported platform: 'windows'",
            CHECK.validate_manifest(manifest),
        )

    def test_rejects_a_test_working_directory_inside_git_metadata(self) -> None:
        manifest = deepcopy(self.manifest)
        proposal = self.proposal("proposal", [])
        proposal["tests"] = [
            {
                "group": "portable",
                "platforms": ["linux"],
                "cwd": ".git/hooks",
                "argv": ["git", "status"],
            }
        ]
        manifest["proposals"] = [proposal]
        self.assertIn(
            "proposal test 1 cwd must be a safe relative path",
            CHECK.validate_manifest(manifest),
        )

    def test_applied_dependencies_use_sources_from_the_same_repository(self) -> None:
        valid = deepcopy(self.manifest)
        second = deepcopy(valid["sources"][0])
        second.update(
            {
                "id": "second",
                "path": "Integration/Sources/Second",
                "commit": "c" * 40,
                "purpose": "Second exact base for explicit composition.",
            }
        )
        valid["sources"].append(second)
        parent = self.proposal("parent", [], source="example")
        child = self.proposal("child", ["parent"], source="second")
        child["appliesAfter"] = ["parent"]
        valid["proposals"] = [parent, child]
        self.assertEqual(CHECK.validate_manifest(valid), [])

        missing_order = deepcopy(valid)
        missing_order["proposals"][1]["dependsOn"] = []
        self.assertIn(
            "child applied dependency parent must also be listed in dependsOn",
            CHECK.validate_manifest(missing_order),
        )

        cross_repository = deepcopy(valid)
        cross_repository["sources"][1]["repository"] = (
            "https://github.com/SchmiedmayerLab/other.git"
        )
        self.assertIn(
            "child cannot apply dependency parent from a different repository",
            CHECK.validate_manifest(cross_repository),
        )

    def test_gitmodules_matches_paths_and_allows_repeated_repository_urls(self) -> None:
        manifest = deepcopy(self.manifest)
        second = deepcopy(manifest["sources"][0])
        second.update(
            {
                "id": "second",
                "path": "Integration/Sources/Second",
                "commit": "c" * 40,
                "purpose": "Second exact base.",
            }
        )
        manifest["sources"].append(second)
        valid = """\
[submodule "example"]
\tpath = Integration/Sources/Example
\turl = https://github.com/SchmiedmayerLab/example.git
\tshallow = true
[submodule "second"]
\tpath = Integration/Sources/Second
\turl = https://github.com/SchmiedmayerLab/example.git
\tshallow = true
"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".gitmodules").write_text(valid, encoding="utf-8")
            self.assertEqual(CHECK.verify_gitmodules(root, manifest), [])

            (root / ".gitmodules").write_text(
                valid
                + """\
[submodule "extra"]
\tpath = Integration/Sources/Extra
\turl = https://github.com/SchmiedmayerLab/extra.git
\tbranch = main
\tshallow = true
""",
                encoding="utf-8",
            )
            failures = CHECK.verify_gitmodules(root, manifest)
        self.assertIn(
            "extra has unsupported .gitmodules properties: branch", failures
        )
        self.assertIn(
            "unexpected .gitmodules source: Integration/Sources/Extra -> "
            "https://github.com/SchmiedmayerLab/extra.git",
            failures,
        )

    def test_stage_zero_gitlink_set_must_exactly_match_manifest(self) -> None:
        expected = {"Integration/Sources/Example": "a" * 40}
        with mock.patch.object(
            CHECK, "stage_zero_gitlinks", return_value=(expected, [])
        ):
            self.assertEqual(
                CHECK.verify_gitlink_set(Path("."), deepcopy(self.manifest)), []
            )

        actual = {
            "Integration/Sources/Example": "b" * 40,
            "Integration/Sources/Extra": "c" * 40,
        }
        with mock.patch.object(
            CHECK, "stage_zero_gitlinks", return_value=(actual, [])
        ):
            failures = CHECK.verify_gitlink_set(Path("."), deepcopy(self.manifest))
        self.assertIn(
            f"Integration/Sources/Example gitlink {'b' * 40} != manifest commit "
            f"{'a' * 40}",
            failures,
        )
        self.assertIn(
            "unexpected stage-zero gitlink: Integration/Sources/Extra", failures
        )

    def test_non_stage_zero_gitlink_is_rejected(self) -> None:
        row = f"160000 {'a' * 40} 2\tIntegration/Sources/Example\0"
        with mock.patch.object(CHECK, "run", return_value=row):
            actual, failures = CHECK.stage_zero_gitlinks(Path("."))
        self.assertEqual(actual, {})
        self.assertEqual(
            failures,
            ["gitlink is not at stage zero: Integration/Sources/Example"],
        )


if __name__ == "__main__":
    unittest.main()
