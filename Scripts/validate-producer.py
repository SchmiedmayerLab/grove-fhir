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
import uuid
from pathlib import Path, PurePosixPath
from typing import Any


PACKAGE_ALIAS = re.compile(r"^[a-z][a-z0-9-]*$")
PACKAGE_ID = re.compile(r"^[a-z0-9.-]+$")
GROVE_PROFILE = "https://grovealliance.org/fhir/"
EXCHANGE_BUNDLE_PROFILE = (
    "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-exchange-bundle"
)
ENTRY_IDENTIFIER_EXTENSION = (
    "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-exchange-entry-identifier"
)
ENTRY_UUID_NAMESPACE = uuid.UUID("a9a39cf1-c944-5d15-a3c2-c395969ea101")
TOP_LEVEL_KEYS = {"schemaVersion", "fhirVersion", "producer", "packages", "resources"}
CATALOG_ROOT = Path(__file__).parents[1] / "catalog"


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


def all_references(value: Any) -> list[str]:
    references: list[str] = []
    if isinstance(value, dict):
        reference = value.get("reference")
        if isinstance(reference, str):
            references.append(reference)
        for child in value.values():
            references.extend(all_references(child))
    elif isinstance(value, list):
        for child in value:
            references.extend(all_references(child))
    return references


def complete_identifier(value: Any, label: str) -> tuple[str, str]:
    if not isinstance(value, dict):
        raise ProducerValidationError(f"{label} must be an Identifier")
    system = value.get("system")
    identifier_value = value.get("value")
    if not isinstance(system, str) or not system or not isinstance(identifier_value, str) or not identifier_value:
        raise ProducerValidationError(f"{label} must have a complete system and value")
    return system, identifier_value


def canonical_json_string(value: str) -> str:
    """Serialize one Unicode scalar-value string using RFC 8785/JCS escaping."""
    escapes = {
        '"': '\\"',
        "\\": "\\\\",
        "\b": "\\b",
        "\t": "\\t",
        "\n": "\\n",
        "\f": "\\f",
        "\r": "\\r",
    }
    output = ['"']
    for character in value:
        point = ord(character)
        if 0xD800 <= point <= 0xDFFF:
            raise ProducerValidationError("entry identity contains an invalid Unicode surrogate")
        if character in escapes:
            output.append(escapes[character])
        elif point <= 0x1F:
            output.append(f"\\u{point:04x}")
        else:
            output.append(character)
    output.append('"')
    return "".join(output)


def canonical_identifier_name(system: str, value: str) -> str:
    """Return the RFC 8785 serialization of exactly ``[system, value]``."""
    return f"[{canonical_json_string(system)},{canonical_json_string(value)}]"


def expected_entry_full_url(system: str, value: str) -> str:
    name = canonical_identifier_name(system, value)
    return f"urn:uuid:{uuid.uuid5(ENTRY_UUID_NAMESPACE, name)}"


def adapter_profile_contract() -> tuple[set[str], set[str]]:
    """Return the exact shared-measurement and adapter profile sets."""
    measurements = read_json(CATALOG_ROOT / "measurement-catalog.json")
    claims = read_json(CATALOG_ROOT / "profile-claims.json")
    shared = {
        f"https://grovealliance.org/fhir/mobile/StructureDefinition/{entry['profile']}"
        for entry in measurements["measurements"]
    }
    adapters = set(claims["observationAdapterClaim"]["adapterProfiles"])
    return shared, adapters


def validate_adapter_profile_claim(resource: dict[str, Any], label: str) -> None:
    """Require an adapter Observation to claim exactly shared metric + adapter."""
    if resource.get("resourceType") != "Observation":
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list) or any(not isinstance(profile, str) for profile in profiles):
        raise ProducerValidationError(f"{label} has invalid meta.profile")
    shared_profiles, adapter_profiles = adapter_profile_contract()
    claimed_adapters = set(profiles) & adapter_profiles
    if not claimed_adapters:
        return
    claimed_shared = set(profiles) & shared_profiles
    if len(claimed_adapters) != 1 or len(claimed_shared) != 1 or len(profiles) != 2 or len(set(profiles)) != 2:
        raise ProducerValidationError(
            f"{label} adapter Observation must claim exactly one shared measurement profile "
            "and exactly one adapter profile"
        )


def validate_exchange_bundle(resource: dict[str, Any], label: str) -> None:
    profiles = resource.get("meta", {}).get("profile", [])
    if EXCHANGE_BUNDLE_PROFILE not in profiles:
        return
    if resource.get("type") != "collection":
        raise ProducerValidationError(f"{label} exchange Bundle must have type collection")
    complete_identifier(resource.get("identifier"), f"{label} Bundle.identifier")
    entries = resource.get("entry")
    if not isinstance(entries, list) or not entries:
        raise ProducerValidationError(f"{label} exchange Bundle must contain entries")
    full_urls: set[str] = set()
    internal_logical_references: set[str] = set()
    entry_resources: list[dict[str, Any]] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or not isinstance(entry.get("resource"), dict):
            raise ProducerValidationError(f"{label} entry[{index}] must contain a resource")
        extensions = entry.get("extension", [])
        identities = [
            extension.get("valueIdentifier")
            for extension in extensions
            if isinstance(extension, dict) and extension.get("url") == ENTRY_IDENTIFIER_EXTENSION
        ] if isinstance(extensions, list) else []
        if len(identities) != 1:
            raise ProducerValidationError(f"{label} entry[{index}] must have one entry identifier")
        system, value = complete_identifier(identities[0], f"{label} entry[{index}] identity")
        expected = expected_entry_full_url(system, value)
        if entry.get("fullUrl") != expected:
            raise ProducerValidationError(f"{label} entry[{index}] fullUrl is not the deterministic UUID URN")
        if expected in full_urls:
            raise ProducerValidationError(f"{label} repeats entry fullUrl {expected}")
        full_urls.add(expected)
        entry_resource = entry["resource"]
        validate_adapter_profile_claim(entry_resource, f"{label} entry[{index}].resource")
        entry_resources.append(entry_resource)
        resource_type = entry_resource.get("resourceType")
        resource_id = entry_resource.get("id")
        if isinstance(resource_type, str) and isinstance(resource_id, str):
            internal_logical_references.add(f"{resource_type}/{resource_id}")
    for reference in all_references(entry_resources):
        if reference.startswith("urn:uuid:") and reference not in full_urls:
            raise ProducerValidationError(f"{label} has unresolved internal UUID reference {reference}")
        if reference in internal_logical_references:
            raise ProducerValidationError(f"{label} internal entry reference must use its UUID URN: {reference}")


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
        validate_adapter_profile_claim(resource, relative)
        validate_exchange_bundle(resource, relative)
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
