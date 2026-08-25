"""Tests for deterministic FHIR package semantic snapshots and diffs."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import tarfile
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from Scripts import fhir_package_semantic_diff as DIFF
from Scripts import fhir_package_semantic_snapshot as SNAPSHOT


class FHIRPackageSemanticTests(unittest.TestCase):
    @staticmethod
    def _resources() -> dict[str, dict[str, object]]:
        return {
            "StructureDefinition-grove-observation.json": {
                "resourceType": "StructureDefinition",
                "id": "grove-observation",
                "url": "https://example.org/fhir/StructureDefinition/grove-observation",
                "version": "0.1.0",
                "name": "GroveObservation",
                "status": "draft",
                "date": "2026-08-19",
                "kind": "resource",
                "abstract": False,
                "type": "Observation",
                "baseDefinition": "http://hl7.org/fhir/StructureDefinition/Observation",
                "derivation": "constraint",
                "text": {"status": "generated", "div": "<div>volatile narrative</div>"},
                "meta": {"lastUpdated": "2026-08-19T07:00:00Z"},
                "snapshot": {"element": [{"id": "Observation", "path": "Observation"}]},
                "differential": {
                    "element": [
                        {
                            "id": "Observation.value[x]",
                            "path": "Observation.value[x]",
                            "sliceName": "measurement",
                            "min": 1,
                            "max": "1",
                            "mustSupport": True,
                            "type": [
                                {
                                    "code": "Quantity",
                                    "profile": [
                                        "http://hl7.org/fhir/StructureDefinition/SimpleQuantity"
                                    ],
                                    "targetProfile": [
                                        "http://hl7.org/fhir/StructureDefinition/Observation"
                                    ],
                                }
                            ],
                            "fixedCode": "fixed",
                            "patternQuantity": {
                                "system": "http://unitsofmeasure.org",
                                "code": "1",
                            },
                            "slicing": {
                                "discriminator": [{"type": "value", "path": "code"}],
                                "ordered": False,
                                "rules": "open",
                            },
                            "binding": {
                                "strength": "required",
                                "valueSet": "https://example.org/fhir/ValueSet/measurements",
                            },
                            "constraint": [
                                {
                                    "key": "grove-1",
                                    "severity": "error",
                                    "human": "A measurement is present",
                                    "expression": "exists()",
                                }
                            ],
                        }
                    ]
                },
            },
            "CodeSystem-measurements.json": {
                "resourceType": "CodeSystem",
                "id": "measurements",
                "url": "https://example.org/fhir/CodeSystem/measurements",
                "version": "0.1.0",
                "name": "Measurements",
                "status": "active",
                "date": "2026-08-19",
                "content": "complete",
                "concept": [{"code": "heart-rate", "display": "Heart rate"}],
            },
            "ValueSet-measurements.json": {
                "resourceType": "ValueSet",
                "id": "measurements",
                "url": "https://example.org/fhir/ValueSet/measurements",
                "version": "0.1.0",
                "name": "Measurements",
                "status": "active",
                "compose": {
                    "include": [
                        {"system": "https://example.org/fhir/CodeSystem/measurements"}
                    ]
                },
            },
            "NamingSystem-device-identifiers.json": {
                "resourceType": "NamingSystem",
                "id": "device-identifiers",
                "name": "DeviceIdentifiers",
                "status": "active",
                "kind": "identifier",
                "date": "2026-08-19",
                "uniqueId": [
                    {
                        "type": "uri",
                        "value": "https://example.org/identifier/device",
                        "preferred": True,
                    }
                ],
            },
            "ImplementationGuide-example.json": {
                "resourceType": "ImplementationGuide",
                "id": "example",
                "url": "https://example.org/fhir/ImplementationGuide/example",
                "version": "0.1.0",
                "name": "ExampleGuide",
                "status": "draft",
                "date": "2026-08-19T07:00:00Z",
                "packageId": "org.example.fhir",
                "fhirVersion": ["4.0.1"],
                "definition": {
                    "parameter": [
                        {"code": "path-resource", "value": "input/resources"},
                        {"code": "generate", "value": "xml"},
                    ],
                    "page": {
                        "nameUrl": "index.html",
                        "title": "Overview",
                        "generation": "markdown",
                    },
                    "resource": [
                        {
                            "extension": [
                                {
                                    "url": (
                                        "http://hl7.org/fhir/StructureDefinition/"
                                        "implementationguide-page"
                                    ),
                                    "valueUri": "StructureDefinition-grove-observation.html",
                                }
                            ],
                            "reference": {
                                "reference": "StructureDefinition/grove-observation"
                            }
                        }
                    ]
                },
                "manifest": {
                    "rendering": "file:///tmp/output",
                    "resource": [
                        {
                            "reference": {
                                "reference": "StructureDefinition/grove-observation"
                            },
                            "relativePath": "StructureDefinition-grove-observation.html",
                        }
                    ],
                },
            },
            "example/Observation-example.json": {
                "resourceType": "Observation",
                "id": "example",
                "meta": {
                    "lastUpdated": "2026-08-19T07:00:00Z",
                    "profile": [
                        "https://example.org/fhir/StructureDefinition/grove-observation|0.1.0"
                    ],
                },
                "text": {"status": "generated", "div": "<div>example</div>"},
                "status": "final",
                "code": {"text": "Heart rate"},
                "subject": {"reference": "Patient/example"},
                "valueQuantity": {
                    "value": 72,
                    "system": "http://unitsofmeasure.org",
                    "code": "/min",
                },
            },
        }

    def _write_package(
        self,
        root: Path,
        resources: dict[str, dict[str, object]] | None = None,
        metadata: dict[str, object] | None = None,
        reverse: bool = False,
    ) -> Path:
        package = root / "package"
        package.mkdir(parents=True)
        metadata = metadata or {
            "name": "org.example.fhir",
            "version": "0.1.0",
            "canonical": "https://example.org/fhir",
            "url": "file:///private/tmp/build/output",
            "date": "20260819070000",
            "description": "Example guide (built Wed, Aug 19, 2026 07:00-0700)",
            "directories": {"lib": "/private/tmp/build/package"},
            "fhirVersions": ["4.0.1"],
            "dependencies": {
                "hl7.fhir.uv.extensions.r4": "5.3.0",
                "hl7.fhir.r4.core": "4.0.1",
            },
        }
        (package / "package.json").write_text(
            json.dumps(metadata, sort_keys=reverse), encoding="utf-8"
        )
        entries = list((resources or self._resources()).items())
        if reverse:
            entries.reverse()
        for name, resource in entries:
            destination = package / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(
                json.dumps(resource, sort_keys=reverse), encoding="utf-8"
            )
        index_entries = []
        for name, resource in entries:
            if "/" in name:
                continue
            entry = {
                "filename": name,
                "resourceType": resource["resourceType"],
                "id": resource.get("id"),
            }
            for field in ("url", "version"):
                if field in resource:
                    entry[field] = resource[field]
            index_entries.append(entry)
        (package / ".index.json").write_text(
            json.dumps({"index-version": 2, "files": index_entries}),
            encoding="utf-8",
        )
        return root

    def test_snapshot_covers_package_and_conformance_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = self._write_package(Path(directory))
            snapshot = SNAPSHOT.create_snapshot(package)

        self.assertEqual(snapshot["package"]["name"], "org.example.fhir")
        self.assertEqual(snapshot["normalization"], SNAPSHOT.NORMALIZATION)
        self.assertEqual(
            snapshot["referenceModel"],
            {
                "fhirVersion": "4.0.1",
                "package": "hl7.fhir.r4.core",
                "version": "4.0.1",
                "archiveSha256": (
                    "ebd7731df7d36b5b7d39d5fb6c9d77b44bb7fe5742f1a2e87f164738c3289d44"
                ),
            },
        )
        self.assertNotIn("date", snapshot["package"])
        self.assertNotIn("url", snapshot["package"])
        self.assertNotIn("directories", snapshot["package"])
        self.assertEqual(
            snapshot["dependencies"],
            {
                "hl7.fhir.r4.core": "4.0.1",
                "hl7.fhir.uv.extensions.r4": "5.3.0",
            },
        )

        key = "https://example.org/fhir/StructureDefinition/grove-observation"
        structure = snapshot["structureDefinitions"][key]["resource"]
        element = structure["differential"]["element"][0]
        self.assertEqual(element["min"], 1)
        self.assertEqual(element["max"], "1")
        self.assertTrue(element["mustSupport"])
        self.assertEqual(element["type"][0]["code"], "Quantity")
        self.assertIn("profile", element["type"][0])
        self.assertIn("targetProfile", element["type"][0])
        self.assertEqual(element["fixedCode"], "fixed")
        self.assertEqual(element["patternQuantity"]["code"], "1")
        self.assertEqual(element["slicing"]["rules"], "open")
        self.assertEqual(element["binding"]["strength"], "required")
        self.assertEqual(element["constraint"][0]["key"], "grove-1")
        self.assertEqual(structure["date"], "2026-08-19")
        self.assertEqual(
            structure["snapshot"],
            {"element": [{"id": "Observation", "path": "Observation"}]},
        )
        self.assertNotIn("text", structure)
        self.assertNotIn("meta", structure)

        self.assertEqual(len(snapshot["codeSystems"]), 1)
        self.assertEqual(len(snapshot["valueSets"]), 1)
        self.assertEqual(len(snapshot["namingSystems"]), 1)
        guide = next(iter(snapshot["implementationGuides"].values()))["resource"]
        self.assertIn("definition", guide)
        self.assertNotIn("date", guide)
        self.assertEqual(
            guide["definition"]["parameter"], [{"code": "generate", "value": "xml"}]
        )
        self.assertEqual(
            guide["definition"]["page"],
            {"title": "Overview", "generation": "markdown"},
        )
        self.assertNotIn("extension", guide["definition"]["resource"][0])
        self.assertEqual(
            guide["manifest"],
            {
                "resource": [
                    {
                        "reference": {
                            "reference": "StructureDefinition/grove-observation"
                        }
                    }
                ]
            },
        )
        example = snapshot["examples"]["Observation/example"]
        self.assertRegex(example["sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(
            example["profiles"],
            ["https://example.org/fhir/StructureDefinition/grove-observation|0.1.0"],
        )
        self.assertEqual(example["resource"]["valueQuantity"]["value"], 72)
        self.assertNotIn("text", example["resource"])
        self.assertIn(
            {
                "source": "Observation/example",
                "kind": "reference",
                "target": "Patient/example",
                "path": "/subject/reference",
            },
            snapshot["referenceGraph"],
        )
        self.assertIn(
            {
                "source": "Observation/example",
                "kind": "canonical",
                "target": "https://example.org/fhir/StructureDefinition/grove-observation|0.1.0",
                "path": "/meta/profile/0",
            },
            snapshot["referenceGraph"],
        )
        self.assertEqual(SNAPSHOT.validate_snapshot(snapshot), [])

    def test_authored_implementation_guide_date_is_preserved(self) -> None:
        guide = deepcopy(self._resources()["ImplementationGuide-example.json"])
        guide["date"] = "2025-01-02T03:04:05Z"
        sanitized = SNAPSHOT.sanitize_resource(guide, "20260819070000")
        self.assertEqual(sanitized["date"], "2025-01-02T03:04:05Z")

    def test_exact_publisher_canonical_date_is_removed(self) -> None:
        code_system = deepcopy(self._resources()["CodeSystem-measurements.json"])
        code_system["date"] = "2026-08-19T07:00:00-07:00"
        sanitized = SNAPSHOT.sanitize_resource(code_system, "20260819070000")
        self.assertNotIn("date", sanitized)

    def test_authored_datetime_near_build_clock_remains_semantic(self) -> None:
        code_system = deepcopy(self._resources()["CodeSystem-measurements.json"])
        code_system["date"] = "2026-08-19T07:00:01-07:00"
        sanitized = SNAPSHOT.sanitize_resource(code_system, "20260819070000")
        self.assertEqual(sanitized["date"], "2026-08-19T07:00:01-07:00")

    def test_snapshot_is_deterministic_across_file_and_key_order(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = SNAPSHOT.create_snapshot(self._write_package(root / "first"))
            second = SNAPSHOT.create_snapshot(
                self._write_package(root / "second", reverse=True)
            )
        self.assertEqual(first, second)
        self.assertEqual(
            SNAPSHOT.canonical_json_bytes(first), SNAPSHOT.canonical_json_bytes(second)
        )

    def test_r4_reference_graph_uses_core_canonical_element_types(self) -> None:
        resources = [
            {
                "resourceType": "CodeSystem",
                "id": "codes",
                "url": "https://example.org/CodeSystem/codes",
                "supplements": "https://example.org/CodeSystem/base|1",
            },
            {
                "resourceType": "CapabilityStatement",
                "id": "capability",
                "rest": [
                    {
                        "compartment": ["http://hl7.org/fhir/CompartmentDefinition/Patient"],
                        "resource": [
                            {
                                "type": "Observation",
                                "supportedProfile": ["https://example.org/Profile/Observation"],
                            }
                        ],
                    }
                ],
            },
            {
                "resourceType": "OperationDefinition",
                "id": "operation",
                "inputProfile": "https://example.org/Profile/Input",
                "outputProfile": "https://example.org/Profile/Output",
            },
            {
                "resourceType": "ImplementationGuide",
                "id": "guide",
                "dependsOn": [
                    {
                        "packageId": "example.dependency",
                        "version": "1.0.0",
                        "uri": "https://example.org/ImplementationGuide/dependency",
                    }
                ],
            },
            {
                "resourceType": "StructureMap",
                "id": "map",
                "structure": [
                    {"url": "https://example.org/StructureDefinition/source", "mode": "source"}
                ],
            },
            {
                "resourceType": "TestScript",
                "id": "test",
                "metadata": {
                    "capability": [
                        {"capabilities": "https://example.org/CapabilityStatement/server"}
                    ]
                },
            },
            {
                "resourceType": "ExampleScenario",
                "id": "scenario",
                "workflow": ["https://example.org/PlanDefinition/workflow"],
            },
            {
                "resourceType": "MessageDefinition",
                "id": "message",
                "parent": ["https://example.org/MessageDefinition/parent"],
                "replaces": ["https://example.org/MessageDefinition/old"],
                "graph": ["https://example.org/GraphDefinition/message"],
            },
            {
                "resourceType": "PlanDefinition",
                "id": "plan",
                "action": [
                    {
                        "definitionCanonical": (
                            "https://example.org/ActivityDefinition/action"
                        )
                    }
                ],
            },
            {
                "resourceType": "StructureDefinition",
                "id": "profile",
                "differential": {
                    "element": [
                        {
                            "id": "Observation",
                            "path": "Observation",
                            "definition": "Human prose is not a canonical reference.",
                            "constraint": [
                                {
                                    "key": "rule",
                                    "source": (
                                        "https://example.org/StructureDefinition/"
                                        "rule-source"
                                    ),
                                }
                            ],
                        }
                    ]
                },
            },
        ]
        bundle = {
            "resourceType": "Bundle",
            "id": "all",
            "entry": [{"resource": resource} for resource in resources],
        }
        edges = SNAPSHOT._reference_edges("Bundle/all", bundle, "4.0.1")
        targets = {edge["target"] for edge in edges if edge["kind"] == "canonical"}
        self.assertEqual(
            targets,
            {
                "https://example.org/CodeSystem/base|1",
                "http://hl7.org/fhir/CompartmentDefinition/Patient",
                "https://example.org/Profile/Observation",
                "https://example.org/Profile/Input",
                "https://example.org/Profile/Output",
                "https://example.org/ImplementationGuide/dependency",
                "https://example.org/StructureDefinition/source",
                "https://example.org/CapabilityStatement/server",
                "https://example.org/PlanDefinition/workflow",
                "https://example.org/MessageDefinition/parent",
                "https://example.org/MessageDefinition/old",
                "https://example.org/GraphDefinition/message",
                "https://example.org/ActivityDefinition/action",
                "https://example.org/StructureDefinition/rule-source",
            },
        )
        self.assertNotIn("Human prose is not a canonical reference.", targets)

    def test_r5_reference_graph_uses_its_versioned_core_model(self) -> None:
        bundle = {
            "resourceType": "Bundle",
            "id": "r5",
            "entry": [
                {
                    "resource": {
                        "resourceType": "ConceptMap",
                        "id": "map",
                        "group": [
                            {
                                "source": "https://example.org/CodeSystem/source",
                                "target": "https://example.org/CodeSystem/target",
                            }
                        ],
                    }
                },
                {
                    "resource": {
                        "resourceType": "TestScript",
                        "id": "test",
                        "scope": [
                            {"artifact": "https://example.org/CapabilityStatement/scope"}
                        ],
                    }
                },
                {
                    "resource": {
                        "resourceType": "Subscription",
                        "id": "subscription",
                        "topic": "https://example.org/SubscriptionTopic/topic",
                    }
                },
            ],
        }
        edges = SNAPSHOT._reference_edges("Bundle/r5", bundle, "5.0.0")
        self.assertEqual(
            {edge["target"] for edge in edges if edge["kind"] == "canonical"},
            {
                "https://example.org/CodeSystem/source",
                "https://example.org/CodeSystem/target",
                "https://example.org/CapabilityStatement/scope",
                "https://example.org/SubscriptionTopic/topic",
            },
        )

    def test_r4_ambiguous_canonical_names_use_exact_paths(self) -> None:
        resources = [
            {
                "resourceType": "ActivityDefinition",
                "transform": "https://example.org/StructureMap/activity",
            },
            {
                "resourceType": "CapabilityStatement",
                "instantiates": ["https://example.org/CapabilityStatement/base"],
            },
            {
                "resourceType": "MessageDefinition",
                "base": "https://example.org/MessageDefinition/base",
                "parent": ["https://example.org/MessageDefinition/parent"],
                "allowedResponse": [
                    {"message": "https://example.org/MessageDefinition/response"}
                ],
            },
            {
                "resourceType": "OperationDefinition",
                "base": "https://example.org/OperationDefinition/base",
            },
            {
                "resourceType": "PlanDefinition",
                "action": [
                    {"transform": "https://example.org/StructureMap/plan-action"}
                ],
            },
            {
                "resourceType": "Questionnaire",
                "derivedFrom": ["https://example.org/Questionnaire/base"],
            },
            {
                "resourceType": "SearchParameter",
                "derivedFrom": "https://example.org/SearchParameter/base",
                "base": ["Patient", "Observation"],
            },
            {
                "resourceType": "TestReport",
                "setup": {
                    "action": [
                        {
                            "assert": {"message": "Expected status diagnostic"},
                            "operation": {"message": "Sent request diagnostic"},
                        }
                    ]
                },
            },
            {
                "resourceType": "StructureMap",
                "group": [
                    {
                        "rule": [
                            {"target": [{"transform": "copy"}]},
                        ]
                    }
                ],
            },
            {
                "resourceType": "MedicationAdministration",
                "instantiates": ["urn:workflow:medication"],
            },
            {
                "resourceType": "NutritionOrder",
                "instantiates": ["urn:workflow:nutrition"],
            },
        ]
        bundle = {
            "resourceType": "Bundle",
            "entry": [{"resource": resource} for resource in resources],
        }
        edges = SNAPSHOT._reference_edges("Bundle/r4-ambiguous", bundle, "4.0.1")
        self.assertEqual(
            {edge["target"] for edge in edges if edge["kind"] == "canonical"},
            {
                "https://example.org/StructureMap/activity",
                "https://example.org/CapabilityStatement/base",
                "https://example.org/MessageDefinition/base",
                "https://example.org/MessageDefinition/parent",
                "https://example.org/MessageDefinition/response",
                "https://example.org/OperationDefinition/base",
                "https://example.org/StructureMap/plan-action",
                "https://example.org/Questionnaire/base",
                "https://example.org/SearchParameter/base",
            },
        )

    def test_r5_ambiguous_canonical_names_use_exact_paths(self) -> None:
        resources = [
            {
                "resourceType": "ActivityDefinition",
                "transform": "https://example.org/StructureMap/activity",
            },
            {
                "resourceType": "ActorDefinition",
                "derivedFrom": ["https://example.org/ActorDefinition/base"],
            },
            {
                "resourceType": "CapabilityStatement",
                "instantiates": ["https://example.org/CapabilityStatement/base"],
            },
            {
                "resourceType": "MessageDefinition",
                "base": "https://example.org/MessageDefinition/base",
                "parent": ["https://example.org/MessageDefinition/parent"],
                "allowedResponse": [
                    {"message": "https://example.org/MessageDefinition/response"}
                ],
            },
            {
                "resourceType": "OperationDefinition",
                "base": "https://example.org/OperationDefinition/base",
            },
            {
                "resourceType": "PlanDefinition",
                "action": [
                    {"transform": "https://example.org/StructureMap/plan-action"}
                ],
            },
            {
                "resourceType": "Questionnaire",
                "derivedFrom": ["https://example.org/Questionnaire/base"],
            },
            {
                "resourceType": "RequestOrchestration",
                "action": [
                    {"transform": "https://example.org/StructureMap/request-action"}
                ],
            },
            {
                "resourceType": "Requirements",
                "derivedFrom": ["https://example.org/Requirements/base"],
                "statement": [
                    {
                        "key": "statement-key",
                        "derivedFrom": "prior-statement-key",
                        "parent": "parent-statement-key",
                    }
                ],
            },
            {
                "resourceType": "SearchParameter",
                "derivedFrom": "https://example.org/SearchParameter/base",
                "base": ["Patient", "Observation"],
            },
            {
                "resourceType": "SubscriptionTopic",
                "derivedFrom": ["https://example.org/SubscriptionTopic/base"],
            },
            {
                "resourceType": "TestReport",
                "setup": {
                    "action": [
                        {
                            "assert": {"message": "Expected status diagnostic"},
                            "operation": {"message": "Sent request diagnostic"},
                        }
                    ]
                },
            },
            {
                "resourceType": "StructureMap",
                "group": [
                    {
                        "rule": [
                            {"target": [{"transform": "copy"}]},
                        ]
                    }
                ],
            },
            {
                "resourceType": "NutritionOrder",
                "instantiates": ["urn:workflow:nutrition"],
            },
        ]
        bundle = {
            "resourceType": "Bundle",
            "entry": [{"resource": resource} for resource in resources],
        }
        edges = SNAPSHOT._reference_edges("Bundle/r5-ambiguous", bundle, "5.0.0")
        self.assertEqual(
            {edge["target"] for edge in edges if edge["kind"] == "canonical"},
            {
                "https://example.org/StructureMap/activity",
                "https://example.org/ActorDefinition/base",
                "https://example.org/CapabilityStatement/base",
                "https://example.org/MessageDefinition/base",
                "https://example.org/MessageDefinition/parent",
                "https://example.org/MessageDefinition/response",
                "https://example.org/OperationDefinition/base",
                "https://example.org/StructureMap/plan-action",
                "https://example.org/Questionnaire/base",
                "https://example.org/StructureMap/request-action",
                "https://example.org/Requirements/base",
                "https://example.org/SearchParameter/base",
                "https://example.org/SubscriptionTopic/base",
            },
        )

    def test_package_archive_matches_the_unpacked_package(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            unpacked = self._write_package(root / "unpacked")
            archive = root / "package.tgz"
            with tarfile.open(archive, "w:gz") as package:
                for path in sorted((unpacked / "package").iterdir()):
                    package.add(path, arcname=f"package/{path.name}")
            directory_snapshot = SNAPSHOT.create_snapshot(unpacked)
            archive_snapshot = SNAPSHOT.create_snapshot(archive)
        self.assertEqual(directory_snapshot, archive_snapshot)

    def test_only_build_noise_is_ignored(self) -> None:
        first_resources = self._resources()
        second_resources = deepcopy(first_resources)
        second_resources["example/Observation-example.json"]["text"] = {
            "status": "generated",
            "div": "<div>completely different narrative</div>",
        }
        second_resources["example/Observation-example.json"]["meta"]["lastUpdated"] = (
            "2030-01-01T00:00:00Z"
        )
        second_resources["ImplementationGuide-example.json"]["manifest"] = {
            "rendering": "file:///another/machine/output",
            "resource": [
                {
                    "reference": {
                        "reference": "StructureDefinition/grove-observation"
                    },
                    "relativePath": "elsewhere/profile.html",
                }
            ],
        }
        second_resources["ImplementationGuide-example.json"]["date"] = (
            "2030-01-01T00:00:00Z"
        )
        first_metadata = None
        second_metadata = {
            "name": "org.example.fhir",
            "version": "0.1.0",
            "canonical": "https://example.org/fhir",
            "url": "/another/build/output",
            "date": "20300101000000",
            "description": "Example guide (built Tue, Jan 1, 2030 00:00+0000)",
            "directories": {"lib": "/another/build/package"},
            "fhirVersions": ["4.0.1"],
            "dependencies": {
                "hl7.fhir.r4.core": "4.0.1",
                "hl7.fhir.uv.extensions.r4": "5.3.0",
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = SNAPSHOT.create_snapshot(
                self._write_package(root / "first", metadata=first_metadata)
            )
            second = SNAPSHOT.create_snapshot(
                self._write_package(
                    root / "second", resources=second_resources, metadata=second_metadata
                )
            )
        self.assertEqual(first, second)
        self.assertEqual(DIFF.semantic_diff(first, second)["summary"]["total"], 0)

    def test_decimal_precision_is_semantic_and_human_diffable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first_package = self._write_package(root / "first")
            second_package = self._write_package(root / "second")
            first_example = first_package / "package/example/Observation-example.json"
            second_example = second_package / "package/example/Observation-example.json"
            first_example.write_text(
                first_example.read_text(encoding="utf-8").replace('"value": 72', '"value": 1.20'),
                encoding="utf-8",
            )
            second_example.write_text(
                second_example.read_text(encoding="utf-8").replace('"value": 72', '"value": 1.2'),
                encoding="utf-8",
            )
            before = SNAPSHOT.create_snapshot(first_package)
            after = SNAPSHOT.create_snapshot(second_package)
        before_example = before["examples"]["Observation/example"]
        after_example = after["examples"]["Observation/example"]
        self.assertNotEqual(before_example["sha256"], after_example["sha256"])
        self.assertEqual(
            before_example["resource"]["valueQuantity"]["value"].as_tuple().exponent,
            -2,
        )
        report = DIFF.semantic_diff(before, after)
        self.assertIn(
            "/examples/Observation~1example/resource/valueQuantity/value",
            [change["path"] for change in report["changes"]],
        )

    def test_package_member_selection_fails_closed_but_excludes_publisher_diagnostics(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = self._write_package(root / "package")
            baseline = SNAPSHOT.create_snapshot(package)
            other = package / "package/other"
            other.mkdir()
            (other / "validation-summary.json").write_text(
                '{"not":"a FHIR resource"}', encoding="utf-8"
            )
            self.assertEqual(SNAPSHOT.create_snapshot(package), baseline)
            (other / "authored.json").write_text(
                '{"resourceType":"Observation","id":"misplaced"}', encoding="utf-8"
            )
            with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "unsupported JSON members"):
                SNAPSHOT.create_snapshot(package)
            (other / "authored.json").unlink()
            (package / "package/example/broken.json").write_text("[]", encoding="utf-8")
            with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "not a FHIR resource"):
                SNAPSHOT.create_snapshot(package)

    def test_package_directory_rejects_symlinked_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = self._write_package(root / "package")
            outside = root / "outside.json"
            outside.write_text(
                '{"resourceType":"Observation","id":"outside"}', encoding="utf-8"
            )
            (package / "package/example/link.json").symlink_to(outside)
            with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "contains a symlink"):
                SNAPSHOT.create_snapshot(package)

    def test_package_directory_rejects_symlinked_package_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outside = self._write_package(root / "outside")
            inside = root / "inside"
            inside.mkdir()
            (inside / "package").symlink_to(outside / "package", target_is_directory=True)
            with self.assertRaisesRegex(SNAPSHOT.SnapshotError, "root may not be a symlink"):
                SNAPSHOT.create_snapshot(inside)

    def test_authored_dates_and_differential_rules_are_not_stripped(self) -> None:
        first_resources = self._resources()
        second_resources = deepcopy(first_resources)
        second_resources["CodeSystem-measurements.json"]["date"] = "2026-08-20"
        second_resources["StructureDefinition-grove-observation.json"]["differential"][
            "element"
        ][0]["min"] = 0
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            before = SNAPSHOT.create_snapshot(
                self._write_package(root / "before", resources=first_resources)
            )
            after = SNAPSHOT.create_snapshot(
                self._write_package(root / "after", resources=second_resources)
            )
        report = DIFF.semantic_diff(before, after)
        changed_paths = {
            change["path"]
            for change in report["changes"]
            if change["kind"] == "changed"
        }
        self.assertTrue(any(path.endswith("/resource/date") for path in changed_paths))
        self.assertTrue(
            any(
                "/resource/differential/element/" in path and path.endswith("/min")
                for path in changed_paths
            )
        )
        self.assertEqual(report["summary"]["changed"], 2)

    def test_canonical_resources_align_across_versions(self) -> None:
        first_resources = self._resources()
        second_resources = deepcopy(first_resources)
        second_resources["StructureDefinition-grove-observation.json"]["version"] = "0.4.0"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            before = SNAPSHOT.create_snapshot(
                self._write_package(root / "before", resources=first_resources)
            )
            after = SNAPSHOT.create_snapshot(
                self._write_package(root / "after", resources=second_resources)
            )
        report = DIFF.semantic_diff(before, after)
        structure_changes = [
            change
            for change in report["changes"]
            if "/structureDefinitions/" in change["path"]
        ]
        self.assertEqual(len(structure_changes), 1)
        self.assertEqual(structure_changes[0]["kind"], "changed")
        self.assertTrue(structure_changes[0]["path"].endswith("/resource/version"))

    def test_diff_aligns_keyed_fhir_arrays_across_insertions(self) -> None:
        before = {"element": [{"id": "A", "min": 0}, {"id": "B", "min": 1}]}
        after = {
            "element": [
                {"id": "A", "min": 0},
                {"id": "X", "min": 0},
                {"id": "B", "min": 1},
            ]
        }
        changes = DIFF.semantic_diff(before, after)["changes"]
        self.assertEqual(
            changes,
            [
                {
                    "kind": "added",
                    "path": "/element/@id=X",
                    "after": {"id": "X", "min": 0},
                }
            ],
        )

    def test_diff_aligns_value_set_and_reference_graph_insertions(self) -> None:
        edge = {
            "source": "Observation/example",
            "kind": "reference",
            "target": "Patient/example",
            "path": "/subject/reference",
        }
        inserted_edge = {
            "source": "Observation/example",
            "kind": "canonical",
            "target": "https://example.org/Profile",
            "path": "/meta/profile/0",
        }
        before = {
            "include": [{"system": "https://example.org/a"}],
            "referenceGraph": [edge],
        }
        after = {
            "include": [
                {"system": "https://example.org/new"},
                {"system": "https://example.org/a"},
            ],
            "referenceGraph": [inserted_edge, edge],
        }
        changes = DIFF.semantic_diff(before, after)["changes"]
        self.assertEqual(len(changes), 2)
        self.assertEqual({change["kind"] for change in changes}, {"added"})
        self.assertTrue(
            any(
                "@system=https:~1~1example.org~1new" in change["path"]
                for change in changes
            )
        )
        self.assertTrue(any("@edge=" in change["path"] for change in changes))

    def test_diff_reports_baseline_addition_and_removal_deterministically(self) -> None:
        before = {
            "schemaVersion": 1,
            "package": {"name": "example", "version": "1"},
            "examples": {"Observation/old": {"sha256": "a"}},
        }
        after = {
            "schemaVersion": 1,
            "package": {"name": "example", "version": "2"},
            "examples": {"Observation/new": {"sha256": "b"}},
        }
        first = DIFF.semantic_diff(before, after)
        second = DIFF.semantic_diff(deepcopy(before), deepcopy(after))
        self.assertEqual(first, second)
        self.assertEqual(first["summary"], {"added": 1, "removed": 1, "changed": 1, "total": 3})
        self.assertEqual(
            [change["path"] for change in first["changes"]],
            [
                "/examples/Observation~1old",
                "/examples/Observation~1new",
                "/package/version",
            ],
        )


if __name__ == "__main__":
    unittest.main()
