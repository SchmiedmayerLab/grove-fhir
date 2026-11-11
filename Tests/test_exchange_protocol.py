"""Conformance tests for the Grove exchange protocol."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from Scripts import canonical_json as CANONICAL
from Scripts import exchange_protocol as PROTOCOL


ROOT = Path(__file__).parents[1]

# The record-content vector's conversion Provenance without `id` and grove-record-version (P') and
# its one output (O), in canonical form, as the record-centric spec states them.
RECORD_CONTENT_PROVENANCE = (
    b'{"activity":{"coding":[{"code":"transform","system":"http://terminology.hl7.org/CodeSystem/iso-21089-lifecycle"}]},'
    b'"agent":[{"type":{"coding":[{"code":"assembler","system":"http://terminology.hl7.org/CodeSystem/provenance-participant-type"}]},'
    b'"who":{"reference":"urn:uuid:aef62dba-db7e-5a99-a854-3b5ec312312f"}}],"entity":[{"role":"source",'
    b'"what":{"identifier":{"system":"https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1",'
    b'"type":{"coding":[{"code":"source-record","system":"https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role"}]},'
    b'"value":"v0:test-key:1:ptHr751zWyYfaR2WIvrP1TfnVEK4bInC__ibP_AYfVY"}}}],'
    b'"meta":{"profile":["https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-conversion-provenance"]},'
    b'"occurredDateTime":"2026-08-20T10:30:02-07:00","recorded":"2026-08-20T17:30:02Z",'
    b'"resourceType":"Provenance","target":[{"reference":"urn:uuid:a9b76bbc-f523-5ef4-9919-813ec70553e5"}]}'
)
RECORD_CONTENT_OUTPUT = (
    b'{"code":{"coding":[{"code":"8867-4","system":"http://loinc.org"}]},"effectiveDateTime":"2026-08-20T08:30:00.251-07:00",'
    b'"identifier":[{"system":"https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1",'
    b'"type":{"coding":[{"code":"source-record","system":"https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role"}]},'
    b'"value":"v0:test-key:1:ptHr751zWyYfaR2WIvrP1TfnVEK4bInC__ibP_AYfVY"},'
    b'{"system":"https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1",'
    b'"type":{"coding":[{"code":"source-output","system":"https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role"}]},'
    b'"value":"v0:test-key:1:PPULnf0LKpASjIj8mU5TKafPKig_oqWND3_dHFShGd8"}],'
    b'"meta":{"profile":["https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-heart-rate"]},'
    b'"resourceType":"Observation","status":"final","subject":{"identifier":{"system":"https://study.example.org/fhir/identifiers/participant",'
    b'"value":"participant-001"},"type":"Patient"},"valueQuantity":{"code":"/min","system":"http://unitsofmeasure.org",'
    b'"unit":"beats/minute","value":72}}'
)
SOURCE_RECORD_SYSTEM = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
SOURCE_RECORD_VALUE = "v0:test-key:1:ptHr751zWyYfaR2WIvrP1TfnVEK4bInC__ibP_AYfVY"
RECORD_VERSION_SYSTEM = "https://study.example.org/fhir/NamingSystem/grove-record-version-v0/test-key/1"
RECORD_RETRACTION_SYSTEM = (
    "https://study.example.org/fhir/NamingSystem/grove-record-retraction-v0/test-key/1"
)
SUBJECT_SYSTEM = "https://study.example.org/fhir/identifiers/participant"
# The spec's D3/D4 vectors: record-content digests, record-version and record-retraction values
# with their fullUrls.
RECORD_CONTENT_DIGESTS = {
    "heart-rate-72": "zQn6qLSfmufltslE_5oFb25RNjY1-XN5s547r43EumY",
    "heart-rate-72-0": "1VvPJMtUBZEzD8DX5WFNjMr8pMVyKERNzlUyAKQLpuk",
}
RECORD_VERSIONS = {
    "heart-rate-72": (
        "v0:test-key:1:xjbzwZqYyBE1boHxzOoS09iLXEMrvo0o8dpxtlwPQhE",
        "urn:uuid:af53df9f-24e4-5773-9301-a3887fdf2f57",
    ),
    "heart-rate-72-0": (
        "v0:test-key:1:z2SXdSGr63iLne5oavwMibQClshhTEABve_JEZLljCo",
        "urn:uuid:b0624977-9c3f-574d-82ae-112f578bae1a",
    ),
}
RECORD_RETRACTION = (
    "v0:test-key:1:0JJ96w-JxTpK7Bb-910L_61f3KJdI8Cr4eSGTpJ7L7o",
    "urn:uuid:03e766bb-9cc6-51b2-b67e-e8902e01513f",
)
DIGEST = "A" * 43


def valid_components(kind: str, names: tuple[str, ...]) -> list[str]:
    """Return components that pass every per-component check of `kind`."""
    components = [f"component-{index}" for index in range(len(names))]
    if kind.startswith("provider-"):
        components[0] = "withings"
    for index, name in enumerate(names):
        if name in PROTOCOL.UNSIGNED_DECIMAL_COMPONENTS:
            components[index] = "0"
        elif name in PROTOCOL.DIGEST_COMPONENTS:
            components[index] = DIGEST
        elif name == "node-role":
            components[index] = sorted(PROTOCOL.SNAPSHOT_NODE_ROLES[kind])[0]
    return components


def record_content_provenance(extension_value: str = SOURCE_RECORD_VALUE) -> dict:
    """Return P' with an `id` and a grove-record-version extension, which the digest removes."""
    provenance = CANONICAL.loads_lossless(RECORD_CONTENT_PROVENANCE)
    return {
        "id": "not-in-the-digest",
        "extension": [{
            "url": PROTOCOL.RECORD_VERSION_EXTENSION,
            "valueIdentifier": {"system": RECORD_VERSION_SYSTEM, "value": extension_value},
        }],
        **provenance,
    }


def record_content_output(value: bytes = b"72") -> dict:
    return CANONICAL.loads_lossless(
        RECORD_CONTENT_OUTPUT.replace(b'"value":72}}', b'"value":' + value + b"}}")
    )


class ExchangeProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(
            (ROOT / "catalog/exchange-protocol.json").read_text(encoding="utf-8")
        )
        cls.vectors = cls.catalog["testVectors"]
        cls.key = bytes.fromhex(cls.vectors["keyHex"])

    def test_every_hmac_vector_is_exact(self) -> None:
        self.assertEqual(
            {vector["identityKind"] for vector in self.vectors["identities"]},
            {
                item["kind"]
                for item in self.catalog["opaqueIdentity"]["identityKinds"]
            },
        )
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

    def test_every_identity_kind_has_one_distinct_example_system(self) -> None:
        kinds = {
            item["kind"] for item in self.catalog["opaqueIdentity"]["identityKinds"]
        }
        rows = self.vectors["identitySystems"]
        self.assertEqual({row["identityKind"] for row in rows}, kinds)
        self.assertEqual(len(rows), len(kinds))
        self.assertEqual(len({row["system"] for row in rows}), len(kinds))

    def test_vectors_use_the_recommended_identifier_system_forms(self) -> None:
        root = "https://study.example.org/fhir"
        opaque = self.catalog["opaqueIdentity"]["recommendedSystemForm"]
        for row in self.vectors["identitySystems"]:
            with self.subTest(kind=row["identityKind"]):
                expected = (
                    opaque.replace("<deployment-root>", root)
                    .replace("<identity-kind>", row["identityKind"])
                    .replace("<key-id>", self.vectors["keyId"])
                    .replace("<epoch>", str(self.vectors["epoch"]))
                )
                self.assertEqual(row["system"], expected)
        systems = {row["identityKind"]: row["system"] for row in self.vectors["identitySystems"]}
        self.assertEqual(systems["record-version"], RECORD_VERSION_SYSTEM)
        self.assertEqual(systems["record-retraction"], RECORD_RETRACTION_SYSTEM)
        # No event or entry-node identifier exists any more, so neither has a system form.
        self.assertNotIn("event", self.catalog)
        self.assertNotIn("entryNode", self.catalog["entryIdentity"])

    def test_study_context_names_the_corpus_context_snapshot_roles(self) -> None:
        self.assertNotIn("entryNodeRoles", self.catalog["lifecycle"]["active"]["studyContext"])
        roles = self.catalog["entryIdentity"]["contextSnapshotRoles"]
        self.assertEqual(
            roles, ["patient", "research-study", "research-subject", "plan-definition", "questionnaire-response"]
        )
        # The node role is inside the HMAC, so the corpus shows it only through the keyed resource type.
        role_of = dict(zip(
            ("Patient", "ResearchStudy", "ResearchSubject", "PlanDefinition", "QuestionnaireResponse"), roles
        ))
        entry_key = self.catalog["extensions"]["entryKey"]
        corpus = ROOT / "Conformance/corpora/study-attribution"
        used = set()
        for path in sorted(corpus.glob("*.json")):
            bundle = json.loads(path.read_text(encoding="utf-8"))
            # Receiver exports are not exchange Bundles and carry no entry keys.
            if not any(profile.endswith("/grove-mobile-exchange-bundle") for profile in bundle.get("meta", {}).get("profile", [])):
                continue
            for entry in bundle["entry"]:
                resource_type = entry["resource"]["resourceType"]
                if resource_type not in role_of:
                    continue
                keys = [item for item in entry.get("extension", []) if item["url"] == entry_key]
                with self.subTest(file=path.name, fullUrl=entry["fullUrl"]):
                    self.assertEqual(len(keys), 1)
                    key = keys[0]["valueIdentifier"]
                    self.assertEqual(key["type"]["coding"][0]["code"], "context-snapshot")
                    self.assertRegex(key["value"], r"^v0:test-key:1:[A-Za-z0-9_-]{43}$")
                    used.add(role_of[resource_type])
        self.assertTrue(set(roles) - {"questionnaire-response"} <= used)
        admitted = {
            target["url"] for target in self.catalog["referencePolicy"]["extensionTargets"]
        }
        self.assertIn("http://hl7.org/fhir/StructureDefinition/workflow-researchStudy", admitted)
        self.assertNotIn(
            "http://hl7.org/fhir/StructureDefinition/workflow-instantiatesCanonical", admitted
        )

    def test_refusals_and_omissions_are_registered_client_rules(self) -> None:
        rows = self.catalog["producerDiagnostics"]
        codes = [row["code"] for row in rows]
        self.assertEqual(len(codes), len(set(codes)))
        self.assertEqual(
            {code.split(".")[0] for code in codes},
            {
                "mobile-exchange", "mobile-output", "mobile-retraction", "mobile-support",
                "mobile-device", "mobile-input", "mobile-omission", "healthkit-clinical", "healthkit-ecg",
                "healthkit-input", "healthkit-device", "health-connect-provenance", "sensor-recording-document",
            },
        )
        for row in rows:
            with self.subTest(code=row["code"]):
                namespace = row["code"].split(".")[0]
                if namespace.endswith(("-input", "-omission")):
                    self.assertEqual(row["emittedBy"], "client")
                if namespace.endswith("-omission"):
                    self.assertEqual(row.get("severity"), "warning")
                else:
                    self.assertNotEqual(row.get("severity"), "warning")
        self.assertIn("mobile-input.unclassified", codes)
        self.assertEqual(sum(row.get("severity") == "warning" for row in rows), 4)

    def test_record_centric_diagnostics_replace_the_event_diagnostics(self) -> None:
        codes = {row["code"]: row for row in self.catalog["producerDiagnostics"]}
        for deleted in (
            "mobile-exchange.event-identity",
            "mobile-exchange.entry-node-digest",
            "mobile-exchange.entry-node-ordinal",
            "mobile-exchange.entry-node-key",
            "mobile-exchange.event-times",
        ):
            with self.subTest(deleted=deleted):
                self.assertNotIn(deleted, codes)
        for added in (
            "mobile-exchange.entry-key",
            "mobile-exchange.content-snapshot-key",
            "mobile-exchange.record-version-key",
            "mobile-exchange.record-version-extension",
            "mobile-exchange.context-snapshot-extension",
            "mobile-exchange.canonical-json",
            "mobile-exchange.record-times",
            "mobile-exchange.output-targeted-once",
            "mobile-exchange.distinct-source-record",
            "mobile-exchange.cross-record-reference",
            "mobile-exchange.single-subject",
            "mobile-exchange.bundle-identifier",
            "mobile-retraction.retraction-key",
        ):
            with self.subTest(added=added):
                self.assertIn(added, codes)
        for code in (
            "mobile-exchange.record-version-key",
            "mobile-exchange.record-version-extension",
            "mobile-exchange.context-snapshot-extension",
            "mobile-exchange.canonical-json",
            "mobile-retraction.retraction-key",
        ):
            with self.subTest(code=code):
                self.assertEqual(codes[code]["emittedBy"], "conformance-kit")
        # The two Bundle profiles are never mixed: an active Bundle carries no retraction
        # Provenance, and a retraction Bundle no transform Provenance.
        transform = codes["mobile-exchange.transform-provenance"]["reason"]
        self.assertIn("exactly one for each record", transform)
        self.assertIn("no retraction Provenance", transform)
        retraction = codes["mobile-retraction.provenance"]["reason"]
        self.assertIn("no transform Provenance", retraction)
        self.assertIn("distinct record-retraction key", retraction)
        self.assertIn("a retraction Provenance carries none", codes["mobile-exchange.record-version-extension"]["reason"])
        for row in codes.values():
            with self.subTest(code=row["code"]):
                self.assertNotRegex(row["reason"], r"\bevents?\b")

    def test_invalid_hmac_vectors_fail_closed(self) -> None:
        expected_messages = {
            "empty-component": "must not be empty",
            "provider-kind-required": "provider components require identity kind",
            "non-canonical-part-index": "must be a canonical unsigned decimal",
            "non-canonical-digest": "must be a 43-character base64url SHA-256 digest",
        }
        for vector in self.vectors["invalidIdentities"]:
            with self.subTest(vector=vector["id"]), self.assertRaisesRegex(
                PROTOCOL.ExchangeProtocolError,
                expected_messages[vector["expectedError"]],
            ):
                PROTOCOL.derive_hmac_identity(
                    key=self.key,
                    key_id=self.vectors["keyId"],
                    epoch=self.vectors["epoch"],
                    identity_kind=vector["identityKind"],
                    components=vector["components"],
                )

    def test_unsigned_decimal_components_are_declared_once(self) -> None:
        requirements = self.catalog["opaqueIdentity"]["componentRequirements"]
        self.assertEqual(set(requirements["unsignedDecimal"]), PROTOCOL.UNSIGNED_DECIMAL_COMPONENTS)
        names = {name for kind in self.catalog["opaqueIdentity"]["identityKinds"] for name in kind["components"]}
        self.assertLessEqual(PROTOCOL.UNSIGNED_DECIMAL_COMPONENTS, names)
        rejected = {vector["components"][-1] for vector in self.vectors["invalidIdentities"] if vector["expectedError"] == "non-canonical-part-index"}
        self.assertEqual(rejected, {"-1", "01"})

    def test_digest_components_are_declared_once(self) -> None:
        requirements = self.catalog["opaqueIdentity"]["componentRequirements"]
        self.assertEqual(set(requirements["digestComponents"]), PROTOCOL.DIGEST_COMPONENTS)
        names = {name for kind in self.catalog["opaqueIdentity"]["identityKinds"] for name in kind["components"]}
        self.assertLessEqual(PROTOCOL.DIGEST_COMPONENTS, names)
        for digest in ("A" * 42, "A" * 44, "A" * 42 + "=", "A" * 42 + "+", "A" * 42 + "/", " " + "A" * 42):
            for kind, index in (("record-version", 2), ("device-snapshot", 3), ("context-snapshot", 3)):
                components = valid_components(kind, PROTOCOL.IDENTITY_KIND_COMPONENT_NAMES[kind])
                components[index] = digest
                with self.subTest(kind=kind, digest=digest), self.assertRaisesRegex(
                    PROTOCOL.ExchangeProtocolError, "must be a 43-character base64url SHA-256 digest"
                ):
                    PROTOCOL.derive_hmac_identity(
                        key=self.key, key_id="test-key", epoch=1, identity_kind=kind, components=components
                    )

    def test_snapshot_node_roles_are_closed(self) -> None:
        self.assertEqual(
            PROTOCOL.CONTEXT_SNAPSHOT_NODE_ROLES,
            tuple(self.catalog["entryIdentity"]["contextSnapshotRoles"]),
        )
        self.assertEqual(PROTOCOL.DEVICE_SNAPSHOT_NODE_ROLES, ("application", "host", "recording-device"))
        for kind, roles in PROTOCOL.SNAPSHOT_NODE_ROLES.items():
            other = PROTOCOL.SNAPSHOT_NODE_ROLES[
                "context-snapshot" if kind == "device-snapshot" else "device-snapshot"
            ]
            for role in (*sorted(roles), *sorted(other), "application-device", "Patient"):
                components = [SUBJECT_SYSTEM, "participant-001", role, DIGEST]
                with self.subTest(kind=kind, role=role):
                    if role in roles:
                        PROTOCOL.derive_hmac_identity(
                            key=self.key, key_id="test-key", epoch=1, identity_kind=kind, components=components
                        )
                    else:
                        with self.assertRaisesRegex(PROTOCOL.ExchangeProtocolError, rf"{kind}[.]node-role must be one of"):
                            PROTOCOL.derive_hmac_identity(
                                key=self.key, key_id="test-key", epoch=1, identity_kind=kind, components=components
                            )

    def test_length_frames_are_unambiguous_and_preserve_unicode(self) -> None:
        self.assertNotEqual(
            PROTOCOL.frame_fields(["ab", "c"]),
            PROTOCOL.frame_fields(["a", "bc"]),
        )
        self.assertEqual(PROTOCOL.frame_fields([""]), b"\x00\x00\x00\x00")
        self.assertNotEqual(
            PROTOCOL.derive_hmac_identity(
                key=self.key,
                key_id="test-key",
                epoch=1,
                identity_kind="source-record",
                components=["adapter", "ab", "c", "scope", "record|東京"],
            ),
            PROTOCOL.derive_hmac_identity(
                key=self.key,
                key_id="test-key",
                epoch=1,
                identity_kind="source-record",
                components=["adapter", "a", "bc", "scope", "record|東京"],
            ),
        )

    def test_typed_identity_components_are_nonempty_unicode_scalar_strings(self) -> None:
        requirements = self.catalog["opaqueIdentity"]["componentRequirements"]
        self.assertEqual(
            set(requirements),
            {
                "valueType", "nonEmpty", "arity", "unsignedDecimal", "unsignedDecimalForm",
                "digestComponents", "digestForm",
            },
        )
        self.assertEqual(requirements["valueType"], "unicode-scalar-string")
        self.assertIs(requirements["nonEmpty"], True)
        self.assertEqual(requirements["arity"], "exactly-kind-components")
        self.assertEqual(requirements["unsignedDecimal"], ["part-index"])
        self.assertEqual(
            requirements["unsignedDecimalForm"],
            "A canonical unsigned decimal: 0, or a nonzero digit followed by digits, with no sign, whitespace, or leading zero.",
        )
        self.assertEqual(
            sorted(requirements["digestComponents"]), ["content-digest", "record-content-digest"]
        )
        catalog_names = {
            item["kind"]: tuple(item["components"])
            for item in self.catalog["opaqueIdentity"]["identityKinds"]
        }
        self.assertEqual(PROTOCOL.IDENTITY_KIND_COMPONENT_NAMES, catalog_names)
        for kind, names in catalog_names.items():
            valid = valid_components(kind, names)
            PROTOCOL.derive_hmac_identity(
                key=self.key, key_id="test-key", epoch=1, identity_kind=kind, components=valid
            )
            for index, name in enumerate(names):
                components = valid.copy()
                components[index] = ""
                with self.subTest(kind=kind, component=name), self.assertRaisesRegex(
                    PROTOCOL.ExchangeProtocolError,
                    rf"{kind}[.]{name} must not be empty",
                ):
                    PROTOCOL.derive_hmac_identity(
                        key=self.key,
                        key_id="test-key",
                        epoch=1,
                        identity_kind=kind,
                        components=components,
                    )
        invalid_scalar = ["adapter", "source", "https://scope.example", "scope", "\ud800"]
        with self.assertRaisesRegex(
            PROTOCOL.ExchangeProtocolError,
            "source-record[.]native-record-id must contain Unicode scalar values",
        ):
            PROTOCOL.derive_hmac_identity(
                key=self.key,
                key_id="test-key",
                epoch=1,
                identity_kind="source-record",
                components=invalid_scalar,
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

    def test_full_url_vectors_are_exact(self) -> None:
        self.assertNotIn("event", self.vectors)
        self.assertNotIn("entryNode", self.vectors)
        for vector in self.vectors["fullUrls"]:
            with self.subTest(vector=vector["id"]):
                self.assertEqual(
                    PROTOCOL.entry_full_url(vector["system"], vector["value"]),
                    vector["fullUrl"],
                )
        catalog = {
            (vector["system"], vector["value"]): vector["fullUrl"] for vector in self.vectors["fullUrls"]
        }
        for system, (value, full_url) in (
            *((RECORD_VERSION_SYSTEM, version) for version in RECORD_VERSIONS.values()),
            (RECORD_RETRACTION_SYSTEM, RECORD_RETRACTION),
        ):
            with self.subTest(value=value):
                self.assertEqual(PROTOCOL.entry_full_url(system, value), full_url)
                self.assertEqual(catalog[(system, value)], full_url)

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
                # Devices are never retracted, so no target role names a Device snapshot.
                # The source record as a whole is no one resource, so its target is untyped.
                "source-record": {
                    "identifierRole": "source-record",
                    "resourceTypes": [],
                },
            },
        )
        paths = self.catalog["referencePolicy"]["paths"]
        self.assertEqual(
            len(paths),
            len({(item["resourceType"], item["path"]) for item in paths}),
        )
        path_targets = {
            (item["resourceType"], item["path"]): item["targetTypes"]
            for item in paths
        }
        self.assertEqual(
            path_targets[("QuestionnaireResponse", "subject")],
            ["Patient"],
        )
        self.assertTrue(all(isinstance(item["repeating"], bool) for item in paths))
        self.assertEqual(
            {
                (item["resourceType"], item["path"])
                for item in paths
                if item["repeating"]
            },
            {
                ("Observation", "focus"),
                ("Observation", "hasMember"),
                ("Observation", "derivedFrom"),
                ("ResearchStudy", "protocol"),
            },
        )
        patient = self.catalog["referencePolicy"]["identifierOnlyPatient"]
        self.assertEqual(
            set(patient["reservedSystems"]),
            set(self.catalog["codeSystems"].values()),
        )
        self.assertIn("exact", patient["valueRule"])
        self.assertIn("producer/deployment obligations", patient["systemRule"])
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
            "context-snapshot",
            "record-version",
            "record-retraction",
        }
        self.assertEqual({item["identifierRole"] for item in kinds}, role_codes)
        self.assertEqual(
            {item["kind"]: item["identifierRole"] for item in kinds if item["kind"] in role_codes},
            {code: code for code in role_codes},
        )
        for code in ("event", "entry-node"):
            with self.subTest(removed=code):
                self.assertNotIn(code, {item["identifierRole"] for item in kinds})
        provider = next(item for item in kinds if item["kind"] == "provider-record")
        self.assertIn("provider-scope-system", provider["components"])
        self.assertIn("provider-scope-value", provider["components"])
        by_kind = {item["kind"]: item for item in kinds}
        for generic_kind, provider_kind in (
            ("source-record", "provider-record"),
            ("source-output", "provider-output"),
            ("source-artifact", "provider-artifact"),
        ):
            with self.subTest(provider_kind=provider_kind):
                self.assertEqual(
                    by_kind[provider_kind]["identifierRole"],
                    by_kind[generic_kind]["identifierRole"],
                )
                self.assertNotEqual(
                    by_kind[provider_kind]["components"],
                    by_kind[generic_kind]["components"],
                )

    def test_every_adapter_identity_declaration_matches_protocol_exactly(self) -> None:
        protocol_kinds = {
            item["kind"]: item
            for item in self.catalog["opaqueIdentity"]["identityKinds"]
        }
        for filename in (
            "healthkit-adapter.json",
            "health-connect-adapter.json",
            "sensorkit-adapter.json",
            "providers-adapter.json",
        ):
            catalog = json.loads((ROOT / "catalog" / filename).read_text(encoding="utf-8"))
            for declaration_name, declaration in catalog["identity"].items():
                if not isinstance(declaration, dict) or "identityKind" not in declaration:
                    continue
                kind = declaration["identityKind"]
                with self.subTest(catalog=filename, declaration=declaration_name):
                    self.assertIn(kind, protocol_kinds)
                    self.assertEqual(
                        declaration["identifierRole"],
                        protocol_kinds[kind]["identifierRole"],
                    )
                    self.assertEqual(
                        declaration["components"],
                        protocol_kinds[kind]["components"],
                    )

    def test_release_is_0_8_0_and_the_protocol_version_stays_0(self) -> None:
        self.assertEqual(self.catalog["version"], "0.8.0")
        self.assertEqual(self.catalog["releaseVersion"], "0.8.0")
        self.assertEqual(self.catalog["protocolVersion"], 0)
        manifest = json.loads((ROOT / "catalog/release-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(self.catalog["releaseVersion"], manifest["releaseVersion"])

    def test_the_bundle_is_a_container_of_records_with_no_event(self) -> None:
        self.assertNotIn("event", self.catalog)
        bundle = self.catalog["bundle"]
        self.assertEqual(set(bundle), {"semanticUnit", "recordUnit", "identifier", "times", "retry", "transport"})
        self.assertIn("one or more records of one kind, active or retraction", bundle["semanticUnit"])
        self.assertIn("of one subject", bundle["semanticUnit"])
        self.assertIn("changes no record", bundle["semanticUnit"])
        self.assertEqual(
            bundle["identifier"],
            {"cardinality": "0..1", "groveRoleAllowed": False, "rule": bundle["identifier"]["rule"]},
        )
        self.assertIn("enters no identity", bundle["identifier"]["rule"])
        self.assertEqual(set(bundle["times"]), {"occurred", "recorded", "packed"})
        self.assertIn("enters no identity", bundle["times"]["packed"])
        self.assertIn("versionSelection", bundle["times"]["recorded"])
        self.assertIn("record version", bundle["retry"])
        # Directed reachability, so a shared hub cannot connect an orphaned supporting node.
        for member in ("Provenance.agent.who", "Provenance.entity.agent.who", "Device.parent", "directed reachability"):
            with self.subTest(member=member):
                self.assertIn(member, bundle["recordUnit"])

    def test_extensions_and_search_parameter_name_the_record_keys(self) -> None:
        mobile = "https://grovealliance.org/fhir/mobile/"
        extensions = self.catalog["extensions"]
        self.assertNotIn("entryNodeKey", extensions)
        self.assertEqual(extensions["entryKey"], mobile + "StructureDefinition/grove-exchange-entry-key")
        self.assertEqual(extensions["recordVersion"], mobile + "StructureDefinition/grove-record-version")
        self.assertEqual(extensions["contextSnapshot"], mobile + "StructureDefinition/grove-context-snapshot")
        self.assertEqual(PROTOCOL.RECORD_VERSION_EXTENSION, extensions["recordVersion"])
        self.assertEqual(PROTOCOL.CONTEXT_SNAPSHOT_EXTENSION, extensions["contextSnapshot"])
        self.assertEqual(
            self.catalog["searchParameters"],
            {"provenanceRecordVersion": mobile + "SearchParameter/grove-provenance-record-version"},
        )

    def test_entry_identity_selects_record_and_content_keys(self) -> None:
        identity = self.catalog["entryIdentity"]
        self.assertNotIn("entryNode", identity)
        self.assertEqual(
            identity["resourceIdentifierPriority"],
            [
                "source-output", "source-artifact", "source-record", "writer-record",
                "device-snapshot", "context-snapshot", "recording-device",
            ],
        )
        self.assertEqual(identity["provenanceKey"], {"active": "record-version", "retraction": "record-retraction"})
        self.assertEqual(self.catalog["lifecycle"]["retraction"]["entryKey"], "record-retraction")
        self.assertIn("never selects an entry key", identity["selection"])
        self.assertIn("grove-record-version", identity["selection"])
        self.assertIn("grove-context-snapshot", identity["selection"])
        self.assertIn("Only a retraction Provenance carries its key on the entry alone", identity["selection"])
        kinds = {item["kind"]: item for item in self.catalog["opaqueIdentity"]["identityKinds"]}
        for kind in (*identity["provenanceKey"].values(), "device-snapshot", "context-snapshot"):
            with self.subTest(kind=kind):
                self.assertEqual(kinds[kind]["identifierRole"], kind)

    def test_canonical_json_and_record_version_are_machine_readable(self) -> None:
        canonical = self.catalog["canonicalJson"]
        self.assertEqual(
            set(canonical), {"name", "input", "output", "members", "strings", "numbers", "literals"}
        )
        self.assertEqual(canonical["name"], "grove-canonical-json-v0")
        for error in ("invalid-utf8", "byte-order-mark", "non-ascii-member-name", "duplicate-member", "unpaired-surrogate"):
            with self.subTest(error=error):
                self.assertIn(error, canonical["input"])
        self.assertIn("no trailing newline", canonical["output"])
        record = self.catalog["recordVersion"]
        self.assertEqual(record["contentDomain"], "org.grovealliance.fhir.record-content.v0")
        self.assertEqual(PROTOCOL.RECORD_CONTENT_DOMAIN, record["contentDomain"])
        self.assertEqual(record["digestComponent"], "record-content-digest")
        self.assertEqual(record["receiverUse"], "equality-and-tie-break")
        self.assertIn("Resource.id", record["exclusions"])
        self.assertIn(self.catalog["extensions"]["recordVersion"], record["exclusions"])
        self.assertIn("Nothing else is removed", record["exclusions"])
        self.assertIn("never parse or recompute", record["receiverRule"])
        self.assertIn("has no grove-record-version", record["retractionKey"])

    def test_version_selection_is_one_normative_set_rule(self) -> None:
        selection = self.catalog["lifecycle"]["active"]["versionSelection"]
        self.assertEqual(
            list(selection),
            [
                "scope", "exactRetry", "alteredRetry", "writerEvidence", "writerOrder",
                "recordedOrder", "tieBreak", "membership", "history", "retraction",
            ],
        )
        self.assertIn("Drop every version", selection["writerOrder"])
        self.assertIn("the longer is greater", selection["writerOrder"])
        self.assertIn("never compared as text and never rounded", selection["recordedOrder"])
        self.assertIn("unsigned bytewise UTF-8", selection["tieBreak"])
        self.assertIn("then the greatest Identifier.system", selection["tieBreak"])
        self.assertIn("never a maximum taken independently for each output", selection["membership"])
        self.assertIn("Every accepted version stays", selection["history"])
        # H26: a retraction addresses its whole source record, before or after, never undone.
        for clause in (
            "every output of every version of its Provenance.entity source record",
            "accepted before or after the retraction",
            "informative",
            "never un-retracted",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, selection["retraction"])

    def test_retraction_addresses_its_whole_source_record(self) -> None:
        retraction = self.catalog["lifecycle"]["retraction"]
        self.assertIn("that whole record", retraction["meaning"])
        self.assertIn("informative", retraction["target"])
        self.assertIn("neither address nor bind an output", retraction["target"])
        self.assertIn("every version of the source record", retraction["sink"])
        self.assertIn("need not resolve the targets", retraction["sink"])
        self.assertIn("Devices are never retracted", retraction["sink"])
        self.assertIn(
            "the retraction address is the Provenance's source-record entity",
            retraction["nativeRecordIdentifier"]["prohibitions"],
        )
        self.assertNotIn("device-snapshot", retraction["targetRoles"])

    def test_payload_equality_separates_retries_lexemes_and_altered_retries(self) -> None:
        equality = self.catalog["payload"]["equality"]
        self.assertEqual(set(equality), {"formatting", "decimalLexeme", "alteredRetry", "vectors"})
        self.assertIn("exact retry", equality["formatting"])
        self.assertIn("new version", equality["decimalLexeme"])
        self.assertIn("record-version keys only", equality["alteredRetry"])
        self.assertIn("duplicate retraction", equality["alteredRetry"])
        for vector in ("reformatted-retry", "lexeme-retry", "altered-retry", "testVectors.canonicalJson", "testVectors.recordContents"):
            with self.subTest(vector=vector):
                self.assertIn(vector, equality["vectors"])

    def test_recording_device_carries_one_content_snapshot_and_requires_a_unit_token(self) -> None:
        device = self.catalog["recordingDevice"]
        self.assertIn("omit", device["unknownInstance"].lower())
        self.assertIn("exactly one device-snapshot identifier", device["snapshots"])

    def test_test_key_is_explicitly_forbidden_in_production(self) -> None:
        self.assertIn("Public conformance key", self.vectors["warning"])
        self.assertTrue(
            self.catalog["opaqueIdentity"]["keyRequirements"]["testKeysProhibited"]
        )


class RecordIdentityTests(unittest.TestCase):
    """The record-centric identities: content snapshots, record versions, and retractions."""

    key = bytes(range(32))

    @classmethod
    def setUpClass(cls) -> None:
        cls.vectors = json.loads(
            (ROOT / "catalog/exchange-protocol.json").read_text(encoding="utf-8")
        )["testVectors"]

    def test_catalog_record_content_vectors_match_the_spec(self) -> None:
        self.assertEqual(
            {vector["id"]: vector["recordContentDigest"] for vector in self.vectors["recordContents"]},
            RECORD_CONTENT_DIGESTS,
        )
        for vector in self.vectors["recordContents"]:
            with self.subTest(vector=vector["id"]):
                provenance = CANONICAL.loads_lossless(vector["provenance"].encode("utf-8"))
                outputs = [CANONICAL.loads_lossless(output.encode("utf-8")) for output in vector["outputs"]]
                self.assertEqual(
                    PROTOCOL.record_content_digest(provenance, outputs), vector["recordContentDigest"]
                )

    def test_catalog_record_identity_vectors_match_the_spec(self) -> None:
        identities = {vector["id"]: vector for vector in self.vectors["identities"]}
        expected = {
            **{f"record-version-{name}": value for name, (value, _) in RECORD_VERSIONS.items()},
            "record-retraction-heart-rate": RECORD_RETRACTION[0],
        }
        for vector_id, value in expected.items():
            with self.subTest(vector=vector_id):
                self.assertEqual(identities[vector_id]["value"], value)
        self.assertEqual(
            identities["record-version-heart-rate-72"]["components"],
            [SOURCE_RECORD_SYSTEM, SOURCE_RECORD_VALUE, RECORD_CONTENT_DIGESTS["heart-rate-72"]],
        )
        self.assertEqual(
            identities["record-retraction-heart-rate"]["components"],
            [SOURCE_RECORD_SYSTEM, SOURCE_RECORD_VALUE],
        )

    def test_identity_components_have_the_record_centric_positions(self) -> None:
        expected = {
            "device-snapshot": ("subject-system", "subject-value", "node-role", "content-digest"),
            "context-snapshot": ("subject-system", "subject-value", "node-role", "content-digest"),
            "record-version": ("source-record-system", "source-record-value", "record-content-digest"),
            "record-retraction": ("source-record-system", "source-record-value"),
        }
        self.assertEqual(len(PROTOCOL.IDENTITY_KIND_COMPONENT_NAMES), 13)
        for kind, names in expected.items():
            with self.subTest(kind=kind):
                self.assertEqual(PROTOCOL.IDENTITY_KIND_COMPONENT_NAMES[kind], names)
        common = {"key": self.key, "key_id": "test-key", "epoch": 1}
        cases = (
            (
                PROTOCOL.device_snapshot_identity(
                    **common, subject_system="s", subject_value="p", node_role="host", content_digest=DIGEST,
                ),
                "device-snapshot", ["s", "p", "host", DIGEST],
            ),
            (
                PROTOCOL.context_snapshot_identity(
                    **common, subject_system="s", subject_value="p", node_role="patient", content_digest=DIGEST,
                ),
                "context-snapshot", ["s", "p", "patient", DIGEST],
            ),
            (
                PROTOCOL.record_version_identity(
                    **common, source_record_system="s", source_record_value="v", record_content_digest=DIGEST,
                ),
                "record-version", ["s", "v", DIGEST],
            ),
            (
                PROTOCOL.record_retraction_identity(**common, source_record_system="s", source_record_value="v"),
                "record-retraction", ["s", "v"],
            ),
        )
        values = set()
        for value, kind, components in cases:
            with self.subTest(kind=kind):
                self.assertEqual(
                    value,
                    PROTOCOL.derive_hmac_identity(**common, identity_kind=kind, components=components),
                )
                values.add(value)
        self.assertEqual(len(values), len(cases))

    def test_record_content_vectors_are_exact(self) -> None:
        self.assertEqual(
            CANONICAL.canonical_bytes(CANONICAL.loads_lossless(RECORD_CONTENT_PROVENANCE)),
            RECORD_CONTENT_PROVENANCE,
        )
        self.assertEqual(
            CANONICAL.canonical_bytes(CANONICAL.loads_lossless(RECORD_CONTENT_OUTPUT)),
            RECORD_CONTENT_OUTPUT,
        )
        for vector, value in (("heart-rate-72", b"72"), ("heart-rate-72-0", b"72.0")):
            with self.subTest(vector=vector):
                self.assertEqual(
                    PROTOCOL.record_content_digest(record_content_provenance(), [record_content_output(value)]),
                    RECORD_CONTENT_DIGESTS[vector],
                )

    def test_record_version_and_retraction_vectors_are_exact(self) -> None:
        for vector, (value, full_url) in RECORD_VERSIONS.items():
            with self.subTest(vector=vector):
                actual = PROTOCOL.record_version_identity(
                    key=self.key,
                    key_id="test-key",
                    epoch="1",
                    source_record_system=SOURCE_RECORD_SYSTEM,
                    source_record_value=SOURCE_RECORD_VALUE,
                    record_content_digest=RECORD_CONTENT_DIGESTS[vector],
                )
                self.assertEqual(actual, value)
                self.assertEqual(PROTOCOL.entry_full_url(RECORD_VERSION_SYSTEM, actual), full_url)
        retraction = PROTOCOL.record_retraction_identity(
            key=self.key,
            key_id="test-key",
            epoch="1",
            source_record_system=SOURCE_RECORD_SYSTEM,
            source_record_value=SOURCE_RECORD_VALUE,
        )
        self.assertEqual(retraction, RECORD_RETRACTION[0])
        self.assertEqual(PROTOCOL.entry_full_url(RECORD_RETRACTION_SYSTEM, retraction), RECORD_RETRACTION[1])
        # The tie-break between the two versions (equal writer evidence and recorded) is bytewise.
        self.assertGreater(
            RECORD_VERSIONS["heart-rate-72-0"][0].encode("utf-8"),
            RECORD_VERSIONS["heart-rate-72"][0].encode("utf-8"),
        )

    def test_record_content_excludes_only_id_and_the_record_version_extension(self) -> None:
        expected = RECORD_CONTENT_DIGESTS["heart-rate-72"]
        output = record_content_output()
        bare = CANONICAL.loads_lossless(RECORD_CONTENT_PROVENANCE)
        self.assertEqual(PROTOCOL.record_content_digest(bare, [output]), expected)
        # The extension's own value never enters its preimage, nor does any output's `id`.
        self.assertEqual(
            PROTOCOL.record_content_digest(record_content_provenance("v0:other:1:" + DIGEST), [output]),
            expected,
        )
        self.assertEqual(PROTOCOL.record_content_digest(bare, [{**output, "id": "output-id"}]), expected)
        two_versions = record_content_provenance()
        two_versions["extension"] = two_versions["extension"] * 2
        self.assertEqual(PROTOCOL.record_content_digest(two_versions, [output]), expected)
        other_extension = {"url": "https://example.org/other", "valueString": "kept"}
        kept = record_content_provenance()
        kept["extension"] = [*kept["extension"], other_extension]
        self.assertNotEqual(PROTOCOL.record_content_digest(kept, [output]), expected)
        self.assertEqual(
            PROTOCOL.record_content_digest(kept, [output]),
            PROTOCOL.record_content_digest({**bare, "extension": [other_extension]}, [output]),
        )
        for changed in (
            {**bare, "recorded": "2026-08-20T17:31:02Z"},
            {**bare, "recorded": "2026-08-20T17:30:02.000Z"},
            {**bare, "meta": {"profile": []}},
        ):
            with self.subTest(changed=changed):
                self.assertNotEqual(PROTOCOL.record_content_digest(changed, [output]), expected)
        self.assertNotEqual(
            PROTOCOL.record_content_digest(bare, [{**output, "status": "amended"}]), expected
        )

    def test_record_content_frames_every_output_in_target_order(self) -> None:
        output = record_content_output()
        second = record_content_output(b"73")
        provenance = CANONICAL.loads_lossless(RECORD_CONTENT_PROVENANCE)
        provenance["target"] = [*provenance["target"], {"reference": "urn:uuid:second"}]
        forward = PROTOCOL.record_content_digest(provenance, [output, second])
        self.assertNotEqual(forward, PROTOCOL.record_content_digest(provenance, [second, output]))
        bundle = {
            "resourceType": "Bundle",
            "entry": [
                {"fullUrl": "urn:uuid:second", "resource": second},
                {"fullUrl": "urn:uuid:a9b76bbc-f523-5ef4-9919-813ec70553e5", "resource": output},
            ],
        }
        self.assertEqual(PROTOCOL.record_outputs(bundle, provenance), [output, second])
        self.assertEqual(
            PROTOCOL.record_content_digest(provenance, PROTOCOL.record_outputs(bundle, provenance)), forward
        )
        for outputs in ([output], [output, second, second], output, []):
            with self.subTest(count=len(outputs)), self.assertRaises(PROTOCOL.ExchangeProtocolError):
                PROTOCOL.record_content_digest(provenance, outputs)  # type: ignore[arg-type]
        with self.assertRaisesRegex(PROTOCOL.ExchangeProtocolError, "resolves to no entry"):
            PROTOCOL.record_outputs({"entry": bundle["entry"][:1]}, provenance)
        with self.assertRaisesRegex(PROTOCOL.ExchangeProtocolError, "repeats"):
            PROTOCOL.record_outputs({"entry": [*bundle["entry"], bundle["entry"][0]]}, provenance)
        with self.assertRaisesRegex(PROTOCOL.ExchangeProtocolError, "starts with a Provenance"):
            PROTOCOL.record_content_digest(output, [output])
        # Lexemes are part of the content: a tree that lost them has no record content.
        with self.assertRaises(CANONICAL.CanonicalJSONError):
            PROTOCOL.record_content_digest(provenance, [output, json.loads(RECORD_CONTENT_OUTPUT)])

    def test_content_digest_excludes_id_and_the_own_snapshot_key_only(self) -> None:
        role_system = PROTOCOL.IDENTIFIER_ROLE_SYSTEM

        def typed(role: str, value: str) -> dict:
            return {
                "type": {"coding": [{"system": role_system, "code": role}]},
                "system": f"https://study.example.org/fhir/NamingSystem/grove-{role}-v0/test-key/1",
                "value": value,
            }

        device = CANONICAL.loads_lossless(
            b'{"resourceType":"Device","manufacturer":"Apple Inc.","version":[{"value":"17.0"}]}'
        )
        expected = PROTOCOL.base64url_no_padding(hashlib.sha256(CANONICAL.canonical_bytes(device)).digest())
        self.assertEqual(PROTOCOL.content_digest(device), expected)
        keyed = {**device, "id": "device-1", "identifier": [typed("device-snapshot", "v0:test-key:1:" + DIGEST)]}
        self.assertEqual(PROTOCOL.content_digest(keyed), expected)
        unit = typed("recording-device", "v0:test-key:1:" + DIGEST)
        self.assertEqual(
            PROTOCOL.content_digest({**keyed, "identifier": [unit, *keyed["identifier"]]}),
            PROTOCOL.content_digest({**device, "identifier": [unit]}),
        )
        self.assertNotEqual(PROTOCOL.content_digest({**device, "identifier": [unit]}), expected)
        # Another node type's snapshot role is content, not the Device's own key.
        self.assertNotEqual(
            PROTOCOL.content_digest({**device, "identifier": [typed("context-snapshot", "x")]}), expected
        )
        self.assertNotEqual(
            PROTOCOL.content_digest({**device, "version": [{"value": "17.1"}]}), expected
        )
        study = {
            "resourceType": "ResearchStudy",
            "status": "active",
            "identifier": [{"system": "https://study.example.org/studies", "value": "mhc"}],
        }
        self.assertEqual(
            PROTOCOL.content_digest({**study, "identifier": [*study["identifier"], typed("context-snapshot", "x")]}),
            PROTOCOL.content_digest(study),
        )
        for resource_type in ("Patient", "ResearchSubject", "PlanDefinition"):
            with self.subTest(resource_type=resource_type):
                node = {"resourceType": resource_type, "status": "active"}
                self.assertEqual(
                    PROTOCOL.content_digest({**node, "identifier": [typed("context-snapshot", "x")]}),
                    PROTOCOL.content_digest(node),
                )
        response = CANONICAL.loads_lossless(
            b'{"resourceType":"QuestionnaireResponse","status":"completed",'
            b'"identifier":{"system":"https://study.example.org/responses","value":"r-1"},'
            b'"item":[{"linkId":"1","answer":[{"valueDecimal":72.0}]}]}'
        )
        snapshot = {
            "url": PROTOCOL.CONTEXT_SNAPSHOT_EXTENSION,
            "valueIdentifier": typed("context-snapshot", "v0:test-key:1:" + DIGEST),
        }
        other = {"url": "https://example.org/other", "valueString": "kept"}
        response_digest = PROTOCOL.content_digest(response)
        self.assertEqual(PROTOCOL.content_digest({**response, "id": "r", "extension": [snapshot]}), response_digest)
        self.assertEqual(
            PROTOCOL.content_digest({**response, "extension": [snapshot, other]}),
            PROTOCOL.content_digest({**response, "extension": [other]}),
        )
        self.assertNotEqual(PROTOCOL.content_digest({**response, "extension": [other]}), response_digest)
        # The submission identifier is content: an amended response keeps it and gets a new key.
        amended = {**response, "status": "amended"}
        self.assertNotEqual(PROTOCOL.content_digest(amended), response_digest)
        for resource in ({"resourceType": "Observation"}, {}, []):
            with self.subTest(resource=resource), self.assertRaises(PROTOCOL.ExchangeProtocolError):
                PROTOCOL.content_digest(resource)  # type: ignore[arg-type]
        with self.assertRaises(CANONICAL.CanonicalJSONError):
            PROTOCOL.content_digest({"resourceType": "Device", "version": [{"value": 17.0}]})


if __name__ == "__main__":
    unittest.main()
