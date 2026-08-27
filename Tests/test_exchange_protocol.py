"""Conformance tests for the Grove 0.6 exchange protocol."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import unittest
from pathlib import Path

from Scripts import exchange_protocol as PROTOCOL


ROOT = Path(__file__).parents[1]


class ExchangeProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(
            (ROOT / "catalog/exchange-protocol.json").read_text(encoding="utf-8")
        )
        cls.vectors = cls.catalog["testVectors"]
        cls.key = bytes.fromhex(cls.vectors["keyHex"])

    def test_every_hmac_vector_is_exact(self) -> None:
        for vector in self.vectors["identities"]:
            with self.subTest(vector=vector["id"]):
                actual = PROTOCOL.derive_hmac_identity(
                    key=self.key,
                    key_id=self.vectors["keyId"],
                    epoch=self.vectors["epoch"],
                    identity_kind=vector["identityKind"],
                    components=vector["components"],
                )
                self.assertEqual(actual, vector["value"])
                self.assertEqual(
                    PROTOCOL.parse_hmac_identity(actual),
                    (self.vectors["keyId"], self.vectors["epoch"], actual.rsplit(":", 1)[1]),
                )

    def test_length_frames_are_unambiguous_and_preserve_unicode(self) -> None:
        self.assertNotEqual(
            PROTOCOL.frame_fields(["ab", "c"]),
            PROTOCOL.frame_fields(["a", "bc"]),
        )
        self.assertNotEqual(
            PROTOCOL.derive_hmac_identity(
                key=self.key,
                key_id="test-key",
                epoch=1,
                identity_kind="source-record",
                components=["adapter", "ab", "c", "", "record|東京"],
            ),
            PROTOCOL.derive_hmac_identity(
                key=self.key,
                key_id="test-key",
                epoch=1,
                identity_kind="source-record",
                components=["adapter", "a", "bc", "", "record|東京"],
            ),
        )

    def test_key_kind_and_epoch_fail_closed(self) -> None:
        with self.assertRaisesRegex(PROTOCOL.ExchangeProtocolError, "at least 32"):
            PROTOCOL.derive_hmac_identity(
                key=b"short",
                key_id="key",
                epoch=1,
                identity_kind="source-record",
                components=["record"],
            )
        for key_id, epoch, kind in (
            ("bad:key", 1, "source-record"),
            ("key", 0, "source-record"),
            ("key", "01", "source-record"),
            ("key", 1, "Source Record"),
        ):
            with self.subTest(key_id=key_id, epoch=epoch, kind=kind), self.assertRaises(
                PROTOCOL.ExchangeProtocolError
            ):
                PROTOCOL.derive_hmac_identity(
                    key=self.key,
                    key_id=key_id,
                    epoch=epoch,
                    identity_kind=kind,
                    components=["record"],
                )

    def test_identity_kind_and_component_arity_are_closed(self) -> None:
        catalog_kinds = {
            item["kind"]: len(item["components"])
            for item in self.catalog["opaqueIdentity"]["identityKinds"]
        }
        self.assertEqual(PROTOCOL.IDENTITY_KIND_COMPONENTS, catalog_kinds)
        for kind, count in (*catalog_kinds.items(), ("future-kind", 1)):
            components = [f"component-{index}" for index in range(count)]
            if kind != "future-kind":
                components.pop()
            with self.subTest(kind=kind), self.assertRaises(
                PROTOCOL.ExchangeProtocolError
            ):
                PROTOCOL.derive_hmac_identity(
                    key=self.key,
                    key_id="test-key",
                    epoch=1,
                    identity_kind=kind,
                    components=components,
                )

    def test_adapter_only_active_output_types_resolve_to_exact_claims(self) -> None:
        policy = self.catalog["lifecycle"]["active"][
            "adapterOnlyOutputProfileClaims"
        ]
        claims = json.loads(
            (ROOT / policy["authority"]).read_text(encoding="utf-8")
        )
        declared = set(policy["resourceTypes"])
        resolved = {claims["healthConnectSpecimenClaim"]["resourceType"]}
        resolved.update(
            claim["resourceType"]
            for claim in claims["healthKitPlatformExclusiveResourceClaims"]
        )
        self.assertEqual(
            declared,
            {
                "Specimen",
                "VisionPrescription",
                "MedicationAdministration",
                "MedicationStatement",
            },
        )
        self.assertEqual(resolved, declared)

    def test_event_entry_node_and_full_url_vectors_are_exact(self) -> None:
        event = self.vectors["event"]
        self.assertEqual(
            PROTOCOL.event_identity(event["producerInstance"], event["sequence"]),
            event["value"],
        )
        node = self.vectors["entryNode"]
        self.assertEqual(
            PROTOCOL.entry_node_identity(
                event_system=event["system"],
                event_value=event["value"],
                role=node["role"],
                ordinal=node["ordinal"],
            ),
            node["value"],
        )
        self.assertEqual(
            PROTOCOL.entry_full_url(node["system"], node["value"]),
            node["fullUrl"],
        )
        for vector in self.vectors["fullUrls"]:
            with self.subTest(vector=vector["id"]):
                self.assertEqual(
                    PROTOCOL.entry_full_url(vector["system"], vector["value"]),
                    vector["fullUrl"],
                )

    def test_entry_node_is_event_role_and_ordinal_scoped(self) -> None:
        event = self.vectors["event"]
        values = {
            PROTOCOL.entry_node_identity(
                event_system=event["system"],
                event_value=event["value"],
                role=role,
                ordinal=ordinal,
            )
            for role, ordinal in (
                ("conversion-provenance", 0),
                ("conversion-provenance", 1),
                ("application-device", 0),
            )
        }
        self.assertEqual(len(values), 3)

    def test_retraction_roles_and_internal_reference_targets_are_closed(self) -> None:
        self.assertEqual(
            self.catalog["lifecycle"]["retraction"]["targetRoles"],
            {
                "primary-output": {
                    "identifierRole": "source-output",
                    "resourceTypes": [
                        "Observation",
                        "VisionPrescription",
                        "MedicationAdministration",
                        "MedicationStatement",
                    ],
                },
                "source-artifact": {
                    "identifierRole": "source-output",
                    "resourceTypes": ["DocumentReference"],
                },
                "child-output": {
                    "identifierRole": "source-output",
                    "resourceTypes": ["Observation"],
                },
                "specimen": {
                    "identifierRole": "source-output",
                    "resourceTypes": ["Specimen"],
                },
                "device-snapshot": {
                    "identifierRole": "device-snapshot",
                    "resourceTypes": ["Device"],
                },
            },
        )
        paths = self.catalog["referencePolicy"]["paths"]
        self.assertEqual(
            len(paths),
            len({(item["resourceType"], item["path"]) for item in paths}),
        )
        extensions = self.catalog["referencePolicy"]["extensionTargets"]
        self.assertEqual(len(extensions), len({item["url"] for item in extensions}))

    def test_identifier_systems_are_absolute_ascii_uris(self) -> None:
        for invalid in (
            "relative/path",
            "https://例.example/識別子",
            "https://example.org/a b",
            "https://example.org/%ZZ",
        ):
            with self.subTest(system=invalid), self.assertRaisesRegex(
                PROTOCOL.ExchangeProtocolError, "absolute RFC 3986 URI"
            ):
                PROTOCOL.entry_full_url(invalid, "value")

    def test_identity_kinds_are_closed_and_role_typed(self) -> None:
        kinds = self.catalog["opaqueIdentity"]["identityKinds"]
        self.assertEqual(len({item["kind"] for item in kinds}), len(kinds))
        role_codes = {
            "source-record",
            "source-output",
            "writer-record",
            "source-artifact",
            "source-context",
            "recording-device",
            "device-snapshot",
        }
        self.assertTrue({item["identifierRole"] for item in kinds} <= role_codes)
        provider = next(item for item in kinds if item["kind"] == "provider-record")
        self.assertIn("provider-scope-system", provider["components"])
        self.assertIn("provider-scope-value", provider["components"])

    def test_test_key_is_explicitly_forbidden_in_production(self) -> None:
        self.assertIn("Public conformance key", self.vectors["warning"])
        self.assertTrue(
            self.catalog["opaqueIdentity"]["keyRequirements"]["testKeysProhibited"]
        )


if __name__ == "__main__":
    unittest.main()
