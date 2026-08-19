#!/usr/bin/env python3
"""Apply and test external change proposals in disposable Git repositories."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parent.parent
CHECKER_PATH = ROOT / "Scripts/check-integration-sources.py"
CHECKER_SPEC = importlib.util.spec_from_file_location(
    "check_integration_sources", CHECKER_PATH
)
if CHECKER_SPEC is None or CHECKER_SPEC.loader is None:
    raise RuntimeError(f"Cannot load integration checker: {CHECKER_PATH}")
CHECKER = importlib.util.module_from_spec(CHECKER_SPEC)
CHECKER_SPEC.loader.exec_module(CHECKER)

MAX_PATCH_BYTES = 20 * 1024 * 1024


class ProposalValidationError(RuntimeError):
    """A proposal cannot be materialized or validated safely."""


def command_environment(home: Path) -> dict[str, str]:
    """Return a predictable environment without inherited Git repository state."""
    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("GIT_")
        and key not in {"HOME", "TMPDIR", "JDK_JAVA_OPTIONS", "_JAVA_OPTIONS"}
    }
    environment.update(
        {
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_NO_LAZY_FETCH": "1",
            "GIT_TERMINAL_PROMPT": "0",
            "HOME": str(home),
            "TMPDIR": str(home / "tmp"),
        }
    )
    (home / "tmp").mkdir(parents=True, exist_ok=True)
    return environment


def run_command(
    arguments: Sequence[str],
    *,
    cwd: Path,
    environment: dict[str, str],
    capture_output: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run one argv command directly, never through a command shell."""
    try:
        return subprocess.run(
            list(arguments),
            cwd=cwd,
            env=environment,
            check=True,
            capture_output=capture_output,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or error.stdout or "").strip()
        suffix = f": {detail}" if detail else ""
        rendered = " ".join(arguments)
        raise ProposalValidationError(
            f"command failed in {cwd}: {rendered}{suffix}"
        ) from error
    except OSError as error:
        rendered = " ".join(arguments)
        raise ProposalValidationError(
            f"cannot execute command in {cwd}: {rendered}: {error}"
        ) from error


def output(
    *arguments: str, cwd: Path, environment: dict[str, str]
) -> str:
    return run_command(
        arguments, cwd=cwd, environment=environment
    ).stdout.strip()


def secure_path(
    root: Path,
    relative: str,
    *,
    kind: str,
) -> Path:
    """Resolve a repository-relative path while rejecting every symlink hop."""
    try:
        safe_relative = CHECKER.safe_relative_path(relative)
    except ValueError as error:
        raise ProposalValidationError(str(error)) from error
    if kind == "test cwd" and ".git" in safe_relative.parts:
        raise ProposalValidationError("test cwd cannot enter Git metadata")

    root = root.resolve(strict=True)
    candidate = root
    for component in safe_relative.parts:
        candidate /= component
        try:
            metadata = candidate.lstat()
        except FileNotFoundError as error:
            raise ProposalValidationError(f"missing {kind}: {relative}") from error
        if stat.S_ISLNK(metadata.st_mode):
            raise ProposalValidationError(f"{kind} traverses a symlink: {relative}")

    try:
        candidate.resolve(strict=True).relative_to(root)
    except (OSError, ValueError) as error:
        raise ProposalValidationError(f"{kind} escapes its root: {relative}") from error
    if kind in {"file", "patch"} and not candidate.is_file():
        raise ProposalValidationError(f"{kind} is not a regular file: {relative}")
    if kind in {"source", "test cwd"} and not candidate.is_dir():
        raise ProposalValidationError(f"{kind} is not a directory: {relative}")
    return candidate


def read_manifest(root: Path, relative: Path) -> dict[str, Any]:
    try:
        manifest_path = secure_path(root, relative.as_posix(), kind="file")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProposalValidationError(
            f"cannot read integration manifest: {error}"
        ) from error
    failures = CHECKER.validate_manifest(manifest)
    if failures:
        raise ProposalValidationError(
            "invalid integration manifest:\n- " + "\n- ".join(failures)
        )
    return manifest


def ordered_proposals(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Return stable dependency order; manifest validation has rejected cycles."""
    proposals = {proposal["id"]: proposal for proposal in manifest["proposals"]}
    result: list[dict[str, Any]] = []
    visited: set[str] = set()

    def visit(identifier: str) -> None:
        if identifier in visited:
            return
        proposal = proposals[identifier]
        for dependency in proposal["dependsOn"]:
            visit(dependency)
        visited.add(identifier)
        result.append(proposal)

    for proposal in manifest["proposals"]:
        visit(proposal["id"])
    return result


def selected_proposals(
    manifest: dict[str, Any], identifiers: Sequence[str]
) -> tuple[list[dict[str, Any]], set[str]]:
    """Return dependency-ordered proposals and the explicitly requested roots."""
    ordered = ordered_proposals(manifest)
    if not identifiers:
        return ordered, set()

    proposals = {proposal["id"]: proposal for proposal in ordered}
    unknown = sorted(set(identifiers) - set(proposals))
    if unknown:
        raise ProposalValidationError(
            "unknown integration proposal: " + ", ".join(unknown)
        )
    roots = set(identifiers)
    included: set[str] = set()

    def include(identifier: str) -> None:
        if identifier in included:
            return
        for dependency in proposals[identifier]["dependsOn"]:
            include(dependency)
        included.add(identifier)

    for identifier in identifiers:
        include(identifier)
    return [proposal for proposal in ordered if proposal["id"] in included], roots


def application_plan(
    proposal: dict[str, Any], proposals: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """Return opt-in same-repository patch ancestors followed by the proposal."""
    result: list[dict[str, Any]] = []
    visited: set[str] = set()

    def visit(current: dict[str, Any]) -> None:
        if current["id"] in visited:
            return
        for dependency in current.get("appliesAfter", []):
            visit(proposals[dependency])
        visited.add(current["id"])
        result.append(current)

    visit(proposal)
    return result


def load_patches(root: Path, manifest: dict[str, Any]) -> dict[str, bytes]:
    """Read checksum-verified patch bytes before creating any workspaces."""
    patches: dict[str, bytes] = {}
    for proposal in manifest["proposals"]:
        patch = secure_path(root, proposal["patch"], kind="patch")
        try:
            descriptor = os.open(
                patch,
                os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
            )
        except OSError as error:
            raise ProposalValidationError(
                f"cannot open {proposal['id']} patch safely: {error}"
            ) from error
        with os.fdopen(descriptor, "rb") as stream:
            metadata = os.fstat(stream.fileno())
            if not stat.S_ISREG(metadata.st_mode):
                raise ProposalValidationError(
                    f"{proposal['id']} patch is not a regular file"
                )
            contents = stream.read(MAX_PATCH_BYTES + 1)
        if len(contents) > MAX_PATCH_BYTES:
            raise ProposalValidationError(
                f"{proposal['id']} patch exceeds {MAX_PATCH_BYTES} bytes"
            )
        checksum = hashlib.sha256(contents).hexdigest()
        if checksum != proposal["sha256"]:
            raise ProposalValidationError(
                f"{proposal['id']} patch checksum {checksum} != "
                f"{proposal['sha256']}"
            )
        patches[proposal["id"]] = contents
    return patches


def source_state(
    source: Path, *, environment: dict[str, str]
) -> tuple[str, str, str, str]:
    """Capture external checkout state so validation can prove it stayed unchanged."""
    head = output("git", "rev-parse", "HEAD", cwd=source, environment=environment)
    status = output(
        "git",
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        cwd=source,
        environment=environment,
    )
    references = output(
        "git",
        "for-each-ref",
        "--format=%(refname) %(objectname)",
        cwd=source,
        environment=environment,
    )
    configuration = output(
        "git",
        "config",
        "--local",
        "--null",
        "--list",
        cwd=source,
        environment=environment,
    )
    return head, status, references, configuration


def declared_gitlinks(
    root: Path, sources: dict[str, dict[str, Any]]
) -> dict[str, str]:
    """Read every declared source commit from the root index without opening it."""
    try:
        gitlinks, failures = CHECKER.stage_zero_gitlinks(root)
    except subprocess.CalledProcessError as error:
        raise ProposalValidationError(
            f"cannot read repository gitlinks: {error}"
        ) from error
    if failures:
        raise ProposalValidationError(
            "invalid repository gitlinks:\n- " + "\n- ".join(failures)
        )

    for identifier, source in sources.items():
        path = source["path"]
        recorded = gitlinks.get(path)
        if recorded is None:
            raise ProposalValidationError(
                f"{identifier} source is not a stage-zero gitlink: {path}"
            )
        if recorded != source["commit"]:
            raise ProposalValidationError(
                f"{identifier} gitlink {recorded} != declared commit "
                f"{source['commit']}"
            )
    return gitlinks


def required_source_ids(
    ordered: Sequence[dict[str, Any]],
    proposals: dict[str, dict[str, Any]],
) -> set[str]:
    """Return physical sources needed by the selected dependency/apply closure."""
    required: set[str] = set()
    for proposal in ordered:
        required.add(proposal["source"])
        required.update(
            applied["source"] for applied in application_plan(proposal, proposals)
        )
    return required


def verified_source_path(
    *,
    root: Path,
    identifier: str,
    source: dict[str, Any],
    gitlinks: dict[str, str],
    environment: dict[str, str],
) -> Path:
    """Verify one initialized source before allowing it into materialization."""
    path = secure_path(root, source["path"], kind="source")
    try:
        git_metadata = (path / ".git").lstat()
    except FileNotFoundError as error:
        raise ProposalValidationError(
            f"{identifier} integration source is not initialized"
        ) from error
    if stat.S_ISLNK(git_metadata.st_mode):
        raise ProposalValidationError(
            f"{identifier} integration source Git metadata is a symlink"
        )
    recorded = gitlinks[source["path"]]
    head = output("git", "rev-parse", "HEAD", cwd=path, environment=environment)
    if head != recorded:
        raise ProposalValidationError(
            f"{identifier} checkout {head} != stage-zero gitlink {recorded}"
        )
    if output(
        "git",
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        cwd=path,
        environment=environment,
    ):
        raise ProposalValidationError(
            f"{identifier} integration source contains local changes"
        )
    if output(
        "git",
        "rev-parse",
        "--abbrev-ref",
        "HEAD",
        cwd=path,
        environment=environment,
    ) != "HEAD":
        raise ProposalValidationError(
            f"{identifier} integration source checkout is not detached"
        )
    origin = output(
        "git", "remote", "get-url", "origin", cwd=path, environment=environment
    )
    if origin != source["repository"]:
        raise ProposalValidationError(
            f"{identifier} origin {origin!r} != {source['repository']!r}"
        )
    return path


def materialize_exact_commit(
    *,
    source: Path,
    commit: str,
    destination: Path,
    environment: dict[str, str],
) -> None:
    """Create a self-contained, detached repository from an exact physical source."""
    source_git_directory = Path(
        output(
            "git",
            "rev-parse",
            "--absolute-git-dir",
            cwd=source,
            environment=environment,
        )
    ).resolve(strict=True)
    source_objects = source_git_directory / "objects"
    if source_objects.is_symlink() or not source_objects.is_dir():
        raise ProposalValidationError(
            f"source object database is not a regular directory: {source_objects}"
        )
    if os.pathsep in str(source_objects):
        raise ProposalValidationError("source object path contains a path separator")

    output(
        "git",
        "cat-file",
        "-e",
        f"{commit}^{{commit}}",
        cwd=source,
        environment=environment,
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    run_command(
        ["git", "init", "--quiet", "--template=", str(destination)],
        cwd=destination.parent,
        environment=environment,
    )

    alternate_environment = dict(environment)
    alternate_environment["GIT_ALTERNATE_OBJECT_DIRECTORIES"] = str(source_objects)
    run_command(
        [
            "git",
            "-c",
            "advice.detachedHead=false",
            "checkout",
            "--quiet",
            "--detach",
            commit,
        ],
        cwd=destination,
        environment=alternate_environment,
    )

    # A physical source may be shallow. Mark its exact commit as the temporary
    # repository's boundary so repack copies the tree without requiring parents.
    (destination / ".git/shallow").write_text(f"{commit}\n", encoding="ascii")
    run_command(
        ["git", "repack", "--quiet", "-a", "-d"],
        cwd=destination,
        environment=alternate_environment,
    )

    alternates_file = destination / ".git/objects/info/alternates"
    if alternates_file.exists() or alternates_file.is_symlink():
        raise ProposalValidationError(
            "temporary repository retained an object alternate"
        )
    actual = output(
        "git", "rev-parse", "HEAD", cwd=destination, environment=environment
    )
    if actual != commit:
        raise ProposalValidationError(
            f"temporary repository materialized {actual}; expected {commit}"
        )
    output(
        "git",
        "cat-file",
        "-e",
        f"{commit}^{{commit}}",
        cwd=destination,
        environment=environment,
    )
    run_command(
        ["git", "fsck", "--no-dangling"],
        cwd=destination,
        environment=environment,
    )
    if output("git", "remote", cwd=destination, environment=environment):
        raise ProposalValidationError("temporary repository unexpectedly has a remote")


def write_patch(workspace: Path, identifier: str, contents: bytes) -> Path:
    patch_directory = workspace / "patches"
    patch_directory.mkdir(parents=True, exist_ok=True)
    patch = patch_directory / f"{identifier}.patch"
    patch.write_bytes(contents)
    return patch


def apply_patch(
    repository: Path,
    patch: Path,
    *,
    environment: dict[str, str],
) -> None:
    for mode in ("--check", None):
        arguments = ["git", "apply"]
        if mode is not None:
            arguments.append(mode)
        arguments.extend(["--", str(patch)])
        run_command(
            arguments,
            cwd=repository,
            environment=environment,
        )


def run_declared_tests(
    repository: Path,
    proposal: dict[str, Any],
    *,
    environment: dict[str, str],
    platform: str,
    test_group: str,
    require_group: bool,
) -> None:
    tests = [
        test
        for test in proposal.get("tests", [])
        if test["group"] == test_group
    ]
    if require_group and not tests:
        raise ProposalValidationError(
            f"{proposal['id']} declares no tests in requested group {test_group}"
        )
    disallowed = [test for test in tests if platform not in test["platforms"]]
    if disallowed:
        allowed = ", ".join(disallowed[0]["platforms"])
        raise ProposalValidationError(
            f"{proposal['id']} test group {test_group} does not support "
            f"platform {platform}; allowed: {allowed}"
        )
    for index, test in enumerate(tests, start=1):
        cwd = secure_path(repository, test["cwd"], kind="test cwd")
        print(
            f"  {test_group} test {index}: {' '.join(test['argv'])}",
            flush=True,
        )
        run_command(
            test["argv"],
            cwd=cwd,
            environment=environment,
            capture_output=False,
        )


def validate_proposals(
    root: Path,
    manifest: dict[str, Any],
    *,
    platform: str,
    test_group: str,
    proposal_ids: Sequence[str] = (),
) -> None:
    ordered, requested_roots = selected_proposals(manifest, proposal_ids)
    if not ordered:
        print("No integration proposals are declared; no external code was executed.")
        return

    proposals = {
        proposal["id"]: proposal for proposal in manifest["proposals"]
    }
    sources = {source["id"]: source for source in manifest["sources"]}
    patches = load_patches(root, manifest)
    gitlinks = declared_gitlinks(root, sources)
    required_sources = required_source_ids(ordered, proposals)

    with tempfile.TemporaryDirectory(prefix="grove-fhir-proposals-") as directory:
        workspace = Path(directory).resolve(strict=True)
        home = workspace / "home"
        environment = command_environment(home)
        source_paths = {
            identifier: verified_source_path(
                root=root,
                identifier=identifier,
                source=sources[identifier],
                gitlinks=gitlinks,
                environment=environment,
            )
            for identifier in sorted(required_sources)
        }
        before = {
            identifier: source_state(path, environment=environment)
            for identifier, path in source_paths.items()
        }
        try:
            for ordinal, proposal in enumerate(ordered, start=1):
                identifier = proposal["id"]
                source_id = proposal["source"]
                commit = sources[source_id]["commit"]
                repository = workspace / "repositories" / f"{ordinal}-{identifier}"
                materialize_exact_commit(
                    source=source_paths[source_id],
                    commit=commit,
                    destination=repository,
                    environment=environment,
                )
                plan = application_plan(proposal, proposals)
                print(
                    f"Validating {identifier} at {commit} "
                    f"({len(plan)} patch{'es' if len(plan) != 1 else ''})",
                    flush=True,
                )
                for applied in plan:
                    patch = write_patch(
                        workspace, applied["id"], patches[applied["id"]]
                    )
                    apply_patch(repository, patch, environment=environment)
                run_declared_tests(
                    repository,
                    proposal,
                    environment=environment,
                    platform=platform,
                    test_group=test_group,
                    require_group=identifier in requested_roots,
                )

                actual = output(
                    "git", "rev-parse", "HEAD", cwd=repository, environment=environment
                )
                if actual != commit:
                    raise ProposalValidationError(
                        f"{identifier} changed HEAD from {commit} to {actual}"
                    )
                if output(
                    "git",
                    "rev-parse",
                    "--abbrev-ref",
                    "HEAD",
                    cwd=repository,
                    environment=environment,
                ) != "HEAD":
                    raise ProposalValidationError(
                        f"{identifier} created or checked out a branch"
                    )
                if output(
                    "git",
                    "for-each-ref",
                    "--format=%(refname)",
                    cwd=repository,
                    environment=environment,
                ):
                    raise ProposalValidationError(
                        f"{identifier} created a reference in its temporary repository"
                    )
                if output(
                    "git", "remote", cwd=repository, environment=environment
                ):
                    raise ProposalValidationError(
                        f"{identifier} added a remote to its temporary repository"
                    )
        finally:
            after = {
                identifier: source_state(path, environment=environment)
                for identifier, path in source_paths.items()
            }
            changed = [
                identifier
                for identifier in source_paths
                if before[identifier] != after[identifier]
            ]
            if changed:
                raise ProposalValidationError(
                    "validation changed integration source checkouts: "
                    + ", ".join(changed)
                )

    print(
        f"Validated {len(ordered)} integration proposals for {platform}/"
        f"{test_group} in disposable repositories"
    )


def host_platform() -> str:
    """Return the supported manifest platform for this Python process."""
    if sys.platform == "darwin":
        return "macos"
    if sys.platform.startswith("linux"):
        return "linux"
    raise ProposalValidationError(f"unsupported validation host: {sys.platform}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest", type=Path, default=Path("Integration/sources.json")
    )
    parser.add_argument(
        "--platform", required=True, choices=sorted(CHECKER.TEST_PLATFORMS)
    )
    parser.add_argument("--test-group", required=True)
    parser.add_argument("--proposal", action="append", default=[])
    arguments = parser.parse_args()
    try:
        if not CHECKER.IDENTIFIER.fullmatch(arguments.test_group):
            raise ProposalValidationError(
                "test group must be a lowercase identifier"
            )
        actual_platform = host_platform()
        if arguments.platform != actual_platform:
            raise ProposalValidationError(
                f"requested platform {arguments.platform} does not match "
                f"validation host {actual_platform}"
            )
        manifest = read_manifest(ROOT, arguments.manifest)
        validate_proposals(
            ROOT,
            manifest,
            platform=arguments.platform,
            test_group=arguments.test_group,
            proposal_ids=arguments.proposal,
        )
    except ProposalValidationError as error:
        print(f"Integration proposal validation failed: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
