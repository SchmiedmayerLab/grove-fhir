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

    def make_source(self, root: Path) -> tuple[Path, str, str]:
        source = root / "Integration/Sources/Example"
        source.mkdir(parents=True)
        self.git(source, "init", "--quiet", "--initial-branch=main", "--template=")
        (source / "value.txt").write_text("before\n", encoding="utf-8")
        self.git(source, "add", "value.txt")
        self.git(
            source,
            "-c",
            "commit.gpgsign=false",
            "commit",
            "--quiet",
            "-m",
            "Initial fixture",
        )
        first = self.git(source, "rev-parse", "HEAD")
        (source / "second.txt").write_text("second base\n", encoding="utf-8")
        self.git(source, "add", "second.txt")
        self.git(
            source,
            "-c",
            "commit.gpgsign=false",
            "commit",
            "--quiet",
            "-m",
            "Second fixture",
        )
        second = self.git(source, "rev-parse", "HEAD")
        return source, first, second

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
        target: str,
        contents: bytes,
        depends_on: list[str] | None = None,
        applies_after: list[str] | None = None,
        tests: list[dict[str, object]] | None = None,
    ) -> dict[str, object]:
        proposal: dict[str, object] = {
            "id": identifier,
            "source": "example",
            "target": target,
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
            "schemaVersion": 2,
            "sources": [
                {
                    "id": "example",
                    "repository": "https://github.com/SchmiedmayerLab/example.git",
                    "path": "Integration/Sources/Example",
                    "gitlink": second,
                    "targets": [
                        {
                            "id": "first",
                            "ref": "refs/heads/main",
                            "commit": first,
                        },
                        {
                            "id": "second",
                            "ref": "refs/pull/2/head",
                            "commit": second,
                            "predecessor": "first",
                        },
                    ],
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
            source, first, second = self.make_source(root)
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
                "parent", target="first", contents=parent_patch
            )
            child = self.proposal(
                "child",
                target="second",
                contents=child_patch,
                depends_on=["parent"],
                applies_after=["parent"],
                tests=[test],
            )
            self.write_patches(
                root, [("parent", parent_patch), ("child", child_patch)]
            )
            before = self.git(source, "status", "--porcelain=v1")
            VALIDATE.validate_proposals(
                root,
                self.manifest(first, second, [child, parent]),
                platform="linux",
                test_group="portable",
            )
            self.assertEqual(self.git(source, "rev-parse", "HEAD"), second)
            self.assertEqual(self.git(source, "status", "--porcelain=v1"), before)

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
            _, first, second = self.make_source(root)
            contents = self.patch_contents("before", "after")
            proposal = self.proposal(
                "proposal", target="second", contents=contents
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
            source, first, second = self.make_source(root)
            contents = self.patch_contents("not-the-base", "after")
            proposal = self.proposal(
                "proposal", target="second", contents=contents
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
