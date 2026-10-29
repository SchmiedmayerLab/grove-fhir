"""Keep every Observation example and fixture to the guides' performer rule."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOTS = ("Conformance", "questionnaire/fixtures")


class ObservationPerformerTests(unittest.TestCase):
    """A performer names who carried out a measurement, so an example may state one only where a source does.

    HealthKit states a performer only when separate source evidence identifies a responsible party, Health Connect's
    capture mode never justifies one, and the semantic vectors admit `Observation.performer` only through the
    `questionnaire.default` rule, where a response's explicit `author` becomes it. An example that states the Patient
    regardless depicts output no conforming adapter produces.
    """

    def test_only_the_questionnaire_rule_admits_a_performer(self) -> None:
        corpus = json.loads(
            (ROOT / "Conformance/corpora/mobile-semantics/corpus.json").read_text(encoding="utf-8")
        )
        admitting = {
            name for name, rule in corpus["sourceContextRules"].items()
            if "Observation.performer" in rule.get("allowedAdditions", [])
        }
        self.assertEqual(admitting, {"questionnaire.default"})

    def test_no_guide_example_states_a_performer(self) -> None:
        stating = []
        for path in sorted(ROOT.glob("*/input/fsh/*.fsh")):
            text = path.read_text(encoding="utf-8")
            for block in re.split(r"(?=^Instance: )", text, flags=re.MULTILINE):
                if not block.startswith("Instance: "):
                    continue
                if re.search(r"^\* performer\b", block, re.MULTILINE):
                    name = block.split("\n", 1)[0].removeprefix("Instance: ")
                    stating.append(f"{path.relative_to(ROOT)}: {name}")
        self.assertEqual(stating, [])

    def test_only_a_response_sourced_fixture_states_a_performer(self) -> None:
        def observations(value: object):
            if isinstance(value, dict):
                if value.get("resourceType") == "Observation":
                    yield value
                for nested in value.values():
                    yield from observations(nested)
            elif isinstance(value, list):
                for nested in value:
                    yield from observations(nested)

        def entry_types(value: object) -> dict[str, str]:
            """The resource type each Bundle entry's fullUrl names, so a urn:uuid reference resolves."""
            types: dict[str, str] = {}
            if isinstance(value, dict):
                for entry in value.get("entry", []) if value.get("resourceType") == "Bundle" else []:
                    types[entry.get("fullUrl", "")] = entry.get("resource", {}).get("resourceType", "")
                for nested in value.values():
                    types |= entry_types(nested)
            elif isinstance(value, list):
                for nested in value:
                    types |= entry_types(nested)
            return types

        stating, sourced = [], 0
        for root in FIXTURE_ROOTS:
            for path in sorted((ROOT / root).rglob("*.json")):
                document = json.loads(path.read_text(encoding="utf-8"))
                types = entry_types(document)
                for observation in observations(document):
                    if "performer" not in observation:
                        continue
                    derived = [
                        types.get(source.get("reference", ""), source.get("reference", "").split("/", 1)[0])
                        for source in observation.get("derivedFrom", [])
                    ]
                    if "QuestionnaireResponse" in derived:
                        sourced += 1
                    else:
                        stating.append(f"{path.relative_to(ROOT)}: {observation.get('id', '?')}")
        self.assertEqual(stating, [])
        # The questionnaire extraction fixtures keep the one admitted performer.
        self.assertGreater(sourced, 0)


if __name__ == "__main__":
    unittest.main()
