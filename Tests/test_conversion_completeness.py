#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#

"""Guards for the conversion-completeness work: what a source provides must reach the output."""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADAPTER = json.loads((ROOT / "catalog/healthkit-adapter.json").read_text(encoding="utf-8"))


class NotificationEventsAreConsistentTests(unittest.TestCase):
    """A screening notification is admitted or refused on its shape, never one at a time."""

    def test_every_notification_event_shares_one_status(self) -> None:
        events = {
            row["sourceTypeIdentifier"]: row["status"]
            for row in ADAPTER["rows"]
            if row["sourceTypeIdentifier"].startswith("HKCategoryTypeIdentifier")
            and row["sourceTypeIdentifier"].endswith("Event")
        }
        refused = sorted(
            identifier
            for identifier, status in events.items()
            if status != "supported"
        )
        self.assertEqual(refused, [], "a screening notification is refused while its peers are not")


class RetainedMetadataIsDisjointTests(unittest.TestCase):
    """The retained set and the modelled set never carry the same key."""

    def test_no_modelled_key_is_also_retained(self) -> None:
        source = (
            ROOT / "stack/Grove/Sources/GroveHealthKitFHIR/HealthKitConverter+RetainedMetadata.swift"
        )
        if not source.exists():
            self.skipTest("the Grove implementation is not checked out beside the guides")
        declared = set(re.findall(r"HKMetadataKey[A-Za-z]+", source.read_text(encoding="utf-8")))
        used = set()
        for path in (ROOT / "stack/Grove/Sources/GroveHealthKitFHIR").glob("*.swift"):
            if path == source:
                continue
            used.update(re.findall(r"HKMetadataKey[A-Za-z]+", path.read_text(encoding="utf-8")))
        # Every key the converter reads elsewhere must be declared modelled, or it would be both
        # read into an element and retained verbatim, letting the two copies disagree.
        self.assertEqual(used - declared, set())
