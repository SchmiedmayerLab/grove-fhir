#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#

import json
import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RENDERER = ROOT / "Scripts/render-measurement-profiles.py"

FIXTURE_FILES = (
    "catalog/exchange-protocol.json",
    "catalog/healthkit-adapter.json",
    "catalog/health-connect-adapter.json",
    "catalog/providers-adapter.json",
    "catalog/measurement-catalog.json",
    "catalog/terminology/loinc-concepts.json",
    "catalog/terminology/ucum-units.json",
    "mobile/input/data/terminology-reviews.json",
    "mobile/input/fsh/aliases.fsh",
    "mobile/input/fsh/terminology.fsh",
    "mobile/input/fsh/profiles.fsh",
    "mobile/input/fsh/generated-measurement-profiles.fsh",
    "healthkit/input/fsh/generated-measurement-profiles.fsh",
    "healthkit/input/fsh/terminology.fsh",
    "health-connect/input/fsh/generated-measurement-profiles.fsh",
    "withings/input/fsh/generated-measurement-profiles.fsh",
    "oura/input/fsh/generated-measurement-profiles.fsh",
    "google-health/input/fsh/generated-measurement-profiles.fsh",
)

EXCHANGE_PROTOCOL_SPEC = importlib.util.spec_from_file_location(
    "exchange_protocol", ROOT / "Scripts/exchange_protocol.py"
)
assert EXCHANGE_PROTOCOL_SPEC is not None and EXCHANGE_PROTOCOL_SPEC.loader is not None
EXCHANGE_PROTOCOL = importlib.util.module_from_spec(EXCHANGE_PROTOCOL_SPEC)
EXCHANGE_PROTOCOL_SPEC.loader.exec_module(EXCHANGE_PROTOCOL)

RENDERER_SPEC = importlib.util.spec_from_file_location(
    "render_measurement_profiles", RENDERER
)
assert RENDERER_SPEC is not None and RENDERER_SPEC.loader is not None
RENDERER_MODULE = importlib.util.module_from_spec(RENDERER_SPEC)
RENDERER_SPEC.loader.exec_module(RENDERER_MODULE)


class MeasurementProfileProjectionTests(unittest.TestCase):
    def projected_example_identities(self) -> tuple[dict, list[dict]]:
        """Recompute generated-example projections in memory from their catalogs."""
        contract = RENDERER_MODULE.example_contract(ROOT)
        projections = RENDERER_MODULE.source_identity_projections(ROOT, contract)
        catalog = json.loads(
            (ROOT / "catalog/measurement-catalog.json").read_text(encoding="utf-8")
        )
        rows: list[dict] = []
        for owner_key in RENDERER_MODULE.OWNERS:
            handwritten = RENDERER_MODULE.handwritten_instances(ROOT, owner_key)
            for measurement in catalog["measurements"]:
                if measurement.get("owner", "mobile") != owner_key:
                    continue
                if not measurement.get("generation", {}).get("emit"):
                    continue
                instance = f"{RENDERER_MODULE.fsh_name(measurement['profile'])}Example"
                if instance in handwritten:
                    continue
                rows.append(
                    RENDERER_MODULE.example_identity_record(
                        measurement, owner_key, projections, contract
                    )
                )
        return contract, rows

    def run_renderer(self, root: Path, *extra: str) -> tuple[int, str]:
        result = subprocess.run(
            [sys.executable, str(RENDERER), "--root", str(root), *extra],
            capture_output=True,
            text=True,
        )
        return result.returncode, result.stdout + result.stderr

    def make_fixture(self, directory: Path) -> Path:
        for name in FIXTURE_FILES:
            destination = directory / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)
        return directory

    def remint_ground_truth(self, root: Path) -> None:
        import hashlib

        reviews_path = root / "mobile/input/data/terminology-reviews.json"
        reviews = json.loads(reviews_path.read_text(encoding="utf-8"))
        ground = hashlib.sha256()
        for name in reviews["groundTruthFiles"]:
            ground.update((root / name).read_bytes())
        reviews["groundTruthDigest"] = "sha256:" + ground.hexdigest()
        reviews_path.write_text(json.dumps(reviews, indent=2), encoding="utf-8")

    def edit_catalog(self, root: Path, mutate) -> None:
        path = root / "catalog/measurement-catalog.json"
        catalog = json.loads(path.read_text(encoding="utf-8"))
        mutate(catalog)
        path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")

    def demote_to_hand_written(self, root: Path) -> None:
        """Turn the fixture back into the pre-cutover shape: hand FSH, no emit."""
        generated = root / "mobile/input/fsh/generated-measurement-profiles.fsh"
        blocks = re.sub(r"\A(//[^\n]*\n)+\n", "", generated.read_text(encoding="utf-8"))
        profiles = root / "mobile/input/fsh/profiles.fsh"
        profiles.write_text(
            profiles.read_text(encoding="utf-8") + "\n" + blocks + "\n",
            encoding="utf-8",
        )
        generated.unlink()
        self.edit_catalog(
            root,
            lambda catalog: [
                measurement["generation"].update({"emit": False})
                for measurement in catalog["measurements"]
                if measurement.get("owner", "mobile") == "mobile"
            ],
        )
        self.remint_ground_truth(root)
        code, output = self.run_renderer(root)
        self.assertEqual(code, 0, output)

    def test_generated_profiles_are_current(self) -> None:
        code, output = self.run_renderer(ROOT, "--check")
        self.assertEqual(code, 0, output)
        self.assertIn("222 emitted, 0 parity-checked, problems=0", output)

    def test_root_controls_shared_value_set_example_sources(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_fixture(Path(directory))
            terminology = root / "healthkit/input/fsh/terminology.fsh"
            authored = terminology.read_text(encoding="utf-8")
            fixture_display = "Fixture-only not-present display"
            changed = authored.replace(
                '#not-present "Not present"',
                f'#not-present "{fixture_display}"',
                1,
            )
            self.assertNotEqual(changed, authored)
            terminology.write_text(changed, encoding="utf-8")

            code, output = self.run_renderer(root)
            self.assertEqual(code, 0, output)
            generated = (
                root / "healthkit/input/fsh/generated-measurement-profiles.fsh"
            ).read_text(encoding="utf-8")
            self.assertIn(
                "* valueCodeableConcept = "
                f'GroveSymptomSeverityCS#not-present "{fixture_display}"',
                generated,
            )

    def test_every_generated_example_identity_recomputes_and_matches_fsh(self) -> None:
        contract, examples = self.projected_example_identities()
        for example in examples:
            for field in ("sourceRecord", "sourceOutput"):
                identity = example[field]
                with self.subTest(instance=example["instance"], identity=field):
                    self.assertEqual(
                        identity["value"],
                        EXCHANGE_PROTOCOL.derive_hmac_identity(
                            key=contract["key"],
                            key_id=contract["keyId"],
                            epoch=contract["epoch"],
                            identity_kind=identity["identityKind"],
                            components=identity["components"],
                        ),
                    )
            generated = (
                ROOT / RENDERER_MODULE.OWNERS[example["guide"]]["generated"]
            ).read_text(encoding="utf-8")
            match = re.search(
                rf"^Instance: {re.escape(example['instance'])}\n.*?(?=\n\n|\Z)",
                generated,
                re.M | re.S,
            )
            self.assertIsNotNone(match, example["instance"])
            block = match.group(0)
            for slice_name, identity_name in (
                ("sourceRecord", "sourceRecord"),
                ("sourceOutput", "sourceOutput"),
            ):
                identity = example[identity_name]
                self.assertIn(
                    f'* identifier[{slice_name}].system = "{identity["system"]}"',
                    block,
                )
                self.assertIn(
                    f'* identifier[{slice_name}].value = "{identity["value"]}"',
                    block,
                )

    def test_example_identity_systems_are_kind_specific_and_distinct(self) -> None:
        contract, examples = self.projected_example_identities()
        systems = contract["identitySystemsByKind"]
        self.assertEqual(
            set(systems),
            {
                row["kind"]
                for row in json.loads(
                    (ROOT / "catalog/exchange-protocol.json").read_text(encoding="utf-8")
                )["opaqueIdentity"]["identityKinds"]
            },
        )
        self.assertEqual(len(set(systems.values())), len(systems))
        for example in examples:
            for identity in (example["sourceRecord"], example["sourceOutput"]):
                self.assertEqual(
                    identity["system"], systems[identity["identityKind"]], example["instance"]
                )
            if example["guide"] in {"withings", "oura", "google-health"}:
                source_type = example["sourceType"]
                self.assertEqual(
                    example["sourceRecord"]["identityKind"], "provider-record"
                )
                self.assertEqual(
                    example["sourceOutput"]["identityKind"], "provider-output"
                )
                self.assertNotIn("/", source_type["preimageToken"])
                self.assertEqual(
                    source_type["wireCode"],
                    f"{source_type['providerCode']}/{source_type['preimageToken']}",
                )
                expected_scope = (
                    contract["globalProviderScope"]
                    if example["guide"] == "oura"
                    else contract["providerScope"]
                )
                self.assertEqual(
                    example["sourceRecord"]["components"][2:4],
                    [expected_scope["system"], expected_scope["value"]],
                )

    def test_provider_owned_semantics_are_separate_from_provider_envelopes(self) -> None:
        catalog = json.loads(
            (ROOT / "catalog/measurement-catalog.json").read_text(encoding="utf-8")
        )
        providers = json.loads(
            (ROOT / "catalog/providers-adapter.json").read_text(encoding="utf-8")
        )
        envelope_by_owner = {
            provider["measurementOwner"]: provider["observationProfile"]
            for provider in providers["providers"]
        }
        for owner, envelope in envelope_by_owner.items():
            generated = (
                ROOT / RENDERER_MODULE.OWNERS[owner]["generated"]
            ).read_text(encoding="utf-8")
            measurements = [
                measurement
                for measurement in catalog["measurements"]
                if measurement.get("owner", "mobile") == owner
            ]
            self.assertEqual(
                generated.count("Parent: GroveMobileObservation"),
                len(measurements),
                owner,
            )
            self.assertNotIn(f"Parent: {RENDERER_MODULE.fsh_name(owner)}Observation", generated)
            for measurement in measurements:
                instance = (
                    f"Instance: {RENDERER_MODULE.fsh_name(measurement['profile'])}Example"
                )
                block = generated.split(instance, 1)[1].split("\n\n", 1)[0]
                self.assertIn(f'* meta.profile[+] = "{envelope}"', block)

    def test_example_output_preimages_follow_adapter_catalog_roles(self) -> None:
        _, examples = self.projected_example_identities()
        for example in examples:
            role, discriminator = example["sourceOutput"]["components"][-2:]
            with self.subTest(instance=example["instance"]):
                if example["guide"] == "healthkit":
                    self.assertEqual(role, example["measurementId"])
                    self.assertEqual(discriminator, "single")
                elif example["guide"] == "health-connect":
                    count_rule = example["countRule"]
                    if count_rule in {"exactly-one", "zero-or-one"}:
                        self.assertEqual((role, discriminator), ("single", example["measurementId"]))
                    elif count_rule == "one-per-present-field":
                        self.assertEqual((role, discriminator), ("present-field", example["measurementId"]))
                    elif count_rule == "one-per-sample":
                        self.assertEqual(role, "sample")
                        self.assertIn("|", discriminator)
                    else:
                        self.assertIn(example.get("graphRule"), {"sleep-session-graph", "exercise-session-graph", "mindfulness-session-graph"})

    def test_only_health_connect_examples_emit_source_availability(self) -> None:
        _, examples = self.projected_example_identities()
        for example in examples:
            expected = (
                "Metadata.lastModifiedTime"
                if example["guide"] == "health-connect"
                else "omitted"
            )
            self.assertEqual(example["availability"]["sourceField"], expected)

    def test_duplicate_identity_system_fails_with_kind_aware_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_fixture(Path(directory))
            path = root / "catalog/exchange-protocol.json"
            protocol = json.loads(path.read_text(encoding="utf-8"))
            systems = protocol["testVectors"]["identitySystems"]
            systems[1]["system"] = systems[0]["system"]
            path.write_text(json.dumps(protocol, indent=2) + "\n", encoding="utf-8")
            code, output = self.run_renderer(root, "--check")
            self.assertEqual(code, 1, output)
            self.assertIn("identity systems must be distinct by identity kind", output)

    def test_quantity_domains_project_to_fhir_constraints(self) -> None:
        mobile = (ROOT / "mobile/input/fsh/generated-measurement-profiles.fsh").read_text(
            encoding="utf-8"
        )
        healthkit = (
            ROOT / "healthkit/input/fsh/generated-measurement-profiles.fsh"
        ).read_text(encoding="utf-8")
        self.assertIn("* valueQuantity.value ^minValueDecimal = 0", mobile)
        self.assertIn("* valueQuantity.value ^maxValueDecimal = 100", mobile)
        self.assertIn("(value.ofType(Quantity).value mod 1) = 0", mobile)
        self.assertIn("* valueQuantity.value ^minValueDecimal = -1", healthkit)
        self.assertIn("* valueQuantity.value ^maxValueDecimal = 1", healthkit)
        self.assertIn("(value.ofType(Quantity).value mod 1) = 0", healthkit)

    def test_projection_still_reproduces_hand_written_profiles(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_fixture(Path(directory))
            self.demote_to_hand_written(root)
            code, output = self.run_renderer(root, "--check")
            self.assertEqual(code, 0, output)
            self.assertIn("parity-checked, problems=0", output)

    def test_parity_detects_a_drifted_hand_profile(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_fixture(Path(directory))
            self.demote_to_hand_written(root)
            profiles = root / "mobile/input/fsh/profiles.fsh"
            text = profiles.read_text(encoding="utf-8")
            profiles.write_text(
                text.replace("* code = $loinc#8867-4", "* code = $loinc#8310-5", 1),
                encoding="utf-8",
            )
            self.remint_ground_truth(root)
            code, output = self.run_renderer(root, "--check")
            self.assertEqual(code, 1, output)
            self.assertIn("projection differs from the hand profile", output)

    def test_terminology_change_without_re_review_refuses_generation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_fixture(Path(directory))

            def change_unit(catalog: dict) -> None:
                heart_rate = next(
                    m for m in catalog["measurements"] if m["id"] == "heart-rate"
                )
                heart_rate["quantity"]["code"] = "{beats}/min"

            self.edit_catalog(root, change_unit)
            code, output = self.run_renderer(root, "--check")
            self.assertEqual(code, 2, output)
            self.assertIn("terminology changed since its review", output)
            self.assertIn("generation refused", output)

    def test_missing_review_entry_refuses_generation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_fixture(Path(directory))
            reviews_path = root / "mobile/input/data/terminology-reviews.json"
            reviews = json.loads(reviews_path.read_text(encoding="utf-8"))
            del reviews["entries"]["heart-rate"]
            reviews_path.write_text(json.dumps(reviews, indent=2), encoding="utf-8")
            code, output = self.run_renderer(root, "--check")
            self.assertEqual(code, 2, output)
            self.assertIn("no approved terminology review entry", output)

    def test_emitted_profile_may_not_stay_hand_written(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_fixture(Path(directory))
            generated = root / "mobile/input/fsh/generated-measurement-profiles.fsh"
            block = re.search(
                r"Profile: GroveMobileHeartRate\n.*?(?=\n\n|\Z)",
                generated.read_text(encoding="utf-8"),
                re.S,
            ).group(0)
            profiles = root / "mobile/input/fsh/profiles.fsh"
            profiles.write_text(
                profiles.read_text(encoding="utf-8") + "\n" + block + "\n",
                encoding="utf-8",
            )
            self.remint_ground_truth(root)
            code, output = self.run_renderer(root, "--check")
            self.assertEqual(code, 1, output)
            self.assertIn("still hand-written", output)

    def test_orphaned_generated_file_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_fixture(Path(directory))
            self.demote_to_hand_written(root)
            generated = root / "mobile/input/fsh/generated-measurement-profiles.fsh"
            generated.write_text("// stale\n", encoding="utf-8")
            code, output = self.run_renderer(root, "--check")
            self.assertEqual(code, 1, output)
            self.assertIn("no measurement has generation.emit", output)


if __name__ == "__main__":
    unittest.main()
