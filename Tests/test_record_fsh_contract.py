"""The Mobile FSH carries the record-centric exchange contract the catalog states."""

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


ROOT = Path(__file__).parents[1]
FSH = ROOT / "mobile/input/fsh"
MOBILE = "https://grovealliance.org/fhir/mobile/"
DECLARATION = re.compile(
    r"^(Profile|Extension|Instance|Invariant|RuleSet|CodeSystem|ValueSet|Logical|Alias|Mapping):", re.MULTILINE
)
PAIR = "system.length().toString() & ':' & system & value.length().toString() & ':' & value"


def declarations(text: str) -> dict[str, str]:
    """Every top-level FSH declaration of a file, by its `Kind: Name` header line."""
    starts = [match.start() for match in DECLARATION.finditer(text)]
    blocks = {}
    for start, end in zip(starts, [*starts[1:], len(text)]):
        block = text[start:end]
        blocks[block.split("\n", 1)[0].strip()] = block
    return blocks


def expression(block: str) -> str:
    return block.split('Expression: "', 1)[1].rsplit('"', 1)[0]


def obeyed(block: str) -> set[str]:
    rules = set()
    for line in block.splitlines():
        if line.startswith("* obeys "):
            rules.update(part.strip() for part in line[len("* obeys "):].split(" and "))
    return rules


def codes(block: str) -> set[str]:
    return {line.split()[1][1:] for line in block.splitlines() if line.startswith("* #")}


class RecordFSHContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads((ROOT / "catalog/exchange-protocol.json").read_text(encoding="utf-8"))
        cls.blocks = {}
        for name in ("profiles", "extensions", "terminology", "search-parameters"):
            cls.blocks.update(declarations((FSH / f"{name}.fsh").read_text(encoding="utf-8")))

    def block(self, header: str) -> str:
        self.assertIn(header, self.blocks)
        return self.blocks[header]

    def test_event_and_entry_node_artifacts_are_gone(self) -> None:
        for header in (
            "Invariant: grove-event-identifier-value-1",
            "Invariant: grove-entry-node-value-1",
            "Invariant: grove-active-event-provenance-1",
            "Invariant: grove-retraction-event-provenance-1",
            "Extension: GroveExchangeEntryNodeKey",
        ):
            with self.subTest(removed=header):
                self.assertNotIn(header, self.blocks)
        roles = codes(self.block("CodeSystem: GroveIdentifierRoleCS"))
        self.assertTrue({"context-snapshot", "record-version", "record-retraction", "device-snapshot"} <= roles)
        self.assertFalse({"event", "entry-node"} & roles)
        # Devices are never retracted, so no retraction target plays a Device snapshot.
        self.assertNotIn("device-snapshot", codes(self.block("CodeSystem: GroveRetractionTargetRoleCS")))
        for name in ("profiles", "extensions", "examples"):
            with self.subTest(file=name):
                text = (FSH / f"{name}.fsh").read_text(encoding="utf-8")
                self.assertNotIn("grove-exchange-entry-node-key", text)
                self.assertNotIn("entryNodeKey", text)

    def test_the_entry_key_extension_names_the_three_key_kinds(self) -> None:
        block = self.block("Extension: GroveExchangeEntryKey")
        self.assertIn("Id: grove-exchange-entry-key\n", block)
        self.assertEqual(self.catalog["extensions"]["entryKey"], MOBILE + "StructureDefinition/grove-exchange-entry-key")
        for kind in ("content-snapshot", "record-version", "record-retraction", "grove-context-snapshot"):
            with self.subTest(kind=kind):
                self.assertIn(kind, block)
        for header in ("Profile: GroveMobileExchangeBundle", "Profile: GroveMobileRetractionBundle"):
            with self.subTest(bundle=header):
                self.assertIn("* entry.extension contains GroveExchangeEntryKey named entryKey 1..1 MS", self.block(header))

    def test_the_record_version_extension_is_on_every_conversion_provenance(self) -> None:
        block = self.block("Extension: GroveRecordVersion")
        self.assertIn("Id: grove-record-version\n", block)
        self.assertIn("Context: Provenance\n", block)
        for rule in (
            "* value[x] only Identifier",
            "* valueIdentifier 1..1 MS",
            "* insert GroveOpaqueIdentifier(valueIdentifier, record-version)",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, block)
        self.assertEqual(self.catalog["extensions"]["recordVersion"], MOBILE + "StructureDefinition/grove-record-version")
        conversion = self.block("Profile: GroveMobileConversionProvenance")
        self.assertIn("* extension contains GroveRecordVersion named recordVersion 1..1 MS", conversion)
        retraction = self.block("Profile: GroveMobileRetractionProvenance")
        self.assertIn("grove-retraction-no-record-version-1", obeyed(retraction))
        self.assertNotIn("GroveRecordVersion", retraction)
        self.assertEqual(
            expression(self.block("Invariant: grove-retraction-no-record-version-1")),
            "extension('https://grovealliance.org/fhir/mobile/StructureDefinition/grove-record-version').empty()",
        )

    def test_the_context_snapshot_extension_keys_a_questionnaire_response(self) -> None:
        block = self.block("Extension: GroveContextSnapshot")
        self.assertIn("Id: grove-context-snapshot\n", block)
        self.assertIn("Context: QuestionnaireResponse\n", block)
        for rule in (
            "* value[x] only Identifier",
            "* valueIdentifier 1..1 MS",
            "* insert GroveOpaqueIdentifier(valueIdentifier, context-snapshot)",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, block)
        self.assertEqual(self.catalog["extensions"]["contextSnapshot"], MOBILE + "StructureDefinition/grove-context-snapshot")

    def test_bundle_invariants_tie_each_copy_to_its_entry_key(self) -> None:
        entry_key = "extension('https://grovealliance.org/fhir/mobile/StructureDefinition/grove-exchange-entry-key').value.ofType(Identifier)"
        for name, resource_type, url in (
            ("grove-record-version-entry-key-1", "Provenance", "grove-record-version"),
            ("grove-context-snapshot-entry-key-1", "QuestionnaireResponse", "grove-context-snapshot"),
        ):
            with self.subTest(invariant=name):
                self.assertEqual(
                    expression(self.block(f"Invariant: {name}")),
                    f"entry.where(resource is {resource_type}).all(resource.extension("
                    f"'https://grovealliance.org/fhir/mobile/StructureDefinition/{url}').value.ofType(Identifier)"
                    f".select({PAIR}) = {entry_key}.select({PAIR}))",
                )
        active = obeyed(self.block("Profile: GroveMobileExchangeBundle"))
        retraction = obeyed(self.block("Profile: GroveMobileRetractionBundle"))
        self.assertTrue({
            "grove-active-bundle-provenance-1", "grove-record-version-entry-key-1",
            "grove-context-snapshot-entry-key-1", "grove-exchange-target-distinct-1",
        } <= active)
        self.assertIn("grove-retraction-bundle-provenance-1", retraction)
        # A retraction Bundle carries no conversion Provenance, so it states no record-version copy.
        self.assertFalse({"grove-record-version-entry-key-1", "grove-active-bundle-provenance-1"} & retraction)
        self.assertNotIn("grove-retraction-bundle-provenance-1", active)

    def test_the_two_bundle_profiles_are_never_mixed(self) -> None:
        active = expression(self.block("Invariant: grove-active-bundle-provenance-1"))
        retraction = expression(self.block("Invariant: grove-retraction-bundle-provenance-1"))
        # At least one Provenance, every one of the Bundle's own kind.
        for text, own, other in (
            (active, "iso-21089-lifecycle' and code = 'transform').count() = 1", "grove-lifecycle-event').empty()"),
            (retraction, "code = 'source-record-retracted').count() = 1", "iso-21089-lifecycle').empty()"),
        ):
            with self.subTest(own=own):
                self.assertTrue(text.startswith("entry.resource.ofType(Provenance).exists() and entry.resource.ofType(Provenance).all("))
                self.assertIn(own, text)
                self.assertIn(other, text)
        self.assertIn("entry.resource.all($this is Provenance or $this is Device)", retraction)
        self.assertEqual(
            expression(self.block("Invariant: grove-exchange-target-distinct-1")),
            "entry.resource.ofType(Provenance).target.reference.isDistinct()",
        )

    def test_bundle_identifier_is_an_optional_untyped_transport_id(self) -> None:
        for header in ("Profile: GroveMobileExchangeBundle", "Profile: GroveMobileRetractionBundle"):
            block = self.block(header)
            with self.subTest(bundle=header):
                self.assertIn("* identifier 0..1", block)
                self.assertIn("* identifier.type 0..0", block)
                self.assertNotIn("#event", block)
                self.assertIn("* timestamp 1..1 MS", block)

    def test_the_search_parameter_finds_a_provenance_by_its_record_version(self) -> None:
        block = self.block("Instance: GroveProvenanceRecordVersion")
        url = self.catalog["searchParameters"]["provenanceRecordVersion"]
        self.assertEqual(url, MOBILE + "SearchParameter/grove-provenance-record-version")
        for rule in (
            "InstanceOf: SearchParameter",
            "Usage: #definition",
            '* id = "grove-provenance-record-version"',
            f'* url = "{url}"',
            '* name = "GroveProvenanceRecordVersion"',
            "* status = #active",
            "* code = #grove-record-version",
            "* base = #Provenance",
            "* type = #token",
            "* expression = \"Provenance.extension('https://grovealliance.org/fhir/mobile/StructureDefinition/"
            "grove-record-version').value.ofType(Identifier)\"",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, block)


if __name__ == "__main__":
    unittest.main()
