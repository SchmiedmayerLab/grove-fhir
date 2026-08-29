"""Verify the Questionnaire package, fixture corpora, and paired validator."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "questionnaire/output"
GENERATED = ROOT / "questionnaire/fsh-generated/resources"
VALIDATOR_FIXTURES = ROOT / "questionnaire/fixtures/validator"
PAIR_FIXTURES = ROOT / "questionnaire/fixtures/pairs"
QUESTIONNAIRE_CANONICAL = (
    "https://grovealliance.org/fhir/questionnaire/"
    "Questionnaire/GroveWeeklySymptomCheckInExample"
)

sys.path.insert(0, str(ROOT / "Scripts"))
from questionnaire_fixture_corpus import apply_mutation, load_json, write_json  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "validate_questionnaire", ROOT / "Scripts/validate-questionnaire.py"
)
if spec is None or spec.loader is None:
    raise RuntimeError("Cannot load Questionnaire validator")
validator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = validator
spec.loader.exec_module(validator)

fhir_spec = importlib.util.spec_from_file_location(
    "validate_questionnaire_fhir", ROOT / "Scripts/validate-questionnaire-fhir.py"
)
if fhir_spec is None or fhir_spec.loader is None:
    raise RuntimeError("Cannot load Questionnaire FHIR validator")
fhir_validator = importlib.util.module_from_spec(fhir_spec)
sys.modules[fhir_spec.name] = fhir_validator
fhir_spec.loader.exec_module(fhir_validator)


def import_exchange_protocol():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "grove_exchange_protocol", ROOT / "Scripts/exchange_protocol.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_extraction(name: str) -> dict:
    """Read one committed artifact of the worked extraction example."""
    path = ROOT / "questionnaire/fixtures/extraction" / name
    return json.loads(path.read_text(encoding="utf-8"))


def load_generated(filename: str) -> dict:
    path = GENERATED / filename
    if not path.is_file():
        raise unittest.SkipTest("Questionnaire SUSHI output is not present")
    return json.loads(path.read_text(encoding="utf-8"))


class QuestionnaireContractTests(unittest.TestCase):
    def test_official_validator_fails_closed_on_malformed_or_crashed_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            validator_path = root / "validator.jar"
            package_path = root / "package.tgz"
            resource_path = root / "questionnaire.json"
            outcome_path = root / "outcome.json"
            fhir_home = root / "fhir-home"
            validator_path.write_bytes(b"validator")
            package_path.write_bytes(b"package")
            resource_path.write_text(
                '{"resourceType":"Questionnaire"}\n', encoding="utf-8"
            )
            fhir_home.mkdir()

            def malformed(
                command: list[str], **_: object
            ) -> subprocess.CompletedProcess[str]:
                output = Path(command[command.index("-output") + 1])
                output.write_text("{}\n", encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

            with mock.patch.object(
                fhir_validator.subprocess, "run", side_effect=malformed
            ) as run:
                with self.assertRaisesRegex(RuntimeError, "not an OperationOutcome"):
                    fhir_validator.validate_one(
                        validator_path,
                        package_path,
                        resource_path,
                        outcome_path,
                        False,
                        fhir_home,
                    )
                self.assertEqual(run.call_count, 2)

            def crashed(
                command: list[str], **_: object
            ) -> subprocess.CompletedProcess[str]:
                output = Path(command[command.index("-output") + 1])
                output.write_text(
                    json.dumps(
                        {
                            "resourceType": "OperationOutcome",
                            "issue": [
                                {
                                    "severity": "information",
                                    "code": "informational",
                                }
                            ],
                        }
                    ),
                    encoding="utf-8",
                )
                return subprocess.CompletedProcess(
                    command, 2, stdout="", stderr="validator crashed"
                )

            with mock.patch.object(
                fhir_validator.subprocess, "run", side_effect=crashed
            ) as run:
                with self.assertRaisesRegex(RuntimeError, "unexpected exit code"):
                    fhir_validator.validate_one(
                        validator_path,
                        package_path,
                        resource_path,
                        outcome_path,
                        False,
                        fhir_home,
                    )
                self.assertEqual(run.call_count, 2)

            with mock.patch.object(
                fhir_validator.subprocess,
                "run",
                side_effect=subprocess.TimeoutExpired(
                    cmd=["java"],
                    timeout=fhir_validator.VALIDATOR_TIMEOUT_SECONDS,
                    output=b"partial validator log",
                ),
            ) as run:
                with self.assertRaisesRegex(RuntimeError, "timed out after 180 seconds"):
                    fhir_validator.validate_one(
                        validator_path,
                        package_path,
                        resource_path,
                        outcome_path,
                        False,
                        fhir_home,
                    )
                self.assertEqual(run.call_count, 2)

    def test_official_validator_accepts_a_trustworthy_negative_outcome(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            resource_path = root / "questionnaire.json"
            outcome_path = root / "outcome.json"
            resource_path.write_text(
                '{"resourceType":"Questionnaire"}\n', encoding="utf-8"
            )

            def rejected(
                command: list[str], **_: object
            ) -> subprocess.CompletedProcess[str]:
                output = Path(command[command.index("-output") + 1])
                output.write_text(
                    json.dumps(
                        {
                            "resourceType": "OperationOutcome",
                            "issue": [
                                {
                                    "severity": "error",
                                    "code": "invariant",
                                    "diagnostics": "expected rejection",
                                }
                            ],
                        }
                    ),
                    encoding="utf-8",
                )
                return subprocess.CompletedProcess(command, 1, stdout="", stderr="")

            with mock.patch.object(
                fhir_validator.subprocess, "run", side_effect=rejected
            ) as run:
                errors, _ = fhir_validator.validate_one(
                    root / "validator.jar",
                    root / "package.tgz",
                    resource_path,
                    outcome_path,
                    False,
                    root / "fhir-home",
                )
            self.assertEqual([issue["diagnostics"] for issue in errors], ["expected rejection"])
            self.assertEqual(run.call_count, 1)

    def test_fixture_writer_preserves_exact_decimal_values(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source.json"
            destination = Path(temporary) / "destination.json"
            source.write_text('{"valueDecimal":1.20}\n', encoding="utf-8")

            write_json(destination, load_json(source))

            self.assertEqual(destination.read_bytes(), b'{"valueDecimal":1.20}\n')

    def test_official_corpus_paths_cannot_escape_or_traverse_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            corpus = root / "corpus"
            corpus.mkdir()
            valid = corpus / "valid.json"
            valid.write_text("{}\n", encoding="utf-8")
            outside = root / "outside.json"
            outside.write_text("{}\n", encoding="utf-8")
            (corpus / "linked.json").symlink_to(outside)

            self.assertEqual(
                fhir_validator.resolve_corpus_file(
                    corpus, "valid.json", "Questionnaire fixture"
                ),
                valid,
            )
            with self.assertRaisesRegex(ValueError, "safe relative POSIX path"):
                fhir_validator.resolve_corpus_file(
                    corpus, "../outside.json", "Questionnaire fixture"
                )
            with self.assertRaisesRegex(ValueError, "may not traverse a symlink"):
                fhir_validator.resolve_corpus_file(
                    corpus, "linked.json", "Questionnaire fixture"
                )

    def test_extraction_example_matches_the_measurement_catalog(self) -> None:
        """The worked example is only useful while it still agrees with the catalog.

        An instrument states the codes and units its answers carry; the measurement catalog
        states what the projected Observation must carry. Nothing else compares the two, so a
        catalog edit would otherwise leave the example quietly wrong.
        """
        instrument = load_extraction("questionnaire.json")
        response = load_extraction("questionnaire-response.json")
        catalog = json.loads(
            (ROOT / "catalog/measurement-catalog.json").read_text(encoding="utf-8")
        )
        measurements = {entry["id"]: entry for entry in catalog["measurements"]}
        extract = "http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire-observationExtract"
        category = (
            "http://hl7.org/fhir/uv/sdc/StructureDefinition/"
            "sdc-questionnaire-observation-extract-category"
        )

        def extension(node: dict, url: str) -> dict | None:
            return next((e for e in node.get("extension", []) if e["url"] == url), None)

        def item(items: list, link_id: str) -> dict:
            found = next((i for i in items if i["linkId"] == link_id), None)
            self.assertIsNotNone(found, f"{link_id} is missing from the example")
            return found

        # A scalar measurement extracts on its own, carrying the catalog's code and category.
        weight_item = item(instrument["item"], "body-weight")
        self.assertTrue(extension(weight_item, extract)["valueBoolean"])
        weight = measurements["body-weight"]
        self.assertEqual(
            weight_item["code"][0]["code"], weight["code"]["code"]
        )
        self.assertEqual(
            extension(weight_item, category)["valueCodeableConcept"]["coding"][0]["code"],
            weight["category"]["code"],
        )

        # A component measurement extracts as one panel: the parent carries the panel code and
        # each child names itself a component, so both readings land on one Observation.
        panel_item = item(instrument["item"], "blood-pressure")
        pressure = measurements["blood-pressure"]
        self.assertTrue(extension(panel_item, extract)["valueBoolean"])
        self.assertEqual(panel_item["code"][0]["code"], pressure["code"]["code"])
        components = {component["id"]: component for component in pressure["components"]}
        for link_id, component_id in (("systolic", "systolic"), ("diastolic", "diastolic")):
            child = item(panel_item["item"], link_id)
            self.assertEqual(extension(child, extract)["valueCode"], "component")
            self.assertEqual(child["code"][0]["code"], components[component_id]["code"])

        # The response answers every extracting item, in the unit its measurement fixes.
        answered = item(response["item"], "body-weight")["answer"][0]["valueQuantity"]
        self.assertEqual(answered["code"], weight["quantity"]["code"])
        self.assertEqual(answered["system"], weight["quantity"]["system"])
        panel_answers = item(response["item"], "blood-pressure")["item"]
        for link_id in ("systolic", "diastolic"):
            quantity = item(panel_answers, link_id)["answer"][0]["valueQuantity"]
            self.assertEqual(quantity["code"], components[link_id]["quantity"]["code"])
            self.assertEqual(quantity["system"], components[link_id]["quantity"]["system"])

        # A projection needs the capturing application, which the response states as plain facts.
        writer = extension(
            response,
            "https://grovealliance.org/fhir/questionnaire/StructureDefinition/"
            "grove-questionnaire-writer-context",
        )
        self.assertIsNotNone(writer, "the response carries no writer context")
        carried = {part["url"] for part in writer["extension"]}
        self.assertLessEqual(
            {"applicationIdentifier", "applicationName", "applicationVersion"}, carried
        )


    def test_committed_extraction_fixtures_match_the_built_guide(self) -> None:
        """The committed pair is what the chain is checked against, so it must be the real one.

        The chain tests read fixtures rather than SUSHI output, so they run wherever the suite
        runs. That only holds if the fixtures are the guide's own artifacts, which this compares
        whenever a build is present.
        """
        for fixture, generated in (
            ("questionnaire.json", "Questionnaire-GroveHomeVitalsExample.json"),
            ("questionnaire-response.json", "QuestionnaireResponse-GroveHomeVitalsResponseExample.json"),
        ):
            with self.subTest(fixture=fixture):
                self.assertEqual(
                    load_extraction(fixture),
                    load_generated(generated),
                    f"{fixture} has drifted from the built guide; copy it again",
                )

    def test_exchange_bundle_passes_the_producer_conformance_validator(self) -> None:
        """Hand-checking an envelope is not the same as passing the real validator.

        This runs the repository's own exchange-bundle validation over the worked example,
        so the entry keys, the reference closure, the lifecycle Provenance, and the
        one-source-record rule are enforced by the code that governs every other producer.
        """
        from Scripts.producer_validation.exchange_bundle import validate_exchange_bundle

        bundle = json.loads(
            (ROOT / "questionnaire/fixtures/extraction/exchange-bundle.json").read_text(
                encoding="utf-8"
            )
        )
        validate_exchange_bundle(bundle, "questionnaire extraction example")

    def test_bound_times_carry_the_value_their_binding_declares(self) -> None:
        """A bound time is only useful if it is the right time.

        Asserting merely that a bound Observation avoids `authored` would pass on any wrong
        instant. These check the two declared bindings against what the response actually says:
        the panel takes the answered reading time, and the step count takes the day its wording
        names, computed from `authored` rather than typed by anyone.
        """
        from datetime import date, timedelta

        response = load_extraction("questionnaire-response.json")
        pressure = load_extraction("blood-pressure.json")
        steps = load_extraction("step-count.json")
        authored = response["authored"]
        offset = authored[-6:]

        def answered(items: list, link_id: str) -> dict:
            for item in items:
                if item["linkId"] == link_id:
                    return item
                found = answered(item.get("item", []), link_id)
                if found:
                    return found
            return {}

        # The panel's instant is the answer to its own measurement-time question.
        measured = answered(response["item"], "measured-at")["answer"][0]["valueDateTime"]
        self.assertEqual(pressure["effectiveDateTime"], measured)
        self.assertNotEqual(pressure["effectiveDateTime"], authored)

        # "Yesterday" is the day before the response was authored, in the response's own offset.
        day = date.fromisoformat(authored[:10])
        self.assertEqual(
            steps["effectivePeriod"]["start"], f"{day - timedelta(days=1)}T00:00:00{offset}"
        )
        self.assertEqual(steps["effectivePeriod"]["end"], f"{day}T00:00:00{offset}")
        self.assertNotIn("effectiveDateTime", steps)

        # The weight declares no binding, so it still takes the moment of answering.
        self.assertEqual(load_extraction("body-weight.json")["effectiveDateTime"], authored)

    def test_extraction_ships_a_conformant_exchange_bundle(self) -> None:
        """A projection ships a Bundle, so the worked example has to be one.

        The envelope carries the event identity and the entry keys, and every literal
        reference has to land on an entry in the same Bundle. A loose Observation would
        satisfy neither, and would misrepresent what a receiving system actually gets.
        """
        bundle = json.loads(
            (ROOT / "questionnaire/fixtures/extraction/exchange-bundle.json").read_text(
                encoding="utf-8"
            )
        )
        module = import_exchange_protocol()

        self.assertEqual(bundle["type"], "collection")
        self.assertEqual(
            bundle["identifier"]["type"]["coding"][0]["code"], "event"
        )
        self.assertRegex(bundle["identifier"]["value"], module.EVENT_IDENTITY)
        self.assertIn("timestamp", bundle)

        node_key = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-exchange-entry-node-key"
        urls = set()
        priority = ("source-output", "source-artifact", "source-record", "writer-record",
                    "device-snapshot", "recording-device")
        for entry in bundle["entry"]:
            key = next(e for e in entry["extension"] if e["url"] == node_key)["valueIdentifier"]
            # An entry keys off its own highest-priority typed identity, and falls back to a
            # canonical entry-node key only when the resource carries no typed identity.
            resource = entry["resource"]
            raw = resource.get("identifier") or []
            carried = raw if isinstance(raw, list) else [raw]
            roles = {
                coding["code"]
                for identifier in carried
                if isinstance(identifier, dict)
                for coding in (identifier.get("type") or {}).get("coding") or []
                if coding.get("system", "").endswith("grove-identifier-role")
            }
            expected = next((role for role in priority if role in roles), "entry-node")
            self.assertEqual(key["type"]["coding"][0]["code"], expected)
            self.assertEqual(
                entry["fullUrl"],
                module.entry_full_url(key["system"], key["value"]),
                "fullUrl is derived from the entry node key",
            )
            urls.add(entry["fullUrl"])
        self.assertEqual(len(urls), len(bundle["entry"]), "entry fullUrls are distinct")

        present = [entry["resource"]["resourceType"] for entry in bundle["entry"]]
        for required in ("Patient", "QuestionnaireResponse", "Device", "Observation", "Provenance"):
            self.assertIn(required, present)
        self.assertEqual(present.count("Provenance"), 1, "exactly one conversion Provenance")
        self.assertEqual(present.count("Observation"), 3)

        # Literal closure: a reference that leaves the Bundle cannot be resolved by a receiver.
        def references(node: object) -> list:
            if isinstance(node, dict):
                found = []
                for key, value in node.items():
                    if key == "reference" and isinstance(value, str):
                        found.append(value)
                    else:
                        found.extend(references(value))
                return found
            if isinstance(node, list):
                return [r for value in node for r in references(value)]
            return []

        for reference in references(bundle["entry"]):
            self.assertIn(reference, urls, f"{reference} does not resolve inside the Bundle")

        provenance = next(
            entry["resource"] for entry in bundle["entry"]
            if entry["resource"]["resourceType"] == "Provenance"
        )
        self.assertEqual(
            provenance["meta"]["profile"],
            ["https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-conversion-provenance"],
        )
        self.assertEqual(provenance["agent"][0]["type"]["coding"][0]["code"], "assembler")
        targets = {t["reference"] for t in provenance["target"]}
        observations = {
            entry["fullUrl"] for entry in bundle["entry"]
            if entry["resource"]["resourceType"] == "Observation"
        }
        self.assertEqual(targets, observations, "the Provenance targets every projected output")

    def test_writer_context_reaches_the_projected_device_snapshots(self) -> None:
        """Carrying the capturing application only matters if it arrives somewhere.

        Every field the response states about the writer is checked into the Device snapshots
        the projection builds, and the Observations are checked to reference them, so the
        context cannot quietly stop at the response.
        """
        response = load_extraction("questionnaire-response.json")
        directory = ROOT / "questionnaire/fixtures/extraction"
        application = json.loads((directory / "application-device.json").read_text(encoding="utf-8"))
        host = json.loads((directory / "host-device.json").read_text(encoding="utf-8"))

        writer = next(
            e
            for e in response["extension"]
            if e["url"].endswith("grove-questionnaire-writer-context")
        )
        stated = {part["url"]: part for part in writer["extension"]}

        def version(device: dict, code: str) -> str:
            entry = next(
                v for v in device["version"] if v["type"]["coding"][0]["code"] == code
            )
            return entry["value"]

        # The application snapshot repeats what the response stated, and nothing else.
        self.assertEqual(
            application["deviceName"][0]["name"], stated["applicationName"]["valueString"]
        )
        self.assertEqual(version(application, "531975"), stated["applicationVersion"]["valueString"])
        self.assertEqual(version(application, "build"), stated["applicationBuild"]["valueString"])
        declared = stated["applicationIdentifier"]["valueIdentifier"]
        self.assertIn(
            {"system": declared["system"], "value": declared["value"]},
            [
                {"system": i.get("system"), "value": i.get("value")}
                for i in application["identifier"]
            ],
        )

        # The host snapshot hangs off the application snapshot and carries the host facts.
        self.assertEqual(application["parent"]["reference"], f"Device/{host['id']}")
        self.assertEqual(host["modelNumber"], stated["hostModel"]["valueString"])
        self.assertEqual(
            version(host, "os-version"), stated["hostOperatingSystemVersion"]["valueString"]
        )

        # Both projected Observations point at the application snapshot as their gateway.
        gateway = "http://hl7.org/fhir/StructureDefinition/observation-gatewayDevice"
        for name in ("body-weight.json", "blood-pressure.json"):
            observation = json.loads((directory / name).read_text(encoding="utf-8"))
            reference = next(
                e for e in observation["extension"] if e["url"] == gateway
            )["valueReference"]["reference"]
            self.assertEqual(reference, f"Device/{application['id']}")

    def test_worked_example_pair_validates_against_its_own_instrument(self) -> None:
        """The response has to be a legal answer to this instrument, not merely a legal response.

        Profile validation checks the response in isolation. The paired validator is what
        catches an answer at a linkId the instrument never declared, or in a unit it never
        offered, which is exactly what a projection would then carry into an Observation.
        """
        fixtures = ROOT / "questionnaire/fixtures/extraction"
        instrument = fixtures / "questionnaire.json"
        response = fixtures / "questionnaire-response.json"
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "Scripts/validate-questionnaire.py"),
                "--questionnaire",
                str(instrument),
                "--response",
                str(response),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            completed.returncode, 0, f"the worked pair does not validate: {completed.stdout}"
        )

    def test_documentation_shows_the_example_it_claims_to_show(self) -> None:
        """A snippet that has drifted from the example teaches the wrong thing.

        Every instrument line the page prints is checked back against the authored FSH, and
        the values it states for the extracted Observations are checked against the fixtures.
        """
        page = (ROOT / "questionnaire/input/pagecontent/measurements.md").read_text(
            encoding="utf-8"
        )
        authored = (ROOT / "questionnaire/input/fsh/examples.fsh").read_text(encoding="utf-8")
        printed = [
            line.strip()
            for line in page.splitlines()
            if line.startswith("* item[")
        ]
        self.assertTrue(printed, "the page prints no instrument lines")
        for line in printed:
            self.assertIn(line, authored, f"the page prints a line the example does not have: {line}")

        directory = ROOT / "questionnaire/fixtures/extraction"
        weight = json.loads((directory / "body-weight.json").read_text(encoding="utf-8"))
        pressure = json.loads((directory / "blood-pressure.json").read_text(encoding="utf-8"))
        components = {
            component["code"]["coding"][0]["code"]: component["valueQuantity"]
            for component in pressure["component"]
        }
        stated = (
            f"{weight['code']['coding'][0]['code']}",
            f"{weight['valueQuantity']['value']}",
            f"{pressure['code']['coding'][0]['code']}",
            f"{components['8480-6']['value']}",
            f"{components['8462-4']['value']}",
        )
        for value in stated:
            self.assertIn(value, page, f"the page never states {value}")

    def test_extraction_derives_the_documented_observations(self) -> None:
        """The chain has to close: instrument, then response, then Observation.

        Everything an extractor can know comes from the instrument and the response. Deriving
        the Observations here from those two alone, and holding the result against the
        published fixtures, is what keeps the worked example a system rather than three
        separately plausible documents.
        """
        instrument = load_extraction("questionnaire.json")
        response = load_extraction("questionnaire-response.json")
        directory = ROOT / "questionnaire/fixtures/extraction"
        extract = "http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire-observationExtract"
        category = (
            "http://hl7.org/fhir/uv/sdc/StructureDefinition/"
            "sdc-questionnaire-observation-extract-category"
        )

        def extension(node: dict, url: str) -> dict | None:
            return next((e for e in node.get("extension", []) if e["url"] == url), None)

        def answers(items: list, link_id: str) -> dict:
            return next(item for item in items if item["linkId"] == link_id)

        # Observation-based extraction, from the two documents and nothing else.
        derived: list[dict] = []
        for question in instrument["item"]:
            marker = extension(question, extract)
            if not (marker and marker.get("valueBoolean")):
                continue
            answered = answers(response["item"], question["linkId"])
            declared = extension(question, category)
            observation = {
                "code": question["code"][0]["code"],
                "category": (
                    declared["valueCodeableConcept"]["coding"][0]["code"] if declared else None
                ),
                "subject": response["subject"]["reference"],
            }
            # An item that binds a time supplies its own; everything else takes `authored`.
            bound = [
                e for e in question.get("extension", [])
                if e["url"].endswith("sdc-questionnaire-definitionExtractValue")
            ]
            timed = [
                child for child in question.get("item", [])
                if any(
                    e["url"].endswith("sdc-questionnaire-definitionExtractValue")
                    for e in child.get("extension", [])
                )
            ]
            observation["timeIsBound"] = bool(bound or timed)
            if not observation["timeIsBound"]:
                observation["effectiveDateTime"] = response["authored"]
            children = [
                child
                for child in question.get("item", [])
                if (extension(child, extract) or {}).get("valueCode") == "component"
            ]
            if children:
                observation["component"] = {
                    child["code"][0]["code"]: answers(answered["item"], child["linkId"])["answer"][0][
                        "valueQuantity"
                    ]
                    for child in children
                }
            else:
                answer = answered["answer"][0]
                # A quantity answer carries its own unit; an integer answer takes the unit the
                # instrument fixes with questionnaire-unit.
                if "valueQuantity" in answer:
                    observation["value"] = answer["valueQuantity"]
                else:
                    fixed = next(
                        e for e in question["extension"]
                        if e["url"].endswith("StructureDefinition/questionnaire-unit")
                    )["valueCoding"]
                    observation["value"] = {
                        "value": answer["valueInteger"],
                        "system": fixed["system"],
                        "code": fixed["code"],
                    }
            derived.append(observation)

        self.assertEqual(len(derived), 3, "the instrument extracts three Observations")

        published = {
            json.loads((directory / name).read_text(encoding="utf-8"))["code"]["coding"][0]["code"]:
                json.loads((directory / name).read_text(encoding="utf-8"))
            for name in ("body-weight.json", "blood-pressure.json", "step-count.json")
        }
        self.assertEqual({item["code"] for item in derived}, set(published))

        for item in derived:
            with self.subTest(code=item["code"]):
                fixture = published[item["code"]]
                if item["category"] is not None:
                    self.assertEqual(fixture["category"][0]["coding"][0]["code"], item["category"])
                if item["timeIsBound"]:
                    # The binding takes the time out of `authored`, which is the whole point.
                    self.assertNotEqual(fixture.get("effectiveDateTime"), response["authored"])
                else:
                    self.assertEqual(fixture["effectiveDateTime"], item["effectiveDateTime"])
                self.assertEqual(fixture["subject"]["reference"], item["subject"])
                self.assertEqual(
                    fixture["derivedFrom"][0]["reference"],
                    f"QuestionnaireResponse/{response['id']}",
                )
                if "component" in item:
                    self.assertEqual(
                        {c["code"]["coding"][0]["code"]: c["valueQuantity"] for c in fixture["component"]},
                        item["component"],
                    )
                    self.assertNotIn("valueQuantity", fixture)
                else:
                    emitted = fixture["valueQuantity"]
                    self.assertEqual(emitted["value"], item["value"]["value"])
                    self.assertEqual(emitted["code"], item["value"]["code"])
                    self.assertEqual(emitted["system"], item["value"]["system"])

        # What extraction cannot supply, the projecting system adds; it is not derivable here.
        for fixture in published.values():
            self.assertTrue(fixture["identifier"], "the projector mints the opaque identities")


    def test_extracted_observations_carry_the_mobile_output_envelope(self) -> None:
        """What extraction produces has to be checkable, not just described.

        These fixtures are the Observations the worked example extracts to. Holding them
        against the measurement catalog and the mobile output envelope keeps the documented
        result honest, and keeps the gap against an adapter-produced Observation visible.
        """
        catalog = json.loads(
            (ROOT / "catalog/measurement-catalog.json").read_text(encoding="utf-8")
        )
        measurements = {entry["id"]: entry for entry in catalog["measurements"]}
        directory = ROOT / "questionnaire/fixtures/extraction"

        def role(identifier: dict) -> str:
            return identifier["type"]["coding"][0]["code"]

        for measurement_id in ("body-weight", "blood-pressure"):
            with self.subTest(measurement=measurement_id):
                observation = json.loads(
                    (directory / f"{measurement_id}.json").read_text(encoding="utf-8")
                )
                measurement = measurements[measurement_id]

                self.assertEqual(
                    observation["meta"]["profile"],
                    [f"https://grovealliance.org/fhir/mobile/StructureDefinition/{measurement['profile']}"],
                )
                self.assertEqual(
                    observation["code"]["coding"][0]["code"], measurement["code"]["code"]
                )
                self.assertEqual(
                    observation["category"][0]["coding"][0]["code"],
                    measurement["category"]["code"],
                )

                # The mobile output envelope: both opaque identities, a subject, and a time.
                roles = {role(identifier) for identifier in observation["identifier"]}
                self.assertEqual(roles, {"source-record", "source-output"})
                for identifier in observation["identifier"]:
                    self.assertRegex(identifier["value"], r"^v2:[^:]+:[1-9][0-9]*:[A-Za-z0-9_-]{43}$")
                    self.assertTrue(identifier["system"].startswith("https://"))
                self.assertEqual(observation["status"], "final")
                self.assertIn("subject", observation)
                self.assertIn("effectiveDateTime", observation)

                # Self-report is always declared, and the answer it came from stays reachable.
                extensions = {e["url"]: e for e in observation["extension"]}
                recording = extensions[
                    "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-recording-method"
                ]
                self.assertEqual(
                    recording["valueCodeableConcept"]["coding"][0]["code"], "manual-entry"
                )
                self.assertTrue(
                    observation["derivedFrom"][0]["reference"].startswith("QuestionnaireResponse/")
                )

                # The value carries the unit its measurement fixes, scalar or component.
                if measurement["valueKind"] == "components":
                    components = {c["id"]: c for c in measurement["components"]}
                    emitted = {
                        c["code"]["coding"][0]["code"]: c["valueQuantity"]
                        for c in observation["component"]
                    }
                    self.assertEqual(
                        set(emitted), {c["code"] for c in components.values()}
                    )
                    for component in components.values():
                        quantity = emitted[component["code"]]
                        self.assertEqual(quantity["code"], component["quantity"]["code"])
                        self.assertEqual(quantity["system"], component["quantity"]["system"])
                    self.assertNotIn("valueQuantity", observation)
                else:
                    quantity = observation["valueQuantity"]
                    self.assertEqual(quantity["code"], measurement["quantity"]["code"])
                    self.assertEqual(quantity["system"], measurement["quantity"]["system"])


    def test_profiles_derive_from_sdc_and_publish_named_rules(self) -> None:
        questionnaire = load_generated("StructureDefinition-grove-questionnaire.json")
        response = load_generated("StructureDefinition-grove-questionnaire-response.json")

        self.assertEqual(
            questionnaire["baseDefinition"],
            "http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire",
        )
        self.assertEqual(
            response["baseDefinition"],
            "http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaireresponse",
        )
        questionnaire_rules = {
            constraint["key"]
            for element in questionnaire["differential"]["element"]
            for constraint in element.get("constraint", [])
        }
        self.assertEqual(
            questionnaire_rules,
            {
                "qg-canonical-1",
                "qg-version-1",
                "qg-version-algorithm-1",
                "qg-item-text-1",
                "qg-reference-1",
                "qg-repeats-1",
                "qg-enable-1",
                "qg-expression-1",
                "qg-variable-name-1",
                "qg-initial-1",
                "qg-length-1",
                "qg-decimal-1",
                "qg-value-bounds-1",
                "qg-quantity-1",
                "qg-unit-1",
                "qg-attachment-1",
                "qg-occurrence-1",
                "qg-min-max-1",
                "qg-style-sensitive-1",
            },
        )
        response_rules = {
            constraint["key"]
            for element in response["differential"]["element"]
            for constraint in element.get("constraint", [])
        }
        self.assertEqual(
            response_rules,
            {
                "gqr-canonical-1",
                "gqr-identifier-1",
                "gqr-completion-mode-1",
            },
        )
        questionnaire_constraints = {
            constraint["key"]: constraint["expression"]
            for element in questionnaire["differential"]["element"]
            for constraint in element.get("constraint", [])
        }
        response_constraints = {
            constraint["key"]: constraint["expression"]
            for element in response["differential"]["element"]
            for constraint in element.get("constraint", [])
        }
        self.assertIn(
            r"^https?://[^\\s/?#|]+[^\\s|#]*$",
            questionnaire_constraints["qg-canonical-1"],
        )
        self.assertIn(
            r"^https?://[^\\s/?#|]+[^\\s|#]*[|]",
            response_constraints["gqr-canonical-1"],
        )
        self.assertIn(
            "(0|[1-9][0-9]*)[.]",
            response_constraints["gqr-canonical-1"],
        )

    def test_profile_exposes_root_target_constraints_and_sdc_hidden_behavior(self) -> None:
        questionnaire = load_generated("StructureDefinition-grove-questionnaire.json")
        elements = {
            element["id"]: element
            for element in questionnaire["differential"]["element"]
        }
        profile_fsh = (ROOT / "questionnaire/input/fsh/profiles.fsh").read_text(
            encoding="utf-8"
        )
        self.assertIn("* url 1..1 MS", profile_fsh)
        self.assertIn("Questionnaire.extension:targetConstraint", elements)
        self.assertIn("Questionnaire.item.extension:targetConstraint", elements)
        self.assertEqual(
            elements["Questionnaire.extension:variable.value[x].name"]["min"],
            1,
        )
        self.assertEqual(
            elements["Questionnaire.item.extension:variable.value[x].name"]["min"],
            1,
        )

        published_path = OUTPUT / "StructureDefinition-grove-questionnaire.json"
        if published_path.is_file():
            published = json.loads(published_path.read_text(encoding="utf-8"))
            hidden = next(
                element
                for element in published["snapshot"]["element"]
                if element["id"] == "Questionnaire.item.extension:hidden"
            )
            self.assertTrue(hidden["mustSupport"])

        all_text = json.dumps(questionnaire["differential"], sort_keys=True)
        self.assertIn("rendering-styleSensitive", all_text)

    def test_completion_mode_fixes_system_and_code_but_not_display(self) -> None:
        response = load_generated("StructureDefinition-grove-questionnaire-response.json")
        elements = {
            element["id"]: element
            for element in response["differential"]["element"]
        }
        coding = elements[
            "QuestionnaireResponse.extension:completionMode.value[x].coding"
        ]
        self.assertEqual((coding["min"], coding["max"]), (1, "1"))
        self.assertEqual(
            elements[
                "QuestionnaireResponse.extension:completionMode.value[x].coding.system"
            ]["fixedUri"],
            "http://terminology.hl7.org/CodeSystem/v3-ParticipationMode",
        )
        self.assertEqual(
            elements[
                "QuestionnaireResponse.extension:completionMode.value[x].coding.code"
            ]["fixedCode"],
            "ELECTRONIC",
        )
        self.assertFalse(
            any("coding.display" in element["id"] for element in elements.values())
        )

    def test_introductory_pair_uses_exact_identity_and_answer_nesting(self) -> None:
        questionnaire = load_generated(
            "Questionnaire-GroveWeeklySymptomCheckInExample.json"
        )
        response = load_generated(
            "QuestionnaireResponse-GroveWeeklySymptomCheckInResponseExample.json"
        )

        self.assertEqual(questionnaire["url"], QUESTIONNAIRE_CANONICAL)
        self.assertEqual(questionnaire["version"], "1.0.0")
        self.assertEqual(response["questionnaire"], f"{QUESTIONNAIRE_CANONICAL}|1.0.0")
        severity = response["item"][0]["item"][0]["answer"][0]["item"][0]
        self.assertEqual(severity["linkId"], "pain-severity")
        self.assertEqual(
            severity["answer"][0]["valueCoding"],
            {
                "system": "http://snomed.info/sct",
                "code": "6736007",
                "display": "Moderate severity",
            },
        )
        self.assertEqual(validator.validate_pair(questionnaire, response), [])

    def test_response_item_text_is_optional_and_locale_neutral(self) -> None:
        questionnaire = load_json(PAIR_FIXTURES / "valid/questionnaire.json")
        response = load_json(PAIR_FIXTURES / "valid/response.json")
        value_sets = [load_json(PAIR_FIXTURES / "valid/value-set.json")]

        without_text = copy.deepcopy(response)
        for item in validator.response_items(without_text.get("item", [])):
            item.pop("text", None)
        self.assertEqual(validator.validate_response(without_text), [])
        self.assertEqual(
            validator.validate_pair(questionnaire, without_text, value_sets),
            [],
        )

        localized = copy.deepcopy(response)
        localized["item"][0]["text"] = "Identität"
        localized["item"][0]["item"][0]["text"] = "Wie heißen Sie?"
        self.assertEqual(validator.validate_response(localized), [])
        self.assertEqual(
            validator.validate_pair(questionnaire, localized, value_sets),
            [],
        )

        questionnaire_without_prompt = copy.deepcopy(questionnaire)
        questionnaire_without_prompt["item"][0]["item"][0].pop("text")
        self.assertIn(
            "qg-item-text-1",
            {
                issue.rule
                for issue in validator.validate_questionnaire(
                    questionnaire_without_prompt
                )
            },
        )

    def test_static_validator_corpus_has_one_mutation_and_expected_rule(self) -> None:
        manifest = load_json(VALIDATOR_FIXTURES / "cases.json")
        official_case_ids = {
            case["id"]
            for case in manifest["invalid"]
            if case.get("fhirValidator") is not False
        }
        self.assertEqual(
            set(fhir_validator.load_expectations(official_case_ids)),
            official_case_ids,
        )
        for relative in manifest["valid"]:
            resource = load_json(VALIDATOR_FIXTURES / relative)
            issues = (
                validator.validate_questionnaire(resource)
                if resource["resourceType"] == "Questionnaire"
                else validator.validate_response(resource)
            )
            self.assertEqual(issues, [], relative)

        identifiers: set[str] = set()
        for case in manifest["invalid"]:
            with self.subTest(case=case["id"]):
                self.assertNotIn(case["id"], identifiers)
                identifiers.add(case["id"])
                self.assertEqual(set(case["mutation"]), set(case["mutation"]) & {"op", "path", "from", "value"})
                base = load_json(VALIDATOR_FIXTURES / case["base"])
                invalid = apply_mutation(base, case["mutation"])
                issues = (
                    validator.validate_questionnaire(invalid)
                    if invalid["resourceType"] == "Questionnaire"
                    else validator.validate_response(invalid)
                )
                self.assertEqual(
                    [(issue.rule, issue.severity) for issue in issues],
                    [(case["expectedRule"], "error")],
                )

    def test_official_validator_expectations_reject_extra_or_overlapping_errors(self) -> None:
        def issue(message_id: str) -> dict:
            return {
                "severity": "error",
                "code": "invariant",
                "expression": ["Questionnaire"],
                "details": {"text": f"Constraint failed: {message_id}"},
                "extension": [
                    {
                        "url": fhir_validator.MESSAGE_ID_URL,
                        "valueString": message_id,
                    }
                ],
            }

        expected = [
            {
                "messageId": "intended-rule",
                "code": "invariant",
                "expression": "Questionnaire",
            }
        ]
        self.assertIsNone(
            fhir_validator.exact_error_failure([issue("intended-rule")], expected)
        )
        self.assertIsNotNone(
            fhir_validator.exact_error_failure(
                [issue("intended-rule"), issue("unrelated-rule")], expected
            )
        )
        self.assertIsNotNone(
            fhir_validator.exact_error_failure(
                [issue("intended-rule")], expected + [{"code": "invariant"}]
            )
        )

    def test_pair_corpus_covers_each_cross_resource_rule(self) -> None:
        manifest = load_json(PAIR_FIXTURES / "cases.json")
        questionnaire = load_json(PAIR_FIXTURES / manifest["questionnaire"])
        response = load_json(PAIR_FIXTURES / manifest["response"])
        in_progress = load_json(PAIR_FIXTURES / manifest["additionalValidResponses"][0])
        value_sets = [load_json(PAIR_FIXTURES / path) for path in manifest["valueSets"]]
        self.assertEqual(validator.validate_pair(questionnaire, response, value_sets), [])
        self.assertEqual(validator.validate_pair(questionnaire, in_progress, value_sets), [])
        for case in manifest["additionalValidSubjectCases"]:
            valid = response
            mutations = case.get("mutations", [case.get("mutation")])
            for mutation in mutations:
                valid = apply_mutation(valid, mutation)
            with self.subTest(case=case["id"]):
                self.assertEqual(
                    validator.validate_pair(questionnaire, valid, value_sets), []
                )

        expected_rules: set[str] = set()
        for case in manifest["invalid"]:
            with self.subTest(case=case["id"]):
                target = in_progress if case["target"] == "inProgressResponse" else response
                invalid = apply_mutation(target, case["mutation"])
                issues = validator.validate_pair(questionnaire, invalid, value_sets)
                self.assertEqual(
                    [(issue.rule, issue.severity) for issue in issues],
                    [(case["expectedRule"], "error")],
                )
                expected_rules.add(case["expectedRule"])
        self.assertEqual(
            expected_rules,
            {
                "pair-questionnaire-canonical",
                "pair-subject-type",
                "pair-item-nesting",
                "pair-answer-type",
                "pair-inline-option",
                "pair-valueset-membership",
                "pair-repeats",
                "pair-answer-occurrence",
                "pair-required-item",
                "pair-item-unknown",
                "pair-item-duplicate",
                "pair-item-misplaced",
                "pair-item-disabled",
                "pair-response-entered-in-error",
            },
        )

    def test_cli_emits_stable_machine_readable_report(self) -> None:
        command = [
            sys.executable,
            str(ROOT / "Scripts/validate-questionnaire.py"),
            "--questionnaire",
            str(PAIR_FIXTURES / "valid/questionnaire.json"),
            "--response",
            str(PAIR_FIXTURES / "valid/response.json"),
            "--value-set",
            str(PAIR_FIXTURES / "valid/value-set.json"),
            "--json",
        ]
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        self.assertEqual(json.loads(result.stdout), {"issues": [], "valid": True})

    def test_enable_when_not_equal_uses_any_answer_semantics(self) -> None:
        condition = {
            "enableWhen": [
                {
                    "question": "choice",
                    "operator": "!=",
                    "answerCoding": {
                        "system": "https://example.org/codes",
                        "code": "a",
                    },
                }
            ]
        }
        expected = {"system": "https://example.org/codes", "code": "a"}
        other = {"system": "https://example.org/codes", "code": "b"}

        self.assertFalse(validator.evaluate_enable_when(condition, {}))
        self.assertFalse(
            validator.evaluate_enable_when(condition, {"choice": [expected]})
        )
        self.assertTrue(
            validator.evaluate_enable_when(condition, {"choice": [expected, other]})
        )

    def test_target_constraint_evaluation_is_status_and_severity_aware(self) -> None:
        questionnaire = load_json(PAIR_FIXTURES / "valid/questionnaire.json")
        completed = load_json(PAIR_FIXTURES / "valid/response.json")
        in_progress = load_json(PAIR_FIXTURES / "valid/response-in-progress.json")
        value_sets = [load_json(PAIR_FIXTURES / "valid/value-set.json")]

        def with_constraint(severity: str) -> dict:
            constrained = copy.deepcopy(questionnaire)
            constrained.setdefault("extension", []).append(
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/targetConstraint",
                    "extension": [
                        {"url": "key", "valueId": f"review-{severity}"},
                        {"url": "severity", "valueCode": severity},
                        {
                            "url": "expression",
                            "valueExpression": {
                                "language": "text/fhirpath",
                                "expression": "%resource.item.exists()",
                            },
                        },
                        {"url": "human", "valueString": "Review the response."},
                    ],
                }
            )
            return constrained

        error_issues = validator.validate_pair(
            with_constraint("error"), completed, value_sets
        )
        warning_issues = validator.validate_pair(
            with_constraint("warning"), completed, value_sets
        )
        in_progress_issues = validator.validate_pair(
            with_constraint("error"), in_progress, value_sets
        )

        self.assertIn(
            ("pair-expression-engine-required", "error"),
            {(issue.rule, issue.severity) for issue in error_issues},
        )
        self.assertIn(
            ("pair-expression-engine-required", "warning"),
            {(issue.rule, issue.severity) for issue in warning_issues},
        )
        self.assertNotIn(
            "pair-expression-engine-required",
            {issue.rule for issue in in_progress_issues},
        )

    def test_built_package_pins_sdc_and_the_matching_extension_package(self) -> None:
        archive_path = OUTPUT / "package.tgz"
        if not archive_path.is_file():
            self.skipTest("Questionnaire Publisher package is not present")
        with tarfile.open(archive_path, "r:gz") as archive:
            package_file = archive.extractfile("package/package.json")
            self.assertIsNotNone(package_file)
            package = json.load(package_file)
        self.assertEqual(package["name"], "org.grovealliance.fhir.questionnaire")
        self.assertEqual(package["version"], "0.6.0")
        self.assertEqual(package["dependencies"].get("hl7.fhir.uv.sdc"), "4.0.0")
        self.assertEqual(
            package["dependencies"].get("hl7.fhir.uv.extensions.r4"),
            "5.3.0",
        )


if __name__ == "__main__":
    unittest.main()
