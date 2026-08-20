#!/usr/bin/env python3
"""Re-derive closed adapter source inventories from the platforms that define them.

Each adapter catalog claims to enumerate a platform's source concepts exactly, so the
claim is re-derived here rather than trusted.

A producer tags an Observation with the identifier the platform hands back at runtime.
For most Apple constants that string equals the constant's own name, but not for all of
them, and two sample types have no constant at all. The Apple inventories are therefore
read by running code inside a simulator on the SDK baseline, not by parsing headers:
headers give the names to resolve, the runtime gives the identifiers. Health Connect
needs none of this because its codes are class names in the published artifact.
"""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
DUMPER = ROOT / "Scripts/apple-identifier-dump.m"

APPLE_DOCUMENTATION = "https://developer.apple.com"
APPLE_SYMBOL_INDEX = "https://developer.apple.com/tutorials/data/index/{framework}"
ANDROID_RECORD_DOCUMENTATION = (
    "https://developer.android.com/reference/androidx/health/connect/client/records/{record}"
)
HEALTH_CONNECT_ARTIFACT = (
    "https://dl.google.com/dl/android/maven2/androidx/health/connect"
    "/connect-client/{version}/connect-client-{version}.aar"
)

# Sample types Apple publishes without an identifier constant. The dumper reads these
# from the type itself and reports them under the accessor that returns them, which is
# documented on the returned type rather than on the class holding the accessor.
# Headers whose hashes pin the exact SDK the identifiers were read from.
EVIDENCE_HEADERS = {
    "HealthKit": ("HKTypeIdentifiers.h", "HKObjectType.h", "HKMetadata.h", "HKMetadataEnums.h"),
    "SensorKit": ("SRSensor.h",),
}

HEALTHKIT_ACCESSORS = {
    "HKObjectType.electrocardiogramType()": "HKElectrocardiogramType",
    "HKSampleType.audiogramSampleType()": "HKAudiogramSampleType",
}

# Abstract supertypes in the Health Connect record hierarchy, which are not readable
# record classes.
HEALTH_CONNECT_ABSTRACT = frozenset(
    {"Record", "InstantaneousRecord", "IntervalRecord", "SeriesRecord"}
)

_TYPED_IDENTIFIER = re.compile(r"HK_EXTERN\s+(HK\w*TypeIdentifier)\s+const\s+(HK\w+)")
_UNTYPED_IDENTIFIER = re.compile(r"HK_EXTERN\s+NSString\s*\*\s*const\s+(HK\w+)")
_SENSOR = re.compile(r"SR_EXTERN\s+SRSensor\s+const\s+(SRSensor\w+)")

# HealthKit source types declared as plain strings. Metadata keys, sort identifiers,
# predicate key paths, and device properties share that declaration shape, so the
# source types are named rather than pattern-matched.
_HEALTHKIT_UNTYPED = frozenset(
    {
        "HKDataTypeIdentifierHeartbeatSeries",
        "HKDataTypeIdentifierStateOfMind",
        "HKDataTypeIdentifierUserAnnotatedMedicationConcept",
        "HKMedicationDoseEventTypeIdentifierMedicationDoseEvent",
        "HKVisionPrescriptionTypeIdentifier",
        "HKWorkoutRouteTypeIdentifier",
        "HKWorkoutTypeIdentifier",
    }
)


class PlatformUnavailable(RuntimeError):
    """A platform source of truth is not reachable from this machine."""


def _run(command: list[str], **kwargs: Any) -> str:
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, check=True, **kwargs
        )
    except (OSError, subprocess.CalledProcessError) as error:
        detail = getattr(error, "stderr", "") or error
        raise PlatformUnavailable(f"{' '.join(command)}: {detail}") from error
    return result.stdout.strip()


def _download(url: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            ["curl", "--silent", "--show-error", "--fail", "--location",
             "--output", str(destination), url],
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        destination.unlink(missing_ok=True)
        raise PlatformUnavailable(f"could not download {url}") from error
    return destination


# --------------------------------------------------------------------------- #
# Declared constant names
# --------------------------------------------------------------------------- #


def sdk_baseline() -> dict[str, str]:
    version = _run(["xcrun", "--sdk", "iphoneos", "--show-sdk-version"])
    xcode = _run(["xcodebuild", "-version"]).split()
    return {
        "platform": "iPhoneOS",
        "version": version,
        "xcodeVersion": xcode[1],
        "xcodeBuild": xcode[-1],
    }


def framework_headers(framework: str) -> Path:
    sdk = Path(_run(["xcrun", "--sdk", "iphoneos", "--show-sdk-path"]))
    headers = sdk / f"System/Library/Frameworks/{framework}.framework/Headers"
    if not headers.is_dir():
        raise PlatformUnavailable(f"{framework} headers not found at {headers}")
    return headers


def header_hashes(framework: str) -> dict[str, str]:
    headers = framework_headers(framework)
    return {
        name: hashlib.sha256((headers / name).read_bytes()).hexdigest()
        for name in EVIDENCE_HEADERS[framework]
        if (headers / name).is_file()
    }


def _header_text(framework: str) -> str:
    return "\n".join(
        header.read_text(errors="ignore")
        for header in framework_headers(framework).rglob("*.h")
    )


def healthkit_constant_names() -> list[str]:
    text = _header_text("HealthKit")
    names = {name for _, name in _TYPED_IDENTIFIER.findall(text)}
    names |= {name for name in _UNTYPED_IDENTIFIER.findall(text) if name in _HEALTHKIT_UNTYPED}
    missing = _HEALTHKIT_UNTYPED - names
    if missing:
        raise PlatformUnavailable(f"SDK is missing expected source types: {sorted(missing)}")
    return sorted(names)


def sensorkit_constant_names() -> list[str]:
    names = sorted(set(_SENSOR.findall(_header_text("SensorKit"))))
    if not names:
        raise PlatformUnavailable("no SRSensor constants found in the SensorKit headers")
    return names


# --------------------------------------------------------------------------- #
# Runtime identifiers, read inside a simulator on the SDK baseline
# --------------------------------------------------------------------------- #


def _simulator_on_baseline(major: str) -> tuple[str, bool]:
    """A booted device on the baseline runtime, and whether we created it."""
    devices = json.loads(_run(["xcrun", "simctl", "list", "devices", "--json"]))["devices"]
    runtime = next(
        (key for key in devices if key.endswith(f"iOS-{major}-0") or f"iOS-{major}-" in key),
        None,
    )
    if runtime is None:
        raise PlatformUnavailable(f"no installed iOS {major} simulator runtime")
    for device in devices[runtime]:
        if device.get("state") == "Booted":
            return device["udid"], False
    identifier = _run(
        ["xcrun", "simctl", "create", "grove-platform-inventory", "iPhone 17 Pro", runtime]
    )
    _run(["xcrun", "simctl", "boot", identifier])
    subprocess.run(["xcrun", "simctl", "bootstatus", identifier, "-b"], capture_output=True)
    return identifier, True


def apple_identifier_values(names: list[str]) -> dict[str, str]:
    """Map each constant name, and each class accessor, to the identifier it yields."""
    if not DUMPER.is_file():
        raise PlatformUnavailable(f"{DUMPER} is missing")
    baseline = sdk_baseline()
    major = baseline["version"].split(".")[0]
    with tempfile.TemporaryDirectory() as scratch:
        work = Path(scratch)
        listing, binary = work / "names.txt", work / "dump"
        listing.write_text("\n".join(names), encoding="utf-8")
        _run([
            "xcrun", "--sdk", "iphonesimulator", "clang", "-fobjc-arc",
            "-target", f"arm64-apple-ios{baseline['version']}-simulator",
            "-framework", "Foundation", "-framework", "HealthKit", "-framework", "SensorKit",
            str(DUMPER), "-o", str(binary),
        ])
        device, created = _simulator_on_baseline(major)
        try:
            dumped = _run(["xcrun", "simctl", "spawn", device, str(binary), str(listing)])
        finally:
            if created:
                subprocess.run(["xcrun", "simctl", "delete", device], capture_output=True)
    values = dict(line.split("\t", 1) for line in dumped.splitlines() if "\t" in line)
    expected = set(names) | set(HEALTHKIT_ACCESSORS)
    if values.keys() != expected:
        raise PlatformUnavailable(
            f"the simulator resolved {len(values)} of {len(expected)} identifiers"
        )
    return values


# --------------------------------------------------------------------------- #
# Apple documentation, from the published symbol index
# --------------------------------------------------------------------------- #


def _walk(nodes: list[dict[str, Any]]) -> Iterator[dict[str, Any]]:
    for node in nodes:
        yield node
        yield from _walk(node.get("children") or [])


def apple_documentation(framework: str, *, refresh: bool = False) -> dict[str, dict[str, Any]]:
    """Documentation page and vendor flags for every symbol the index publishes."""
    cached = ROOT / ".build" / "symbol-index" / f"{framework}.json"
    if refresh or not cached.is_file():
        _download(APPLE_SYMBOL_INDEX.format(framework=framework), cached)
    index = json.loads(cached.read_text(encoding="utf-8"))
    languages = index.get("interfaceLanguages", {})
    if "occ" not in languages:
        raise PlatformUnavailable(f"{framework} index has no Objective-C interface")
    pages: dict[str, dict[str, Any]] = {}
    for node in _walk(languages["occ"]):
        title = node.get("title", "")
        if title and "path" in node:
            pages.setdefault(title, {
                "documentation": f"{APPLE_DOCUMENTATION}{node['path']}",
                "beta": bool(node.get("beta")),
                "deprecated": bool(node.get("deprecated")),
            })
    return pages


# --------------------------------------------------------------------------- #
# Inventories
# --------------------------------------------------------------------------- #


def _by_identifier(
    values: dict[str, str], pages: dict[str, dict[str, Any]], symbols: list[str]
) -> dict[str, dict[str, Any]]:
    """Collapse symbols onto the identifier they yield, keeping every declaring name.

    Apple can rename a constant while keeping its value, which leaves two names for one
    source type. The identifier is what a producer emits, so it is what the code is.
    """
    inventory: dict[str, dict[str, Any]] = {}
    for symbol in symbols:
        identifier = values[symbol]
        entry = inventory.setdefault(identifier, {"symbols": [], "documentation": None})
        entry["symbols"].append(symbol)
        page = pages.get(HEALTHKIT_ACCESSORS.get(symbol, symbol))
        # A renamed constant keeps its predecessor's value; document the current name.
        if page and (entry["documentation"] is None or not page["deprecated"]):
            entry["documentation"] = page["documentation"]
    return dict(sorted(inventory.items()))


def healthkit_inventory(*, refresh: bool = False) -> dict[str, dict[str, Any]]:
    names = healthkit_constant_names()
    values = apple_identifier_values(names)
    pages = apple_documentation("healthkit", refresh=refresh)
    return _by_identifier(values, pages, names + list(HEALTHKIT_ACCESSORS))


def sensorkit_inventory(*, refresh: bool = False) -> dict[str, dict[str, Any]]:
    names = sensorkit_constant_names()
    values = apple_identifier_values(names)
    pages = apple_documentation("sensorkit", refresh=refresh)
    return {
        symbol: {
            "identifier": values[symbol],
            "documentation": pages.get(symbol, {}).get("documentation"),
        }
        for symbol in names
    }


def health_connect_inventory(version: str) -> dict[str, Any]:
    """Every concrete Record class published by the Health Connect client artifact."""
    archive = ROOT / ".build" / "health-connect" / f"connect-client-{version}.aar"
    if not archive.is_file():
        _download(HEALTH_CONNECT_ARTIFACT.format(version=version), archive)
    with zipfile.ZipFile(archive) as aar, aar.open("classes.jar") as raw:
        with zipfile.ZipFile(raw) as classes:
            names = classes.namelist()
    prefix = "androidx/health/connect/client/records/"
    records = {
        name[len(prefix) : -len(".class")]
        for name in names
        if name.startswith(prefix)
        and name.endswith("Record.class")
        and "$" not in name
        and "/" not in name[len(prefix) :]
    }
    concrete = sorted(records - HEALTH_CONNECT_ABSTRACT)
    if not concrete:
        raise PlatformUnavailable(f"no Record classes found in {archive}")
    return {
        "artifact": f"androidx.health.connect:connect-client:{version}",
        "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "records": {
            record: {"documentation": ANDROID_RECORD_DOCUMENTATION.format(record=record)}
            for record in concrete
        },
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", choices=("healthkit", "sensorkit", "health-connect"))
    parser.add_argument("--health-connect-version", default="1.1.0")
    arguments = parser.parse_args()
    payloads = {
        "healthkit": healthkit_inventory,
        "sensorkit": sensorkit_inventory,
        "health-connect": lambda: health_connect_inventory(arguments.health_connect_version),
    }
    print(json.dumps(payloads[arguments.inventory](), indent=2, sort_keys=True))
