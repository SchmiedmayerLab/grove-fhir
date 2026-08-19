#!/usr/bin/env python3
"""Validate the accepted cross-resource study graph and its one-mutation corpus."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

try:
    from fhir_fixture_corpus import (
        build_cases,
        load_bases,
        load_manifest,
        validate_with,
    )
except ModuleNotFoundError:  # Imported as Scripts.validate_study_graph in tests.
    from Scripts.fhir_fixture_corpus import (  # type: ignore[no-redef]
        build_cases,
        load_bases,
        load_manifest,
        validate_with,
    )


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CORPUS = ROOT / "Conformance/study-graph/corpus.json"


def diagnostic(
    code: str, reason: str, location: str
) -> dict[str, str]:
    return {
        "code": code,
        "reason": reason,
        "location": location,
        "severity": "error",
    }


RULES = {
    "identity": diagnostic(
        "study-graph.identity",
        "Every accepted graph resource has one unique logical id and a matching unique fullUrl.",
        "Bundle.entry",
    ),
    "roles": diagnostic(
        "study-graph.roles",
        "The accepted graph contains exactly one resource for every declared study role and no ambiguous extras.",
        "Bundle.entry",
    ),
    "plan-version": diagnostic(
        "study-graph.plan-version",
        "The accepted study graph is explicitly pinned to PlanDefinition version 42.",
        "Bundle.entry[1].resource.version",
    ),
    "protocol": diagnostic(
        "study-graph.protocol",
        "ResearchStudy.protocol references the accepted versioned PlanDefinition.",
        "Bundle.entry[2].resource.protocol[0].reference",
    ),
    "enrollment-study": diagnostic(
        "study-graph.enrollment-study",
        "ResearchSubject.study references the accepted ResearchStudy.",
        "Bundle.entry[3].resource.study.reference",
    ),
    "enrollment-participant": diagnostic(
        "study-graph.enrollment-participant",
        "ResearchSubject.individual references the participant used by accepted study data.",
        "Bundle.entry[3].resource.individual.reference",
    ),
    "observation-study": diagnostic(
        "study-graph.observation-study",
        "The standard workflow-researchStudy extension references the accepted ResearchStudy.",
        "Bundle.entry[5].resource.extension[0].valueReference.reference",
    ),
    "provenance-target": diagnostic(
        "study-graph.provenance-target",
        "Conversion Provenance targets the accepted study Observation.",
        "Bundle.entry[6].resource.target[0].reference",
    ),
    "provenance-assembler": diagnostic(
        "study-graph.provenance-assembler",
        "Conversion Provenance identifies the application Device that assembled the FHIR resources.",
        "Bundle.entry[6].resource.agent[0].who.reference",
    ),
    "provenance-plan-source": diagnostic(
        "study-graph.provenance-plan-source",
        "Conversion Provenance identifies the exact versioned PlanDefinition as a source entity.",
        "Bundle.entry[6].resource.entity[1].what.reference",
    ),
    "provenance-enrollment-source": diagnostic(
        "study-graph.provenance-enrollment-source",
        "Conversion Provenance identifies the influencing ResearchSubject enrollment as a source entity.",
        "Bundle.entry[6].resource.entity[2].what.reference",
    ),
    "provenance-required": diagnostic(
        "study-graph.provenance-required",
        "The accepted graph includes conversion Provenance for the exchanged Observation.",
        "Bundle.entry",
    ),
}


EXPECTED_RESOURCES = {
    ("Patient", "accepted-participant"),
    ("PlanDefinition", "accepted-plan"),
    ("ResearchStudy", "accepted-study"),
    ("ResearchSubject", "accepted-enrollment"),
    ("Device", "accepted-application"),
    ("Observation", "accepted-heart-rate"),
    ("Provenance", "accepted-conversion"),
}
FULL_URL_BASE = "https://study.example.org/fhir"


def _resources(
    bundle: Mapping[str, Any],
) -> tuple[dict[tuple[str, str], Mapping[str, Any]], bool]:
    indexed: dict[tuple[str, str], Mapping[str, Any]] = {}
    full_urls: set[str] = set()
    identity_valid = True
    for entry in bundle.get("entry", []):
        if not isinstance(entry, dict) or not isinstance(entry.get("resource"), dict):
            identity_valid = False
            continue
        resource = entry["resource"]
        resource_type = resource.get("resourceType")
        identifier = resource.get("id")
        full_url = entry.get("fullUrl")
        if not (
            isinstance(resource_type, str)
            and resource_type
            and isinstance(identifier, str)
            and identifier
            and isinstance(full_url, str)
            and full_url
        ):
            identity_valid = False
            continue
        logical_id = (resource_type, identifier)
        expected_full_url = f"{FULL_URL_BASE}/{resource_type}/{identifier}"
        if (
            logical_id in indexed
            or full_url in full_urls
            or full_url != expected_full_url
        ):
            identity_valid = False
        else:
            indexed[logical_id] = resource
            full_urls.add(full_url)
    return indexed, identity_valid


def _reference(value: Any) -> str | None:
    if not isinstance(value, dict):
        return None
    reference = value.get("reference")
    return reference if isinstance(reference, str) else None


def _first_reference(value: Any) -> str | None:
    if not isinstance(value, list) or not value:
        return None
    return _reference(value[0])


def validate_graph(resource: Any) -> Iterable[Mapping[str, str]]:
    """Return reason-specific graph diagnostics outside StructureDefinition scope."""
    if not isinstance(resource, dict) or resource.get("resourceType") != "Bundle":
        return [RULES["provenance-required"]]
    indexed, identity_valid = _resources(resource)
    plan = indexed.get(("PlanDefinition", "accepted-plan"), {})
    study = indexed.get(("ResearchStudy", "accepted-study"), {})
    subject = indexed.get(("ResearchSubject", "accepted-enrollment"), {})
    observation = indexed.get(("Observation", "accepted-heart-rate"), {})
    provenance = indexed.get(("Provenance", "accepted-conversion"))

    diagnostics: list[Mapping[str, str]] = []
    if not identity_valid:
        return [RULES["identity"]]
    actual_resources = set(indexed)
    if (
        provenance is None
        and actual_resources == EXPECTED_RESOURCES - {("Provenance", "accepted-conversion")}
        and len(resource.get("entry", [])) == len(EXPECTED_RESOURCES) - 1
    ):
        return [RULES["provenance-required"]]
    if actual_resources != EXPECTED_RESOURCES or len(resource.get("entry", [])) != len(
        EXPECTED_RESOURCES
    ):
        return [RULES["roles"]]
    if plan.get("version") != "42":
        diagnostics.append(RULES["plan-version"])
    if _first_reference(study.get("protocol")) != "PlanDefinition/accepted-plan":
        diagnostics.append(RULES["protocol"])
    if _reference(subject.get("study")) != "ResearchStudy/accepted-study":
        diagnostics.append(RULES["enrollment-study"])
    if _reference(subject.get("individual")) != "Patient/accepted-participant":
        diagnostics.append(RULES["enrollment-participant"])

    study_extensions = [
        extension
        for extension in observation.get("extension", [])
        if isinstance(extension, dict)
        and extension.get("url")
        == "http://hl7.org/fhir/StructureDefinition/workflow-researchStudy"
    ]
    if (
        len(study_extensions) != 1
        or _reference(study_extensions[0].get("valueReference"))
        != "ResearchStudy/accepted-study"
    ):
        diagnostics.append(RULES["observation-study"])

    if provenance is None:
        return [RULES["provenance-required"]]
    if _first_reference(provenance.get("target")) != "Observation/accepted-heart-rate":
        diagnostics.append(RULES["provenance-target"])
    agents = provenance.get("agent")
    assembler = agents[0] if isinstance(agents, list) and agents else {}
    if not isinstance(assembler, dict) or _reference(assembler.get("who")) != (
        "Device/accepted-application"
    ):
        diagnostics.append(RULES["provenance-assembler"])
    entities = provenance.get("entity")
    entity_references = [
        _reference(entity.get("what"))
        for entity in entities
        if isinstance(entities, list) and isinstance(entity, dict)
    ] if isinstance(entities, list) else []
    if "PlanDefinition/accepted-plan" not in entity_references:
        diagnostics.append(RULES["provenance-plan-source"])
    if "ResearchSubject/accepted-enrollment" not in entity_references:
        diagnostics.append(RULES["provenance-enrollment-source"])
    return diagnostics


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    arguments = parser.parse_args(argv)
    try:
        manifest = load_manifest(arguments.corpus)
        bases = load_bases(manifest, arguments.corpus)
        cases = build_cases(manifest, bases)
        failures = validate_with(manifest, bases, cases, validate_graph)
    except (OSError, ValueError) as error:
        print(f"Study graph evidence is invalid: {error}", file=sys.stderr)
        return 1
    if failures:
        print("Study graph evidence failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(
        f"Validated {len(bases)} accepted study graph and {len(cases)} "
        "reason-specific one-mutation cases"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
