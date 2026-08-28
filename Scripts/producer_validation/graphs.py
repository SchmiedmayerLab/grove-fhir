"""Cross-resource provenance and source-entity graph closure."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Any

from .context import CATALOG_ROOT, HMAC_IDENTITY
from .diagnostics import ProducerValidationError, contract_failure
from .identity import identifier_role, typed_resource_identifiers
from .io import read_json
from .references import complete_identifier


def validate_adapter_provenance_graph(
    entry_resources: list[dict[str, Any]],
    resources_by_full_url: dict[str, dict[str, Any]],
    label: str,
) -> None:
    """Bind every adapter output for one source record to one internal Provenance."""
    claims = read_json(CATALOG_ROOT / "profile-claims.json")[
        "adapterConversionProvenanceClaims"
    ]

    def source_value(resource: dict[str, Any], role: str) -> tuple[str, str]:
        identity = typed_resource_identifiers(resource, f"{label} {role}").get(
            "source-record"
        )
        if identity is None:
            raise ProducerValidationError(
                f"{label} {role} must carry exactly one typed source-record Identifier"
            )
        return identity

    url_by_resource = {id(resource): url for url, resource in resources_by_full_url.items()}
    for claim in claims:
        target_profiles = set(claim["targetAdapterProfiles"])
        outputs_by_source: dict[tuple[str, str], set[str]] = {}
        provenances_by_source: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for resource in entry_resources:
            profiles = resource.get("meta", {}).get("profile", [])
            profile_set = set(profiles) if isinstance(profiles, list) else set()
            if profile_set & target_profiles:
                source = source_value(resource, "output")
                outputs_by_source.setdefault(source, set()).add(url_by_resource[id(resource)])
            if claim["profile"] in profile_set:
                entity = resource["entity"][0]["what"]["identifier"]
                if identifier_role(entity, f"{label} Provenance source entity") != "source-record":
                    raise ProducerValidationError(
                        f"{label} Provenance source entity must carry the source-record role"
                    )
                source = complete_identifier(entity, f"{label} Provenance source entity")
                if HMAC_IDENTITY.fullmatch(source[1]) is None:
                    raise ProducerValidationError(
                        f"{label} Provenance source entity must be a canonical v2 HMAC identity"
                    )
                provenances_by_source.setdefault(source, []).append(resource)

        for source, output_urls in outputs_by_source.items():
            provenances = provenances_by_source.get(source, [])
            if len(provenances) != 1:
                raise ProducerValidationError(
                    f"{label} {claim['adapter']} source record must have exactly one "
                    "conversion Provenance in the same Bundle"
                )
            provenance = provenances[0]
            target_urls = [target["reference"] for target in provenance["target"]]
            if any(not url.startswith("urn:uuid:") for url in target_urls):
                raise ProducerValidationError(
                    f"{label} adapter conversion Provenance targets must be internal UUID references"
                )
            if len(target_urls) != len(set(target_urls)):
                raise ProducerValidationError(
                    f"{label} adapter conversion Provenance repeats a target"
                )
            for target_url in target_urls:
                target = resources_by_full_url.get(target_url)
                if target is None:
                    raise ProducerValidationError(
                        f"{label} adapter conversion Provenance has an unresolved target"
                    )
                target_profile_set = set(target.get("meta", {}).get("profile", []))
                if not target_profile_set & target_profiles:
                    raise ProducerValidationError(
                        f"{label} adapter conversion Provenance targets a resource "
                        "outside its adapter output contract"
                    )
                if source_value(target, "target") != source:
                    raise ProducerValidationError(
                        f"{label} adapter conversion Provenance source entity and target "
                        "must carry the same source-record Identifier"
                    )
            if set(target_urls) != output_urls:
                raise ProducerValidationError(
                    f"{label} adapter conversion Provenance must target every structured "
                    "and raw output for its source record"
                )
        extra_sources = set(provenances_by_source) - set(outputs_by_source)
        if extra_sources:
            raise ProducerValidationError(
                f"{label} adapter conversion Provenance has no output for its source record"
            )

def exact_source_entity(
    provenance: dict[str, Any],
    label: str,
) -> tuple[str, str]:
    """Return the sole logical source-record identity of a lifecycle Provenance."""
    entities = provenance.get("entity")
    if not isinstance(entities, list) or len(entities) != 1:
        raise contract_failure(
            "mobile-exchange.single-source-entity",
            "Provenance.entity",
            f"{label} must identify exactly one source record",
        )
    entity = entities[0]
    what = entity.get("what") if isinstance(entity, dict) else None
    if (
        not isinstance(entity, dict)
        or entity.get("role") != "source"
        or not isinstance(what, dict)
        or "reference" in what
        or "resource" in what
    ):
        raise contract_failure(
            "mobile-exchange.logical-source-entity",
            "Provenance.entity[0].what",
            f"{label} source must be exactly one logical Identifier entity with role source",
        )
    identifier = what.get("identifier")
    if identifier_role(identifier, f"{label} source identifier") != "source-record":
        raise ProducerValidationError(
            f"{label} source must carry the source-record role"
        )
    pair = complete_identifier(identifier, f"{label} source identifier")
    if HMAC_IDENTITY.fullmatch(pair[1]) is None:
        raise ProducerValidationError(
            f"{label} source identifier is not a canonical Grove v2 HMAC identity"
        )
    return pair
