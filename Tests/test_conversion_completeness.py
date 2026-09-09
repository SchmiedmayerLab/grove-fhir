#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#

"""Guide-owned conversion-admission checks; real converter behavior belongs to producer tests."""

import json
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
