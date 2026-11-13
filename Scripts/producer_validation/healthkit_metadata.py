"""Validate the typed HealthKit source-metadata extension."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
# SPDX-License-Identifier: MIT

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.parse import urlsplit

from .context import CATALOG_ROOT
from .diagnostics import ProducerValidationError
from .io import read_json
from .payloads import parse_fhir_instant
from .references import extensions_with_url


def validate_healthkit_metadata(resource: dict[str, Any], label: str) -> None:
    """Keep source values typed without admitting arbitrary nested FHIR content."""
    contract = read_json(CATALOG_ROOT / "healthkit-adapter.json")["metadataExtension"]
    url = contract["url"]
    extensions = extensions_with_url(resource, url)
    if not extensions:
        return

    def fail(reason: str) -> None:
        raise ProducerValidationError(f"{label} HealthKit metadata {reason}")

    if len(extensions) != 1:
        fail("must have exactly one container")
    profiles = resource.get("meta", {}).get("profile", [])
    if resource.get("resourceType") not in contract["resourceTypes"] or not any(
        isinstance(profile, str)
        and profile.startswith("https://grovealliance.org/fhir/healthkit/StructureDefinition/")
        for profile in profiles
    ):
        fail("requires a HealthKit output profile")
    container = extensions[0]
    if set(container) != {"url", "extension"}:
        fail("container must contain only typed entries")
    entries = container["extension"]
    if not isinstance(entries, list) or not entries:
        fail("container must not be empty")
    seen: set[str] = set()
    previous: bytes | None = None
    for item in entries:
        if not isinstance(item, dict) or set(item) != {"url", "extension"} or item["url"] != "entry":
            fail("entry must have defined key and value children")
        children = item["extension"]
        if not isinstance(children, list) or len(children) != 2 or not all(isinstance(child, dict) for child in children):
            fail("entry must have exactly a key and a value")
        key_child, entry = children
        if set(key_child) != {"url", "valueString"} or key_child["url"] != "key":
            fail("entry key must be a valueString")
        key = key_child["valueString"]
        if not isinstance(key, str) or not key or key in seen:
            fail("keys must be nonempty and unique")
        try:
            ordered_key = key.encode("utf-16-be", errors="strict")
        except UnicodeError:
            fail("key must be valid Unicode")
        if previous is not None and ordered_key <= previous:
            fail("keys must follow UTF-16 ordering")
        previous = ordered_key
        seen.add(key)
        if len(entry) != 2 or entry.get("url") != "value":
            fail("entry must contain exactly one typed value")
        value_names = set(entry) - {"url"}
        if len(value_names) != 1 or not value_names <= set(contract["valueElements"]):
            fail("entry has an unsupported value type")
        name = next(iter(value_names))
        value = entry[name]
        if name == "valueString":
            if not isinstance(value, str) or not value:
                fail("string must be nonempty")
        elif name == "valueBoolean":
            if not isinstance(value, bool):
                fail("Boolean must be true or false")
        elif name == "valueDecimal":
            if not _finite_number(value):
                fail("decimal must be finite")
        elif name == "valueDateTime":
            parse_fhir_instant(value, f"{label} metadata date")
        elif name == "valueCoding":
            if not isinstance(value, dict) or not set(value) <= {"system", "code", "display"}:
                fail("coding has unsupported fields")
            if not _absolute_uri(value.get("system")) or not _nonempty(value.get("code")):
                fail("coding requires a system and code")
            if "display" in value and not _nonempty(value["display"]):
                fail("coding display must be nonempty")
        elif name == "valueQuantity":
            if not isinstance(value, dict) or not set(value) <= {"value", "system", "code", "unit"}:
                fail("quantity has unsupported fields")
            if not _finite_number(value.get("value")) or value.get("system") != "http://unitsofmeasure.org" or not _nonempty(value.get("code")):
                fail("quantity requires a finite value and UCUM code")
            if "unit" in value and not _nonempty(value["unit"]):
                fail("quantity unit must be nonempty")


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _absolute_uri(value: Any) -> bool:
    if not _nonempty(value) or any(c.isspace() for c in value):
        return False
    try:
        return bool(urlsplit(value).scheme)
    except ValueError:
        return False


def _finite_number(value: Any) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        return False
    try:
        return Decimal(str(value)).is_finite()
    except InvalidOperation:
        return False
