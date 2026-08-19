"""Tests for disposable integration proposal validation."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / "Scripts/validate-integration-proposals.py"
SPECIFICATION = importlib.util.spec_from_file_location(
    "validate_integration_proposals", SCRIPT
)
assert SPECIFICATION and SPECIFICATION.loader
VALIDATE = importlib.util.module_from_spec(SPECIFICATION)
SPECIFICATION.loader.exec_module(VALIDATE)


class IntegrationProposalValidationTests(unittest.TestCase):
    @staticmethod
    def git(repository: Path, *arguments: str) -> str:
        result = subprocess.run(
            ["git", *arguments],
            cwd=repository,
            check=True,
            capture_output=True,
            text=True,
            env={
                **os.environ,
                "GIT_CONFIG_NOSYSTEM": "1",
                "GIT_CONFIG_GLOBAL": os.devnull,
                "GIT_AUTHOR_NAME": "Proposal Test",
                "GIT_AUTHOR_EMAIL": "proposal-test@example.com",
                "GIT_COMMITTER_NAME": "Proposal Test",
                "GIT_COMMITTER_EMAIL": "proposal-test@example.com",
            },
        )
        return result.stdout.strip()

    def make_sources(self, root: Path) -> tuple[Path, Path, str, str]:
        self.git(root, "init", "--quiet", "--initial-branch=main", "--template=")
        upstream = root / "upstream"
        upstream.mkdir()
        self.git(
            upstream, "init", "--quiet", "--initial-branch=main", "--template="
        )
        (upstream / "value.txt").write_text("before\n", encoding="utf-8")
        self.git(upstream, "add", "value.txt")
        self.git(
            upstream,
            "-c",
            "commit.gpgsign=false",
            "commit",
            "--quiet",
            "-m",
            "Initial fixture",
        )
        first = self.git(upstream, "rev-parse", "HEAD")
        (upstream / "second.txt").write_text("second base\n", encoding="utf-8")
        self.git(upstream, "add", "second.txt")
        self.git(
            upstream,
            "-c",
            "commit.gpgsign=false",
            "commit",
            "--quiet",
            "-m",
            "Second fixture",
        )
        second = self.git(upstream, "rev-parse", "HEAD")

        sources = root / "Integration/Sources"
        sources.mkdir(parents=True)
        first_source = sources / "ExampleFirst"
        second_source = sources / "ExampleSecond"
        self.git(root, "clone", "--quiet", str(upstream), str(first_source))
        self.git(root, "clone", "--quiet", str(upstream), str(second_source))
        self.git(first_source, "checkout", "--quiet", "--detach", first)
        self.git(second_source, "checkout", "--quiet", "--detach", second)
        for source in (first_source, second_source):
            self.git(
                source,
                "remote",
                "set-url",
                "origin",
                "https://github.com/SchmiedmayerLab/example.git",
            )
        self.git(
            root,
            "update-index",
            "--add",
            "--cacheinfo",
            f"160000,{first},Integration/Sources/ExampleFirst",
        )
        self.git(
            root,
            "update-index",
            "--add",
            "--cacheinfo",
            f"160000,{second},Integration/Sources/ExampleSecond",
        )
        return first_source, second_source, first, second

    @staticmethod
    def patch_contents(before: str, after: str) -> bytes:
        return (
            "diff --git a/value.txt b/value.txt\n"
            "--- a/value.txt\n"
            "+++ b/value.txt\n"
            "@@ -1 +1 @@\n"
            f"-{before}\n"
            f"+{after}\n"
        ).encode()

    @staticmethod
    def proposal(
        identifier: str,
        *,
        source: str,
        contents: bytes,
        depends_on: list[str] | None = None,
        applies_after: list[str] | None = None,
        tests: list[dict[str, object]] | None = None,
    ) -> dict[str, object]:
        proposal: dict[str, object] = {
            "id": identifier,
            "source": source,
            "patch": f"Integration/Patches/{identifier}.patch",
            "sha256": hashlib.sha256(contents).hexdigest(),
            "dependsOn": depends_on or [],
            "appliesAfter": applies_after or [],
            "claims": [f"{identifier} exercises the proposal validator."],
        }
        if tests is not None:
            proposal["tests"] = tests
        return proposal

    @staticmethod
    def manifest(
        first: str,
        second: str,
        proposals: list[dict[str, object]],
    ) -> dict[str, object]:
        return {
            "schemaVersion": 3,
            "sources": [
                {
                    "id": "example-first",
                    "repository": "https://github.com/SchmiedmayerLab/example.git",
                    "path": "Integration/Sources/ExampleFirst",
                    "commit": first,
                    "purpose": "First exact proposal base.",
                },
                {
                    "id": "example-second",
                    "repository": "https://github.com/SchmiedmayerLab/example.git",
                    "path": "Integration/Sources/ExampleSecond",
                    "commit": second,
                    "purpose": "Second exact proposal base.",
                }
            ],
            "proposals": proposals,
        }

    def write_patches(
        self, root: Path, proposals: list[tuple[str, bytes]]
    ) -> None:
        patch_directory = root / "Integration/Patches"
        patch_directory.mkdir(parents=True)
        for identifier, contents in proposals:
            (patch_directory / f"{identifier}.patch").write_bytes(contents)

    def test_validates_an_explicit_patch_stack_on_different_exact_bases(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first_source, second_source, first, second = self.make_sources(root)
            parent_patch = self.patch_contents("before", "middle")
            child_patch = self.patch_contents("middle", "after")
            test = {
                "group": "portable",
                "platforms": ["linux", "macos"],
                "cwd": ".",
                "argv": [
                    sys.executable,
                    "-c",
                    "from pathlib import Path; "
                    "assert Path('value.txt').read_text() == 'after\\n'",
                ],
            }
            parent = self.proposal(
                "parent", source="example-first", contents=parent_patch
            )
            child = self.proposal(
                "child",
                source="example-second",
                contents=child_patch,
                depends_on=["parent"],
                applies_after=["parent"],
                tests=[test],
            )
            self.write_patches(
                root, [("parent", parent_patch), ("child", child_patch)]
            )
            before = {
                source: VALIDATE.source_state(source, environment=os.environ.copy())
                for source in (first_source, second_source)
            }
            VALIDATE.validate_proposals(
                root,
                self.manifest(first, second, [child, parent]),
                platform="linux",
                test_group="portable",
            )
            after = {
                source: VALIDATE.source_state(source, environment=os.environ.copy())
                for source in (first_source, second_source)
            }
            self.assertEqual(after, before)

    def test_orders_cross_source_dependencies_without_applying_them(self) -> None:
        manifest = {
            "proposals": [
                {"id": "consumer", "dependsOn": ["producer"]},
                {"id": "producer", "dependsOn": []},
            ]
        }
        self.assertEqual(
            [
                proposal["id"]
                for proposal in VALIDATE.ordered_proposals(manifest)
            ],
            ["producer", "consumer"],
        )

    def test_an_omitted_test_list_executes_no_inferred_command(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, _, first, second = self.make_sources(root)
            contents = self.patch_contents("before", "after")
            proposal = self.proposal(
                "proposal", source="example-second", contents=contents
            )
            self.write_patches(root, [("proposal", contents)])
            with patch.object(VALIDATE, "run_declared_tests") as run_tests:
                VALIDATE.validate_proposals(
                    root,
                    self.manifest(first, second, [proposal]),
                    platform="linux",
                    test_group="portable",
                )
            run_tests.assert_called_once()
            self.assertNotIn("tests", run_tests.call_args.args[1])

    def test_a_patch_failure_still_leaves_the_source_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, source, first, second = self.make_sources(root)
            contents = self.patch_contents("not-the-base", "after")
            proposal = self.proposal(
                "proposal", source="example-second", contents=contents
            )
            self.write_patches(root, [("proposal", contents)])
            before_head = self.git(source, "rev-parse", "HEAD")
            before_status = self.git(source, "status", "--porcelain=v1")
            with self.assertRaisesRegex(
                VALIDATE.ProposalValidationError, "git apply --check"
            ):
                VALIDATE.validate_proposals(
                    root,
                    self.manifest(first, second, [proposal]),
                    platform="linux",
                    test_group="portable",
                )
            self.assertEqual(self.git(source, "rev-parse", "HEAD"), before_head)
            self.assertEqual(
                self.git(source, "status", "--porcelain=v1"), before_status
            )

    def test_rejects_a_genuine_change_in_an_exact_source_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, _, first, second = self.make_sources(root)
            contents = self.patch_contents("before", "after")
            proposal = self.proposal(
                "proposal", source="example-first", contents=contents
            )
            self.write_patches(root, [("proposal", contents)])
            (source / "value.txt").write_text("changed\n", encoding="utf-8")

            with self.assertRaisesRegex(
                VALIDATE.ProposalValidationError,
                "example-first integration source contains local changes",
            ):
                VALIDATE.validate_proposals(
                    root,
                    self.manifest(first, second, [proposal]),
                    platform="linux",
                    test_group="portable",
                    proposal_ids=["proposal"],
                )

    def test_selected_proposal_does_not_require_an_unrelated_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, unrelated, first, second = self.make_sources(root)
            contents = self.patch_contents("before", "after")
            proposal = self.proposal(
                "proposal",
                source="example-first",
                contents=contents,
                tests=[
                    {
                        "group": "portable",
                        "platforms": ["linux", "macos"],
                        "cwd": ".",
                        "argv": ["git", "diff", "--check"],
                    }
                ],
            )
            self.write_patches(root, [("proposal", contents)])
            unrelated.rename(root / "uninitialized-unrelated-source")

            VALIDATE.validate_proposals(
                root,
                self.manifest(first, second, [proposal]),
                platform="linux",
                test_group="portable",
                proposal_ids=["proposal"],
            )

    def test_selected_proposal_rejects_a_missing_required_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            required, _, first, second = self.make_sources(root)
            contents = self.patch_contents("before", "after")
            proposal = self.proposal(
                "proposal", source="example-first", contents=contents
            )
            self.write_patches(root, [("proposal", contents)])
            required.rename(root / "uninitialized-required-source")

            with self.assertRaisesRegex(
                VALIDATE.ProposalValidationError,
                "missing source: Integration/Sources/ExampleFirst",
            ):
                VALIDATE.validate_proposals(
                    root,
                    self.manifest(first, second, [proposal]),
                    platform="linux",
                    test_group="portable",
                    proposal_ids=["proposal"],
                )

    def test_rejects_a_symlinked_patch_and_test_working_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            patches = root / "Integration/Patches"
            patches.mkdir(parents=True)
            real_patch = root / "real.patch"
            real_patch.write_text("patch", encoding="utf-8")
            (patches / "proposal.patch").symlink_to(real_patch)
            with self.assertRaisesRegex(
                VALIDATE.ProposalValidationError, "traverses a symlink"
            ):
                VALIDATE.secure_path(
                    root, "Integration/Patches/proposal.patch", kind="patch"
                )

            repository = root / "repository"
            repository.mkdir()
            outside = root / "outside"
            outside.mkdir()
            (repository / "linked").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(
                VALIDATE.ProposalValidationError, "traverses a symlink"
            ):
                VALIDATE.secure_path(repository, "linked", kind="test cwd")

    def test_run_command_passes_argv_without_a_shell(self) -> None:
        completed = subprocess.CompletedProcess(["tool"], 0, "", "")
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(
                VALIDATE.subprocess, "run", return_value=completed
            ) as invoked:
                VALIDATE.run_command(
                    ["tool", "literal argument"],
                    cwd=Path(directory),
                    environment={},
                )
        self.assertEqual(invoked.call_args.args[0], ["tool", "literal argument"])
        self.assertNotIn("shell", invoked.call_args.kwargs)

    def test_disposable_environment_rejects_java_option_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "home"
            with patch.dict(
                os.environ,
                {
                    "JAVA_TOOL_OPTIONS": "-Duser.home=/exact-private-cache",
                    "JDK_JAVA_OPTIONS": "-Duser.home=/override-one",
                    "_JAVA_OPTIONS": "-Duser.home=/override-two",
                    "GRADLE_USER_HOME": "/exact-gradle-cache",
                },
            ):
                environment = VALIDATE.command_environment(home)

            self.assertEqual(
                environment["JAVA_TOOL_OPTIONS"],
                "-Duser.home=/exact-private-cache",
            )
            self.assertNotIn("JDK_JAVA_OPTIONS", environment)
            self.assertNotIn("_JAVA_OPTIONS", environment)
            self.assertEqual(
                environment["GRADLE_USER_HOME"], "/exact-gradle-cache"
            )

    def test_runs_only_the_explicit_group_on_its_declared_platform(self) -> None:
        tests = [
            {
                "group": "portable",
                "platforms": ["linux", "macos"],
                "cwd": ".",
                "argv": [sys.executable, "-c", "pass"],
            },
            {
                "group": "macos-contract",
                "platforms": ["macos"],
                "cwd": ".",
                "argv": ["swift", "test"],
            },
        ]
        proposal = {"id": "proposal", "tests": tests}
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(VALIDATE, "run_command") as run:
                VALIDATE.run_declared_tests(
                    Path(directory),
                    proposal,
                    environment={},
                    platform="linux",
                    test_group="portable",
                    require_group=True,
                )
            run.assert_called_once()
            self.assertEqual(
                run.call_args.args[0], [sys.executable, "-c", "pass"]
            )

            with self.assertRaisesRegex(
                VALIDATE.ProposalValidationError,
                "does not support platform linux",
            ):
                VALIDATE.run_declared_tests(
                    Path(directory),
                    proposal,
                    environment={},
                    platform="linux",
                    test_group="macos-contract",
                    require_group=True,
                )

    def test_explicit_selection_includes_dependencies_and_requires_root_group(self) -> None:
        manifest = {
            "proposals": [
                {"id": "child", "dependsOn": ["parent"]},
                {"id": "unrelated", "dependsOn": []},
                {"id": "parent", "dependsOn": []},
            ]
        }
        ordered, roots = VALIDATE.selected_proposals(manifest, ["child"])
        self.assertEqual(
            [proposal["id"] for proposal in ordered], ["parent", "child"]
        )
        self.assertEqual(roots, {"child"})
        with self.assertRaisesRegex(
            VALIDATE.ProposalValidationError, "unknown integration proposal: missing"
        ):
            VALIDATE.selected_proposals(manifest, ["missing"])

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(
                VALIDATE.ProposalValidationError,
                "declares no tests in requested group portable",
            ):
                VALIDATE.run_declared_tests(
                    Path(directory),
                    {"id": "child", "tests": []},
                    environment={},
                    platform="linux",
                    test_group="portable",
                    require_group=True,
                )


if __name__ == "__main__":
    unittest.main()
