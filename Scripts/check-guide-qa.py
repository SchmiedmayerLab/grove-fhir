#!/usr/bin/env python3
"""Report IG Publisher QA counts and fail on errors or warnings.

The offline structural lane may explicitly account for Publisher 2.3.3 findings
that say its absent terminology client could not validate external codes. Those
exceptions are deliberately narrower than Publisher suppressions: MIME errors
must match a generated DocumentReference and the authoritative format registry;
no-service warnings must match a coding in the generated resource and Grove's
pinned terminology evidence. The default/online lane remains strict.
"""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
from collections import namedtuple
import html
import json
import os
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "Scripts"))
from ucum_expression import UcumError, UcumTable  # noqa: E402

LOINC = "http://loinc.org"
SNOMED = "http://snomed.info/sct"
UCUM = "http://unitsofmeasure.org"


SUPPRESSED_MESSAGE = re.compile(
    r"<li>((?:WARNING|ERROR):.*?)\s*"
    r"<span[^>]*>\(([0-9]+) uses\)</span></li>",
    re.DOTALL,
)

RENDERED_TEMPLATE_ERROR = re.compile(
    r"<p>\s*Script\s+[^<\r\n]+:\s*[^<\r\n]+</p>",
    re.IGNORECASE,
)


FindingCounts = namedtuple(
    "FindingCounts",
    (
        "raw_errors",
        "exact_suppressed_errors",
        "offline_terminology_errors",
        "unsuppressed_errors",
        "raw_warnings",
        "exact_suppressed_warnings",
        "offline_terminology_warnings",
        "unsuppressed_warnings",
    ),
)


def finding_counts(
    qa: dict[str, object],
    exact_suppressions: dict[str, int],
    offline_terminology_errors: int = 0,
    offline_terminology_warnings: int = 0,
) -> FindingCounts:
    """Normalize Publisher's asymmetric treatment of ignored errors/warnings.

    Publisher 2.3.3 removes ignored warnings and HTML-link errors from the JSON
    totals, but keeps ignored resource-validation errors in ``qa.json.errs``. The
    HTML suppressed section is therefore the authoritative exact count for both
    severities. ``validate_suppressions`` separately requires each configured
    message to appear exactly once, and repository tests close the admitted error
    families.
    """

    publisher_errors = int(qa.get("errs", qa.get("errors", 0)))
    publisher_unsuppressed_warnings = int(qa.get("warnings", 0))
    suppressed_link_errors = sum(
        count
        for message, count in exact_suppressions.items()
        if message.startswith("ERROR: en/")
    )
    suppressed_validation_errors = sum(
        count
        for message, count in exact_suppressions.items()
        if message.startswith("ERROR: ") and not message.startswith("ERROR: en/")
    )
    suppressed_errors = suppressed_link_errors + suppressed_validation_errors
    suppressed_warnings = sum(
        count
        for message, count in exact_suppressions.items()
        if message.startswith("WARNING: ")
    )
    accounted_validation_errors = suppressed_validation_errors + offline_terminology_errors
    if publisher_errors < accounted_validation_errors:
        raise ValueError(
            "Publisher error count is smaller than its accounted exact "
            "resource-validation error count"
        )
    if publisher_unsuppressed_warnings < offline_terminology_warnings:
        raise ValueError(
            "Publisher warning count is smaller than its accounted exact "
            "offline terminology warning count"
        )
    return FindingCounts(
        raw_errors=publisher_errors + suppressed_link_errors,
        exact_suppressed_errors=suppressed_errors,
        offline_terminology_errors=offline_terminology_errors,
        unsuppressed_errors=publisher_errors - accounted_validation_errors,
        raw_warnings=publisher_unsuppressed_warnings + suppressed_warnings,
        exact_suppressed_warnings=suppressed_warnings,
        offline_terminology_warnings=offline_terminology_warnings,
        unsuppressed_warnings=(
            publisher_unsuppressed_warnings - offline_terminology_warnings
        ),
    )


ERROR_ROW = re.compile(
    r'<tr[^>]*>\s*'
    r'<td><b>(?P<path>.*?)</b></td>\s*'
    r'<td><b>error</b></td>\s*'
    r'<td><b>(?P<message>.*?)</b>\s*'
    r'<span[^>]*>(?P<diagnostic>[^<]+)</span></td>\s*'
    r'<td>.*?</td>\s*</tr>',
    re.DOTALL,
)

WARNING_ROW = re.compile(
    r'<tr[^>]*>\s*'
    r'<td><b>(?P<path>.*?)</b></td>\s*'
    r'<td><b>warning</b></td>\s*'
    r'<td><b>(?P<message>.*?)</b>\s*'
    r'<span[^>]*>(?P<diagnostic>[^<]*)</span></td>\s*'
    r'<td>.*?</td>\s*</tr>',
    re.DOTALL,
)

OFFLINE_MIME_MESSAGE = re.compile(
    r"^The value provided \('(?P<code>[^']+)'\) was not found in the value set "
    r"'MimeType' \(http://hl7\.org/fhir/ValueSet/mimetypes\|4\.0\.1\), and a code "
    r"is required from this value set \(error message = Cannot invoke "
    r'"org\.hl7\.fhir\.r5\.terminologies\.client\.TerminologyClientContext\.getAddress\(\)" '
    r'because "tc" is null\)$'
)

CONTENT_TYPE_PATH = re.compile(
    r"^DocumentReference\.content\[(?P<index>[0-9]+)\]\.attachment\.contentType "
    r"\(l[0-9]+/c[0-9]+\)$"
)

OFFLINE_NO_SERVICE_MESSAGE = re.compile(
    r"^Unable to validate code '(?P<code>.*)' in system '(?P<system>[^']+)' "
    r"because the validator is running without terminology services$"
)

UNKNOWN_CODE_SYSTEM_MESSAGE = re.compile(
    r"^A definition for CodeSystem '(?P<system>[^']+)' could not be found, "
    r"so the code cannot be validated$"
)

IMPLEMENTATION_LANGUAGE_SYSTEM_PATH = re.compile(
    r"^ImplementationGuide\.language\.system \(l[0-9]+/c[0-9]+\)$"
)

IMPLEMENTATION_LANGUAGE_PATH = re.compile(
    r"^ImplementationGuide\.language \(l[0-9]+/c[0-9]+\)$"
)

STRUCTURE_DEFINITION_PATTERN_PATH = re.compile(
    r"^StructureDefinition\.(?P<section>snapshot|differential)\.element\["
    r"(?P<index>[0-9]+)\]\.pattern\.ofType\(CodeableConcept\) "
    r"\(l[0-9]+/c[0-9]+\)$"
)

RESOURCE_CODEABLE_CONCEPT_PATH = re.compile(
    r"^(?P<resource>[A-Z][A-Za-z]+)(?P<segments>"
    r"(?:\.[A-Za-z][A-Za-z0-9]*(?:\[[0-9]+\])?)+) "
    r"\(l[0-9]+/c[0-9]+\)$"
)

UCUM_QUANTITY_PATH = re.compile(
    r"^(?P<resource>[A-Z][A-Za-z]+)"
    r"(?P<component>\.component\[(?P<index>[0-9]+)\])?"
    r"\.value\.ofType\(Quantity\)\."
    r"(?P<leaf>system|code\.system|code) \(l[0-9]+/c[0-9]+\)$"
)

OFFLINE_CODEABLE_CONCEPT_MESSAGE = (
    'Error Cannot invoke "org.hl7.fhir.r5.terminologies.client.'
    'TerminologyClientContext.getAddress()" because "tc" is null validating '
    "CodeableConcept"
)

BCP47 = "urn:ietf:bcp:47"
ISO_IEEE_11073 = "urn:iso:std:iso:11073:10101"


def plain_html(fragment: str) -> str:
    """Normalize one Publisher HTML cell without weakening its wording."""
    plain = html.unescape(re.sub(r"<[^>]+>", "", fragment)).replace("\u200b", "")
    return " ".join(plain.split())


def offline_mime_error_count(
    guide: Path,
    registry_path: Path = ROOT / "catalog/format-registry.json",
) -> int:
    """Count only Publisher 2.3.3's exact registered-MIME false positive.

    Every accepted row is tied back to the generated resource and its registry
    format. Any changed Publisher version, path, diagnostic, value set, message,
    resource type, format system/code, or content type does not match and remains
    an unsuppressed error in ``finding_counts``.
    """

    qa_html = (guide / "output/qa.html").read_text(encoding="utf-8")
    if "IG Publisher Version: v2.3.3" not in qa_html:
        return 0

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    media_types = set(registry["mediaTypes"])
    format_system = registry["codeSystem"]
    formats = registry["formats"]
    count = 0

    for section in re.split(r"<h2>", qa_html)[1:]:
        resource_match = re.match(
            r'\s*<a href="[^"]+">fsh-generated/resources/'
            r'(?P<filename>[^<]+)\.json</a>',
            section,
        )
        if resource_match is None:
            continue
        resource_path = (
            guide
            / "fsh-generated/resources"
            / f"{resource_match.group('filename')}.json"
        )
        try:
            resource = json.loads(resource_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if resource.get("resourceType") != "DocumentReference":
            continue

        table = section.partition("</table>")[0]
        for raw_row in re.findall(r"<tr[^>]*>.*?</tr>", table, re.DOTALL):
            row = ERROR_ROW.fullmatch(raw_row)
            if row is None:
                continue
            if plain_html(row.group("diagnostic")) != "Terminology_TX_NoValid_16":
                continue
            path_match = CONTENT_TYPE_PATH.fullmatch(plain_html(row.group("path")))
            message_match = OFFLINE_MIME_MESSAGE.fullmatch(
                plain_html(row.group("message"))
            )
            if path_match is None or message_match is None:
                continue
            code = message_match.group("code")
            if code not in media_types:
                continue
            index = int(path_match.group("index"))
            content = resource.get("content")
            if not isinstance(content, list) or index >= len(content):
                continue
            entry = content[index]
            if not isinstance(entry, dict):
                continue
            attachment = entry.get("attachment")
            format_coding = entry.get("format")
            if not isinstance(attachment, dict) or not isinstance(format_coding, dict):
                continue
            format_code = format_coding.get("code")
            registered_format = formats.get(format_code)
            if (
                attachment.get("contentType") != code
                or format_coding.get("system") != format_system
                or not isinstance(registered_format, dict)
                or registered_format.get("contentType") != code
            ):
                continue
            count += 1
    return count


def resource_contains_coding(value: object, system: str, code: str) -> bool:
    """Whether a generated resource actually carries one exact system/code pair."""
    if isinstance(value, dict):
        if value.get("system") == system and value.get("code") == code:
            return True
        return any(
            resource_contains_coding(child, system, code) for child in value.values()
        )
    if isinstance(value, list):
        return any(resource_contains_coding(child, system, code) for child in value)
    return False


def terminology_evidence() -> tuple[
    dict[str, object], dict[str, object], UcumTable, set[str]
]:
    """Load the checked-in terminology evidence used by offline QA accounting."""
    terminology = ROOT / "catalog/terminology"
    loinc = json.loads(
        (terminology / "loinc-concepts.json").read_text(encoding="utf-8")
    )["concepts"]
    snomed = json.loads(
        (terminology / "snomed-concepts.json").read_text(encoding="utf-8")
    )["concepts"]
    ucum = UcumTable(
        json.loads((terminology / "ucum-units.json").read_text(encoding="utf-8"))
    )
    ucum_annotations = set(
        json.loads(
            (terminology / "ucum-annotations.json").read_text(encoding="utf-8")
        )["annotations"]
    )
    return loinc, snomed, ucum, ucum_annotations


def iso_11073_evidence() -> dict[str, object]:
    """Load the exact ISO/IEEE 11073 system/code excerpt admitted offline."""
    evidence = json.loads(
        (
            ROOT
            / "catalog/terminology/iso-11073-10101-concepts.json"
        ).read_text(encoding="utf-8")
    )
    concepts = evidence.get("concepts")
    if evidence.get("system") != ISO_IEEE_11073 or not isinstance(concepts, dict):
        raise ValueError("invalid ISO/IEEE 11073 terminology evidence")
    return concepts


PUBLISHER_RESOURCE_ANNOTATION = re.compile(
    r"/\*(?P<resource>[A-Z][A-Za-z0-9]+)/(?P<id>[A-Za-z0-9.-]+)\*/"
)
FHIR_PATH_LOCATION = re.compile(
    r"^(?P<body>.+) \(l[0-9]+/c[0-9]+\)$"
)
FHIR_PATH_SEGMENT = re.compile(
    r"^(?P<name>[A-Za-z][A-Za-z0-9]*)(?:\[(?P<index>[0-9]+)\])?$"
)
STRUCTURE_DEFINITION_CODING_SYSTEM_PATH = re.compile(
    r"^StructureDefinition\.(?P<section>snapshot|differential)\.element\["
    r"(?P<element>[0-9]+)\]\.pattern\.ofType\(CodeableConcept\)\.coding\["
    r"(?P<coding>[0-9]+)\]\.system$"
)


def resolve_fhir_path(resource: dict[str, object], path: str) -> object:
    """Resolve the simple indexed instance paths used by Publisher QA rows."""
    resource_type, separator, segments = path.partition(".")
    if not separator or resource.get("resourceType") != resource_type:
        return None
    value: object = resource
    for raw_segment in segments.split("."):
        segment = FHIR_PATH_SEGMENT.fullmatch(raw_segment)
        if segment is None or not isinstance(value, dict):
            return None
        value = value.get(segment.group("name"))
        raw_index = segment.group("index")
        if raw_index is not None:
            index = int(raw_index)
            if not isinstance(value, list) or index >= len(value):
                return None
            value = value[index]
    return value


def coding_at_system_warning_path(
    resource: dict[str, object], path: str
) -> dict[str, object] | None:
    """Resolve only Publisher paths that point to one Coding.system value."""
    location = FHIR_PATH_LOCATION.fullmatch(path)
    if location is None:
        return None
    body = location.group("body")
    for annotation in PUBLISHER_RESOURCE_ANNOTATION.finditer(body):
        annotated_path = PUBLISHER_RESOURCE_ANNOTATION.sub(
            "", body[: annotation.start()]
        )
        annotated = resolve_fhir_path(resource, annotated_path)
        if (
            not isinstance(annotated, dict)
            or annotated.get("resourceType") != annotation.group("resource")
            or annotated.get("id") != annotation.group("id")
        ):
            return None
    body = PUBLISHER_RESOURCE_ANNOTATION.sub("", body)
    structure_path = STRUCTURE_DEFINITION_CODING_SYSTEM_PATH.fullmatch(body)
    if structure_path is not None:
        if resource.get("resourceType") != "StructureDefinition":
            return None
        section = resource.get(structure_path.group("section"))
        elements = section.get("element") if isinstance(section, dict) else None
        element_index = int(structure_path.group("element"))
        if not isinstance(elements, list) or element_index >= len(elements):
            return None
        element = elements[element_index]
        concept = (
            element.get("patternCodeableConcept")
            if isinstance(element, dict)
            else None
        )
        codings = concept.get("coding") if isinstance(concept, dict) else None
        coding_index = int(structure_path.group("coding"))
        if not isinstance(codings, list) or coding_index >= len(codings):
            return None
        coding = codings[coding_index]
        return coding if isinstance(coding, dict) else None

    if not body.endswith(".system"):
        return None
    parent_path = body[: -len(".system")]
    if not re.search(r"(?:^|\.)coding\[[0-9]+\]$", parent_path):
        return None
    value = resolve_fhir_path(resource, parent_path)
    return value if isinstance(value, dict) else None


def iso_11073_coding_is_ratified(
    coding: object, concepts: dict[str, object]
) -> bool:
    """Require the exact ISO/IEEE system, pinned code, and any stated display."""
    if not isinstance(coding, dict) or coding.get("system") != ISO_IEEE_11073:
        return False
    code = coding.get("code")
    row = concepts.get(code) if isinstance(code, str) else None
    if not isinstance(row, dict) or row.get("status") != "verified":
        return False
    display = coding.get("display")
    return display is None or display == row.get("display")


def ratified_external_code(
    system: str,
    code: str,
    loinc: dict[str, object],
    snomed: dict[str, object],
    ucum: UcumTable,
    ucum_annotations: set[str],
) -> bool:
    """Check one external code against the deterministic terminology evidence."""
    if system == LOINC:
        row = loinc.get(code)
        return isinstance(row, dict) and row.get("status") == "ACTIVE"
    if system == SNOMED:
        row = snomed.get(code)
        return isinstance(row, dict) and row.get("status") == "ACTIVE"
    if system != UCUM:
        return False
    try:
        parsed = ucum.parse(code)
    except UcumError:
        return False
    return set(parsed.annotations) <= ucum_annotations


def offline_no_service_warning_count(guide: Path) -> int:
    """Count exact no-service warnings backed by pinned terminology evidence.

    The warning must occur on a generated resource that actually carries the
    reported coding. LOINC and SNOMED codes must be active in the pinned excerpts;
    UCUM must parse under the pinned essence table and use only approved annotations.
    Other systems, messages, diagnostics, resource contexts, and Publisher versions
    remain ordinary unsuppressed warnings.
    """

    qa_html = (guide / "output/qa.html").read_text(encoding="utf-8")
    if "IG Publisher Version: v2.3.3" not in qa_html:
        return 0
    loinc, snomed, ucum, ucum_annotations = terminology_evidence()
    count = 0

    for section in re.split(r"<h2>", qa_html)[1:]:
        resource_match = re.match(
            r'\s*<a href="[^"]+">fsh-generated/resources/'
            r'(?P<filename>[^<]+)\.json</a>',
            section,
        )
        if resource_match is None:
            continue
        resource_path = (
            guide
            / "fsh-generated/resources"
            / f"{resource_match.group('filename')}.json"
        )
        try:
            resource = json.loads(resource_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        table = section.partition("</table>")[0]
        for raw_row in re.findall(r"<tr[^>]*>.*?</tr>", table, re.DOTALL):
            row = WARNING_ROW.fullmatch(raw_row)
            if row is None or plain_html(row.group("diagnostic")) != (
                "Error_validating_code_running_without_terminology_services"
            ):
                continue
            message_match = OFFLINE_NO_SERVICE_MESSAGE.fullmatch(
                plain_html(row.group("message"))
            )
            if message_match is None:
                continue
            system = message_match.group("system")
            code = message_match.group("code")
            if not resource_contains_coding(resource, system, code):
                continue
            if not ratified_external_code(
                system, code, loinc, snomed, ucum, ucum_annotations
            ):
                continue
            count += 1
    return count


def offline_unknown_code_system_warning_count(guide: Path) -> int:
    """Count exact offline lookup failures for two external system identifiers.

    BCP 47 is admitted only for the generated ImplementationGuide's literal
    English language. ISO/IEEE 11073 is admitted only when the warning points to
    the exact Coding.system and its adjacent code is in the pinned terminology
    excerpt. UCUM is admitted only for the exact Quantity path and a code accepted
    by the pinned UCUM tables. Other systems and contexts remain unsuppressed.
    """

    qa_html = (guide / "output/qa.html").read_text(encoding="utf-8")
    if "IG Publisher Version: v2.3.3" not in qa_html:
        return 0
    loinc, snomed, ucum, ucum_annotations = terminology_evidence()
    iso_11073 = iso_11073_evidence()
    count = 0

    for section in re.split(r"<h2>", qa_html)[1:]:
        resource_match = re.match(
            r'\s*<a href="[^"]+">fsh-generated/resources/'
            r'(?P<filename>[^<]+)\.json</a>',
            section,
        )
        if resource_match is None:
            continue
        # Publisher injects the configured default language into its generated
        # ImplementationGuide output, while SUSHI's intermediate file omits it.
        # Resolve the exact resource Publisher validated.
        resource_path = guide / "output" / f"{resource_match.group('filename')}.json"
        try:
            resource = json.loads(resource_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        table = section.partition("</table>")[0]
        for raw_row in re.findall(r"<tr[^>]*>.*?</tr>", table, re.DOTALL):
            row = WARNING_ROW.fullmatch(raw_row)
            if row is None:
                continue
            message_match = UNKNOWN_CODE_SYSTEM_MESSAGE.fullmatch(
                plain_html(row.group("message"))
            )
            if message_match is None:
                continue
            path = plain_html(row.group("path"))
            diagnostic = plain_html(row.group("diagnostic"))
            system = message_match.group("system")
            if system == BCP47:
                if resource.get("resourceType") != "ImplementationGuide":
                    continue
                if resource.get("language") != "en":
                    continue
                if IMPLEMENTATION_LANGUAGE_SYSTEM_PATH.fullmatch(path):
                    if diagnostic != "UNKNOWN_CODESYSTEM":
                        continue
                elif IMPLEMENTATION_LANGUAGE_PATH.fullmatch(path):
                    if diagnostic:
                        continue
                else:
                    continue
                count += 1
                continue
            if (
                system == ISO_IEEE_11073
                and diagnostic == "UNKNOWN_CODESYSTEM"
                and iso_11073_coding_is_ratified(
                    coding_at_system_warning_path(resource, path), iso_11073
                )
            ):
                count += 1
                continue
            if system != UCUM:
                continue
            quantity_path = UCUM_QUANTITY_PATH.fullmatch(path)
            if (
                quantity_path is None
                or resource.get("resourceType") != quantity_path.group("resource")
            ):
                continue
            value: object = resource
            raw_index = quantity_path.group("index")
            if raw_index is not None:
                if not isinstance(value, dict):
                    continue
                components = value.get("component")
                index = int(raw_index)
                if not isinstance(components, list) or index >= len(components):
                    continue
                value = components[index]
            if not isinstance(value, dict):
                continue
            quantity = value.get("valueQuantity")
            if not isinstance(quantity, dict):
                continue
            code = quantity.get("code")
            if quantity.get("system") != UCUM or not isinstance(code, str):
                continue
            if not ratified_external_code(
                UCUM, code, loinc, snomed, ucum, ucum_annotations
            ):
                continue
            if quantity_path.group("leaf") == "code":
                if diagnostic:
                    continue
            elif diagnostic != "UNKNOWN_CODESYSTEM":
                continue
            count += 1
    return count


def resolve_codeable_concept_path(resource: dict[str, object], path: str) -> object:
    """Resolve the limited instance paths emitted by the accepted warning family."""
    match = RESOURCE_CODEABLE_CONCEPT_PATH.fullmatch(path)
    if match is None or resource.get("resourceType") != match.group("resource"):
        return None
    value: object = resource
    for segment, raw_index in re.findall(
        r"\.([A-Za-z][A-Za-z0-9]*)(?:\[([0-9]+)\])?", match.group("segments")
    ):
        if not isinstance(value, dict) or segment not in value:
            return None
        value = value[segment]
        if raw_index:
            index = int(raw_index)
            if not isinstance(value, list) or index >= len(value):
                return None
            value = value[index]
    return value


def codeable_concept_is_ratified(
    value: object,
    loinc: dict[str, object],
    snomed: dict[str, object],
    ucum: UcumTable,
    ucum_annotations: set[str],
) -> bool:
    """Require every Coding in a CodeableConcept to have pinned valid evidence."""
    if not isinstance(value, dict):
        return False
    codings = value.get("coding")
    if not isinstance(codings, list) or not codings:
        return False
    for coding in codings:
        if not isinstance(coding, dict):
            return False
        system = coding.get("system")
        code = coding.get("code")
        if not isinstance(system, str) or not isinstance(code, str):
            return False
        if not ratified_external_code(
            system, code, loinc, snomed, ucum, ucum_annotations
        ):
            return False
    return True


def offline_codeable_concept_warning_count(guide: Path) -> int:
    """Count exact Publisher tc-null warnings whose complete coding is pinned.

    StructureDefinition pattern paths are resolved against Publisher's generated
    snapshot/differential output. Instance paths are resolved against SUSHI's
    generated resource. The exact path and every coding must be independently
    valid in Grove's pinned terminology evidence.
    """

    qa_html = (guide / "output/qa.html").read_text(encoding="utf-8")
    if "IG Publisher Version: v2.3.3" not in qa_html:
        return 0
    loinc, snomed, ucum, ucum_annotations = terminology_evidence()
    count = 0

    for section in re.split(r"<h2>", qa_html)[1:]:
        resource_match = re.match(
            r'\s*<a href="[^"]+">fsh-generated/resources/'
            r'(?P<filename>[^<]+)\.json</a>',
            section,
        )
        if resource_match is None:
            continue
        filename = resource_match.group("filename")
        source_path = guide / "fsh-generated/resources" / f"{filename}.json"
        publisher_path = guide / "output" / f"{filename}.json"
        try:
            source_resource = json.loads(source_path.read_text(encoding="utf-8"))
            publisher_resource = json.loads(
                publisher_path.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError):
            continue
        table = section.partition("</table>")[0]
        for raw_row in re.findall(r"<tr[^>]*>.*?</tr>", table, re.DOTALL):
            row = WARNING_ROW.fullmatch(raw_row)
            if row is None:
                continue
            if plain_html(row.group("diagnostic")) != (
                "Terminology_TX_Error_CodeableConcept"
            ):
                continue
            if plain_html(row.group("message")) != OFFLINE_CODEABLE_CONCEPT_MESSAGE:
                continue
            path = plain_html(row.group("path"))
            pattern_match = STRUCTURE_DEFINITION_PATTERN_PATH.fullmatch(path)
            if pattern_match is not None:
                if publisher_resource.get("resourceType") != "StructureDefinition":
                    continue
                elements = publisher_resource.get(pattern_match.group("section"), {})
                if not isinstance(elements, dict):
                    continue
                elements = elements.get("element")
                index = int(pattern_match.group("index"))
                if not isinstance(elements, list) or index >= len(elements):
                    continue
                element = elements[index]
                if not isinstance(element, dict):
                    continue
                concept = element.get("patternCodeableConcept")
            else:
                concept = resolve_codeable_concept_path(source_resource, path)
            if codeable_concept_is_ratified(
                concept, loinc, snomed, ucum, ucum_annotations
            ):
                count += 1
    return count


def configured_suppressions(path: Path) -> list[str]:
    """Read only exact, resource-scoped Publisher suppression messages."""
    messages: list[str] = []
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#") or line == "== Suppressed Messages ==":
            continue
        if not line.startswith(("WARNING: ", "ERROR: ")):
            raise ValueError(
                f"{path}:{line_number} is a broad suppression; exact messages must "
                "start with WARNING: or ERROR:"
            )
        messages.append(" ".join(line.split()))
    if len(messages) != len(set(messages)):
        raise ValueError(f"{path} repeats an exact suppression")
    return messages


def exercised_suppressions(path: Path) -> dict[str, int]:
    """Extract exact suppressed messages and their Publisher use counts."""
    qa = path.read_text(encoding="utf-8")
    _, marker, suppressed = qa.partition('<a name="suppressed">')
    if not marker:
        return {}
    suppressed = suppressed.partition('<a name="sorted">')[0]
    result: dict[str, int] = {}
    for raw_message, raw_count in SUPPRESSED_MESSAGE.findall(suppressed):
        message = " ".join(html.unescape(re.sub(r"<[^>]+>", "", raw_message)).split())
        if message in result:
            raise ValueError(f"{path} repeats suppressed message {message!r}")
        result[message] = int(raw_count)
    return result


BROKEN_LINK = re.compile(r"The link '([^']+)'")


def broken_link_targets(qa_path: Path) -> set[str]:
    """Every distinct target the Publisher could not resolve.

    Counted separately from warnings: the Publisher reports broken links in its own tally, so a
    guide can carry them while reporting zero warnings, which is how they stayed invisible.
    """
    qa = qa_path.read_text(encoding="utf-8")
    _, marker, internal = qa.partition('<a name="internal">')
    if not marker:
        return set()
    plain = html.unescape(re.sub(r"<[^>]+>", " ", internal)).replace("\u200b", "")
    return set(BROKEN_LINK.findall(plain))


def configured_broken_links(path: Path) -> set[str]:
    """Targets a guide declares unresolvable, each with a reason in the file."""
    if not path.is_file():
        return set()
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }


def validate_broken_links(guide: Path) -> list[str]:
    declared = configured_broken_links(guide / "input" / "expectedBrokenLinks.txt")
    found = broken_link_targets(guide / "output" / "qa.html")
    problems = [f"undeclared broken link: {target}" for target in sorted(found - declared)]
    problems.extend(
        f"declared broken link no longer occurs: {target}" for target in sorted(declared - found)
    )
    return problems


def validate_suppressions(guide: Path) -> list[str]:
    """Return exact configuration/execution mismatches for one built guide."""
    configured_path = guide / "input" / "ignoreWarnings.txt"
    qa_path = guide / "output" / "qa.html"
    if not configured_path.is_file():
        return [f"missing {configured_path}"]
    if not qa_path.is_file():
        return [f"missing {qa_path}"]
    try:
        configured = configured_suppressions(configured_path)
        exercised = exercised_suppressions(qa_path)
    except ValueError as error:
        return [str(error)]
    problems = [
        f"configured suppression was not exercised exactly: {message}"
        for message in configured
        if exercised.get(message) != 1
    ]
    problems.extend(
        f"Publisher exercised an unconfigured suppression: {message}"
        for message in sorted(set(exercised) - set(configured))
    )
    return problems


def validate_rendered_pages(guide: Path) -> list[str]:
    """Reject Publisher template failures that are absent from ``qa.json``.

    The Publisher can replace a failed ``json``/``xml`` Liquid directive with a
    visible ``Script …: …`` paragraph, return success, and report zero errors.
    That is broken documentation even though the resource-validation ledger is
    clean, so inspect the materialized pages as part of the same fail-closed gate.
    """

    output = guide / "output"
    if not output.is_dir():
        return [f"missing {output}"]
    problems: list[str] = []
    for page in sorted(output.rglob("*.html")):
        rendered = page.read_text(encoding="utf-8", errors="replace")
        for match in RENDERED_TEMPLATE_ERROR.finditer(rendered):
            problems.append(
                "rendered template error in "
                f"{page.relative_to(guide)}: {plain_html(match.group(0))}"
            )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", action="store_true", help="append a table to the GitHub job summary")
    parser.add_argument(
        "--offline-terminology",
        action="store_true",
        help=(
            "account only exact Publisher 2.3.3 absent-terminology-client findings "
            "backed by authoritative registry or terminology evidence"
        ),
    )
    parser.add_argument("guides", nargs="+", type=Path)
    arguments = parser.parse_args()

    rows: list[tuple[str, FindingCounts | None, int]] = []
    failed = False
    for guide in arguments.guides:
        qa_path = guide / "output" / "qa.json"
        if not qa_path.is_file():
            print(f"{guide}: missing {qa_path}")
            rows.append((str(guide), None, -1))
            failed = True
            continue
        qa = json.loads(qa_path.read_text(encoding="utf-8"))
        hints = int(qa.get("hints", 0))
        suppression_problems = validate_suppressions(guide)
        suppression_problems.extend(validate_broken_links(guide))
        suppression_problems.extend(validate_rendered_pages(guide))
        try:
            exact_suppressions = exercised_suppressions(guide / "output" / "qa.html")
            offline_terminology_errors = (
                offline_mime_error_count(guide)
                if arguments.offline_terminology
                else 0
            )
            offline_terminology_warnings = (
                offline_no_service_warning_count(guide)
                + offline_unknown_code_system_warning_count(guide)
                + offline_codeable_concept_warning_count(guide)
                if arguments.offline_terminology
                else 0
            )
            counts = finding_counts(
                qa,
                exact_suppressions,
                offline_terminology_errors,
                offline_terminology_warnings,
            )
        except ValueError as error:
            suppression_problems.append(str(error))
            counts = FindingCounts(-1, -1, -1, -1, -1, -1, -1, -1)
        rows.append((str(guide), counts, hints))
        print(
            f"{guide}: raw-errors={counts.raw_errors} "
            f"exact-suppressed-errors={counts.exact_suppressed_errors} "
            f"offline-terminology-errors={counts.offline_terminology_errors} "
            f"unsuppressed-errors={counts.unsuppressed_errors} "
            f"raw-warnings={counts.raw_warnings} "
            f"exact-suppressed-warnings={counts.exact_suppressed_warnings} "
            f"offline-terminology-warnings={counts.offline_terminology_warnings} "
            f"unsuppressed-warnings={counts.unsuppressed_warnings} hints={hints} "
            f"broken-links={len(broken_link_targets(guide / 'output' / 'qa.html'))}"
        )
        failed |= counts.unsuppressed_errors != 0 or counts.unsuppressed_warnings != 0
        for problem in suppression_problems:
            print(f"{guide}: {problem}")
        failed |= bool(suppression_problems)

    if arguments.summary and (summary_path := os.environ.get("GITHUB_STEP_SUMMARY")):
        with Path(summary_path).open("a", encoding="utf-8") as summary:
            summary.write("## FHIR implementation-guide QA\n\n")
            summary.write(
                "| Guide | Raw errors | Exact-suppressed errors | "
                "Offline terminology errors | Unsuppressed errors | "
                "Raw warnings | Exact-suppressed warnings | "
                "Offline terminology warnings | Unsuppressed warnings | Hints |\n"
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n"
            )
            for guide, counts, hints in rows:
                if counts is None:
                    summary.write(
                        f"| `{guide}` | - | - | - | - | - | - | - | - | {hints} |\n"
                    )
                    continue
                summary.write(
                    f"| `{guide}` | {counts.raw_errors} | "
                    f"{counts.exact_suppressed_errors} | "
                    f"{counts.offline_terminology_errors} | "
                    f"{counts.unsuppressed_errors} | "
                    f"{counts.raw_warnings} | {counts.exact_suppressed_warnings} | "
                    f"{counts.offline_terminology_warnings} | "
                    f"{counts.unsuppressed_warnings} | {hints} |\n"
                )

    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
