#!/usr/bin/env python3
"""Verify immutable external-source pins used by integration proposals."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
COMMIT = re.compile(r"^[0-9a-f]{40}$")
IDENTIFIER = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REPOSITORY = re.compile(
    r"^https://github\.com/SchmiedmayerLab/[A-Za-z0-9][A-Za-z0-9._-]*\.git$"
)
SOURCE_PATH = re.compile(r"^Integration/Sources/[A-Za-z0-9][A-Za-z0-9._-]*$")
REFERENCE = re.compile(
    r"^refs/(?:heads/[A-Za-z0-9](?:[A-Za-z0-9._/-]*[A-Za-z0-9])?"
    r"|pull/[1-9][0-9]*/head)$"
)
PATCH_PATH = re.compile(
    r"^Integration/Patches/[a-z0-9](?:[a-z0-9._/-]*[a-z0-9])?\.patch$"
)


def safe_relative_path(value: str) -> Path:
    """Return a normalized repository-relative path without allowing traversal."""
    path = PurePosixPath(value)
    if (
        not value
        or "\0" in value
        or "\\" in value
        or path.is_absolute()
        or ".." in path.parts
        or (value != "." and path.as_posix() != value)
    ):
        raise ValueError(f"unsafe integration path: {value!r}")
    return Path(*path.parts)


def valid_reference(value: Any) -> bool:
    """Accept only unambiguous GitHub branch and pull-request provenance refs."""
    if not isinstance(value, str) or not REFERENCE.fullmatch(value):
        return False
    forbidden = ("..", "//", "@{", "/.", "./")
    return not any(token in value for token in forbidden) and not value.endswith(
        ".lock"
    )


def first_cycle(graph: dict[str, list[str]]) -> list[str] | None:
    """Return one dependency cycle, including its repeated first node."""
    states: dict[str, int] = {}
    stack: list[str] = []
    positions: dict[str, int] = {}

    def visit(node: str) -> list[str] | None:
        states[node] = 1
        positions[node] = len(stack)
        stack.append(node)
        for dependency in graph.get(node, []):
            if dependency not in graph:
                continue
            state = states.get(dependency, 0)
            if state == 0:
                cycle = visit(dependency)
                if cycle:
                    return cycle
            elif state == 1:
                return [*stack[positions[dependency] :], dependency]
        stack.pop()
        positions.pop(node)
        states[node] = 2
        return None

    for node in sorted(graph):
        if states.get(node, 0) == 0:
            cycle = visit(node)
            if cycle:
                return cycle
    return None


def validate_test_commands(proposal_id: str, tests: Any) -> list[str]:
    failures: list[str] = []
    if not isinstance(tests, list) or not tests:
        return [f"{proposal_id} must declare at least one structured test command"]
    for index, test in enumerate(tests):
        label = f"{proposal_id} test {index + 1}"
        if not isinstance(test, dict):
            failures.append(f"{label} must be an object with cwd and argv")
            continue
        unknown = sorted(set(test) - {"cwd", "argv"})
        if unknown:
            failures.append(
                f"{label} contains unsupported fields: {', '.join(unknown)}"
            )
        cwd = test.get("cwd")
        try:
            safe_relative_path(cwd if isinstance(cwd, str) else "")
        except ValueError:
            failures.append(f"{label} cwd must be a safe relative path")
        argv = test.get("argv")
        if (
            not isinstance(argv, list)
            or not argv
            or any(
                not isinstance(argument, str)
                or not argument
                or "\0" in argument
                for argument in argv
            )
        ):
            failures.append(f"{label} argv must contain nonempty strings")
    return failures


def validate_manifest(manifest: Any) -> list[str]:
    failures: list[str] = []
    if not isinstance(manifest, dict):
        return ["integration manifest must be a JSON object"]
    if manifest.get("schemaVersion") != 1:
        failures.append("integration manifest schemaVersion must be 1")
    sources = manifest.get("sources")
    if not isinstance(sources, list) or not sources:
        return [*failures, "integration manifest must contain sources"]

    source_ids: set[str] = set()
    paths: set[str] = set()
    repositories: set[str] = set()
    target_keys: set[tuple[str, str]] = set()
    for source in sources:
        if not isinstance(source, dict):
            failures.append("every integration source must be an object")
            continue
        source_id = source.get("id")
        if not isinstance(source_id, str) or not IDENTIFIER.fullmatch(source_id):
            failures.append(f"invalid integration source id: {source_id!r}")
            continue
        if source_id in source_ids:
            failures.append(f"duplicate integration source id: {source_id}")
        source_ids.add(source_id)

        path = source.get("path")
        if not isinstance(path, str) or not SOURCE_PATH.fullmatch(path):
            failures.append(
                f"{source_id} path must be one directory under Integration/Sources"
            )
        elif path in paths:
            failures.append(f"duplicate integration source path: {path}")
        else:
            paths.add(path)

        repository = source.get("repository")
        if not isinstance(repository, str) or not REPOSITORY.fullmatch(repository):
            failures.append(
                f"{source_id} repository must be an HTTPS SchmiedmayerLab .git URL"
            )
        elif repository in repositories:
            failures.append(f"duplicate integration repository: {repository}")
        else:
            repositories.add(repository)

        gitlink_value = source.get("gitlink")
        gitlink_is_valid = isinstance(gitlink_value, str) and COMMIT.fullmatch(
            gitlink_value
        )
        if not gitlink_is_valid:
            failures.append(f"{source_id} gitlink must be a full lowercase commit SHA")

        targets = source.get("targets")
        if not isinstance(targets, list) or not targets:
            failures.append(f"{source_id} must contain at least one target")
            continue
        target_ids: set[str] = set()
        target_commits: set[str] = set()
        predecessor_graph: dict[str, list[str]] = {}
        for target in targets:
            target_id = target.get("id") if isinstance(target, dict) else None
            if not isinstance(target_id, str) or not IDENTIFIER.fullmatch(target_id):
                failures.append(
                    f"{source_id} contains an invalid target id: {target_id!r}"
                )
                continue
            key = (source_id, target_id)
            if key in target_keys:
                failures.append(
                    f"duplicate integration target: {source_id}/{target_id}"
                )
            target_keys.add(key)
            target_ids.add(target_id)

            reference = target.get("ref")
            if not valid_reference(reference):
                failures.append(
                    f"{source_id}/{target_id} must use a valid heads or "
                    "pull-request ref"
                )
            commit = target.get("commit")
            if not isinstance(commit, str) or not COMMIT.fullmatch(commit):
                failures.append(
                    f"{source_id}/{target_id} commit must be a full lowercase SHA"
                )
            else:
                target_commits.add(commit)

            predecessor = target.get("predecessor")
            predecessor_graph[target_id] = []
            if predecessor is not None:
                if not isinstance(predecessor, str) or not IDENTIFIER.fullmatch(
                    predecessor
                ):
                    failures.append(
                        f"{source_id}/{target_id} predecessor must be a target id"
                    )
                else:
                    predecessor_graph[target_id].append(predecessor)

        for target_id, predecessors in predecessor_graph.items():
            for predecessor in predecessors:
                if predecessor not in target_ids:
                    failures.append(
                        f"{source_id}/{target_id} references unknown predecessor: "
                        f"{predecessor}"
                    )
        cycle = first_cycle(predecessor_graph)
        if cycle:
            failures.append(
                f"{source_id} target predecessor cycle: {' -> '.join(cycle)}"
            )
        if gitlink_is_valid and gitlink_value not in target_commits:
            failures.append(
                f"{source_id} gitlink must equal one declared target commit"
            )

    proposals = manifest.get("proposals")
    if not isinstance(proposals, list):
        failures.append("integration manifest proposals must be a list")
        return failures

    proposal_ids: set[str] = set()
    proposal_dependencies: dict[str, list[str]] = {}
    for proposal in proposals:
        if not isinstance(proposal, dict):
            failures.append("every integration proposal must be an object")
            continue
        proposal_id = proposal.get("id")
        if not isinstance(proposal_id, str) or not IDENTIFIER.fullmatch(proposal_id):
            failures.append(f"invalid integration proposal id: {proposal_id!r}")
            continue
        if proposal_id in proposal_ids:
            failures.append(f"duplicate integration proposal id: {proposal_id}")
        proposal_ids.add(proposal_id)

        source_id = proposal.get("source")
        target_id = proposal.get("target")
        if (source_id, target_id) not in target_keys:
            failures.append(
                f"{proposal_id} references unknown target: {source_id}/{target_id}"
            )

        patch = proposal.get("patch")
        if not isinstance(patch, str) or not PATCH_PATH.fullmatch(patch):
            failures.append(
                f"{proposal_id} patch must be under Integration/Patches and end "
                "in .patch"
            )
        else:
            try:
                safe_relative_path(patch)
            except ValueError as error:
                failures.append(f"{proposal_id}: {error}")

        checksum = proposal.get("sha256")
        if not isinstance(checksum, str) or not re.fullmatch(r"[0-9a-f]{64}", checksum):
            failures.append(f"{proposal_id} sha256 must be a lowercase SHA-256 digest")

        dependencies = proposal.get("dependsOn")
        valid_dependencies: list[str] = []
        if not isinstance(dependencies, list):
            failures.append(f"{proposal_id} dependsOn must be a list")
        else:
            seen_dependencies: set[str] = set()
            for dependency in dependencies:
                if not isinstance(dependency, str) or not IDENTIFIER.fullmatch(
                    dependency
                ):
                    failures.append(
                        f"{proposal_id} contains an invalid dependency id: "
                        f"{dependency!r}"
                    )
                elif dependency in seen_dependencies:
                    failures.append(
                        f"{proposal_id} contains duplicate dependency: {dependency}"
                    )
                else:
                    seen_dependencies.add(dependency)
                    valid_dependencies.append(dependency)
        proposal_dependencies[proposal_id] = valid_dependencies

        failures.extend(validate_test_commands(proposal_id, proposal.get("tests")))
        claims = proposal.get("claims")
        if (
            not isinstance(claims, list)
            or not claims
            or any(not isinstance(claim, str) or not claim.strip() for claim in claims)
        ):
            failures.append(
                f"{proposal_id} must declare at least one nonempty contract claim"
            )

    for proposal_id, dependencies in proposal_dependencies.items():
        for dependency in dependencies:
            if dependency not in proposal_ids:
                failures.append(
                    f"{proposal_id} references unknown proposal dependency: "
                    f"{dependency}"
                )
    dependency_cycle = first_cycle(proposal_dependencies)
    if dependency_cycle:
        failures.append(
            f"proposal dependency cycle: {' -> '.join(dependency_cycle)}"
        )
    return failures


def run(*arguments: str, cwd: Path) -> str:
    result = subprocess.run(
        arguments,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def gitlink(root: Path, relative: str) -> str:
    output = run("git", "ls-files", "--stage", "--", relative, cwd=root)
    rows = [row for row in output.splitlines() if row]
    if len(rows) != 1:
        raise ValueError(f"{relative} is not one tracked gitlink")
    metadata, recorded_path = rows[0].split("\t", 1)
    mode, revision, stage = metadata.split()
    if mode != "160000" or stage != "0" or recorded_path != relative:
        raise ValueError(f"{relative} is not a stage-zero gitlink")
    return revision


def verify_gitmodules(root: Path, manifest: dict[str, Any]) -> list[str]:
    """Require `.gitmodules` to describe exactly the manifest's source set."""
    failures: list[str] = []
    try:
        output = run(
            "git",
            "config",
            "--file",
            ".gitmodules",
            "--get-regexp",
            r"^submodule\..*\..*$",
            cwd=root,
        )
    except subprocess.CalledProcessError as error:
        return [f"cannot read .gitmodules: {error}"]

    modules: dict[str, dict[str, str]] = {}
    for row in output.splitlines():
        try:
            key, value = row.split(maxsplit=1)
            prefix, property_name = key.rsplit(".", 1)
            marker, module_name = prefix.split(".", 1)
        except ValueError:
            failures.append(f"invalid .gitmodules entry: {row!r}")
            continue
        if marker != "submodule" or not module_name:
            failures.append(f"invalid .gitmodules key: {key}")
            continue
        properties = modules.setdefault(module_name, {})
        if property_name in properties:
            failures.append(
                f"duplicate .gitmodules property: {module_name}.{property_name}"
            )
        properties[property_name] = value

    actual_pairs: set[tuple[str, str]] = set()
    actual_paths: set[str] = set()
    actual_repositories: set[str] = set()
    for module_name, properties in modules.items():
        unsupported = sorted(set(properties) - {"path", "url", "shallow"})
        if unsupported:
            failures.append(
                f"{module_name} has unsupported .gitmodules properties: "
                f"{', '.join(unsupported)}"
            )
        path = properties.get("path")
        repository = properties.get("url")
        if path is None or repository is None:
            failures.append(f"{module_name} must declare path and url in .gitmodules")
            continue
        if properties.get("shallow") != "true":
            failures.append(f"{module_name} must set shallow = true in .gitmodules")
        if path in actual_paths:
            failures.append(f"duplicate .gitmodules path: {path}")
        actual_paths.add(path)
        if repository in actual_repositories:
            failures.append(f"duplicate .gitmodules repository: {repository}")
        actual_repositories.add(repository)
        actual_pairs.add((path, repository))

    expected_pairs = {
        (source["path"], source["repository"]) for source in manifest["sources"]
    }
    for path, repository in sorted(expected_pairs - actual_pairs):
        failures.append(f"missing .gitmodules source: {path} -> {repository}")
    for path, repository in sorted(actual_pairs - expected_pairs):
        failures.append(f"unexpected .gitmodules source: {path} -> {repository}")
    if len(modules) != len(manifest["sources"]):
        failures.append(
            ".gitmodules must contain exactly one entry for every manifest source"
        )
    return failures


def verify_repository(
    *, root: Path, source: dict[str, Any], fetch_targets: bool
) -> list[str]:
    failures: list[str] = []
    source_id = source["id"]
    relative = source["path"]
    checkout = root / safe_relative_path(relative)
    try:
        recorded = gitlink(root, relative)
    except (ValueError, subprocess.CalledProcessError) as error:
        return [f"{source_id}: {error}"]
    if recorded != source["gitlink"]:
        failures.append(
            f"{source_id} manifest gitlink {source['gitlink']} != index {recorded}"
        )
    if not checkout.exists():
        failures.append(f"{source_id} submodule is not initialized: {relative}")
        return failures
    try:
        head = run("git", "rev-parse", "HEAD", cwd=checkout)
        if head != recorded:
            failures.append(f"{source_id} checkout {head} != gitlink {recorded}")
        if run("git", "status", "--porcelain", cwd=checkout):
            failures.append(f"{source_id} submodule contains local changes")
        remote = run("git", "remote", "get-url", "origin", cwd=checkout)
        if remote != source["repository"]:
            failures.append(
                f"{source_id} origin {remote!r} != {source['repository']!r}"
            )
            return failures
        if fetch_targets:
            for target in source["targets"]:
                run(
                    "git",
                    "fetch",
                    "--quiet",
                    "--no-tags",
                    "--depth",
                    "1",
                    "origin",
                    target["commit"],
                    cwd=checkout,
                )
                fetched = run(
                    "git", "rev-parse", "--verify", "FETCH_HEAD^{commit}", cwd=checkout
                )
                if fetched != target["commit"]:
                    failures.append(
                        f"{source_id}/{target['id']} fetched {fetched}; "
                        f"expected {target['commit']}"
                    )
    except subprocess.CalledProcessError as error:
        failures.append(f"{source_id}: git command failed: {error}")
    return failures


def verify_proposals(root: Path, manifest: dict[str, Any]) -> list[str]:
    """Verify proposal artifacts without applying or executing them."""
    failures: list[str] = []
    for proposal in manifest["proposals"]:
        patch = root / safe_relative_path(proposal["patch"])
        if patch.is_symlink() or not patch.is_file():
            failures.append(f"{proposal['id']} patch is missing: {proposal['patch']}")
            continue
        actual = hashlib.sha256(patch.read_bytes()).hexdigest()
        if actual != proposal["sha256"]:
            failures.append(
                f"{proposal['id']} patch checksum {actual} != {proposal['sha256']}"
            )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest", type=Path, default=Path("Integration/sources.json")
    )
    parser.add_argument("--fetch-targets", action="store_true")
    arguments = parser.parse_args()
    manifest_path = (ROOT / arguments.manifest).resolve()
    try:
        manifest_path.relative_to(ROOT)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Cannot read integration manifest: {error}")
        return 1

    failures = validate_manifest(manifest)
    if not failures:
        failures.extend(verify_gitmodules(ROOT, manifest))
        for source in manifest["sources"]:
            failures.extend(
                verify_repository(
                    root=ROOT,
                    source=source,
                    fetch_targets=arguments.fetch_targets,
                )
            )
        failures.extend(verify_proposals(ROOT, manifest))
    if failures:
        print("Integration source checks failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(
        f"Verified {len(manifest['sources'])} integration sources, "
        f"{sum(len(source['targets']) for source in manifest['sources'])} targets, "
        f"and {len(manifest['proposals'])} proposals"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
