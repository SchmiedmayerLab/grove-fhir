"""Shared fixtures for producer-validation domain regressions."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import copy
import json
import subprocess
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest import mock

from Scripts import fhir_fixture_corpus as CORPUS
from Scripts.exchange_protocol import (
    derive_hmac_identity,
    entry_node_identity,
    event_identity,
)
from Scripts.producer_validation import context


ROOT = Path(__file__).parents[1]


def typed_identifier(role: str, system: str, value: str) -> dict[str, object]:
    return {
        "type": {"coding": [{
            "system": context.IDENTIFIER_ROLE_SYSTEM,
            "code": role,
        }]},
        "system": system,
        "value": value,
    }


class ProducerValidationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.example = ROOT / "Conformance/example-producer/manifest.json"

    @staticmethod
    def outcome(path: Path, issues: list[dict[str, str]]) -> dict[str, object]:
        return {
            "resourceType": "OperationOutcome",
            "extension": [{
                "url": context.VALIDATOR_FILE_EXTENSION,
                "valueString": str(path),
            }],
            "issue": issues,
        }
