#!/usr/bin/env python3
"""Validate producer-emitted R4 resources without executing the producer."""

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
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any


PACKAGE_ALIAS = re.compile(r"^[a-z][a-z0-9-]*$")
PACKAGE_ID = re.compile(r"^[a-z0-9.-]+$")
GROVE_PROFILE = "https://grovealliance.org/fhir/"
TOP_LEVEL_KEYS = {"schemaVersion", "fhirVersion", "producer", "packages", "resources"}


class ProducerValidationError(ValueError):
    """A deterministic producer-contract validation failure."""


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ProducerValidationError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProducerValidationError(f"cannot read JSON {path}: {error}") from error


def require_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    unknown = set(value) - expected
    if unknown:
        raise ProducerValidationError(f"{label} has unsupported fields: {', '.join(sorted(unknown))}")


def safe_resource_path(root: Path, value: Any) -> Path:
    if not isinstance(value, str) or not value.endswith(".json"):
        raise ProducerValidationError("resource path must be a relative JSON file")
    candidate = PurePosixPath(value)
    if candidate.is_absolute() or not candidate.parts or any(part in {"", ".", ".."} for part in candidate.parts):
        raise ProducerValidationError(f"unsafe resource path: {value!r}")
    path = root.joinpath(*candidate.parts)
    if path.is_symlink() or not path.is_file() or path.resolve().parent != root.resolve() and root.resolve() not in path.resolve().parents:
        raise ProducerValidationError(f"resource is absent, linked, or outside the manifest directory: {value}")
    return path


def validate_manifest(path: Path) -> tuple[dict[str, Any], list[Path]]:
    manifest = read_json(path)
    if not isinstance(manifest, dict):
        raise ProducerValidationError("manifest must be a JSON object")
    require_keys(manifest, TOP_LEVEL_KEYS, "manifest")
    if set(manifest) != TOP_LEVEL_KEYS:
        raise ProducerValidationError("manifest is missing required fields")
    if manifest["schemaVersion"] != 1 or manifest["fhirVersion"] != "4.0.1":
        raise ProducerValidationError("manifest must declare schemaVersion 1 and FHIR 4.0.1")

    producer = manifest["producer"]
    if not isinstance(producer, dict):
        raise ProducerValidationError("producer must be an object")
    require_keys(producer, {"name", "version", "revision"}, "producer")
    if not all(isinstance(producer.get(key), str) and producer[key] for key in ("name", "version")):
        raise ProducerValidationError("producer name and version must be non-empty strings")
    if "revision" in producer and (not isinstance(producer["revision"], str) or not producer["revision"]):
        raise ProducerValidationError("producer revision must be a non-empty string")

    packages = manifest["packages"]
    if not isinstance(packages, list) or not packages:
        raise ProducerValidationError("packages must be a non-empty array")
    aliases: set[str] = set()
    package_ids: set[str] = set()
    for index, package in enumerate(packages):
        if not isinstance(package, dict):
            raise ProducerValidationError(f"packages[{index}] must be an object")
        require_keys(package, {"alias", "packageId", "version"}, f"packages[{index}]")
        if set(package) != {"alias", "packageId", "version"}:
            raise ProducerValidationError(f"packages[{index}] is incomplete")
        alias = package["alias"]
        package_id = package["packageId"]
        if not isinstance(alias, str) or not PACKAGE_ALIAS.fullmatch(alias):
            raise ProducerValidationError(f"invalid package alias: {alias!r}")
        if not isinstance(package_id, str) or not PACKAGE_ID.fullmatch(package_id):
            raise ProducerValidationError(f"invalid package id: {package_id!r}")
        if package["version"] != "0.2.0":
            raise ProducerValidationError("Grove FHIR producer manifests must use package version 0.2.0")
        if alias in aliases or package_id in package_ids:
            raise ProducerValidationError("package aliases and ids must be unique")
        aliases.add(alias)
        package_ids.add(package_id)

    resources = manifest["resources"]
    if not isinstance(resources, list) or not resources:
        raise ProducerValidationError("resources must be a non-empty array")
    paths: list[Path] = []
    relative_paths: set[str] = set()
    for index, entry in enumerate(resources):
        if not isinstance(entry, dict):
            raise ProducerValidationError(f"resources[{index}] must be an object")
        require_keys(entry, {"path", "requiredProfiles"}, f"resources[{index}]")
        if set(entry) != {"path", "requiredProfiles"}:
            raise ProducerValidationError(f"resources[{index}] is incomplete")
        relative = entry["path"]
        if relative in relative_paths:
            raise ProducerValidationError(f"duplicate resource path: {relative}")
        relative_paths.add(relative)
        resource_path = safe_resource_path(path.parent, relative)
        resource = read_json(resource_path)
        if not isinstance(resource, dict) or not isinstance(resource.get("resourceType"), str):
            raise ProducerValidationError(f"{relative} is not a FHIR resource")
        required = entry["requiredProfiles"]
        if (
            not isinstance(required, list)
            or not required
            or any(not isinstance(profile, str) or not profile.startswith(GROVE_PROFILE) for profile in required)
            or len(required) != len(set(required))
        ):
            raise ProducerValidationError(f"{relative} has invalid requiredProfiles")
        actual = resource.get("meta", {}).get("profile", []) if isinstance(resource.get("meta"), dict) else []
        if not isinstance(actual, list) or any(not isinstance(profile, str) for profile in actual):
            raise ProducerValidationError(f"{relative} has invalid meta.profile")
        missing = set(required) - set(actual)
        if missing:
            raise ProducerValidationError(f"{relative} is missing required profiles: {', '.join(sorted(missing))}")
        paths.append(resource_path)
    return manifest, paths


def package_metadata(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ProducerValidationError(f"package is absent or linked: {path}")
    try:
        with tarfile.open(path, "r:gz") as archive:
            member = archive.extractfile("package/package.json")
            if member is None:
                raise ProducerValidationError(f"package has no package/package.json: {path}")
            return json.load(member, object_pairs_hook=unique_object)
    except (tarfile.TarError, OSError, json.JSONDecodeError) as error:
        raise ProducerValidationError(f"cannot read package {path}: {error}") from error


def parse_package_arguments(values: list[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for value in values:
        alias, separator, raw_path = value.partition("=")
        if not separator or not PACKAGE_ALIAS.fullmatch(alias) or not raw_path:
            raise ProducerValidationError(f"--package must be alias=path: {value!r}")
        if alias in result:
            raise ProducerValidationError(f"duplicate --package alias: {alias}")
        result[alias] = Path(raw_path).resolve()
    return result


def validate_packages(manifest: dict[str, Any], supplied: dict[str, Path]) -> list[Path]:
    expected = {entry["alias"]: entry for entry in manifest["packages"]}
    if supplied.keys() != expected.keys():
        missing = expected.keys() - supplied.keys()
        extra = supplied.keys() - expected.keys()
        details = [*(f"missing {item}" for item in sorted(missing)), *(f"unexpected {item}" for item in sorted(extra))]
        raise ProducerValidationError("package arguments do not match manifest: " + ", ".join(details))
    paths: list[Path] = []
    for alias, declaration in expected.items():
        path = supplied[alias]
        metadata = package_metadata(path)
        if metadata.get("name") != declaration["packageId"] or metadata.get("version") != declaration["version"]:
            raise ProducerValidationError(f"{alias} package identity/version does not match the manifest")
        fhir_versions = metadata.get("fhirVersions")
        if fhir_versions != ["4.0.1"]:
            raise ProducerValidationError(f"{alias} package must declare only FHIR 4.0.1")
        paths.append(path)
    return paths


def run_validator(validator: Path, packages: list[Path], resources: list[Path]) -> None:
    if validator.is_symlink() or not validator.is_file():
        raise ProducerValidationError(f"Validator JAR is absent or linked: {validator}")
    with tempfile.TemporaryDirectory(prefix="grove-fhir-producer-") as directory:
        output = Path(directory) / "operation-outcome.json"
        command = ["java", "-jar", str(validator), "-version", "4.0", "-level", "errors"]
        for package in packages:
            command.extend(("-ig", str(package)))
        command.extend(("-output", str(output), *(str(path) for path in resources)))
        result = subprocess.run(command, check=False, text=True)
        if result.returncode != 0:
            raise ProducerValidationError(f"FHIR Validator rejected producer resources (exit {result.returncode})")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--package", action="append", default=[])
    parser.add_argument("--validator", type=Path)
    parser.add_argument("--structural-only", action="store_true")
    arguments = parser.parse_args(argv)
    try:
        manifest_path = arguments.manifest.resolve()
        manifest, resources = validate_manifest(manifest_path)
        if arguments.structural_only:
            if arguments.package or arguments.validator is not None:
                raise ProducerValidationError("--structural-only cannot be combined with package or Validator arguments")
        else:
            if arguments.validator is None:
                raise ProducerValidationError("--validator is required unless --structural-only is used")
            supplied = parse_package_arguments(arguments.package)
            packages = validate_packages(manifest, supplied)
            run_validator(arguments.validator.resolve(), packages, resources)
    except ProducerValidationError as error:
        print(f"Producer conformance failed: {error}", file=sys.stderr)
        return 1
    print(f"Validated {len(resources)} producer resource(s) against FHIR R4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
