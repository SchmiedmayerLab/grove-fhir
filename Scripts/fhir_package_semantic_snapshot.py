#!/usr/bin/env python3
"""Create a deterministic semantic snapshot of a FHIR NPM package.

The snapshot intentionally ignores only FHIR Narrative, known package build timestamps,
and generated publication paths. Authored conformance content, including canonical
resource dates, remains evidence and therefore remains diffable. The exact exclusions
are recorded in every snapshot.
"""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import copy
import hashlib
import re
import tarfile
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

try:
    from fhir_fixture_corpus import canonical_json_bytes, strict_json_loads
except ModuleNotFoundError:  # Imported as Scripts.fhir_package_semantic_snapshot in tests.
    from Scripts.fhir_fixture_corpus import (  # type: ignore[no-redef]
        canonical_json_bytes,
        strict_json_loads,
    )


SNAPSHOT_SCHEMA_VERSION = 1
CANONICAL_RESOURCE_SECTIONS = {
    "StructureDefinition": "structureDefinitions",
    "CodeSystem": "codeSystems",
    "ValueSet": "valueSets",
    "NamingSystem": "namingSystems",
    "ImplementationGuide": "implementationGuides",
}
OTHER_CONFORMANCE_TYPES = frozenset(
    {
        "ActivityDefinition",
        "CapabilityStatement",
        "ChargeItemDefinition",
        "CompartmentDefinition",
        "ConceptMap",
        "EventDefinition",
        "ExampleScenario",
        "GraphDefinition",
        "Library",
        "Measure",
        "MessageDefinition",
        "OperationDefinition",
        "PlanDefinition",
        "Questionnaire",
        "SearchParameter",
        "StructureMap",
        "TerminologyCapabilities",
        "TestScript",
    }
)
FHIR_REFERENCE_MODELS = {
    "4.0.1": {
        "package": "hl7.fhir.r4.core",
        "version": "4.0.1",
        "archiveSha256": "ebd7731df7d36b5b7d39d5fb6c9d77b44bb7fe5742f1a2e87f164738c3289d44",
        # Leaf names derived from every canonical-typed element in the official
        # core package. Names that also occur on non-canonical primitive elements
        # use the versioned path rules below instead of this name set.
        "fields": frozenset(
            {
                "answerValueSet",
                "baseDefinition",
                "capabilities",
                "compartment",
                "defaultValueCanonical",
                "definitionCanonical",
                "derivedFromCanonical",
                "exampleCanonical",
                "fixedCanonical",
                "graph",
                "implementationGuide",
                "import",
                "imports",
                "inputProfile",
                "instantiatesCanonical",
                "library",
                "measure",
                "moduleCanonical",
                "outputProfile",
                "partOf",
                "patternCanonical",
                "profile",
                "questionnaire",
                "replaces",
                "sourceCanonical",
                "supplements",
                "supportedProfile",
                "targetCanonical",
                "targetProfile",
                "valueCanonical",
                "valueSet",
                "workflow",
            }
        ),
    },
    "5.0.0": {
        "package": "hl7.fhir.r5.core",
        "version": "5.0.0",
        "archiveSha256": "74b27cd1bfce9e80eaceac431edf230b0945a443564fbf5512f82e5fa50a80d4",
        "fields": frozenset(
            {
                "abnormalCodedValueSet",
                "actorCanonical",
                "answerValueSet",
                "artifactCanonical",
                "baseDefinition",
                "capabilities",
                "codeMap",
                "compartment",
                "criticalCodedValueSet",
                "defaultValueCanonical",
                "definitionCanonical",
                "derivedFromCanonical",
                "eventCanonical",
                "fixedCanonical",
                "graph",
                "implementationGuide",
                "import",
                "imports",
                "inputProfile",
                "instantiatesCanonical",
                "library",
                "linkCanonical",
                "measure",
                "moduleCanonical",
                "normalCodedValueSet",
                "observationRequirement",
                "observationResultRequirement",
                "otherMap",
                "outputProfile",
                "partOf",
                "patternCanonical",
                "profile",
                "questionnaire",
                "replaces",
                "sourceScopeCanonical",
                "specimenRequirement",
                "structureProfileCanonical",
                "subjectCanonical",
                "subscriptionTopic",
                "supplements",
                "supportedProfile",
                "targetProfile",
                "targetScopeCanonical",
                "typeCanonical",
                "validCodedValueSet",
                "valueAlternatives",
                "valueCanonical",
                "valueSet",
                "workflow",
            }
        ),
    },
}

AMBIGUOUS_CANONICAL_PATHS = {
    "4.0.1": frozenset(
        {
            "ActivityDefinition.transform",
            "CapabilityStatement.instantiates",
            "CapabilityStatement.messaging.supportedMessage.definition",
            "CapabilityStatement.rest.resource.operation.definition",
            "CapabilityStatement.rest.resource.searchParam.definition",
            "ConceptMap.group.element.target.dependsOn.system",
            "ConceptMap.group.unmapped.url",
            "ImplementationGuide.dependsOn.uri",
            "MessageHeader.definition",
            "MessageDefinition.allowedResponse.message",
            "MessageDefinition.base",
            "MessageDefinition.parent",
            "OperationDefinition.base",
            "PlanDefinition.action.transform",
            "Questionnaire.derivedFrom",
            "SearchParameter.component.definition",
            "SearchParameter.derivedFrom",
            "StructureMap.structure.url",
            "TerminologyCapabilities.codeSystem.uri",
        }
    ),
    "5.0.0": frozenset(
        {
            "ActivityDefinition.transform",
            "ActorDefinition.derivedFrom",
            "CapabilityStatement.instantiates",
            "CapabilityStatement.messaging.supportedMessage.definition",
            "CapabilityStatement.rest.resource.operation.definition",
            "CapabilityStatement.rest.resource.searchParam.definition",
            "ConceptMap.group.source",
            "ConceptMap.group.target",
            "ConceptMap.property.system",
            "ImplementationGuide.dependsOn.uri",
            "MessageHeader.definition",
            "MessageDefinition.allowedResponse.message",
            "MessageDefinition.base",
            "MessageDefinition.parent",
            "OperationDefinition.base",
            "PlanDefinition.action.transform",
            "Questionnaire.derivedFrom",
            "RequestOrchestration.action.transform",
            "Requirements.actor",
            "Requirements.derivedFrom",
            "SearchParameter.component.definition",
            "SearchParameter.derivedFrom",
            "StructureMap.structure.url",
            "Subscription.topic",
            "SubscriptionStatus.topic",
            "SubscriptionTopic.derivedFrom",
            "TerminologyCapabilities.codeSystem.uri",
            "TestReport.testScript",
            "TestScript.scope.artifact",
        }
    ),
}
PACKAGE_BUILD_KEYS = frozenset(
    {"build-date", "build-timestamp", "buildDate", "buildTimestamp", "date", "directories"}
)
LOCAL_PATH = re.compile(r"^(?:file:/+|/|[A-Za-z]:[\\/])")
BUILT_SUFFIX = re.compile(r"\s*\(built [^)]*\)\s*$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
PUBLISHER_DIAGNOSTIC_MEMBERS = frozenset(
    {"other/.index.json", "other/validation-oo.json", "other/validation-summary.json"}
)
NORMALIZATION = {
    "schemaVersion": 1,
    "excluded": [
        "FHIR DomainResource.text at every nesting level",
        "FHIR Meta.lastUpdated at every nesting level",
        "package.json date, build-date, buildDate, build-timestamp, and buildTimestamp",
        "package.json directories and local-filesystem url",
        "FHIR Publisher '(built ...)' package description suffix",
        "Canonical resource date only when its wall-clock digits exactly match package.json date",
        "ImplementationGuide rendered page, template, resource, and manifest paths",
        "FHIR Publisher other/.index.json, validation-oo.json, and validation-summary.json",
    ],
}


class SnapshotError(ValueError):
    """Report package or snapshot content that cannot be made unambiguous."""


def semantic_hash(value: Any) -> str:
    """Hash semantic JSON without introducing serialization variance."""
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _safe_archive_name(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if (
        not value
        or "\0" in value
        or "\\" in value
        or path.is_absolute()
        or ".." in path.parts
    ):
        raise SnapshotError(f"unsafe FHIR package archive member: {value!r}")
    return path


def _package_directory(path: Path) -> Path:
    nested = path / "package"
    if nested.is_symlink():
        raise SnapshotError(f"FHIR package root may not be a symlink: {nested}")
    if (nested / "package.json").is_file():
        if not nested.resolve().is_relative_to(path.resolve()):
            raise SnapshotError(f"FHIR package root escapes its input directory: {nested}")
        return nested
    if (path / "package.json").is_file():
        return path
    raise SnapshotError(f"FHIR package directory has no package.json: {path}")


def read_package_json_files(path: Path) -> dict[str, Any]:
    """Read JSON members from an unpacked FHIR package or package.tgz."""
    encoded: dict[str, bytes] = {}
    if path.is_symlink():
        raise SnapshotError(f"FHIR package input may not be a symlink: {path}")
    if path.is_dir():
        package = _package_directory(path)
        package_root = package.resolve()
        for candidate in sorted(package.rglob("*")):
            if candidate.is_symlink():
                raise SnapshotError(f"FHIR package directory contains a symlink: {candidate}")
            if candidate.suffix != ".json":
                continue
            if candidate.is_file():
                if not candidate.resolve().is_relative_to(package_root):
                    raise SnapshotError(f"FHIR package member escapes its directory: {candidate}")
                encoded[candidate.relative_to(package).as_posix()] = candidate.read_bytes()
    elif path.is_file():
        try:
            archive = tarfile.open(path, "r:*")
        except (OSError, tarfile.TarError) as error:
            raise SnapshotError(f"unable to open FHIR package {path}: {error}") from error
        with archive:
            for member in archive.getmembers():
                name = _safe_archive_name(member.name)
                if member.issym() or member.islnk():
                    raise SnapshotError(
                        f"FHIR package archive contains a link: {member.name}"
                    )
                if not member.isfile() or name.suffix != ".json":
                    continue
                parts = name.parts
                if parts and parts[0] == "package":
                    relative = PurePosixPath(*parts[1:]).as_posix()
                else:
                    relative = name.as_posix()
                if not relative:
                    continue
                if relative in encoded:
                    raise SnapshotError(f"duplicate FHIR package member: {relative}")
                extracted = archive.extractfile(member)
                if extracted is None:
                    raise SnapshotError(f"unable to read FHIR package member: {member.name}")
                encoded[relative] = extracted.read()
    else:
        raise SnapshotError(f"FHIR package does not exist: {path}")

    decoded: dict[str, Any] = {}
    for name, data in sorted(encoded.items()):
        try:
            decoded[name] = strict_json_loads(data.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as error:
            raise SnapshotError(f"invalid JSON in FHIR package member {name}: {error}") from error
    if "package.json" not in decoded:
        raise SnapshotError(f"FHIR package has no package/package.json: {path}")
    if not isinstance(decoded["package.json"], dict):
        raise SnapshotError("FHIR package package.json must be an object")
    return decoded


def _semantic_resource_members(files: Mapping[str, Any]) -> list[str]:
    index = files.get(".index.json")
    if not isinstance(index, dict) or index.get("index-version") != 2:
        raise SnapshotError("FHIR package .index.json must use index-version 2")
    entries = index.get("files")
    if not isinstance(entries, list):
        raise SnapshotError("FHIR package .index.json files must be a list")
    indexed: dict[str, Mapping[str, Any]] = {}
    for position, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise SnapshotError(f"FHIR package index entry {position + 1} must be an object")
        filename = entry.get("filename")
        if (
            not isinstance(filename, str)
            or not filename
            or PurePosixPath(filename).name != filename
            or filename in {"package.json", ".index.json"}
        ):
            raise SnapshotError(
                f"FHIR package index entry {position + 1} has an unsafe filename"
            )
        if filename in indexed:
            raise SnapshotError(f"duplicate FHIR package index filename: {filename}")
        indexed[filename] = entry

    root_resources = {
        name
        for name in files
        if "/" not in name and name not in {"package.json", ".index.json"}
    }
    missing = sorted(set(indexed) - files.keys())
    unindexed = sorted(root_resources - indexed.keys())
    if missing:
        raise SnapshotError("FHIR package index references missing files: " + ", ".join(missing))
    if unindexed:
        raise SnapshotError(
            "FHIR package contains unindexed root resources: " + ", ".join(unindexed)
        )

    members = sorted([*indexed, *(name for name in files if name.startswith("example/"))])
    unexpected = sorted(
        name
        for name in files
        if name not in {"package.json", ".index.json"}
        and name not in members
        and name not in PUBLISHER_DIAGNOSTIC_MEMBERS
    )
    if unexpected:
        raise SnapshotError(
            "FHIR package contains unsupported JSON members: " + ", ".join(unexpected)
        )

    for name in members:
        resource = files[name]
        if not isinstance(resource, dict) or not isinstance(resource.get("resourceType"), str):
            raise SnapshotError(f"FHIR package semantic member is not a FHIR resource: {name}")
        entry = indexed.get(name)
        if entry is not None:
            for field in ("resourceType", "id", "url", "version"):
                if field in entry and entry[field] != resource.get(field):
                    raise SnapshotError(
                        f"FHIR package index {field} does not match {name}"
                    )
    return members


def _sanitize_package_metadata(
    metadata: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    package = copy.deepcopy(dict(metadata))
    for key in PACKAGE_BUILD_KEYS:
        package.pop(key, None)
    url = package.get("url")
    if isinstance(url, str) and LOCAL_PATH.match(url):
        package.pop("url")
    description = package.get("description")
    if isinstance(description, str):
        package["description"] = BUILT_SUFFIX.sub("", description)
    dependencies = package.pop("dependencies", {})
    if dependencies is None:
        dependencies = {}
    if not isinstance(dependencies, dict) or any(
        not isinstance(name, str) or not isinstance(version, str)
        for name, version in dependencies.items()
    ):
        raise SnapshotError("FHIR package dependencies must map package ids to versions")
    return package, dict(sorted(dependencies.items()))


def sanitize_resource(
    resource: Mapping[str, Any], package_build_timestamp: str | None = None
) -> dict[str, Any]:
    """Remove only known generated narrative, timestamps, and publication paths."""
    sanitized = copy.deepcopy(dict(resource))
    sanitized.pop("text", None)
    meta = sanitized.get("meta")
    if isinstance(meta, dict):
        meta.pop("lastUpdated", None)
        if not meta:
            sanitized.pop("meta", None)
    if (
        package_build_timestamp is not None
        and (
            sanitized.get("resourceType") in CANONICAL_RESOURCE_SECTIONS
            or sanitized.get("resourceType") in OTHER_CONFORMANCE_TYPES
            or isinstance(sanitized.get("url"), str)
        )
    ):
        date = sanitized.get("date")
        if (
            isinstance(date, str)
            and re.sub(r"[^0-9]", "", date)[:14] == package_build_timestamp
        ):
            sanitized.pop("date")
    if sanitized.get("resourceType") == "ImplementationGuide":
        _strip_implementation_guide_build_data(sanitized)
    _strip_nested_narratives(sanitized)
    return sanitized


def _strip_implementation_guide_build_data(guide: dict[str, Any]) -> None:
    """Remove Publisher timestamps/locations while retaining the IG resource graph."""
    definition = guide.get("definition")
    if isinstance(definition, dict):
        parameters = definition.get("parameter")
        if isinstance(parameters, list):
            definition["parameter"] = [
                parameter
                for parameter in parameters
                if not (
                    isinstance(parameter, dict)
                    and isinstance(parameter.get("code"), str)
                    and parameter["code"].startswith(("path-", "template-"))
                )
            ]
            if not definition["parameter"]:
                definition.pop("parameter")
        extensions = definition.get("extension")
        if isinstance(extensions, list):
            definition["extension"] = [
                extension for extension in extensions if not _is_path_parameter(extension)
            ]
            if not definition["extension"]:
                definition.pop("extension")
        resources = definition.get("resource")
        if isinstance(resources, list):
            for resource in resources:
                if isinstance(resource, dict):
                    _remove_extensions(
                        resource,
                        {"http://hl7.org/fhir/StructureDefinition/implementationguide-page"},
                    )
        _strip_definition_page_paths(definition.get("page"))
    _strip_manifest_paths(guide.get("manifest"))


def _is_path_parameter(extension: Any) -> bool:
    if (
        not isinstance(extension, dict)
        or extension.get("url")
        != "http://hl7.org/fhir/tools/StructureDefinition/ig-parameter"
        or not isinstance(extension.get("extension"), list)
    ):
        return False
    for part in extension["extension"]:
        if not isinstance(part, dict) or part.get("url") != "code":
            continue
        code = part.get("valueCode", part.get("valueString"))
        return isinstance(code, str) and code.startswith(("path-", "template-"))
    return False


def _remove_extensions(value: dict[str, Any], urls: set[str]) -> None:
    extensions = value.get("extension")
    if not isinstance(extensions, list):
        return
    value["extension"] = [
        extension
        for extension in extensions
        if not isinstance(extension, dict) or extension.get("url") not in urls
    ]
    if not value["extension"]:
        value.pop("extension")


def _strip_definition_page_paths(page: Any) -> None:
    if not isinstance(page, dict):
        return
    page.pop("nameUrl", None)
    _remove_extensions(
        page,
        {"http://hl7.org/fhir/tools/StructureDefinition/ig-page-name"},
    )
    children = page.get("page")
    if isinstance(children, list):
        for child in children:
            _strip_definition_page_paths(child)


def _strip_manifest_paths(manifest: Any) -> None:
    """Remove rendered locations while retaining the manifest's resource graph."""
    if not isinstance(manifest, dict):
        return
    manifest.pop("rendering", None)
    manifest.pop("image", None)
    manifest.pop("other", None)
    resources = manifest.get("resource")
    if isinstance(resources, list):
        for resource in resources:
            if isinstance(resource, dict):
                resource.pop("relativePath", None)

    def strip_page_paths(page: Any) -> None:
        if not isinstance(page, dict):
            return
        page.pop("nameUrl", None)
        children = page.get("page")
        if isinstance(children, list):
            for child in children:
                strip_page_paths(child)

    strip_page_paths(manifest.get("page"))


def _strip_nested_narratives(value: Any) -> None:
    if isinstance(value, dict):
        if isinstance(value.get("resourceType"), str):
            value.pop("text", None)
            meta = value.get("meta")
            if isinstance(meta, dict):
                meta.pop("lastUpdated", None)
                if not meta:
                    value.pop("meta", None)
        for child in value.values():
            _strip_nested_narratives(child)
    elif isinstance(value, list):
        for child in value:
            _strip_nested_narratives(child)


def _resource_key(resource: Mapping[str, Any], anonymous_hint: str | None = None) -> str:
    resource_type = resource.get("resourceType")
    canonical = resource.get("url")
    if isinstance(canonical, str) and canonical:
        # Canonical resources align across package versions by URL. The authored
        # version remains in the resource and therefore appears as a field-level diff.
        return canonical
    identifier = resource.get("id")
    if isinstance(resource_type, str) and isinstance(identifier, str) and identifier:
        return f"{resource_type}/{identifier}"
    if isinstance(resource_type, str) and resource_type:
        # Anonymous examples (notably transaction Bundles) have no logical id. A
        # package member stem is stable across edits and contains no machine path.
        if anonymous_hint:
            safe_hint = re.sub(r"[^A-Za-z0-9._-]", "-", anonymous_hint)
            return f"{resource_type}/package-file-{safe_hint}"
        return f"{resource_type}/sha256-{semantic_hash(resource)}"
    raise SnapshotError("FHIR resource has no resourceType")


def _entry(
    resource: Mapping[str, Any], package_build_timestamp: str | None
) -> dict[str, Any]:
    sanitized = sanitize_resource(resource, package_build_timestamp)
    return {"sha256": semantic_hash(sanitized), "resource": sanitized}


def _pointer_token(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _is_canonical_value(
    fhir_version: str,
    resource_type: str,
    logical_path: tuple[str, ...],
    container: Mapping[str, Any],
    key: str,
    value: Any,
) -> bool:
    model = FHIR_REFERENCE_MODELS[fhir_version]
    if key in model["fields"]:
        return True
    absolute_path = ".".join((resource_type, *logical_path))
    if absolute_path in AMBIGUOUS_CANONICAL_PATHS[fhir_version]:
        return True
    if key == "source" and logical_path[-3:] == ("element", "constraint", "source"):
        return True
    return (
        key == "resource"
        and isinstance(container.get("type"), str)
        and isinstance(value, str)
    )


def _reference_edges(
    source: str, resource: Any, fhir_version: str
) -> list[dict[str, str]]:
    edges: set[tuple[str, str, str, str]] = set()
    if fhir_version not in FHIR_REFERENCE_MODELS:
        raise SnapshotError(f"unsupported reference graph FHIR version: {fhir_version}")
    root_resource_type = (
        resource.get("resourceType")
        if isinstance(resource, dict) and isinstance(resource.get("resourceType"), str)
        else ""
    )

    def visit(
        value: Any,
        path: str,
        logical_path: tuple[str, ...],
        current_resource_type: str,
    ) -> None:
        if isinstance(value, dict):
            nested_resource_type = value.get("resourceType")
            if isinstance(nested_resource_type, str):
                current_resource_type = nested_resource_type
                logical_path = ()
            for key, child in value.items():
                child_path = f"{path}/{_pointer_token(key)}"
                child_logical_path = (*logical_path, key)
                if key == "reference" and isinstance(child, str) and child:
                    edges.add((source, "reference", child, child_path))
                elif _is_canonical_value(
                    fhir_version,
                    current_resource_type,
                    child_logical_path,
                    value,
                    key,
                    child,
                ):
                    if isinstance(child, str) and child:
                        edges.add((source, "canonical", child, child_path))
                    elif isinstance(child, list):
                        for index, item in enumerate(child):
                            if isinstance(item, str) and item:
                                edges.add(
                                    (source, "canonical", item, f"{child_path}/{index}")
                                )
                visit(child, child_path, child_logical_path, current_resource_type)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, f"{path}/{index}", logical_path, current_resource_type)

    visit(resource, "", (), root_resource_type)
    return [
        {"source": item[0], "kind": item[1], "target": item[2], "path": item[3]}
        for item in sorted(edges)
    ]


def _example_entry(
    resource: Mapping[str, Any],
    package_build_timestamp: str | None,
) -> dict[str, Any]:
    sanitized = sanitize_resource(resource, package_build_timestamp)
    profiles: list[str] = []
    meta = sanitized.get("meta")
    if isinstance(meta, dict) and isinstance(meta.get("profile"), list):
        profiles = sorted(
            {profile for profile in meta["profile"] if isinstance(profile, str)}
        )
    return {
        "sha256": semantic_hash(sanitized),
        "profiles": profiles,
        "resource": sanitized,
    }


def create_snapshot(path: Path) -> dict[str, Any]:
    """Create a deterministic semantic snapshot for one package source."""
    files = read_package_json_files(path)
    raw_package_date = files["package.json"].get("date")
    package_build_timestamp = (
        raw_package_date
        if isinstance(raw_package_date, str)
        and re.fullmatch(r"[0-9]{14}", raw_package_date)
        else None
    )
    package, dependencies = _sanitize_package_metadata(files["package.json"])
    fhir_versions = package.get("fhirVersions")
    if (
        not isinstance(fhir_versions, list)
        or len(fhir_versions) != 1
        or fhir_versions[0] not in FHIR_REFERENCE_MODELS
    ):
        raise SnapshotError(
            "FHIR package must declare exactly one supported fhirVersions value: "
            + ", ".join(sorted(FHIR_REFERENCE_MODELS))
        )
    fhir_version = fhir_versions[0]
    reference_model = FHIR_REFERENCE_MODELS[fhir_version]
    snapshot: dict[str, Any] = {
        "schemaVersion": SNAPSHOT_SCHEMA_VERSION,
        "normalization": copy.deepcopy(NORMALIZATION),
        "referenceModel": {
            "fhirVersion": fhir_version,
            "package": reference_model["package"],
            "version": reference_model["version"],
            "archiveSha256": reference_model["archiveSha256"],
        },
        "package": package,
        "dependencies": dependencies,
        "structureDefinitions": {},
        "codeSystems": {},
        "valueSets": {},
        "namingSystems": {},
        "implementationGuides": {},
        "otherConformance": {},
        "examples": {},
        "referenceGraph": [],
    }
    reference_graph: list[dict[str, str]] = []
    identities: set[str] = set()
    for name in _semantic_resource_members(files):
        value = files[name]
        resource_type = value["resourceType"]
        sanitized = sanitize_resource(value, package_build_timestamp)
        anonymous_hint = PurePosixPath(name).stem
        key = _resource_key(sanitized, anonymous_hint)
        if resource_type in CANONICAL_RESOURCE_SECTIONS:
            section = snapshot[CANONICAL_RESOURCE_SECTIONS[resource_type]]
            entry = _entry(value, package_build_timestamp)
        elif resource_type in OTHER_CONFORMANCE_TYPES or isinstance(value.get("url"), str):
            section = snapshot["otherConformance"]
            entry = _entry(value, package_build_timestamp)
        else:
            section = snapshot["examples"]
            entry = _example_entry(value, package_build_timestamp)
        if key in identities:
            raise SnapshotError(f"duplicate semantic FHIR resource identity: {key}")
        identities.add(key)
        section[key] = entry
        reference_graph.extend(_reference_edges(key, sanitized, fhir_version))
    snapshot["referenceGraph"] = sorted(
        reference_graph,
        key=lambda edge: (edge["source"], edge["kind"], edge["target"], edge["path"]),
    )
    return snapshot


def write_snapshot(snapshot: Mapping[str, Any], output: Path | None) -> None:
    """Write canonical snapshot JSON to a file or stdout."""
    data = canonical_json_bytes(snapshot)
    if output is None:
        import sys

        sys.stdout.buffer.write(data)
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)


def load_snapshot(path: Path) -> dict[str, Any]:
    """Load a schema-compatible semantic snapshot."""
    try:
        snapshot = strict_json_loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as error:
        raise SnapshotError(f"unable to read semantic snapshot {path}: {error}") from error
    if not isinstance(snapshot, dict):
        raise SnapshotError(f"semantic snapshot must be a JSON object: {path}")
    if snapshot.get("schemaVersion") != SNAPSHOT_SCHEMA_VERSION:
        raise SnapshotError(
            f"unsupported semantic snapshot schemaVersion in {path}: "
            f"{snapshot.get('schemaVersion')!r}"
        )
    failures = validate_snapshot(snapshot)
    if failures:
        raise SnapshotError(f"invalid semantic snapshot {path}:\n" + "\n".join(failures))
    return snapshot


def _structure_definition_coverage(resource: Mapping[str, Any]) -> list[str]:
    """Return missing differential fields only when malformed data would be dropped.

    The snapshot stores the complete authored differential. This helper documents and
    tests the semantic categories the evidence contract promises to retain.
    """
    differential = resource.get("differential")
    if differential is None:
        return []
    if not isinstance(differential, dict) or not isinstance(differential.get("element"), list):
        return ["StructureDefinition.differential.element must be a list"]
    return []


def validate_snapshot(snapshot: Mapping[str, Any]) -> list[str]:
    """Validate snapshot shape and retained StructureDefinition differential content."""
    failures: list[str] = []
    if snapshot.get("schemaVersion") != SNAPSHOT_SCHEMA_VERSION:
        failures.append(f"semantic snapshot schemaVersion must be {SNAPSHOT_SCHEMA_VERSION}")
    required_objects = {
        "package",
        "dependencies",
        "structureDefinitions",
        "codeSystems",
        "valueSets",
        "namingSystems",
        "implementationGuides",
        "otherConformance",
        "examples",
    }
    for field in sorted(required_objects):
        if not isinstance(snapshot.get(field), dict):
            failures.append(f"semantic snapshot {field} must be an object")
    expected_fields = required_objects | {
        "schemaVersion",
        "normalization",
        "referenceGraph",
        "referenceModel",
    }
    unknown = sorted(set(snapshot) - expected_fields)
    if unknown:
        failures.append("semantic snapshot contains unsupported fields: " + ", ".join(unknown))
    if snapshot.get("normalization") != NORMALIZATION:
        failures.append("semantic snapshot normalization contract does not match schema 1")
    reference_model = snapshot.get("referenceModel")
    fhir_version = (
        reference_model.get("fhirVersion")
        if isinstance(reference_model, dict)
        else None
    )
    expected_reference_model = FHIR_REFERENCE_MODELS.get(fhir_version)
    if (
        expected_reference_model is None
        or reference_model
        != {
            "fhirVersion": fhir_version,
            "package": expected_reference_model["package"],
            "version": expected_reference_model["version"],
            "archiveSha256": expected_reference_model["archiveSha256"],
        }
    ):
        failures.append("semantic snapshot referenceModel is unsupported or inconsistent")
    graph = snapshot.get("referenceGraph")
    if not isinstance(graph, list):
        failures.append("semantic snapshot referenceGraph must be a list")
    sections = {
        "structureDefinitions": "StructureDefinition",
        "codeSystems": "CodeSystem",
        "valueSets": "ValueSet",
        "namingSystems": "NamingSystem",
        "implementationGuides": "ImplementationGuide",
        "otherConformance": None,
    }
    expected_graph: list[dict[str, str]] = []
    for section_name, expected_type in sections.items():
        section = snapshot.get(section_name)
        if not isinstance(section, dict):
            continue
        for key, entry in section.items():
            resource = entry.get("resource") if isinstance(entry, dict) else None
            if not isinstance(resource, dict):
                failures.append(f"{section_name} {key} entry must contain resource")
                continue
            if set(entry) != {"sha256", "resource"}:
                failures.append(
                    f"{section_name} {key} entry must contain only sha256 and resource"
                )
            if expected_type is not None and resource.get("resourceType") != expected_type:
                failures.append(
                    f"{section_name} {key} must contain a {expected_type} resource"
                )
            if section_name == "structureDefinitions":
                failures.extend(
                    f"StructureDefinition {key}: {failure}"
                    for failure in _structure_definition_coverage(resource)
                )
            if entry.get("sha256") != semantic_hash(resource):
                failures.append(f"{section_name} {key} semantic hash does not match")
            try:
                identity = _resource_key(resource)
            except SnapshotError as error:
                failures.append(f"{section_name} {key}: {error}")
            else:
                if identity != key:
                    failures.append(
                        f"{section_name} {key} resource identity resolves to {identity}"
                    )
            if isinstance(fhir_version, str) and fhir_version in FHIR_REFERENCE_MODELS:
                expected_graph.extend(_reference_edges(key, resource, fhir_version))

    examples = snapshot.get("examples")
    if isinstance(examples, dict):
        for key, entry in examples.items():
            if not isinstance(entry, dict) or set(entry) != {
                "sha256",
                "profiles",
                "resource",
            }:
                failures.append(
                    f"example {key} must contain sha256, profiles, and resource"
                )
                continue
            if not isinstance(entry.get("sha256"), str) or not SHA256.fullmatch(
                entry["sha256"]
            ):
                failures.append(f"example {key} must contain a lowercase SHA-256")
            resource = entry.get("resource")
            if not isinstance(resource, dict):
                failures.append(f"example {key} resource must be an object")
            elif entry.get("sha256") != semantic_hash(resource):
                failures.append(f"example {key} semantic hash does not match")
            else:
                stable_identity = _resource_key(resource)
                if (
                    not key.startswith(
                        f"{resource.get('resourceType')}/package-file-"
                    )
                    and stable_identity != key
                ):
                    failures.append(
                        f"example {key} resource identity resolves to {stable_identity}"
                    )
                if isinstance(fhir_version, str) and fhir_version in FHIR_REFERENCE_MODELS:
                    expected_graph.extend(_reference_edges(key, resource, fhir_version))
            profiles = entry.get("profiles")
            if (
                not isinstance(profiles, list)
                or any(not isinstance(profile, str) for profile in profiles)
                or profiles != sorted(set(profiles))
            ):
                failures.append(f"example {key} profiles must be sorted unique strings")
            elif isinstance(resource, dict):
                meta = resource.get("meta")
                expected_profiles = (
                    sorted(
                        {
                            profile
                            for profile in meta.get("profile", [])
                            if isinstance(profile, str)
                        }
                    )
                    if isinstance(meta, dict) and isinstance(meta.get("profile"), list)
                    else []
                )
                if profiles != expected_profiles:
                    failures.append(f"example {key} profiles do not match resource.meta.profile")

    if isinstance(graph, list):
        normalized_graph: list[tuple[str, str, str, str]] = []
        for index, edge in enumerate(graph):
            if not isinstance(edge, dict) or set(edge) != {"source", "kind", "target", "path"}:
                failures.append(
                    f"semantic snapshot referenceGraph edge {index + 1} has invalid fields"
                )
                continue
            kind = edge.get("kind")
            if (
                not isinstance(kind, str)
                or kind not in {"canonical", "reference"}
                or any(
                    not isinstance(edge.get(field), str) or not edge[field]
                    for field in ("source", "target", "path")
                )
            ):
                failures.append(
                    f"semantic snapshot referenceGraph edge {index + 1} is invalid"
                )
                continue
            normalized_graph.append(
                (edge["source"], edge["kind"], edge["target"], edge["path"])
            )
        if normalized_graph != sorted(set(normalized_graph)):
            failures.append("semantic snapshot referenceGraph must be sorted and unique")
        if graph != sorted(
            expected_graph,
            key=lambda edge: (
                edge["source"],
                edge["kind"],
                edge["target"],
                edge["path"],
            ),
        ):
            failures.append("semantic snapshot referenceGraph does not match retained resources")
    return failures


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path, help="package directory or package.tgz")
    parser.add_argument("--output", type=Path, help="snapshot path; defaults to stdout")
    arguments = parser.parse_args(argv)
    try:
        snapshot = create_snapshot(arguments.package)
        failures = validate_snapshot(snapshot)
        if failures:
            raise SnapshotError("\n".join(failures))
        write_snapshot(snapshot, arguments.output)
        return 0
    except SnapshotError as error:
        parser.exit(1, f"error: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
