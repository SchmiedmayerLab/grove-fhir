# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from Scripts.fhir_fixture_corpus import build_cases, load_bases, load_manifest


ROOT = Path(__file__).resolve().parent.parent


def load_script(name: str):
    path = ROOT / "Scripts" / name
    specification = importlib.util.spec_from_file_location(name.replace("-", "_"), path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


DOMAIN = load_script("validate-domain-fhir.py")
HEART_RATE = load_script("validate-heart-rate-equivalence.py")
STUDY = load_script("validate-study-graph.py")


class DomainCorpusTests(unittest.TestCase):
    def test_manifests_are_one_mutation_and_expectations_are_exact(self) -> None:
        expected_counts = {"mobile": 61, "healthkit": 14, "health-connect": 30}
        for guide, expected_count in expected_counts.items():
            manifest_path = ROOT / f"Conformance/corpora/{guide}/corpus.json"
            manifest = load_manifest(manifest_path)
            self.assertEqual(len(manifest["cases"]), expected_count)
            self.assertTrue(all(len(case["patch"]) == 1 for case in manifest["cases"]))
            expectations = DOMAIN.load_json(
                ROOT / f"Conformance/corpora/{guide}/validator-expectations.json",
                guide,
            )
            normalized = DOMAIN.validate_expectations(
                expectations, {case["id"] for case in manifest["cases"]}
            )
            self.assertEqual(set(normalized["cases"]), {case["id"] for case in manifest["cases"]})
            self.assertTrue(all(normalized["cases"].values()))

    def test_questionnaire_corpora_are_referenced_not_duplicated(self) -> None:
        index = DOMAIN.load_json(ROOT / "Conformance/corpora/index.json", "index")
        referenced = {item["id"]: item for item in index["referencedCorpora"]}
        self.assertEqual(set(referenced), {"questionnaire-validator", "questionnaire-pairs"})
        self.assertTrue(all(item["ownership"] == "questionnaire" for item in referenced.values()))
        self.assertFalse((ROOT / "Conformance/corpora/questionnaire").exists())

    def test_live_fsh_parser_finds_known_definitions_invariants_and_rules(self) -> None:
        definitions, invariants, rules = DOMAIN.fsh_inventory(
            [ROOT / "mobile/input/fsh/profiles.fsh", ROOT / "mobile/input/fsh/extensions.fsh"]
        )
        self.assertEqual(definitions["GroveMobileObservation"], "grove-mobile-observation")
        self.assertEqual(definitions["GroveRecordingMethod"], "grove-recording-method")
        self.assertIn("grove-mobile-result-1", invariants)
        self.assertIn(
            "RuleSet:GroveMobileObservationRules|* effective[x] only dateTime or Period",
            rules,
        )
        self.assertEqual(len(definitions), 6)
        self.assertEqual(len(invariants), 5)
        self.assertEqual(len(rules), 58)

    def test_live_coverage_inventory_is_complete(self) -> None:
        index = DOMAIN.load_json(ROOT / "Conformance/corpora/index.json", "index")
        reports = DOMAIN.validate_domain_coverage(
            ROOT / "Conformance/corpora/coverage.json",
            DOMAIN.unique_by_id(index["domainCorpora"], "corpora"),
            "6.10.2",
        )
        self.assertEqual(sum(item["structureDefinitionCount"] for item in reports), 9)
        self.assertEqual(sum(item["invariantCount"] for item in reports), 10)
        self.assertEqual(sum(item["computableRuleCount"] for item in reports), 92)
        self.assertEqual(sum(item["validatorLimitationCount"] for item in reports), 1)

    def test_effective_choice_limitation_has_an_effective_custom_witness(self) -> None:
        coverage = DOMAIN.load_json(ROOT / "Conformance/corpora/coverage.json", "coverage")
        limitation = coverage["guides"]["mobile"]["validatorLimitations"][
            "fhir-validator-effective-choice"
        ]
        manifest_path = ROOT / "Conformance/corpora/mobile/corpus.json"
        manifest = load_manifest(manifest_path)
        bases = load_bases(manifest, manifest_path)
        witness = DOMAIN.apply_patch_operation(
            bases[limitation["base"]], limitation["patch"][0]
        )
        self.assertEqual(DOMAIN.mobile_effective_choice_failure(witness), "mobile-effective-choice")

    def test_primitive_cardinality_witnesses_remove_values_and_extensions(self) -> None:
        manifest_path = ROOT / "Conformance/corpora/mobile/corpus.json"
        manifest = load_manifest(manifest_path)
        cases = build_cases(manifest, load_bases(manifest, manifest_path))
        effective = cases["mobile-observation-effective-required"]
        self.assertNotIn("effectiveDateTime", effective)
        self.assertNotIn("_effectiveDateTime", effective)
        missing_start = cases["step-count-period-start-required"]["effectivePeriod"]
        self.assertNotIn("start", missing_start)
        self.assertNotIn("_start", missing_start)
        missing_end = cases["step-count-period-end-required"]["effectivePeriod"]
        self.assertNotIn("end", missing_end)
        self.assertNotIn("_end", missing_end)


class ValidatorOutcomeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.valid = Path("/tmp/valid.json")
        self.invalid = Path("/tmp/invalid.json")
        self.matcher = {
            "code": "structure",
            "expression": "Observation.value[x]",
            "detailsContains": "intended",
        }

    @staticmethod
    def issue(severity: str, text: str, code: str = "structure") -> dict[str, object]:
        return {
            "severity": severity,
            "code": code,
            "expression": ["Observation.value[x]"],
            "details": {"text": text},
        }

    def validate(self, issues: list[dict[str, object]], warnings=None):
        return DOMAIN.validate_outcomes(
            {self.invalid: {"issue": issues}},
            set(),
            {"case": self.invalid},
            {"warningAllowlist": warnings or [], "cases": {"case": [self.matcher]}},
        )[1]

    def test_duplicate_intended_error_is_rejected(self) -> None:
        issue = self.issue("error", "intended")
        self.assertTrue(self.validate([issue, copy.deepcopy(issue)]))

    def test_intended_plus_unrelated_error_is_rejected(self) -> None:
        self.assertTrue(
            self.validate(
                [self.issue("error", "intended"), self.issue("error", "unrelated", "invalid")]
            )
        )

    def test_stale_warning_allowlist_is_rejected(self) -> None:
        failures = self.validate(
            [self.issue("error", "intended")],
            [{"code": "business-rule", "detailsContains": "warning"}],
        )
        self.assertTrue(any("matched no warning" in failure for failure in failures))

    def test_overlapping_warning_allowlist_is_rejected(self) -> None:
        warning = self.issue("warning", "warning", "business-rule")
        matcher = {"code": "business-rule", "detailsContains": "warning"}
        failures = self.validate(
            [self.issue("error", "intended"), warning], [matcher, copy.deepcopy(matcher)]
        )
        self.assertTrue(any("matched 2 allowlist entries" in failure for failure in failures))


class StudyGraphTests(unittest.TestCase):
    def test_every_study_mutation_has_exactly_one_declared_diagnostic(self) -> None:
        manifest_path = ROOT / "Conformance/study-graph/corpus.json"
        manifest = load_manifest(manifest_path)
        bases = load_bases(manifest, manifest_path)
        cases = build_cases(manifest, bases)
        self.assertEqual(len(cases), 15)
        self.assertEqual(list(STUDY.validate_graph(bases["accepted-study-graph"])), [])
        for case in manifest["cases"]:
            self.assertEqual(
                list(STUDY.validate_graph(cases[case["id"]])),
                [case["expectedRule"]],
                case["id"],
            )


class HeartRateEquivalenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.specification_path = ROOT / "Conformance/semantic-equivalence/heart-rate.json"
        cls.specification = HEART_RATE._object(
            HEART_RATE._load_json(cls.specification_path), "specification"
        )

    def static_graph(self, index: int = 0):
        item = self.specification["staticInputs"][index]
        observation = HEART_RATE._repository_input(
            self.specification_path, item["observation"], "observation"
        )
        provenance = HEART_RATE._repository_input(
            self.specification_path, item["provenance"], "provenance"
        )
        return item, HEART_RATE._graph_from_paths(observation, provenance, None)

    def test_static_platforms_are_equivalent_and_gateway_evidenced(self) -> None:
        results = HEART_RATE.validate_specification(self.specification_path)
        self.assertEqual(len(results["static"]), 2)
        self.assertTrue(
            all(item["gatewayExpectation"] == "required" for item in self.specification["staticInputs"])
        )
        self.assertTrue(
            all(
                item["gatewayExpectation"] == "absent-in-export"
                for item in self.specification["implementationInputs"]
            )
        )
        self.assertEqual(
            {item["id"] for item in self.specification["implementationInputs"]},
            {"grove-current-resources", "my-heart-counts-android-conformance"},
        )
        self.assertEqual(
            self.specification["externalDirectoryContract"],
            "evidence-lock-exact-allowlist",
        )

    def test_excluded_identity_and_timestamp_changes_do_not_prove_equivalence(self) -> None:
        item, graph = self.static_graph()
        expected = HEART_RATE.project(
            graph, self.specification["clinicalProfile"], item["adapterProfile"]
        )
        observation = copy.deepcopy(graph.observation)
        observation["id"] = "different-platform-id"
        observation["subject"]["identifier"]["value"] = "different-participant"
        observation["effectiveDateTime"] = "2025-01-02T03:04:05Z"
        observation["issued"] = "2025-01-02T03:04:06Z"
        changed = HEART_RATE.FixtureGraph(observation, graph.provenance, graph.bundle)
        self.assertEqual(
            HEART_RATE.project(
                changed, self.specification["clinicalProfile"], item["adapterProfile"]
            ),
            expected,
        )

    def test_subject_type_must_agree_with_reference(self) -> None:
        item, graph = self.static_graph()
        observation = copy.deepcopy(graph.observation)
        observation["subject"] = {"type": "Patient", "reference": "Group/not-a-patient"}
        with self.assertRaises(HEART_RATE.EquivalenceError):
            HEART_RATE.project(
                HEART_RATE.FixtureGraph(observation, graph.provenance, graph.bundle),
                self.specification["clinicalProfile"],
                item["adapterProfile"],
            )

    def test_quantity_comparator_changes_clinical_semantics(self) -> None:
        item, graph = self.static_graph()
        observation = copy.deepcopy(graph.observation)
        observation["valueQuantity"]["comparator"] = "<"
        projection = HEART_RATE.project(
            HEART_RATE.FixtureGraph(observation, graph.provenance, graph.bundle),
            self.specification["clinicalProfile"],
            item["adapterProfile"],
        )
        self.assertEqual(projection["valueQuantity"]["comparator"], "<")
        self.assertNotEqual(projection, self.specification["expectedProjection"])

    def test_required_gateway_removal_is_rejected(self) -> None:
        item, graph = self.static_graph()
        observation = copy.deepcopy(graph.observation)
        observation["extension"] = [
            extension
            for extension in observation.get("extension", [])
            if extension.get("url") != self.specification["roles"]["gatewayExtension"]
        ]
        with self.assertRaises(HEART_RATE.EquivalenceError):
            HEART_RATE.validate_roles(
                HEART_RATE.FixtureGraph(observation, graph.provenance, graph.bundle),
                item,
                self.specification["roles"],
            )

    def test_reference_identifier_must_agree_with_resolved_target(self) -> None:
        item, graph = self.static_graph(1)
        provenance = copy.deepcopy(graph.provenance)
        provenance["agent"][0]["who"]["identifier"]["value"] = "contradictory-device"
        with self.assertRaisesRegex(HEART_RATE.EquivalenceError, "contradicts"):
            HEART_RATE.validate_roles(
                HEART_RATE.FixtureGraph(graph.observation, provenance, graph.bundle),
                item,
                self.specification["roles"],
            )

    def test_external_evidence_root_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            real = root / "real"
            real.mkdir()
            link = root / "link"
            link.symlink_to(real, target_is_directory=True)
            with self.assertRaises(HEART_RATE.EquivalenceError):
                HEART_RATE._parse_external_evidence([f"fixture={link}"])


class ReceiverEvidenceTests(unittest.TestCase):
    @classmethod
    def node_environment(cls):
        environment = os.environ.copy()
        probe = subprocess.run(
            ["node", "-e", "require('ajv/dist/2020')"],
            cwd=ROOT,
            env=environment,
            capture_output=True,
        )
        if probe.returncode != 0:
            raise unittest.SkipTest("direct Ajv 2020 dependency is not installed")
        return environment

    def test_envelope_schema_has_exactly_five_fields(self) -> None:
        schema = json.loads(
            (ROOT / "Conformance/receiver-envelope/envelope.schema.json").read_text()
        )
        expected = {"operation", "sourceIdentifier", "sourceVersion", "eventSequence", "bundleJson"}
        self.assertEqual(set(schema["required"]), expected)
        self.assertEqual(set(schema["properties"]), expected)
        self.assertFalse(schema["additionalProperties"])

    def test_lifecycle_gate_includes_exact_frozen_metadata_and_limits(self) -> None:
        fixture = json.loads(
            (ROOT / "Conformance/receiver-envelope/lifecycle-cases.json").read_text()
        )
        self.assertEqual(fixture["modelScope"]["outputOwnership"], "partition-local")
        events = {
            event["id"]: event
            for stream in fixture["externalEvidence"]["streams"]
            for event in stream["events"]
        }
        self.assertEqual(events["frozen-step-deletion"]["eventSequence"], "5")
        self.assertEqual(
            sorted(event["bundleSize"] for event in events.values()),
            sorted([7178, 6899, 3433, 5246]),
        )
        self.assertTrue(all(len(event["bundleSha256"]) == 64 for event in events.values()))
        boundary_bytes = {
            (case["field"], case["reason"]): case["expectedBytes"]
            for case in fixture["byteBoundaryCases"]
        }
        self.assertEqual(
            boundary_bytes,
            {
                ("sourceIdentifier.system", None): 2048,
                ("sourceIdentifier.system", "source-identifier-system-bytes"): 2050,
                ("sourceIdentifier.value", None): 4096,
                ("sourceIdentifier.value", "source-identifier-value-bytes"): 4098,
                ("bundleJson.code.text", None): 16 * 1024 * 1024,
                ("bundleJson.code.text", "bundle-json-bytes"): 16 * 1024 * 1024 + 2,
            },
        )

    def test_receiver_gate_runs_with_direct_ajv(self) -> None:
        result = subprocess.run(
            ["node", "Scripts/validate-receiver-evidence.cjs"],
            cwd=ROOT,
            env=self.node_environment(),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("4 collection-limit assertions", result.stdout)

    def test_receiver_rejects_non_regular_external_tree_and_symlink_root(self) -> None:
        environment = self.node_environment()
        filenames = [
            "health-connect-heart-rate-upsert-bundle.json",
            "health-connect-heart-rate-update-bundle.json",
            "health-connect-heart-rate-zero-output-upsert-bundle.json",
            "health-connect-step-deletion-bundle.json",
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root / "evidence"
            evidence.mkdir()
            for filename in filenames:
                (evidence / filename).write_text("{}", encoding="utf-8")
            (evidence / "extra-directory").mkdir()
            command = [
                "node",
                "Scripts/validate-receiver-evidence.cjs",
                "--external-evidence",
                f"my-heart-counts-android-wire={evidence}",
                "--require-external-evidence",
            ]
            result = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("non-regular entries", result.stderr)
            link = root / "evidence-link"
            link.symlink_to(evidence, target_is_directory=True)
            command[3] = f"my-heart-counts-android-wire={link}"
            result = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("may not traverse a symlink", result.stderr)


class ExternalEvidenceInventoryTests(unittest.TestCase):
    @staticmethod
    def unknown_extension_expectation(path: str = "resource.json") -> dict[str, str]:
        return {
            "path": path,
            "expression": "Observation.extension[0]",
            "url": "https://legacy.example/fhir/extension",
            "valueField": "valueString",
        }

    def test_legacy_extension_shape_and_diagnostic_are_exact(self) -> None:
        expectation = self.unknown_extension_expectation()
        resource = {
            "resourceType": "Observation",
            "extension": [
                {
                    "url": expectation["url"],
                    "valueString": "legacy",
                }
            ],
        }
        self.assertEqual(
            DOMAIN.unknown_extension_shape(resource, "resource.json"),
            [expectation],
        )
        issue = {
            "severity": "error",
            "code": "structure",
            "expression": [expectation["expression"]],
            "details": {
                "text": f"The extension {expectation['url']} could not be found so is not allowed here"
            },
            "extension": [
                {
                    "url": DOMAIN.MESSAGE_ID_URL,
                    "valueCode": "Extension_EXT_Unknown_NotHere",
                }
            ],
        }
        self.assertTrue(
            DOMAIN.expected_unknown_extension_issue_matches(issue, expectation)
        )
        changed_issue = copy.deepcopy(issue)
        changed_issue["details"]["text"] += " (changed)"
        self.assertFalse(
            DOMAIN.expected_unknown_extension_issue_matches(changed_issue, expectation)
        )
        changed_resource = copy.deepcopy(resource)
        changed_resource["extension"][0]["valueInteger"] = 1
        del changed_resource["extension"][0]["valueString"]
        self.assertNotEqual(
            DOMAIN.unknown_extension_shape(changed_resource, "resource.json"),
            [expectation],
        )

    def test_validator_outcome_bundle_rejects_malformed_extra_entries(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "resource.json"
            outcome = Path(directory) / "outcome.json"
            outcome.write_text(
                json.dumps(
                    {
                        "resourceType": "Bundle",
                        "entry": [
                            {
                                "resource": {
                                    "resourceType": "OperationOutcome",
                                    "extension": [
                                        {
                                            "url": DOMAIN.FILE_URL,
                                            "valueString": str(source),
                                        }
                                    ],
                                    "issue": [],
                                }
                            },
                            {"fullUrl": "urn:uuid:malformed-extra"},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                DOMAIN.DomainValidationError, "malformed entry"
            ):
                DOMAIN.operation_outcomes(outcome)

    def test_manifest_declares_only_the_two_exact_legacy_contracts(self) -> None:
        manifest = DOMAIN.load_json(ROOT / "Conformance/evidence.json", "evidence")
        declarations = {
            item["id"]: item for item in manifest["externalEvidence"]
        }
        contracts = {
            identifier: declaration["expectedUnknownExtensions"]
            for identifier, declaration in declarations.items()
            if "expectedUnknownExtensions" in declaration
        }
        self.assertEqual(
            {identifier: len(contract) for identifier, contract in contracts.items()},
            {
                "grove-legacy-healthkit-sample": 15,
                "mhc-ios-study-enrollment": 3,
            },
        )
        self.assertTrue(
            all(
                item["url"].startswith("https://bdh.stanford.edu/fhir/defs/")
                for item in contracts["grove-legacy-healthkit-sample"]
            )
        )
        self.assertTrue(
            all(
                item["url"].startswith(
                    "https://myheartcounts.stanford.edu/fhir/StructureDefinition/study-enrollment"
                )
                for item in contracts["mhc-ios-study-enrollment"]
            )
        )

    def test_legacy_contract_is_required_and_propagated_to_the_report(self) -> None:
        expectation = self.unknown_extension_expectation()
        declaration = {
            "id": "legacy",
            "classification": "historical-writer",
            "kind": "file",
            "files": [{"path": "resource.json", "format": "fhir-json"}],
            "expectedUnknownExtensions": [expectation],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "resource.json"
            path.write_text(
                json.dumps(
                    {
                        "resourceType": "Observation",
                        "extension": [
                            {
                                "url": expectation["url"],
                                "valueString": "legacy",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            reports, files, expectations = DOMAIN.resolve_external_evidence(
                {"externalEvidence": [declaration]}, {"legacy": path}, True
            )
            self.assertEqual(len(files), 1)
            self.assertEqual(
                expectations[("legacy", "resource.json")], [expectation]
            )
            self.assertEqual(reports[0]["validationScope"], "r4-core")
            self.assertEqual(reports[0]["expectedErrorCount"], 1)
            self.assertEqual(reports[0]["files"][0]["expectedErrorCount"], 1)

            missing = copy.deepcopy(declaration)
            del missing["expectedUnknownExtensions"]
            with self.assertRaisesRegex(
                DOMAIN.DomainValidationError, "needs expectedUnknownExtensions"
            ):
                DOMAIN.resolve_external_evidence(
                    {"externalEvidence": [missing]}, {"legacy": path}, True
                )

    def test_external_validator_partitions_accepted_and_legacy_scopes(self) -> None:
        expectation = self.unknown_extension_expectation("legacy.json")
        evidence = {
            "externalEvidence": [
                {
                    "id": "accepted",
                    "classification": "accepted-contract",
                    "kind": "file",
                    "files": [{"path": "accepted.json", "format": "fhir-json"}],
                },
                {
                    "id": "legacy",
                    "classification": "legacy-candidate",
                    "kind": "file",
                    "files": [{"path": "legacy.json", "format": "fhir-json"}],
                    "expectedUnknownExtensions": [expectation],
                },
            ]
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            accepted = root / "accepted.json"
            legacy = root / "legacy.json"
            accepted.write_text('{"resourceType":"Patient"}', encoding="utf-8")
            legacy.write_text(
                json.dumps(
                    {
                        "resourceType": "Observation",
                        "extension": [
                            {
                                "url": expectation["url"],
                                "valueString": "legacy",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            set_reports, files, expectations = DOMAIN.resolve_external_evidence(
                evidence,
                {"accepted": accepted, "legacy": legacy},
                True,
            )
            commands: list[list[str]] = []
            extra_legacy_issues: list[object] = []

            def validator_run(command, **_kwargs):
                commands.append(command)
                output = Path(command[command.index("-output") + 1])
                inputs = command[command.index("-jar") + 2 : command.index("-version")]
                self.assertEqual(len(inputs), 1)
                source = Path(inputs[0]).resolve()
                issues = []
                returncode = 0
                if source == legacy.resolve():
                    returncode = 1
                    issues = [
                        {
                            "severity": "error",
                            "code": "structure",
                            "expression": [expectation["expression"]],
                            "details": {
                                "text": f"The extension {expectation['url']} could not be found so is not allowed here"
                            },
                            "extension": [
                                {
                                    "url": DOMAIN.MESSAGE_ID_URL,
                                    "valueCode": "Extension_EXT_Unknown_NotHere",
                                }
                            ],
                        }
                    ]
                    issues.extend(extra_legacy_issues)
                output.write_text(
                    json.dumps(
                        {
                            "resourceType": "OperationOutcome",
                            "extension": [
                                {
                                    "url": DOMAIN.FILE_URL,
                                    "valueString": str(source),
                                }
                            ],
                            "issue": issues,
                        }
                    ),
                    encoding="utf-8",
                )
                return subprocess.CompletedProcess(command, returncode, "", "")

            with mock.patch.object(DOMAIN.subprocess, "run", side_effect=validator_run):
                report, failures = DOMAIN.validate_external_fhir(
                    files,
                    set_reports,
                    expectations,
                    {"guide": root / "guide.tgz"},
                    root / "validator.jar",
                    root / "validator-home",
                    root,
                )

            self.assertEqual(failures, [])
            self.assertEqual(report["expectedErrorCount"], 1)
            self.assertEqual(len(commands), 2)
            self.assertIn("-ig", commands[0])
            self.assertNotIn("-ig", commands[1])
            self.assertIn("accepted.json", " ".join(commands[0]))
            self.assertIn("legacy.json", " ".join(commands[1]))

            extra_legacy_issues.append(None)
            with mock.patch.object(DOMAIN.subprocess, "run", side_effect=validator_run):
                _report, malformed_failures = DOMAIN.validate_external_fhir(
                    files,
                    set_reports,
                    expectations,
                    {"guide": root / "guide.tgz"},
                    root / "validator.jar",
                    root / "validator-home",
                    root,
                )
            self.assertTrue(
                any("malformed issue" in failure for failure in malformed_failures)
            )

    def test_package_override_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "package.tgz"
            package.write_bytes(b"package")
            link = root / "package-link.tgz"
            link.symlink_to(package)
            with self.assertRaises(DOMAIN.DomainValidationError):
                DOMAIN.parse_overrides([f"mobile={link}"])

    def test_exact_tree_and_symlink_root_are_fail_closed(self) -> None:
        evidence = {
            "externalEvidence": [
                {
                    "id": "fixture",
                    "classification": "accepted-contract",
                    "kind": "directory",
                    "files": [
                        {"path": "resource.json", "format": "fhir-json"},
                        {"path": "validation.txt", "format": "validator-transcript"},
                    ],
                }
            ]
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "resource.json").write_text('{"resourceType":"Patient"}', encoding="utf-8")
            (root / "validation.txt").write_text("ok", encoding="utf-8")
            reports, files, expectations = DOMAIN.resolve_external_evidence(
                evidence, {"fixture": root}, True
            )
            self.assertEqual(len(reports), 1)
            self.assertEqual(len(files), 1)
            self.assertEqual(expectations, {})
            (root / "extra").mkdir()
            with self.assertRaises(DOMAIN.DomainValidationError):
                DOMAIN.resolve_external_evidence(evidence, {"fixture": root}, True)
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            real = parent / "real"
            real.mkdir()
            link = parent / "link"
            link.symlink_to(real, target_is_directory=True)
            with self.assertRaises(DOMAIN.DomainValidationError):
                DOMAIN.parse_external_evidence([f"fixture={link}"])


if __name__ == "__main__":
    unittest.main()
