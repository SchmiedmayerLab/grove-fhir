#!/usr/bin/env python3
"""Select the dependency-closed guide set for a draft PR development build."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHA = re.compile(r"^[0-9a-fA-F]{40}$")


def package_graph() -> tuple[list[str], dict[str, set[str]]]:
    graph = json.loads((ROOT / "catalog/package-graph.json").read_text(encoding="utf-8"))
    order = [package["source"] for package in graph["packages"]]
    by_id = {package["packageId"]: package["source"] for package in graph["packages"]}
    reverse: dict[str, set[str]] = {source: set() for source in order}
    for package in graph["packages"]:
        for dependency in package["dependencies"]:
            dependency_source = by_id.get(dependency.split("#", 1)[0])
            if dependency_source is not None:
                reverse[dependency_source].add(package["source"])
    return order, reverse


def seed_for_path(path: str, guides: set[str]) -> set[str]:
    first = path.split("/", 1)[0]
    if first in guides:
        return {first}
    catalog_seeds = {
        "catalog/measurement-catalog.json": {"mobile"},
        "catalog/sensor-catalog.json": {"sensor"},
        "catalog/healthkit-adapter.json": {"healthkit"},
        "catalog/health-connect-adapter.json": {"health-connect"},
        "catalog/health-connect-identity.json": {"health-connect"},
        "catalog/connected-health-adapter.json": {"connected-health"},
        "catalog/sensorkit-adapter.json": {"sensorkit"},
    }
    if path in catalog_seeds:
        return catalog_seeds[path]
    all_guide_prefixes = (
        "Scripts/",
        "Gemfile",
        "package-lock.json",
        "catalog/",
        "publication/config.json",
    )
    if path.startswith(all_guide_prefixes):
        return set(guides)
    return set()


def select(paths: list[str]) -> list[str]:
    order, reverse = package_graph()
    all_guides = set(order)
    selected: set[str] = set()
    for path in paths:
        selected.update(seed_for_path(path, all_guides))
    queue = list(selected)
    while queue:
        source = queue.pop()
        for dependent in reverse[source]:
            if dependent not in selected:
                selected.add(dependent)
                queue.append(dependent)
    return [guide for guide in order if guide in selected]


def changed_paths(base: str, head: str) -> list[str]:
    if not SHA.fullmatch(base) or not SHA.fullmatch(head):
        raise SystemExit("--base and --head must be complete hexadecimal Git SHAs")
    result = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            "--no-renames",
            "--diff-filter=ACDMRTUXB",
            base,
            head,
            "--",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base")
    parser.add_argument("--head")
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args()
    if bool(args.base) != bool(args.head):
        parser.error("--base and --head must be supplied together")
    paths = changed_paths(args.base, args.head) if args.base else args.paths
    print("guides=" + " ".join(select(paths)))


if __name__ == "__main__":
    main()
