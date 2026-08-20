#!/usr/bin/env python3
"""Prove shared heart-rate meaning and distinct platform provenance roles."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from fhir_fixture_corpus import canonical_json_bytes, strict_json_loads
except ModuleNotFoundError:  # Imported as Scripts.validate_heart_rate_equivalence in tests.
    from Scripts.fhir_fixture_corpus import (  # type: ignore[no-redef]
        canonical_json_bytes,
        strict_json_loads,
    )


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SPECIFICATION = ROOT / "Conformance/semantic-equivalence/heart-rate.json"


class EquivalenceError(ValueError):
    """Report incomplete, ambiguous, or semantically unequal evidence."""


def _object(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise EquivalenceError(f"{label} must be an object")
    return value


def _list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise EquivalenceError(f"{label} must be a list")
    return value


def _one(values: list[Any], label: str) -> Any:
    if len(values) != 1:
        raise EquivalenceError(f"{label} must have exactly one match, found {len(values)}")
    return values[0]


def _profiles(resource: Mapping[str, Any], label: str) -> list[str]:
    meta = _object(resource.get("meta"), f"{label}.meta")
    profiles = _list(meta.get("profile"), f"{label}.meta.profile")
    if not all(isinstance(profile, str) and profile for profile in profiles):
        raise EquivalenceError(f"{label}.meta.profile must contain nonempty strings")
    return profiles


def _coding(value: Any, system: str, label: str) -> dict[str, Any]:
    concept = _object(value, label)
    codings = [
        coding
        for coding in concept.get("coding", [])
        if isinstance(coding, dict) and coding.get("system") == system
    ]
    coding = _object(_one(codings, label), label)
    code = coding.get("code")
    if not isinstance(code, str) or not code:
        raise EquivalenceError(f"{label} coding must have a code")
    return {"system": system, "code": code}


def _has_coding(value: Any, system: str, code: str) -> bool:
    if not isinstance(value, dict):
        return False
    return any(
        isinstance(coding, dict)
        and coding.get("system") == system
        and coding.get("code") == code
        for coding in value.get("coding", [])
    )


def _identifier_tokens(resource: Mapping[str, Any], system: str) -> set[tuple[str, str]]:
    return {
        (identifier["system"], identifier["value"])
        for identifier in resource.get("identifier", [])
        if isinstance(identifier, dict)
        and identifier.get("system") == system
        and isinstance(identifier.get("value"), str)
        and identifier["value"]
    }


def _reference_token(reference: Mapping[str, Any]) -> tuple[str, str] | None:
    identifier = reference.get("identifier")
    if not isinstance(identifier, dict):
        return None
    system = identifier.get("system")
    value = identifier.get("value")
    if isinstance(system, str) and system and isinstance(value, str) and value:
        return (system, value)
    return None


def _assert_reference_identifier_matches(
    reference: Mapping[str, Any],
    target: Mapping[str, Any],
    label: str,
) -> Mapping[str, Any]:
    token = _reference_token(reference)
    if token is not None and token not in _identifier_tokens(target, token[0]):
        raise EquivalenceError(
            f"{label}.identifier contradicts the resolved target identifier"
        )
    return target


def _load_json(path: Path) -> Any:
    if path.is_symlink() or not path.is_file():
        raise EquivalenceError(f"input must be a regular file: {path}")
    try:
        return strict_json_loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise EquivalenceError(f"unable to read {path}: {error}") from error


def _path_without_symlinks(path: Path, label: str) -> Path:
    """Return an absolute path only after checking every supplied component."""
    absolute = Path(os.path.abspath(path))
    parts = absolute.parts[1:]
    current = Path(absolute.anchor)
    if parts and (current / parts[0]).is_symlink():
        current = (current / parts[0]).resolve()
        parts = parts[1:]
    for part in parts:
        current /= part
        if current.is_symlink():
            raise EquivalenceError(f"{label} may not traverse a symlink: {current}")
    return current


@dataclass(frozen=True)
class FixtureGraph:
    observation: Mapping[str, Any]
    provenance: Mapping[str, Any]
    bundle: Mapping[str, Any] | None = None

    def resolve(self, reference: Any, owner: Mapping[str, Any], label: str) -> Mapping[str, Any]:
        value = _object(reference, label)
        raw = value.get("reference")
        if not isinstance(raw, str) or not raw:
            raise EquivalenceError(f"{label}.reference must be populated")
        if raw.startswith("#"):
            identifier = raw[1:]
            matches = [
                resource
                for resource in owner.get("contained", [])
                if isinstance(resource, dict) and resource.get("id") == identifier
            ]
            target = _object(_one(matches, f"{label} contained target"), label)
            return _assert_reference_identifier_matches(value, target, label)

        candidates: list[Mapping[str, Any]] = []
        if self.bundle is not None:
            for entry in self.bundle.get("entry", []):
                if not isinstance(entry, dict) or not isinstance(entry.get("resource"), dict):
                    continue
                resource = entry["resource"]
                logical = (
                    f"{resource.get('resourceType')}/{resource.get('id')}"
                    if resource.get("resourceType") and resource.get("id")
                    else None
                )
                if entry.get("fullUrl") == raw or logical == raw:
                    candidates.append(resource)
        for resource in (self.observation, self.provenance):
            logical = (
                f"{resource.get('resourceType')}/{resource.get('id')}"
                if resource.get("resourceType") and resource.get("id")
                else None
            )
            if logical == raw:
                candidates.append(resource)
        unique = {
            canonical_json_bytes(candidate): candidate for candidate in candidates
        }
        target = _object(_one(list(unique.values()), f"{label} target"), label)
        return _assert_reference_identifier_matches(value, target, label)


def _subject_type(observation: Mapping[str, Any], graph: FixtureGraph) -> str:
    subject = _object(observation.get("subject"), "Observation.subject")
    declared = subject.get("type")
    reference = subject.get("reference")
    referenced_type: str | None = None
    if isinstance(reference, str):
        if "/" in reference and not reference.startswith(("#", "urn:")):
            referenced_type = reference.split("/", 1)[0]
        else:
            referenced_type = str(
                graph.resolve(subject, observation, "Observation.subject").get("resourceType")
            )
    if isinstance(declared, str) and declared:
        if referenced_type is not None and referenced_type != declared:
            raise EquivalenceError(
                "Observation.subject.type contradicts the referenced resource type"
            )
        return declared
    if referenced_type is not None:
        return referenced_type
    raise EquivalenceError("Observation.subject must declare or resolve its resource type")


def _effective_kind(observation: Mapping[str, Any]) -> str:
    choices = [
        (json_name.removeprefix("effective"), observation.get(json_name))
        for json_name in (
            "effectiveDateTime",
            "effectivePeriod",
            "effectiveTiming",
            "effectiveInstant",
        )
        if json_name in observation and observation.get(json_name) is not None
    ]
    kind, _value = _one(choices, "Observation.effective[x]")
    return kind[:1].lower() + kind[1:]


def project(
    graph: FixtureGraph,
    clinical_profile: str,
    adapter_profile: str,
) -> dict[str, Any]:
    """Return only the intentionally shared clinical heart-rate semantics."""
    observation = graph.observation
    if observation.get("resourceType") != "Observation":
        raise EquivalenceError("heart-rate fixture must be an Observation")
    profiles = _profiles(observation, "Observation")
    for profile in (clinical_profile, adapter_profile):
        if profile not in profiles:
            raise EquivalenceError(f"Observation.meta.profile is missing {profile}")

    categories = _list(observation.get("category"), "Observation.category")
    category = _one(
        [
            _coding(
                item,
                "http://terminology.hl7.org/CodeSystem/observation-category",
                "Observation.category",
            )
            for item in categories
            if isinstance(item, dict)
            and any(
                isinstance(coding, dict)
                and coding.get("system")
                == "http://terminology.hl7.org/CodeSystem/observation-category"
                for coding in item.get("coding", [])
            )
        ],
        "vital-signs category",
    )
    quantity = _object(observation.get("valueQuantity"), "Observation.valueQuantity")
    return {
        "resourceType": "Observation",
        "clinicalProfile": clinical_profile,
        "status": observation.get("status"),
        "category": category,
        "code": _coding(observation.get("code"), "http://loinc.org", "Observation.code"),
        "subjectType": _subject_type(observation, graph),
        "effectiveKind": _effective_kind(observation),
        "valueQuantity": {
            "value": quantity.get("value"),
            "comparator": quantity.get("comparator"),
            "system": quantity.get("system"),
            "code": quantity.get("code"),
        },
    }


def _require_profile(resource: Mapping[str, Any], profile: str, label: str) -> None:
    if resource.get("resourceType") != "Device":
        raise EquivalenceError(f"{label} must resolve to Device")
    if profile not in _profiles(resource, label):
        raise EquivalenceError(f"{label} is missing profile {profile}")


def validate_roles(
    graph: FixtureGraph,
    input_specification: Mapping[str, Any],
    roles: Mapping[str, Any],
) -> None:
    """Validate roles within one platform without comparing platform identities."""
    observation = graph.observation
    provenance = graph.provenance
    if provenance.get("resourceType") != "Provenance":
        raise EquivalenceError("conversion companion must be Provenance")
    provenance_profile = input_specification.get("provenanceProfile")
    if provenance_profile not in _profiles(provenance, "Provenance"):
        raise EquivalenceError(f"Provenance.meta.profile is missing {provenance_profile}")

    recorder = graph.resolve(
        observation.get("device"), observation, "Observation.device"
    )
    _require_profile(
        recorder,
        str(roles.get("recordingDeviceProfile")),
        "Observation recorder",
    )

    gateway_extensions = [
        extension
        for extension in observation.get("extension", [])
        if isinstance(extension, dict)
        and extension.get("url") == roles.get("gatewayExtension")
    ]
    if len(gateway_extensions) > 1:
        raise EquivalenceError("Observation has more than one gateway-device extension")
    gateway_expectation = input_specification.get("gatewayExpectation")
    if gateway_expectation not in {"required", "absent-in-export"}:
        raise EquivalenceError("gatewayExpectation must be required or absent-in-export")
    if gateway_expectation == "required" and len(gateway_extensions) != 1:
        raise EquivalenceError("Observation must carry its evidenced actual gateway")
    if gateway_expectation == "absent-in-export" and gateway_extensions:
        raise EquivalenceError("Observation export unexpectedly claims an actual gateway")
    if gateway_extensions:
        gateway = graph.resolve(
            gateway_extensions[0].get("valueReference"),
            observation,
            "Observation gateway",
        )
        _require_profile(
            gateway,
            str(roles.get("applicationDeviceProfile")),
            "Observation gateway",
        )

    activity = provenance.get("activity")
    if not _has_coding(
        activity,
        str(roles.get("transformSystem")),
        str(roles.get("transformCode")),
    ):
        raise EquivalenceError("Provenance.activity must identify the transform event")
    assemblers = [
        agent
        for agent in provenance.get("agent", [])
        if isinstance(agent, dict)
        and _has_coding(
            agent.get("type"),
            str(roles.get("assemblerSystem")),
            str(roles.get("assemblerCode")),
        )
    ]
    assembler = _object(_one(assemblers, "Provenance assembler"), "Provenance assembler")
    converter = graph.resolve(
        assembler.get("who"), provenance, "Provenance assembler.who"
    )
    _require_profile(
        converter,
        str(roles.get("applicationDeviceProfile")),
        "Provenance converter",
    )

    source_system = input_specification.get("sourceIdentifierSystem")
    if not isinstance(source_system, str) or not source_system:
        raise EquivalenceError("sourceIdentifierSystem must be a nonempty string")
    observation_sources = _identifier_tokens(observation, source_system)
    if len(observation_sources) != 1:
        raise EquivalenceError(
            f"Observation must have exactly one source identifier from {source_system}"
        )
    source_token = next(iter(observation_sources))
    sources = [
        entity
        for entity in provenance.get("entity", [])
        if isinstance(entity, dict)
        and entity.get("role") == "source"
        and _reference_token(_object(entity.get("what"), "Provenance.entity.what"))
        == source_token
    ]
    source = _object(_one(sources, "matching Provenance source entity"), "source entity")

    observation_tokens = {
        (identifier.get("system"), identifier.get("value"))
        for identifier in observation.get("identifier", [])
        if isinstance(identifier, dict)
        and isinstance(identifier.get("system"), str)
        and isinstance(identifier.get("value"), str)
    }
    matching_targets = []
    for target in provenance.get("target", []):
        if not isinstance(target, dict):
            continue
        token = _reference_token(target)
        if token is not None and token in observation_tokens:
            matching_targets.append(target)
            continue
        if isinstance(target.get("reference"), str):
            resolved = graph.resolve(target, provenance, "Provenance.target")
            if canonical_json_bytes(resolved) == canonical_json_bytes(observation):
                matching_targets.append(target)
    if len(matching_targets) != 1:
        raise EquivalenceError(
            "Provenance must have exactly one target identifying the selected Observation"
        )

    if input_specification.get("requireDataOrigin") is True:
        enterers = [
            agent
            for agent in source.get("agent", [])
            if isinstance(agent, dict)
            and _has_coding(
                agent.get("type"),
                str(roles.get("entererSystem")),
                str(roles.get("entererCode")),
            )
        ]
        enterer = _object(_one(enterers, "source DataOrigin enterer"), "DataOrigin")
        data_origin = graph.resolve(
            enterer.get("who"), provenance, "Provenance source DataOrigin.who"
        )
        if data_origin.get("resourceType") != "Device":
            raise EquivalenceError("source DataOrigin must resolve to Device")


def _repository_input(path: Path, relative: Any, label: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise EquivalenceError(f"{label} must be a relative POSIX path")
    unresolved = _path_without_symlinks(path.parent / relative, label)
    resolved = unresolved.resolve()
    if not resolved.is_relative_to(ROOT):
        raise EquivalenceError(f"{label} escapes the repository")
    return resolved


def _parse_external_evidence(values: Sequence[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for value in values:
        identifier, separator, raw_path = value.partition("=")
        if not separator or not identifier or not raw_path:
            raise EquivalenceError("--external-evidence must use EVIDENCE_SET_ID=PATH")
        if identifier in result:
            raise EquivalenceError(f"duplicate external evidence set: {identifier}")
        unresolved = _path_without_symlinks(
            Path(raw_path), f"external evidence set {identifier}"
        )
        path = unresolved.resolve()
        if not path.is_dir():
            raise EquivalenceError(
                f"external heart-rate evidence set must be a regular directory: {path}"
            )
        result[identifier] = path
    return result


def _graph_from_paths(
    observation_path: Path,
    provenance_path: Path,
    bundle_path: Path | None,
) -> FixtureGraph:
    observation = _object(_load_json(observation_path), str(observation_path))
    provenance = _object(_load_json(provenance_path), str(provenance_path))
    bundle = (
        _object(_load_json(bundle_path), str(bundle_path)) if bundle_path is not None else None
    )
    if bundle is not None and bundle.get("resourceType") != "Bundle":
        raise EquivalenceError(f"companion is not a FHIR Bundle: {bundle_path}")
    return FixtureGraph(observation, provenance, bundle)


def _validate_inputs(
    inputs: list[tuple[Mapping[str, Any], FixtureGraph]],
    clinical_profile: str,
    roles: Mapping[str, Any],
    expected: Any,
) -> list[dict[str, Any]]:
    projections: list[dict[str, Any]] = []
    semantics: set[str] = set()
    for item, graph in inputs:
        identifier = item.get("id")
        semantic_id = item.get("semantics")
        adapter = item.get("adapterProfile")
        if not all(isinstance(value, str) and value for value in (identifier, semantic_id, adapter)):
            raise EquivalenceError("input id, semantics, and adapterProfile must be nonempty")
        if semantic_id in semantics:
            raise EquivalenceError(f"duplicate semantic platform in one comparison: {semantic_id}")
        semantics.add(semantic_id)
        projection = project(graph, clinical_profile, adapter)
        validate_roles(graph, item, roles)
        if canonical_json_bytes(projection) != canonical_json_bytes(expected):
            raise EquivalenceError(f"heart-rate input {identifier} differs from expectedProjection")
        projections.append(projection)
    if len(projections) < 2:
        raise EquivalenceError("heart-rate equivalence requires at least two platform inputs")
    if any(
        canonical_json_bytes(projection) != canonical_json_bytes(projections[0])
        for projection in projections[1:]
    ):
        raise EquivalenceError("heart-rate clinical projections are not equivalent")
    return projections


def validate_specification(
    path: Path,
    external_evidence: Mapping[str, Path] | None = None,
    require_implementation_fixtures: bool = False,
) -> dict[str, list[dict[str, Any]]]:
    specification = _object(_load_json(path), "heart-rate equivalence specification")
    if specification.get("schemaVersion") != 2:
        raise EquivalenceError("heart-rate equivalence schemaVersion must be 2")
    if specification.get("externalDirectoryContract") != "evidence-lock-exact-allowlist":
        raise EquivalenceError(
            "external implementation directories must come from the evidence lock exact allowlist"
        )
    clinical_profile = specification.get("clinicalProfile")
    if not isinstance(clinical_profile, str) or not clinical_profile:
        raise EquivalenceError("clinicalProfile must be a nonempty string")
    roles = _object(specification.get("roles"), "roles")
    expected = _object(specification.get("expectedProjection"), "expectedProjection")
    exclusions = _list(
        specification.get("excludedFromClinicalEquivalence"),
        "excludedFromClinicalEquivalence",
    )
    if not exclusions or any(
        not isinstance(item, dict)
        or not isinstance(item.get("path"), str)
        or not item.get("path")
        or not isinstance(item.get("reason"), str)
        or not item.get("reason")
        for item in exclusions
    ):
        raise EquivalenceError("every clinical-equivalence exclusion needs a path and reason")

    static_items = _list(specification.get("staticInputs"), "staticInputs")
    static_inputs: list[tuple[Mapping[str, Any], FixtureGraph]] = []
    for raw_item in static_items:
        item = _object(raw_item, "static input")
        observation = _repository_input(path, item.get("observation"), "static observation")
        provenance = _repository_input(path, item.get("provenance"), "static provenance")
        bundle_value = item.get("bundle")
        bundle = (
            _repository_input(path, bundle_value, "static bundle")
            if bundle_value is not None
            else None
        )
        static_inputs.append((item, _graph_from_paths(observation, provenance, bundle)))
    results = {
        "static": _validate_inputs(
            static_inputs, clinical_profile, roles, expected
        )
    }

    external = dict(external_evidence or {})
    implementation_items = _list(
        specification.get("implementationInputs"), "implementationInputs"
    )
    implementation_by_id: dict[str, Mapping[str, Any]] = {}
    for raw_item in implementation_items:
        item = _object(raw_item, "implementation input")
        identifier = item.get("id")
        if not isinstance(identifier, str) or not identifier or identifier in implementation_by_id:
            raise EquivalenceError("implementation input ids must be unique nonempty strings")
        implementation_by_id[identifier] = item
    if external or require_implementation_fixtures:
        if set(external) != set(implementation_by_id):
            missing = sorted(set(implementation_by_id) - set(external))
            unknown = sorted(set(external) - set(implementation_by_id))
            details = []
            if missing:
                details.append("missing " + ", ".join(missing))
            if unknown:
                details.append("unknown " + ", ".join(unknown))
            raise EquivalenceError("external evidence sets do not match inventory: " + "; ".join(details))
        implementation_inputs: list[tuple[Mapping[str, Any], FixtureGraph]] = []
        for identifier, item in sorted(implementation_by_id.items()):
            files = _object(item.get("files"), f"implementation {identifier} files")
            if set(files) not in ({"observation", "provenance"}, {"observation", "provenance", "bundle"}):
                raise EquivalenceError(
                    f"implementation {identifier} has unsupported companion file roles"
                )
            root = external[identifier]
            resolved: dict[str, Path] = {}
            for role, filename in files.items():
                if (
                    not isinstance(filename, str)
                    or not filename
                    or "/" in filename
                    or "\\" in filename
                    or filename in {".", ".."}
                ):
                    raise EquivalenceError(
                        f"implementation {identifier} {role} must be a plain filename"
                    )
                unresolved = _path_without_symlinks(
                    root / filename, f"implementation {identifier} {role}"
                )
                candidate = unresolved.resolve()
                if not candidate.is_relative_to(root):
                    raise EquivalenceError(f"implementation {identifier} {role} escapes its set")
                resolved[role] = candidate
            implementation_inputs.append(
                (
                    item,
                    _graph_from_paths(
                        resolved["observation"],
                        resolved["provenance"],
                        resolved.get("bundle"),
                    ),
                )
            )
        results["implementation"] = _validate_inputs(
            implementation_inputs, clinical_profile, roles, expected
        )
    return results


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--specification", type=Path, default=DEFAULT_SPECIFICATION)
    parser.add_argument(
        "--external-evidence",
        action="append",
        default=[],
        metavar="EVIDENCE_SET_ID=PATH",
    )
    parser.add_argument("--require-implementation-fixtures", action="store_true")
    arguments = parser.parse_args(argv)
    try:
        external = _parse_external_evidence(arguments.external_evidence)
        results = validate_specification(
            arguments.specification.resolve(),
            external,
            arguments.require_implementation_fixtures,
        )
    except (EquivalenceError, OSError, ValueError) as error:
        print(f"Heart-rate equivalence validation failed: {error}", file=sys.stderr)
        return 1
    print(
        "Validated "
        + " and ".join(
            f"{len(projections)} {kind} platform fixtures"
            for kind, projections in results.items()
        )
        + " with equivalent heart-rate clinical projections and distinct role graphs"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
