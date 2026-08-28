"""Producer manifest, package archive, and declared-package validation."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import tarfile
from pathlib import Path
from typing import Any

from .context import (
    ADAPTER_PACKAGE_PROFILES, GROVE_PROFILE, PACKAGE_ALIAS, PACKAGE_ID,
    RELEASE_VERSION, TOP_LEVEL_KEYS,
)
from .diagnostics import ProducerValidationError
from .exchange_bundle import validate_exchange_bundle, validate_resource_profile_claims
from .io import (
    read_json, require_keys, resolve_unlinked_regular_file, safe_resource_path,
    unique_object,
)
from .mobile_semantics import validate_mobile_semantic_vectors


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
        if package["version"] != RELEASE_VERSION:
            raise ProducerValidationError(
                f"Grove FHIR producer manifests must use package version {RELEASE_VERSION}"
            )
        if alias in aliases or package_id in package_ids:
            raise ProducerValidationError("package aliases and ids must be unique")
        aliases.add(alias)
        package_ids.add(package_id)

    active_adapter_profiles = {
        profile
        for package_id in package_ids
        if package_id in ADAPTER_PACKAGE_PROFILES
        for profile in ADAPTER_PACKAGE_PROFILES[package_id]
    }

    resources = manifest["resources"]
    if not isinstance(resources, list) or not resources:
        raise ProducerValidationError("resources must be a non-empty array")
    paths: list[Path] = []
    resources_by_path: dict[str, dict[str, Any]] = {}
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
        actual_grove_profiles = {
            profile for profile in actual if profile.startswith(GROVE_PROFILE)
        }
        if set(required) != actual_grove_profiles:
            hidden = actual_grove_profiles - set(required)
            raise ProducerValidationError(
                f"{relative} requiredProfiles must equal its direct Grove meta.profile set; "
                f"unlisted: {', '.join(sorted(hidden))}"
            )
        validate_resource_profile_claims(resource, relative, active_adapter_profiles)
        validate_exchange_bundle(resource, relative, active_adapter_profiles)
        resources_by_path[relative] = resource
        paths.append(resource_path)
    validate_mobile_semantic_vectors(manifest["semanticVectors"], resources_by_path)
    return manifest, paths

def package_metadata(path: Path) -> dict[str, Any]:
    path = resolve_unlinked_regular_file(path, "package")
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
        result[alias] = resolve_unlinked_regular_file(
            Path(raw_path), f"{alias} package"
        )
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
