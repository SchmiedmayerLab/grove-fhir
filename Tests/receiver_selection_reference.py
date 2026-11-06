"""An independent reference of lifecycle.active.versionSelection, for checking declared receiver states.

It is not a receiver: it holds no history, grants, or bindings. It selects the current version of
one source record from a set of accepted versions, exactly as the catalog's set rule states.
"""

# This source file is part of the Grove FHIR open-source project
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
# SPDX-License-Identifier: MIT

from __future__ import annotations

import calendar
from dataclasses import dataclass
from fractions import Fraction
import re
from typing import Any, Iterable


ROLE_SYSTEM = "https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role"
ENTRY_KEY = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-exchange-entry-key"
WRITER_VERSION = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-writer-record-version"
LIFECYCLE_EVENT_SYSTEM = "https://grovealliance.org/fhir/mobile/CodeSystem/grove-lifecycle-event"
INSTANT = re.compile(
    r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d+))?(?:Z|([+-])(\d{2}):(\d{2}))"
)
UNSIGNED_DECIMAL = re.compile(r"0|[1-9][0-9]*")


@dataclass(frozen=True)
class Version:
    """One accepted version: its record-version pair, recorded instant, writer evidence, outputs."""

    key: tuple[str, str]
    recorded: str
    writer: tuple[tuple[str, str], str] | None
    outputs: tuple[str, ...]
    name: str = ""


def instant(lexeme: str) -> Fraction:
    """Seconds since the epoch at the full stated precision; never rounded, never text."""
    match = INSTANT.fullmatch(lexeme)
    if match is None:
        raise ValueError(f"{lexeme!r} is not a FHIR instant")
    year, month, day, hour, minute, second = (int(part) for part in match.groups()[:6])
    fraction, sign, offset_hours, offset_minutes = match.groups()[6:]
    seconds = calendar.timegm((year, month, day, hour, minute, second, 0, 0, 0))
    if sign is not None:
        offset = (int(offset_hours) * 60 + int(offset_minutes)) * 60
        seconds += -offset if sign == "+" else offset
    return seconds + (Fraction(int(fraction), 10 ** len(fraction)) if fraction else Fraction(0))


def writer_version_greater(left: str, right: str) -> bool:
    """Canonical unsigned decimals: the longer is greater, decimals of equal length compare bytewise."""
    for value in (left, right):
        if UNSIGNED_DECIMAL.fullmatch(value) is None:
            raise ValueError(f"{value!r} is not a canonical unsigned decimal")
    return (len(left), left.encode("ascii")) > (len(right), right.encode("ascii"))


def select(versions: Iterable[Version]) -> Version | None:
    """Return the current version of one source record under the versionSelection set rule."""
    versions = list(versions)
    # writerOrder: drop every version beaten by a greater writer version of the same writer pair.
    remaining = [
        version for version in versions
        if not any(
            version.writer is not None and other.writer is not None
            and other.writer[0] == version.writer[0]
            and writer_version_greater(other.writer[1], version.writer[1])
            for other in versions
        )
    ]
    if not remaining:
        return None
    # recordedOrder, then tieBreak: the bytewise-greater Identifier.value, then system.
    return max(
        remaining,
        key=lambda version: (
            instant(version.recorded), version.key[1].encode("utf-8"), version.key[0].encode("utf-8")
        ),
    )


def current_outputs(versions: Iterable[Version], retracted: bool = False) -> tuple[str, ...]:
    """versionSelection.membership and .retraction: the selected version's outputs, or none."""
    if retracted:
        return ()
    selected = select(versions)
    return () if selected is None else selected.outputs


def _role(identifier: Any) -> str | None:
    codings = identifier.get("type", {}).get("coding", []) if isinstance(identifier, dict) else []
    return next((coding.get("code") for coding in codings if coding.get("system") == ROLE_SYSTEM), None)


def writer_evidence(outputs: Iterable[dict[str, Any]]) -> tuple[tuple[str, str], str] | None:
    """versionSelection.writerEvidence: the one writer-record pair and version the outputs state."""
    statements = set()
    for output in outputs:
        writers = [item for item in output.get("identifier", []) if _role(item) == "writer-record"]
        versions = [item.get("valueString") for item in output.get("extension", []) if item.get("url") == WRITER_VERSION]
        if not writers and not versions:
            continue
        if len(writers) != 1 or len(versions) != 1:
            return None
        statements.add(((writers[0]["system"], writers[0]["value"]), versions[0]))
    return statements.pop() if len(statements) == 1 else None


def bundle_versions(bundle: dict[str, Any], name: str = "") -> list[tuple[tuple[str, str], Version]]:
    """Every record version of an active Bundle, with its source-record pair."""
    by_url = {entry["fullUrl"]: entry for entry in bundle["entry"]}
    found = []
    for entry in bundle["entry"]:
        resource = entry["resource"]
        if resource["resourceType"] != "Provenance" or any(
            coding.get("system") == LIFECYCLE_EVENT_SYSTEM for coding in resource["activity"]["coding"]
        ):
            continue
        key = next(item["valueIdentifier"] for item in entry["extension"] if item["url"] == ENTRY_KEY)
        source = resource["entity"][0]["what"]["identifier"]
        targets = [target["reference"] for target in resource["target"]]
        found.append(((source["system"], source["value"]), Version(
            key=(key["system"], key["value"]),
            recorded=resource["recorded"],
            writer=writer_evidence(by_url[url]["resource"] for url in targets),
            outputs=tuple(targets),
            name=name,
        )))
    return found
