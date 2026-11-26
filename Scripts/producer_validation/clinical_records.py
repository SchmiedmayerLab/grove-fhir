"""Clinical Records validation: provider-issued clinical record documents and their attachments."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Any

from .context import (
    ADAPTER_ATTACHMENT_DOCUMENT_PROFILES, CATALOG_ROOT, CLINICAL_RECORD_ATTACHMENT_PROFILE,
    CLINICAL_RECORD_DOCUMENT_PROFILE,
)
from .diagnostics import ProducerValidationError, contract_failure
from .identity import typed_resource_identifiers
from .io import read_json
from .payloads import parse_fhir_instant
from .references import extensions_with_url

ATTACHMENT_GRAPH_RULE = "clinical-record.attachment-graph"
ATTACHMENT_RELATIONSHIP_CODE = "appends"
ATTACHMENT_PAYLOAD_FORMAT = "source-file"
WRITER_RECORD_VERSION_EXTENSION = (
    "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-writer-record-version"
)
# Every adapter catalog names the one lineage extension that carries its source type; an
# adapter attachment carries its document's, a source-neutral one carries none.
ADAPTER_CATALOGS = (
    "healthkit-adapter.json",
    "health-connect-adapter.json",
    "sensorkit-adapter.json",
    "providers-adapter.json",
)


def _profiles(resource: dict[str, Any]) -> list[Any]:
    profiles = resource.get("meta", {}).get("profile", [])
    return profiles if isinstance(profiles, list) else []


def validate_clinical_record_attachment(resource: dict[str, Any], label: str) -> None:
    """Close one clinical record attachment over its own content and relationship.

    Which clinical record document it appends to is a graph question, settled per Bundle by
    ``validate_clinical_record_attachment_graph``.
    """
    if CLINICAL_RECORD_ATTACHMENT_PROFILE not in _profiles(resource):
        return
    if resource.get("resourceType") != "DocumentReference":
        raise ProducerValidationError(
            f"{label} clinical record attachment must be a FHIR R4 DocumentReference"
        )
    contents = resource.get("content")
    if (
        not isinstance(contents, list)
        or len(contents) != 1
        or not isinstance(contents[0], dict)
        or not isinstance(contents[0].get("format"), dict)
        or contents[0]["format"].get("code") != ATTACHMENT_PAYLOAD_FORMAT
    ):
        raise ProducerValidationError(
            f"{label} clinical record attachment must carry exactly one "
            f"{ATTACHMENT_PAYLOAD_FORMAT} payload"
        )
    relations = resource.get("relatesTo")
    relation = relations[0] if isinstance(relations, list) and len(relations) == 1 else None
    target = relation.get("target") if isinstance(relation, dict) else None
    if (
        not isinstance(relation, dict)
        or relation.get("code") != ATTACHMENT_RELATIONSHIP_CODE
        or not isinstance(target, dict)
        or not isinstance(target.get("reference"), str)
        or not target["reference"]
        or "identifier" in target
        or ("type" in target and target["type"] != "DocumentReference")
    ):
        raise contract_failure(
            ATTACHMENT_GRAPH_RULE,
            "DocumentReference.relatesTo",
            f"{label} clinical record attachment must relate by exactly one "
            f"{ATTACHMENT_RELATIONSHIP_CODE} literal reference to its clinical record document",
        )
    identities = typed_resource_identifiers(resource, label)
    identifiers = resource.get("identifier")
    if (
        "writer-record" in identities
        or not isinstance(identifiers, list)
        or len(identifiers) != len(identities)
        or extensions_with_url(resource, WRITER_RECORD_VERSION_EXTENSION)
    ):
        raise ProducerValidationError(
            f"{label} clinical record attachment carries only its source-record, "
            "source-output, and source-artifact identities: no writer record, writer version, "
            "or native identifier"
        )


def _source_type_extension_urls() -> tuple[str, ...]:
    return tuple(
        read_json(CATALOG_ROOT / name)["sourceTypeExtension"]["url"] for name in ADAPTER_CATALOGS
    )


def validate_clinical_record_attachment_graph(
    resources: list[dict[str, Any]],
    resources_by_full_url: dict[str, dict[str, Any]],
    label: str,
) -> None:
    """Bind every attachment to the clinical record document of its own record."""
    rule = ATTACHMENT_GRAPH_RULE
    source_type_urls = _source_type_extension_urls()

    def source_types(resource: dict[str, Any]) -> frozenset[tuple[Any, ...]] | None:
        """Every adapter source-type extension the resource carries, by url and value."""
        found = []
        for url in source_type_urls:
            for extension in extensions_with_url(resource, url):
                if not isinstance(extension, dict):
                    return None
                found.append(tuple(sorted((key, repr(value)) for key, value in extension.items())))
        return frozenset(found)

    def type_codes(resource: dict[str, Any]) -> frozenset[tuple[Any, Any]] | None:
        """The system and code pairs of the document's type, ignoring display text."""
        value = resource.get("type")
        codings = value.get("coding") if isinstance(value, dict) else None
        if not isinstance(codings, list) or not codings:
            return None
        if any(not isinstance(coding, dict) for coding in codings):
            return None
        return frozenset((coding.get("system"), coding.get("code")) for coding in codings)

    def named_targets(value: Any) -> tuple[tuple[Any, ...], ...] | None:
        """What a list of References names, ignoring order, Reference.type, and display text.

        Absent and empty both name nothing; a malformed list is None and never equals anything.
        """
        if value is None:
            return ()
        if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
            return None
        targets = []
        for item in value:
            identifier = item.get("identifier")
            if identifier is not None and not isinstance(identifier, dict):
                return None
            targets.append((
                item.get("reference"),
                (identifier or {}).get("system"),
                (identifier or {}).get("value"),
            ))
        return tuple(sorted(targets, key=repr))

    def studies(resource: dict[str, Any]) -> tuple[tuple[Any, ...], ...] | None:
        context = resource.get("context")
        if context is None:
            return ()
        return named_targets(context.get("related")) if isinstance(context, dict) else None

    def stated_instant(resource: dict[str, Any], name: str) -> Any:
        """The exact instant of DocumentReference.date, so equal instants in other lexemes match."""
        value = resource.get("date")
        return None if value is None else parse_fhir_instant(value, f"{name}.date")

    outputs_by_attachment_source: dict[tuple[str, str], set[tuple[str, str]]] = {}
    for resource in resources:
        profiles = _profiles(resource)
        if CLINICAL_RECORD_ATTACHMENT_PROFILE not in profiles:
            continue
        identities = typed_resource_identifiers(resource, f"{label} clinical attachment")
        relations = resource.get("relatesTo")
        target = (
            relations[0].get("target")
            if isinstance(relations, list)
            and len(relations) == 1
            and isinstance(relations[0], dict)
            else None
        )
        reference = target.get("reference") if isinstance(target, dict) else None
        document = resources_by_full_url.get(reference) if isinstance(reference, str) else None
        document_profiles = _profiles(document) if isinstance(document, dict) else []
        required_document_profiles = {CLINICAL_RECORD_DOCUMENT_PROFILE} | {
            ADAPTER_ATTACHMENT_DOCUMENT_PROFILES[profile]
            for profile in profiles
            if profile in ADAPTER_ATTACHMENT_DOCUMENT_PROFILES
        }
        if (
            not isinstance(document, dict)
            or document.get("resourceType") != "DocumentReference"
            or not required_document_profiles <= set(document_profiles)
        ):
            raise contract_failure(
                rule, "DocumentReference.relatesTo.target",
                f"{label} clinical record attachment must append to a clinical record document "
                "of its own adapter in the same Bundle",
            )
        document_identities = typed_resource_identifiers(
            document, f"{label} clinical record document"
        )
        source = identities.get("source-record")
        if source is None or source != document_identities.get("source-record"):
            raise contract_failure(
                rule, "DocumentReference.identifier",
                f"{label} clinical record attachment must share the source-record identity of "
                "the clinical record document it appends to",
            )
        if source_types(resource) is None or source_types(resource) != source_types(document):
            raise contract_failure(
                rule, "DocumentReference.extension",
                f"{label} clinical record attachment must carry the source type of its clinical "
                "record document, and none where that document carries none",
            )
        if type_codes(resource) is None or type_codes(resource) != type_codes(document):
            raise contract_failure(
                rule, "DocumentReference.type",
                f"{label} clinical record attachment must carry the type coding of its clinical "
                "record document",
            )
        if (
            stated_instant(resource, f"{label} clinical attachment") is None
            or stated_instant(resource, f"{label} clinical attachment")
            != stated_instant(document, f"{label} clinical record document")
        ):
            raise contract_failure(
                rule, "DocumentReference.date",
                f"{label} clinical record attachment must state the date of its clinical record "
                "document",
            )
        attachment_authors = named_targets(resource.get("author"))
        if attachment_authors is None or attachment_authors != named_targets(document.get("author")):
            raise contract_failure(
                rule, "DocumentReference.author",
                f"{label} clinical record attachment must name exactly the authors of its "
                "clinical record document, and none where that document names none",
            )
        attachment_studies = studies(resource)
        if attachment_studies is None or attachment_studies != studies(document):
            raise contract_failure(
                rule, "DocumentReference.context.related",
                f"{label} clinical record attachment must name exactly the studies of its "
                "clinical record document, and none where that document names none",
            )
        # The subject needs no check here: mobile-exchange.single-subject already holds every
        # output of the Bundle to one subject, comparing what each reference resolves to rather
        # than its JSON, so an optional Reference.type or display never decides it.
        output = identities.get("source-output")
        outputs = outputs_by_attachment_source.setdefault(source, set())
        if (
            output is None
            or output in outputs
            or output == document_identities.get("source-output")
        ):
            raise contract_failure(
                rule, "DocumentReference.identifier",
                f"{label} every clinical record attachment of one record needs its own "
                "source-output identity",
            )
        outputs.add(output)
