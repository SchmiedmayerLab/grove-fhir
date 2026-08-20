"""Tests for immutable external integration-source manifests."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).parents[1] / "Scripts/check-integration-sources.py"
SPECIFICATION = importlib.util.spec_from_file_location(
    "check_integration_sources", SCRIPT
)
assert SPECIFICATION and SPECIFICATION.loader
CHECK = importlib.util.module_from_spec(SPECIFICATION)
SPECIFICATION.loader.exec_module(CHECK)


class IntegrationSourceManifestTests(unittest.TestCase):
    manifest = {
        "schemaVersion": 2,
        "sources": [
            {
                "id": "example",
                "repository": "https://github.com/SchmiedmayerLab/example.git",
                "path": "Integration/Sources/Example",
                "gitlink": "a" * 40,
                "targets": [
                    {
                        "id": "main",
                        "ref": "refs/heads/main",
                        "commit": "a" * 40,
                    }
                ],
            }
        ],
        "proposals": [],
    }

    @staticmethod
    def proposal(identifier: str, dependencies: list[str]) -> dict[str, object]:
        return {
            "id": identifier,
            "source": "example",
            "target": "main",
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

    def test_accepts_an_immutable_source_manifest(self) -> None:
        self.assertEqual(CHECK.validate_manifest(deepcopy(self.manifest)), [])

    def test_empty_submodule_directory_is_not_mistaken_for_the_parent_repository(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Integration/Sources/Example").mkdir(parents=True)
            with mock.patch.object(CHECK, "gitlink", return_value="a" * 40):
                failures = CHECK.verify_repository(
                    root=root,
                    source=deepcopy(self.manifest["sources"][0]),
                    fetch_targets=False,
                )
        self.assertEqual(
            failures,
            [
                "example submodule is not initialized: "
                "Integration/Sources/Example"
            ],
        )

    def test_fetches_the_provenance_ref_without_following_its_tip(self) -> None:
        source = deepcopy(self.manifest["sources"][0])
        pinned = source["targets"][0]["commit"]
        advanced_tip = "b" * 40
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            checkout = root / "Integration/Sources/Example"
            (checkout / ".git").mkdir(parents=True)

            def fake_run(*arguments: str, cwd: Path) -> str:
                if arguments == ("git", "rev-parse", "HEAD"):
                    return pinned
                if arguments == ("git", "status", "--porcelain"):
                    return ""
                if arguments == ("git", "remote", "get-url", "origin"):
                    return source["repository"]
                if arguments[:2] == ("git", "fetch"):
                    self.assertEqual(arguments[-1], "refs/heads/main")
                    self.assertNotIn(pinned, arguments)
                    return ""
                if arguments == (
                    "git",
                    "rev-parse",
                    "--verify",
                    "FETCH_HEAD^{commit}",
                ):
                    return advanced_tip
                if arguments == (
                    "git",
                    "merge-base",
                    "--is-ancestor",
                    pinned,
                    advanced_tip,
                ):
                    return ""
                self.fail(f"unexpected git command: {arguments!r}")

            with (
                mock.patch.object(CHECK, "gitlink", return_value=pinned),
                mock.patch.object(CHECK, "run", side_effect=fake_run),
            ):
                failures = CHECK.verify_repository(
                    root=root,
                    source=source,
                    fetch_targets=True,
                )

        self.assertEqual(failures, [])

    def test_accepts_independent_targets_without_implying_array_order(self) -> None:
        manifest = deepcopy(self.manifest)
        manifest["sources"][0]["targets"].append(
            {
                "id": "feature",
                "ref": "refs/pull/12/head",
                "commit": "b" * 40,
            }
        )
        self.assertEqual(CHECK.validate_manifest(manifest), [])

    def test_rejects_duplicate_sources_paths_and_repositories(self) -> None:
        manifest = deepcopy(self.manifest)
        manifest["sources"].append(deepcopy(manifest["sources"][0]))
        failures = CHECK.validate_manifest(manifest)
        self.assertIn("duplicate integration source id: example", failures)
        self.assertIn(
            "duplicate integration source path: Integration/Sources/Example",
            failures,
        )
        self.assertIn(
            "duplicate integration repository: "
            "https://github.com/SchmiedmayerLab/example.git",
            failures,
        )

    def test_rejects_unsafe_source_metadata(self) -> None:
        manifest = deepcopy(self.manifest)
        source = manifest["sources"][0]
        source["path"] = "Integration/Other/Example"
        source["repository"] = (
            "https://github.com/SchmiedmayerLab/../another-owner/example.git"
        )
        failures = CHECK.validate_manifest(manifest)
        self.assertIn(
            "example path must be one directory under Integration/Sources", failures
        )
        self.assertIn(
            "example repository must be an HTTPS SchmiedmayerLab .git URL", failures
        )

    def test_rejects_an_invalid_or_abbreviated_target(self) -> None:
        manifest = deepcopy(self.manifest)
        target = manifest["sources"][0]["targets"][0]
        target["ref"] = "refs/heads/main:refs/heads/overwrite"
        target["commit"] = "abc123"
        failures = CHECK.validate_manifest(manifest)
        self.assertIn(
            "example/main must use a valid heads or pull-request ref", failures
        )
        self.assertIn(
            "example/main commit must be a full lowercase SHA",
            failures,
        )

    def test_requires_the_gitlink_to_be_a_declared_target(self) -> None:
        manifest = deepcopy(self.manifest)
        manifest["sources"][0]["gitlink"] = "c" * 40
        self.assertIn(
            "example gitlink must equal one declared target commit",
            CHECK.validate_manifest(manifest),
        )

    def test_rejects_unknown_and_cyclic_target_predecessors(self) -> None:
        unknown = deepcopy(self.manifest)
        unknown["sources"][0]["targets"][0]["predecessor"] = "missing"
        self.assertIn(
            "example/main references unknown predecessor: missing",
            CHECK.validate_manifest(unknown),
        )

        cyclic = deepcopy(self.manifest)
        main = cyclic["sources"][0]["targets"][0]
        main["predecessor"] = "next"
        cyclic["sources"][0]["targets"].append(
            {
                "id": "next",
                "ref": "refs/heads/next",
                "commit": "b" * 40,
                "predecessor": "main",
            }
        )
        self.assertIn(
            "example target predecessor cycle: main -> next -> main",
            CHECK.validate_manifest(cyclic),
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
        first["command"] = "swift test"
        manifest["proposals"] = [first, second]
        failures = CHECK.validate_manifest(manifest)
        self.assertIn(
            "integration proposal contains unsupported fields: command", failures
        )
        self.assertIn(
            "duplicate integration proposal patch: "
            "Integration/Patches/first.patch",
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
        failures = CHECK.validate_manifest(manifest)
        self.assertIn(
            "proposal test 2 contains duplicate platform: macos", failures
        )

        proposal["tests"][1]["platforms"] = ["windows"]
        self.assertIn(
            "proposal test 2 contains unsupported platform: 'windows'",
            CHECK.validate_manifest(manifest),
        )

    def test_rejects_a_test_working_directory_inside_git_metadata(self) -> None:
        manifest = deepcopy(self.manifest)
        proposal = self.proposal("proposal", [])
        proposal["tests"] = [{"cwd": ".git/hooks", "argv": ["git", "status"]}]
        manifest["proposals"] = [proposal]
        self.assertIn(
            "proposal test 1 cwd must be a safe relative path",
            CHECK.validate_manifest(manifest),
        )

    def test_applied_dependencies_are_explicit_same_source_dependencies(self) -> None:
        valid = deepcopy(self.manifest)
        parent = self.proposal("parent", [])
        child = self.proposal("child", ["parent"])
        child["appliesAfter"] = ["parent"]
        valid["proposals"] = [parent, child]
        self.assertEqual(CHECK.validate_manifest(valid), [])

        missing_order = deepcopy(valid)
        missing_order["proposals"][1]["dependsOn"] = []
        self.assertIn(
            "child applied dependency parent must also be listed in dependsOn",
            CHECK.validate_manifest(missing_order),
        )

        cross_source = deepcopy(valid)
        cross_source["sources"].append(
            {
                "id": "other",
                "repository": "https://github.com/SchmiedmayerLab/other.git",
                "path": "Integration/Sources/Other",
                "gitlink": "c" * 40,
                "targets": [
                    {
                        "id": "main",
                        "ref": "refs/heads/main",
                        "commit": "c" * 40,
                    }
                ],
            }
        )
        cross_source["proposals"][0]["source"] = "other"
        cross_source["proposals"][0]["target"] = "main"
        self.assertIn(
            "child cannot apply cross-source dependency parent",
            CHECK.validate_manifest(cross_source),
        )

    def test_gitmodules_must_exactly_match_manifest_sources(self) -> None:
        valid = """\
[submodule "example"]
\tpath = Integration/Sources/Example
\turl = https://github.com/SchmiedmayerLab/example.git
\tshallow = true
"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".gitmodules").write_text(valid, encoding="utf-8")
            self.assertEqual(
                CHECK.verify_gitmodules(root, deepcopy(self.manifest)), []
            )

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
            failures = CHECK.verify_gitmodules(root, deepcopy(self.manifest))
            self.assertIn(
                "extra has unsupported .gitmodules properties: branch", failures
            )
            self.assertIn(
                "unexpected .gitmodules source: Integration/Sources/Extra -> "
                "https://github.com/SchmiedmayerLab/extra.git",
                failures,
            )
            self.assertIn(
                ".gitmodules must contain exactly one entry for every manifest source",
                failures,
            )


if __name__ == "__main__":
    unittest.main()
