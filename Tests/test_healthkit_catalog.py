"""Lock the complete HealthKit source inventory and shared-coverage claims."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import re
import unittest
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).parents[1]
OLD_MOBILE = {
    "grove-mobile-bmi",
    "grove-mobile-blood-glucose",
    "grove-mobile-capillary-blood-glucose",
    "grove-mobile-serum-plasma-glucose",
    "grove-mobile-interstitial-glucose",
}


def plain_decimal(value: Decimal) -> str:
    """Write a decimal in plain positional notation without trailing fractional zeros."""
    text = format(value, "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def shortest_round_trip(value: float) -> str:
    """Write a binary64 as its shortest round-trip decimal in plain positional notation."""
    # repr is the decimal with the fewest significant digits that converts back to the same
    # binary64, of several the one nearest it, and of two equally near ones the one whose last
    # digit is even; only the notation is normalized here.
    return plain_decimal(Decimal(repr(value)))


def percent_from_fraction(fraction: float) -> str:
    """Shift the fraction's shortest round-trip decimal two places exactly, then round once."""
    # scaleb moves the decimal point exactly, and float() of a decimal is correctly rounded.
    return shortest_round_trip(float(Decimal(shortest_round_trip(fraction)).scaleb(2)))


class HealthKitCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(
            (ROOT / "catalog/healthkit-adapter.json").read_text(encoding="utf-8")
        )
        cls.mobile = json.loads(
            (ROOT / "catalog/measurement-catalog.json").read_text(encoding="utf-8")
        )
        cls.protocol = json.loads(
            (ROOT / "catalog/exchange-protocol.json").read_text(encoding="utf-8")
        )
        cls.claims = json.loads(
            (ROOT / "catalog/profile-claims.json").read_text(encoding="utf-8")
        )

    def test_every_active_output_and_direct_claim_is_machine_closed(self) -> None:
        prefix = "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
        generic = prefix + "healthkit-observation"
        ecg = prefix + "healthkit-ecg-observation"
        active_rows = [
            row for row in self.catalog["rows"]
            if row["status"] in {"supported", "platform-exclusive"}
        ]
        active_healthkit_profiles = {
            profile
            for row in active_rows
            for profile in row["profiles"]
            if profile.startswith(prefix)
        }
        ecg_output_profiles = {
            profile
            for output in self.catalog["sensorAdapterClaims"]["electrocardiogram"]["outputs"]
            for profile in output["profiles"]
            if profile.startswith(prefix)
        }
        active_healthkit_profiles.update(ecg_output_profiles)
        provenance = next(
            claim for claim in self.claims["adapterConversionProvenanceClaims"]
            if claim["adapter"] == "healthkit"
        )
        self.assertEqual(
            provenance["targetAdapterProfiles"], sorted(active_healthkit_profiles)
        )
        self.assertEqual(len(active_healthkit_profiles), 119)

        single_profiles = {
            profile
            for row in self.catalog["rows"]
            if row["status"] == "supported"
            for profile in row["profiles"]
            if profile.startswith(prefix) and profile not in {generic, ecg}
        }
        single_claim = self.claims["healthKitSingleProfileObservationClaims"]
        self.assertEqual(single_claim["cardinality"], 1)
        self.assertFalse(single_claim["otherProfilesAllowed"])
        self.assertEqual(single_claim["profiles"], sorted(single_profiles))
        self.assertEqual(len(single_profiles), 111)

        self.assertEqual(
            self.claims["healthKitRecordingDocumentClaim"]["profiles"],
            [
                "https://grovealliance.org/fhir/sensor/StructureDefinition/"
                "grove-sensor-recording-document",
                prefix + "healthkit-recording-document",
            ],
        )
        self.assertEqual(
            self.claims["healthKitClinicalRecordDocumentClaim"]["profiles"],
            [prefix + "healthkit-clinical-record-document"],
        )
        self.assertEqual(
            {
                (claim["resourceType"], claim["profile"])
                for claim in self.claims["healthKitPlatformExclusiveResourceClaims"]
            },
            {
                ("VisionPrescription", prefix + "healthkit-vision-prescription"),
                ("MedicationAdministration", prefix + "healthkit-medication-dose-event"),
                ("MedicationStatement", prefix + "healthkit-user-annotated-medication"),
            },
        )

    def test_health_concept_links_use_the_shared_opaque_context_identity(self) -> None:
        kinds = {
            row["kind"]: row for row in self.protocol["opaqueIdentity"]["identityKinds"]
        }
        context = self.catalog["identity"]["sourceContext"]
        self.assertEqual(context["identityKind"], "source-context")
        self.assertEqual(context["identifierRole"], "source-context")
        self.assertEqual(context["components"], kinds["source-context"]["components"])
        self.assertIn("HKHealthConceptIdentifier", context["rule"])
        self.assertIn("HMAC", context["rule"])

    def test_clinical_release_representation_uses_standard_mime_parameters(self) -> None:
        representation = self.catalog["clinicalRecordAdmission"]["fhirRepresentation"]
        profiles = (ROOT / "healthkit/input/fsh/profiles.fsh").read_text(
            encoding="utf-8"
        )
        self.assertEqual(representation["resourceType"], "DocumentReference")
        self.assertEqual(
            representation["contentTypeByRelease"],
            {
                "dstu2": "application/fhir+json; fhirVersion=1.0",
                "r4": "application/fhir+json; fhirVersion=4.0",
            },
        )
        self.assertIn("* content.format = $recordingFormat#fhir-resource", profiles)
        self.assertIn("* obeys healthkit-clinical-fhir-content-type-1", profiles)
        self.assertNotIn("HealthKitClinicalFHIRRelease", profiles)
        terminology = (ROOT / "healthkit/input/fsh/terminology.fsh").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("HealthKitClinicalFHIRRelease", terminology)

    def test_clinical_document_has_one_provenance_target_hierarchy(self) -> None:
        profiles = (ROOT / "healthkit/input/fsh/profiles.fsh").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "Profile: HealthKitClinicalRecordDocument\n"
            "Parent: HealthKitRecordingDocument",
            profiles,
        )
        target_rule = next(
            line for line in profiles.splitlines()
            if line.startswith("* target only Reference(")
        )
        self.assertIn("HealthKitRecordingDocument", target_rule)
        self.assertNotIn("HealthKitClinicalRecordDocument", target_rule)

    def test_examples_do_not_reintroduce_a_generic_metadata_channel(self) -> None:
        examples = (ROOT / "healthkit/input/fsh/examples.fsh").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("component[+].code.text", examples)
        self.assertNotIn("ThirdPartyPedometerFirmware", examples)
        self.assertNotIn("stays lossless", examples)

    def test_inventory_is_exact_closed_and_unique(self) -> None:
        rows = self.catalog["rows"]
        source = self.catalog["source"]
        self.assertEqual(
            source["sdkBaseline"],
            {
                "platform": "iPhoneOS",
                "version": "26.5",
                "xcodeVersion": "26.6",
                "xcodeBuild": "17F113",
            },
        )
        self.assertEqual(source["platform"], "Apple HealthKit")
        self.assertEqual(source["accessed"], "2026-08-21")
        self.assertEqual(source["rowCount"], len(rows))
        self.assertEqual(source["derivedAggregateCount"], 1)
        self.assertIn("derived mappings are excluded", source["rowScope"])
        identifiers = [row["sourceTypeIdentifier"] for row in rows]
        self.assertEqual(identifiers, sorted(identifiers))
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertFalse(any("#" in identifier for identifier in identifiers))
        for evidence in source["evidence"]:
            url, path = evidence.get("url", ""), evidence.get("path", "")
            self.assertTrue(
                url.startswith("https://developer.apple.com/") or (ROOT / path).is_file(),
                evidence,
            )
        statuses = set(self.catalog["statusVocabulary"])
        for row in rows:
            self.assertEqual(
                set(row),
                {
                    "sourceTypeIdentifier",
                    "title",
                    "symbols",
                    "documentation",
                    "status",
                    "measurementIDs",
                    "profiles",
                }
                | ({"requirement"} if "requirement" in row else set())
                | (
                    {"clinicalAdmissionContract"}
                    if "clinicalAdmissionContract" in row
                    else set()
                ),
            )
            self.assertIn(row["status"], statuses)
            self.assertEqual(len(row["profiles"]), len(set(row["profiles"])))
            if row["status"] == "supported":
                self.assertTrue(row["measurementIDs"])
                self.assertTrue(row["profiles"])
            elif row["status"] == "platform-exclusive":
                self.assertTrue(row["profiles"])
            else:
                self.assertIsInstance(row.get("requirement"), str)
                self.assertTrue(row["requirement"])

    def test_producer_numeric_canonicalization_reuses_the_mobile_contract(self) -> None:
        # The percent vectors are checked against the rule they pin below.
        self.assertEqual(
            {
                key: value for key, value in self.catalog["producerCanonicalization"].items()
                if key != "percentScalingVectors"
            },
            {
                "mobileEffectiveContract": "catalog/measurement-catalog.json#effectiveCanonicalization",
                "effectivePrecision": "millisecond",
                "effectiveRounding": "half-even",
                "scalarQuantityDecimal": "shortest-round-trip",
                "percentScaling": "shortest-round-trip-decimal-shift-rounded-once",
                "identityPreimages": "unmodified",
                "sensorAndEcgTiming": "excluded",
            },
        )
        self.assertEqual(
            self.mobile["effectiveCanonicalization"]["precision"], "millisecond"
        )
        self.assertEqual(
            self.mobile["effectiveCanonicalization"]["rounding"], "half-even"
        )

    def test_an_interval_under_a_date_time_only_profile_keeps_its_start(self) -> None:
        mapping = (ROOT / "healthkit/input/pagecontent/mapping.md").read_text(encoding="utf-8")
        section = mapping.split("### Values, units, and time\n", 1)[1].split("\n### ", 1)[0]
        # The exception follows the interval rule it narrows, which stays as it was.
        self.assertIn(
            "Use `effectivePeriod` when HealthKit supplies a start and end that define an "
            "interval. Preserve fractional seconds and the numeric offset.\n"
            "Where the selected profile admits only `dateTime`, an interval sample states its "
            "`startDate` as `effectiveDateTime` and withholds its `endDate`.\n",
            section,
        )

    def test_percent_vectors_follow_the_rounded_decimal_shift(self) -> None:
        vectors = self.catalog["producerCanonicalization"]["percentScalingVectors"]
        for vector in vectors:
            with self.subTest(fraction=vector["fraction"]):
                # Each fraction is written as its own shortest round-trip decimal, the text step 1
                # starts from, and each percent is the result of the three steps.
                fraction = float(vector["fraction"])
                self.assertEqual(shortest_round_trip(fraction), vector["fraction"])
                self.assertEqual(percent_from_fraction(fraction), vector["percent"])

        # The vectors tell the rule apart from a binary64 product by 100 and from the shift of
        # step 2 emitted without the rounding of step 3.
        product_failures = {
            vector["fraction"] for vector in vectors
            if shortest_round_trip(float(vector["fraction"]) * 100) != vector["percent"]
        }
        unrounded_failures = {
            vector["fraction"] for vector in vectors
            if plain_decimal(Decimal(vector["fraction"]).scaleb(2)) != vector["percent"]
        }
        self.assertEqual(
            product_failures,
            {
                "0.0000001", "0.0007", "0.07", "0.14", "0.28", "0.282",
                "0.29", "0.5000076293945312", "0.55", "0.56", "0.57", "0.58",
            },
        )
        self.assertEqual(unrounded_failures, {"0.49543508709194095"})

    def test_a_percent_vector_pins_the_even_digit_of_two_equally_near_decimals(self) -> None:
        vectors = {
            vector["fraction"]: vector["percent"]
            for vector in self.catalog["producerCanonicalization"]["percentScalingVectors"]
        }
        fraction = 0.5 + 2 ** -17
        even, odd = "0.5000076293945312", "0.5000076293945313"
        # Both 16-digit decimals convert back to the fraction and lie equally near it, so only the
        # tie-break chooses step 1's decimal, and the two choices emit different percents.
        self.assertEqual(Decimal(fraction), Decimal("0.50000762939453125"))
        self.assertEqual({float(even), float(odd)}, {fraction})
        self.assertEqual(Decimal(odd) - Decimal(fraction), Decimal(fraction) - Decimal(even))
        self.assertEqual(vectors[even], "50.00076293945312")
        self.assertNotEqual(shortest_round_trip(float(Decimal(odd).scaleb(2))), vectors[even])

    def test_application_device_separates_opaque_snapshot_from_bundle_product(self) -> None:
        contract = self.catalog["applicationDeviceIdentity"]
        self.assertEqual(
            contract["profile"],
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-application-device",
        )
        self.assertEqual(contract["snapshotIdentifierRole"], "device-snapshot")
        self.assertEqual(
            contract["bundleIdentifier"],
            {
                "system": "https://grovealliance.org/fhir/healthkit/NamingSystem/apple-bundle-id",
                "typeSystem": "https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-identifier-type",
                "typeCode": "apple-bundle-id",
                "cardinality": "1..1",
                "meaning": "Exact Apple application product bundle identifier; never an installation, host, account, or person identifier.",
            },
        )
        self.assertIn("caller explicitly classifies", contract["classificationRule"])
        profiles = (ROOT / "healthkit/input/fsh/profiles.fsh").read_text(
            encoding="utf-8"
        )
        self.assertIn("Profile: HealthKitApplicationDevice", profiles)
        self.assertIn("identifier[appleBundleId].type", profiles)

    def test_source_application_states_its_build_and_shares_only_the_same_build(self) -> None:
        # HKSourceRevision.version is the source's CFBundleVersion: a build, never a release.
        contract = self.catalog["applicationDeviceIdentity"]
        self.assertIn("CFBundleVersion", contract["sourceBuildRule"])
        self.assertIn(
            "applicationBuild slice, never into applicationVersion", contract["sourceBuildRule"]
        )
        for condition in (
            "HKSource.bundleIdentifier equals that Device's Apple bundle identifier",
            "HKSourceRevision.version is supplied and equals, character for character, "
            "the build that Device states in applicationBuild",
            "the producer never reuses a build across releases of that bundle identifier",
            "every one compared with a converting application Device that states no build",
        ):
            with self.subTest(condition=condition):
                self.assertIn(condition, contract["sameApplicationRule"])
        mapping = (ROOT / "healthkit/input/pagecontent/mapping.md").read_text(encoding="utf-8")
        self.assertIn(
            "copy it unchanged into the typed application-build slice "
            "(`grove-application-version-type#build`), never into the application-version slice.",
            mapping,
        )
        self.assertNotIn("into the typed application-version slice", mapping)
        self.assertIn(
            "- `HKSource.bundleIdentifier` equals the converting application's Apple bundle "
            "identifier;\n"
            "- HealthKit supplies `HKSourceRevision.version`, and it equals, character for "
            "character, the build that the converting application's Device states in its "
            "application-build slice;\n"
            "- the producer never reuses a build across releases of that bundle identifier.\n",
            mapping,
        )
        self.assertIn("The same-application rule below is the only exception.", mapping)
        example = (ROOT / "healthkit/input/fsh/examples.fsh").read_text(encoding="utf-8")
        example = example.split("Instance: HealthKitSourceApplicationDeviceExample\n", 1)[1]
        example = example.split("\nInstance: ", 1)[0]
        self.assertIn(
            '* version[applicationBuild].type = $groveApplicationVersionType#build "Build"', example
        )
        self.assertNotIn("applicationVersion", example)
        terminology = (ROOT / "mobile/input/fsh/terminology.fsh").read_text(encoding="utf-8")
        self.assertIn(
            '#build "Build" "The build of the application the Device snapshot describes', terminology
        )

    def test_unclassified_source_revision_withholds_names_and_keeps_writer_identity(self) -> None:
        # A source entity without an author agent states its HKSourceRevision instead. The two
        # members that can name or identify a person's device need an explicit authorization.
        contract = self.catalog["sourceRevisionExtension"]
        url = "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-source-revision"
        self.assertEqual(contract["url"], url)
        self.assertEqual(
            [(member["url"], member["defaultDisclosure"]) for member in contract["members"]],
            [
                ("sourceName", "withheld"),
                ("sourceBundleIdentifier", "withheld"),
                ("version", "emitted"),
                ("productType", "emitted"),
                ("operatingSystemVersion", "emitted"),
            ],
        )
        self.assertIn("carried only under an explicit deployment authorization", contract["disclosureRule"])
        extensions = (ROOT / "healthkit/input/fsh/extensions.fsh").read_text(encoding="utf-8")
        extension = extensions.split("Extension: HealthKitSourceRevision\n", 1)[1]
        extension = extension.split("\nExtension: ", 1)[0]
        self.assertIn("Id: healthkit-source-revision\n", extension)
        self.assertIn(f"Context: {contract['r4Context']}\n", extension)
        self.assertEqual(
            re.findall(r"^    (\w+) 0[.][.]1 MS", extension, re.MULTILINE),
            [member["url"] for member in contract["members"]],
        )
        for member in contract["members"]:
            with self.subTest(member=member["url"]):
                self.assertIn(
                    f'* extension[{member["url"]}] ^short = "{member["sourceField"]}"', extension
                )
                self.assertIn(f'* extension[{member["url"]}].value[x] only string', extension)
        self.assertIn("* value[x] 0..0", extension)
        self.assertIn(
            "* extension[operatingSystemVersion].valueString obeys "
            "healthkit-source-revision-os-version-1",
            extension,
        )
        profiles = (ROOT / "healthkit/input/fsh/profiles.fsh").read_text(encoding="utf-8")
        provenance = profiles.split("Profile: HealthKitConversionProvenance\n", 1)[1]
        provenance = provenance.split("\nProfile: ", 1)[0]
        self.assertIn("* obeys healthkit-source-revision-writer-1\n", provenance)
        self.assertIn(
            "* entity.extension contains HealthKitSourceRevision named sourceRevision 0..1 MS",
            provenance,
        )
        # Never beside an author agent.
        writer = profiles.split("Invariant: healthkit-source-revision-writer-1\n", 1)[1]
        writer = writer.split("\n\n", 1)[0]
        self.assertIn(
            f"Expression: \"entity.all(extension('{url}').empty() or agent.where(type.coding.where("
            "system = 'http://terminology.hl7.org/CodeSystem/provenance-participant-type' and "
            "code = 'author').exists()).empty())\"\nSeverity: #error",
            writer,
        )
        # All three components always appear: 26.5.0, never 26.5.
        version = profiles.split("Invariant: healthkit-source-revision-os-version-1\n", 1)[1]
        version = version.split("\n\n", 1)[0]
        self.assertIn("Severity: #error", version)
        expression = version.split('Expression: "', 1)[1].split('"', 1)[0]
        match = re.fullmatch(r"[$]this[.]matches[(]'\^(.+)\$'[)]", expression)
        form = re.compile(match.group(1))
        for text in ("26.5.0", "0.0.0", "17.10.3", "8.2.0", "-1.0.0"):
            with self.subTest(admitted=text):
                self.assertIsNotNone(form.fullmatch(text))
        for text in ("26.5", "26.05.0", "-0.0.0", "+26.5.0", "26.5.0.1", " 26.5.0", "26.5.x"):
            with self.subTest(rejected=text):
                self.assertIsNone(form.fullmatch(text))
        mapping = (ROOT / "healthkit/input/pagecontent/mapping.md").read_text(encoding="utf-8")
        section = mapping.split("### Unclassified source revision\n", 1)[1].split("\n### ", 1)[0]
        for member in contract["members"]:
            with self.subTest(row=member["url"]):
                row = next(
                    line for line in section.splitlines() if line.startswith(f"| `{member['url']}` |")
                )
                self.assertTrue(row.endswith(f"| {member['defaultDisclosure']} |"))
        for sentence in (
            "The extension never appears beside an author agent",
            "`sourceName` and `sourceBundleIdentifier` are withheld by default: a producer carries "
            "them only under an explicit deployment authorization",
            "`version`, `productType`, and `operatingSystemVersion` are emitted by default.",
            "all three always appear, so `26.5.0` is never written `26.5`",
            "for a sample from every source, whether the caller classified it as an application, as "
            "a device, or not at all, the writing-application Identifier pair from which the "
            "[revision rules](#logical-identity-and-revisions) derive the `writer-record` "
            "Identifier is the [Apple Bundle Identifier](NamingSystem-apple-bundle-id.html) "
            "namespace with `HKSource.bundleIdentifier`.",
            # An author decides nothing about the writer-record Identifier, whose carriage the
            # revision and withheld-metadata rules decide; a Recording Document carries none.
            "Whether a graph states an author therefore never decides whether its outputs carry "
            "the sample's `writer-record` Identifier and version; the [revision rules]"
            "(#logical-identity-and-revisions) and the [withheld-metadata rules]"
            "(#withheld-metadata) decide that, and withholding `sourceBundleIdentifier` does not "
            "withhold them.",
            # Changed content still takes a new event and new event-scoped identities.
            "changes no Identifier that is not event-scoped, such as a `source-record`, "
            "`source-output`, or `writer-record` Identifier.",
            "is still changed content: it receives a new event sequence and with it new "
            "event-scoped identities",
        ):
            with self.subTest(sentence=sentence):
                self.assertIn(sentence, section)
        self.assertIn(
            "For a sample from every source, whatever the caller's classification, the "
            "writing-application Identifier pair of the writer-record Identifier is the Apple "
            "Bundle Identifier system with HKSource.bundleIdentifier.",
            contract["identityRule"],
        )

    def test_platform_additions_and_derived_aggregate_are_explicit(self) -> None:
        rows = {row["sourceTypeIdentifier"]: row for row in self.catalog["rows"]}
        # This was the one screening notification refused while its eleven peers
        # were supported, and the row carried no rationale for the difference; the notification
        # contract states only that the notification was raised, never a diagnosis.
        hypertension = rows["HKCategoryTypeIdentifierHypertensionEvent"]
        self.assertEqual(hypertension["status"], "supported")
        self.assertEqual(hypertension["measurementIDs"], ["hypertension-notification"])

        renamed = rows["HKCategoryTypeIdentifierAudioExposureEvent"]
        self.assertEqual(renamed["title"], "Audio Exposure Event")
        self.assertIn(
            "HKCategoryTypeIdentifierEnvironmentalAudioExposureEvent",
            renamed["symbols"],
        )

        aggregates = self.catalog["derivedAggregates"]
        self.assertEqual(len(aggregates), 1)
        self.assertEqual(
            aggregates[0],
            {
                "id": "sleep-duration-session-aggregate",
                "title": "Sleep Duration Session Aggregate",
                "sourceTypeIdentifiers": ["HKCategoryTypeIdentifierSleepAnalysis"],
                "scope": "derived-from-platform-samples",
                "status": "deferred",
                "measurementIDs": ["sleep-duration"],
                "profiles": [
                    "https://grovealliance.org/fhir/mobile/StructureDefinition/"
                    "grove-mobile-sleep-duration"
                ],
                "requirement": (
                    "This is not a HealthKit platform source identifier. The Grove "
                    "FHIR contracts do not define the session-boundary aggregation contract; "
                    "individual admitted samples map only to sleep stage."
                ),
            },
        )

    def test_profile_relocation_and_standard_bmi_claim_are_exact(self) -> None:
        self.assertEqual(
            self.catalog["sourceTypeExtension"],
            {
                "url": "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-source-type",
                "valueSystem": "https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-source-type",
                "valueElement": "valueCode",
                "cardinality": "exactly one",
                "contexts": [
                    "Observation",
                    "DocumentReference",
                    "VisionPrescription",
                    "MedicationAdministration",
                    "MedicationStatement",
                ],
                "rule": "Every admitted HealthKit output preserves its exact sourceTypeIdentifier in this lineage extension. Observation.code and DocumentReference.type remain clinical or document concepts; the HealthKit SDK source class is not asserted as an equivalent coding of either meaning.",
            },
        )
        self.assertEqual(
            self.catalog["conversionProvenanceProfile"],
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-conversion-provenance",
        )
        old_suffixes = tuple(f"/{profile}" for profile in OLD_MOBILE)
        for row in self.catalog["rows"]:
            self.assertFalse(any(profile.endswith(old_suffixes) for profile in row["profiles"]))
        bmi_claim = self.catalog["standardAdapterClaims"]["body-mass-index"]
        self.assertEqual(
            bmi_claim["profiles"],
            [
                "http://hl7.org/fhir/StructureDefinition/bmi",
                "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-observation",
            ],
        )
        bmi_row = next(
            row for row in self.catalog["rows"]
            if row["sourceTypeIdentifier"] == "HKQuantityTypeIdentifierBodyMassIndex"
        )
        self.assertEqual(bmi_row["profiles"], bmi_claim["profiles"])
        glucose = next(
            row for row in self.catalog["rows"]
            if row["sourceTypeIdentifier"] == "HKQuantityTypeIdentifierBloodGlucose"
        )
        self.assertEqual(glucose["status"], "supported")
        self.assertEqual(
            glucose["measurementIDs"], ["blood-glucose-unspecified-specimen"]
        )
        ecg = next(
            row for row in self.catalog["rows"]
            if row["sourceTypeIdentifier"] == "HKDataTypeIdentifierElectrocardiogram"
        )
        self.assertEqual(ecg["status"], "supported")
        self.assertEqual(
            ecg["profiles"],
            self.catalog["sensorAdapterClaims"]["electrocardiogram"]["profiles"],
        )
        self.assertEqual(ecg["measurementIDs"], ["electrocardiogram"])
        self.assertIn("timeSinceSampleStart", ecg["requirement"])
        self.assertIn("without fetching or resampling", ecg["requirement"])
        contract = self.catalog["sensorAdapterClaims"]["electrocardiogram"]
        self.assertIn(
            "offset[i] = offset[0] + i * SampledData.period",
            contract["admissionRule"],
        )
        self.assertIn("every voltage is present", contract["admissionRule"])
        symptom = contract["correlatedSymptomEvidence"]
        self.assertEqual(symptom["cardinality"], "0..*")
        self.assertIn("Observation.hasMember", symptom["r4Element"])
        self.assertEqual(len(symptom["sourceTypes"]), 7)
        self.assertIn("source-output Identifier", symptom["rule"])
        self.assertIn("own event Bundle", symptom["exchangeRule"])
        self.assertIn("normal HealthKit", symptom["sourceRevisionRule"])
        self.assertNotIn("authorization", json.dumps(contract).lower())
        self.assertEqual(
            [item["outputRole"] for item in contract["outputs"]],
            ["electrocardiogram", "average-heart-rate"],
        )
        self.assertEqual(
            contract["outputs"][1]["code"],
            {"system": "http://loinc.org", "code": "8867-4", "display": "Heart rate"},
        )
        self.assertIn("validation input only", contract["wireMapping"]["samplingFrequency"])
        self.assertIn(
            "validation input only", contract["wireMapping"]["numberOfVoltageMeasurements"]
        )
        graph = self.claims["healthKitEcgGraphClaim"]
        self.assertEqual(
            graph["averageHeartRate"]["reference"],
            {
                "sourceOutput": "average-heart-rate",
                "r4Path": "Observation.derivedFrom",
                "targetOutput": "electrocardiogram",
                "targetType": "Observation",
                "referenceShape": "resolving-literal",
                "min": 1,
                "max": 1,
            },
        )
        self.assertFalse(graph["correlatedSymptoms"]["sameEventBundle"])
        self.assertEqual(
            graph["correlatedSymptoms"]["statusConditionedCardinality"],
            [
                {"status": "notSet", "min": 0, "max": 0},
                {"status": "none", "min": 0, "max": 0},
                {"status": "present", "min": 1, "max": "*"},
            ],
        )
        examples = (ROOT / "healthkit/input/fsh/examples.fsh").read_text(
            encoding="utf-8"
        )
        average_example = examples.split(
            "Instance: HealthKitECGAverageHeartRateExample", 1
        )[1].split("\nInstance:", 1)[0]
        self.assertIn(
            '* category = $observationCategory#vital-signs "Vital Signs"',
            average_example,
        )
        self.assertIn(
            "* derivedFrom = Reference(HealthKitECGObservationExample)",
            average_example,
        )
        terminology = (ROOT / "healthkit/input/fsh/terminology.fsh").read_text(encoding="utf-8")
        for mapping in contract["closedValueMappings"].values():
            for value in mapping["values"]:
                self.assertIn(f"* #{value['code']} ", terminology)
        self.assertIn("startDate/endDate", contract["effectiveRule"])

    def test_sync_revision_metadata_is_an_exact_fail_closed_pair(self) -> None:
        revision = self.catalog["identity"]["writerRecord"]["revision"]
        self.assertEqual(revision["sourceIdentifier"], "HKMetadataKeySyncIdentifier")
        self.assertEqual(revision["sourceVersion"], "HKMetadataKeySyncVersion")
        self.assertEqual(revision["presenceRule"], "both-or-neither")
        self.assertEqual(revision["versionMinimum"], 0)
        self.assertNotIn("versionMaximum", revision)
        self.assertEqual(revision["invalidDisposition"], "reject-source-record")
        self.assertIn("non-empty String", revision["identifierRule"])
        self.assertIn("canonical unsigned decimal", revision["versionRule"])
        mapping = (ROOT / "healthkit/input/pagecontent/mapping.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("MUST reject either half-pair", mapping)
        self.assertIn("MUST NOT fabricate version `0`", mapping)

    def test_blood_pressure_objects_supply_what_the_correlation_does_not_state(self) -> None:
        mapping = (ROOT / "healthkit/input/pagecontent/mapping.md").read_text(encoding="utf-8")
        heading = "Blood-pressure correlation objects"
        headings = [line[4:] for line in mapping.splitlines() if line.startswith("### ")]
        index = headings.index(heading)
        self.assertEqual(
            headings[index - 1 : index + 2],
            ["Capture mode and performer", heading, "Device, application, and provenance"],
        )
        section = mapping.split(f"### {heading}\n", 1)[1].split("\n### ", 1)[0]
        quoted = set(section.split("`")[1::2])
        # Scope: the catalog's two correlation rows, blood pressure in and food out, because a
        # food correlation's objects convert to Observations of their own.
        correlations = {
            row["sourceTypeIdentifier"] for row in self.catalog["rows"]
            if row["sourceTypeIdentifier"].startswith("HKCorrelationTypeIdentifier")
        }
        self.assertEqual({name for name in quoted if name in correlations}, correlations)
        self.assertIn("does not apply to an `HKCorrelationTypeIdentifierFood` correlation", section)
        # Every code the section names is registered.
        registered = {row["code"] for row in self.protocol["producerDiagnostics"]}
        codes = {name for name in quoted if name.startswith("mobile-")}
        self.assertEqual(
            codes,
            {
                "mobile-omission.source-offset",
                "mobile-input.unsupported-source-value",
                "mobile-omission.recording-method",
                "mobile-omission.unmodeled-metadata",
            },
        )
        self.assertLessEqual(codes, registered)
        for rule in (
            "Use the correlation's `HKMetadataKeyTimeZone` when it carries one, and consult no "
            "object's.",
            "every object that carries one carries the same name, compared character for character",
            "or two objects carry different names, even a link and its target",
            "when an object's consulted value is not a valid IANA time-zone name, even when other "
            "objects carry a valid one.",
            "When the correlation states `HKMetadataKeyWasUserEntered`, its value decides",
            "Otherwise set `manual-entry` when there is at least one object and every object "
            "states `true`",
            "When the correlation or an object states `true` and the Observation carries no "
            "`grove-recording-method` extension, report `mobile-omission.recording-method`.",
            "report the keys withheld from the correlation and its objects as "
            "`mobile-omission.unmodeled-metadata`, naming each key once",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, section)
        # What states the flag is defined once for every sample, so a correlation's 2 defers.
        capture = mapping.split("### Capture mode and performer\n", 1)[1].split("\n### ", 1)[0]
        self.assertIn("any other value, such as 2, states nothing", capture)

    def test_withheld_metadata_follows_what_the_outputs_carry(self) -> None:
        mapping = (ROOT / "healthkit/input/pagecontent/mapping.md").read_text(encoding="utf-8")
        heading = "Withheld metadata"
        headings = [line[4:] for line in mapping.splitlines() if line.startswith("### ")]
        index = headings.index(heading)
        self.assertEqual(
            headings[index - 1 : index + 2],
            ["Supported HealthKit metadata", heading, "Study context"],
        )
        section = mapping.split(f"### {heading}\n", 1)[1].split("\n### ", 1)[0]
        table, constants = {}, {}
        for line in section.splitlines():
            if line.startswith("| `"):
                key, constant, source_types, _ = (
                    cell.strip() for cell in line.strip("|").split("|")
                )
                key, constant = key.strip("`"), constant.strip("`")
                self.assertNotIn(key, table)
                table[key] = ", ".join(name.strip().strip("`") for name in source_types.split(","))
                constants[key] = constant
        # A row names the key by the string the constant holds in an iOS 26.5 simulator on the SDK
        # baseline; these seven hold another string than their constant's name.
        self.assertEqual(
            {key: constant for key, constant in constants.items() if key != constant},
            {
                "HKTimeZone": "HKMetadataKeyTimeZone",
                "HKWasUserEntered": "HKMetadataKeyWasUserEntered",
                "HKHeartRateEventThreshold": "HKMetadataKeyHeartRateEventThreshold",
                "HKLowCardioFitnessEventThreshold": "HKMetadataKeyLowCardioFitnessEventThreshold",
                "HKInsulinDeliveryReason": "HKMetadataKeyInsulinDeliveryReason",
                "HKMenstrualCycleStart": "HKMetadataKeyMenstrualCycleStart",
                "HKSexualActivityProtectionUsed": "HKMetadataKeySexualActivityProtectionUsed",
            },
        )
        every = "every type with an Observation output"
        self.assertEqual(
            {key: source_types for key, source_types in table.items() if source_types != every},
            {
                "HKMetadataKeyHeartRateMotionContext": "HKQuantityTypeIdentifierHeartRate",
                "HKHeartRateEventThreshold": (
                    "HKCategoryTypeIdentifierHighHeartRateEvent, "
                    "HKCategoryTypeIdentifierLowHeartRateEvent"
                ),
                "HKLowCardioFitnessEventThreshold": "HKCategoryTypeIdentifierLowCardioFitnessEvent",
                "HKMetadataKeyAppleECGAlgorithmVersion": "HKDataTypeIdentifierElectrocardiogram",
                "HKInsulinDeliveryReason": "HKQuantityTypeIdentifierInsulinDelivery",
                "HKMenstrualCycleStart": "HKCategoryTypeIdentifierMenstrualFlow",
                "HKSexualActivityProtectionUsed": "HKCategoryTypeIdentifierSexualActivity",
            },
        )
        self.assertEqual(
            {key for key, source_types in table.items() if source_types == every},
            {
                "HKTimeZone",
                "HKWasUserEntered",
                "HKMetadataKeySyncIdentifier",
                "HKMetadataKeySyncVersion",
            },
        )
        rows = {row["sourceTypeIdentifier"]: row for row in self.catalog["rows"]}
        listed = {
            source_type
            for source_types in table.values() if source_types != every
            for source_type in source_types.split(", ")
        }
        for source_type in listed:
            self.assertEqual(rows[source_type]["status"], "supported")
        # A notification's threshold component carries the threshold key its samples hold, so the
        # table lists that key for every supported type whose measurement has the component, and a
        # threshold that an output carries is represented rather than withheld and reported.
        measurements = {row["id"]: row for row in self.mobile["measurements"]}
        thresholds = {
            row["sourceTypeIdentifier"]
            for row in self.catalog["rows"] if row["status"] == "supported"
            for measurement in row["measurementIDs"]
            # A row may name a measurement outside the Mobile catalog, such as the electrocardiogram.
            for component in measurements.get(measurement, {}).get("components") or []
            if component["id"] == "threshold"
        }
        self.assertEqual(
            thresholds,
            {
                *table["HKHeartRateEventThreshold"].split(", "),
                table["HKLowCardioFitnessEventThreshold"],
            },
        )
        # Every key of HealthKit Metadata Keys has a row, and the supported-metadata count agrees.
        terminology = (ROOT / "healthkit/input/fsh/terminology.fsh").read_text(encoding="utf-8")
        key_system = terminology.split("CodeSystem: HealthKitMetadataKeyCS\n", 1)[1].split("\n\n", 1)[0]
        codes = {line.split()[1][1:] for line in key_system.splitlines() if line.startswith("* #")}
        self.assertEqual(len(codes), 5)
        self.assertLessEqual(codes, set(table))
        self.assertIn("Of the five keys in [HealthKit Metadata Keys]", mapping)
        self.assertNotIn("residual key", mapping)
        reasons = {row["code"]: row["reason"] for row in self.protocol["producerDiagnostics"]}
        self.assertEqual(
            reasons["mobile-omission.unmodeled-metadata"],
            "The source record, or a part of it, carries metadata that no output of its graph "
            "represents, so the producer withholds those fields.",
        )
        for rule in (
            "is represented only by the element that this table gives it, for the source types the "
            "table names, and only when an output of the record's graph carries the key's value in "
            "that element.",
            "and report those keys as `mobile-omission.unmodeled-metadata`, naming each key once by "
            "its runtime key.",
            "A runtime key is the string that a metadata dictionary holds as the key, as the table's "
            "first column gives it, not the name of the SDK constant that holds it, which can "
            "differ: `HKMetadataKeyTimeZone` holds `HKTimeZone`.",
            "A key that no SDK constant declares is named the same way.",
            "a key it lists only for other source types, and a listed key whose element no output "
            "carries.",
            "`HKMetadataKeyWasUserEntered` stating `false`, whether the record or a part of it "
            "carries it, maps to no element",
            "and is never reported; a value that states nothing is reported.",
            "represents no key, not even a valid sync pair.",
            "an object of a blood-pressure correlation or an `HKWorkoutEvent` or "
            "`HKWorkoutActivity` of a workout, is represented only when the record itself carries "
            "the same key with an equal value that its graph represents",
            "time-zone names or sync identifiers that match character for character, user-entered "
            "flags that state the same thing, or sync versions that are the same number.",
            "decide instead what a blood-pressure object's `HKMetadataKeyTimeZone` and "
            "`HKMetadataKeyWasUserEntered` contribute.",
            "a half or invalid sync pair that the record itself carries rejects the record even "
            "when no output could carry the pair.",
            "a key that a disclosure policy withholds is not reported.",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, section)
        # Every in-page link of the section names a heading of this page.
        anchors = {
            "".join(c for c in name.lower() if c.isalnum() or c in " -").replace(" ", "-")
            for name in headings
        }
        links = {part.split(")", 1)[0] for part in section.split("](#")[1:]}
        self.assertEqual(len(links), 5)
        self.assertLessEqual(links, anchors)

    def test_insulin_delivery_reason_is_a_required_component_coded_by_its_key(self) -> None:
        base = "https://grovealliance.org/fhir/healthkit/"
        key_system = base + "CodeSystem/healthkit-metadata-key"
        reasons = base + "ValueSet/healthkit-insulin-delivery-reason"
        terminology = (ROOT / "healthkit/input/fsh/terminology.fsh").read_text(encoding="utf-8")
        blocks = {block.split("\n", 1)[0]: block.splitlines() for block in terminology.split("\n\n")}
        # The code is the key the constant holds, and its definition names the constant.
        concept = [
            line for line in blocks["CodeSystem: HealthKitMetadataKeyCS"]
            if line.startswith("* #HKInsulinDeliveryReason ")
        ]
        self.assertEqual(len(concept), 1)
        self.assertIn("the constant HKMetadataKeyInsulinDeliveryReason holds", concept[0])
        # The bound value set admits exactly the existing delivery-reason codes, under the name
        # the generated profile binds.
        value_set = blocks["ValueSet: HealthkitInsulinDeliveryReasonVS"]
        self.assertIn("Id: healthkit-insulin-delivery-reason", value_set)
        self.assertEqual(
            [line for line in value_set if line.startswith("* ")],
            [
                "* ^experimental = false",
                "* include codes from system HealthKitInsulinDeliveryReasonCS",
            ],
        )
        cases = {
            line.split()[1][1:]: line.split('"')[1]
            for line in blocks["CodeSystem: HealthKitInsulinDeliveryReasonCS"]
            if line.startswith("* #")
        }
        self.assertEqual(cases, {"basal": "Basal", "bolus": "Bolus"})
        measurement = next(m for m in self.mobile["measurements"] if m["id"] == "insulin-delivery")
        self.assertEqual(
            measurement["components"],
            [
                {
                    "id": "insulinDeliveryReason",
                    "system": key_system,
                    "code": "HKInsulinDeliveryReason",
                    "cardinality": "1..1",
                    "valueSet": reasons,
                }
            ],
        )
        generated = (ROOT / "healthkit/input/fsh/generated-measurement-profiles.fsh").read_text(
            encoding="utf-8"
        )
        rendered = {block.split("\n", 1)[0]: block.splitlines() for block in generated.split("\n\n")}
        coded = f"* component[insulinDeliveryReason].code = {key_system}#HKInsulinDeliveryReason"
        for rule in (
            "* component contains insulinDeliveryReason 1..1 MS",
            coded,
            "* component[insulinDeliveryReason].valueCodeableConcept 1..1 MS",
            "* component[insulinDeliveryReason].valueCodeableConcept from "
            "HealthkitInsulinDeliveryReasonVS (required)",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, rendered["Profile: HealthkitInsulinDelivery"])
        self.assertIn(coded, rendered["Instance: HealthkitInsulinDeliveryExample"])
        # The page maps each raw value to one of those codes and admits nothing else.
        mapping = (ROOT / "healthkit/input/pagecontent/mapping.md").read_text(encoding="utf-8")
        section = mapping.split("### Supported HealthKit metadata\n", 1)[1].split("\n### ", 1)[0]
        opening = (
            "Another is carried as an adapter-coded component: "
            "`HKMetadataKeyInsulinDeliveryReason`.\n"
        )
        insulin = section.split(opening, 1)[1]
        rows = [
            [cell.strip().strip("`") for cell in line.strip("|").split("|")]
            for line in insulin.splitlines()
            if line.startswith("| `") and not line.startswith("| `HK")
        ]
        self.assertEqual(rows, [["1", "basal", "Basal"], ["2", "bolus", "Bolus"]])
        self.assertEqual({code: display for _, code, display in rows}, cases)
        for rule in (
            "is represented by the required `Observation.component:insulinDeliveryReason` slice",
            "The component's code is `HKInsulinDeliveryReason`, the key that the constant "
            "`HKMetadataKeyInsulinDeliveryReason` holds",
            "A sample that does not carry the key, or carries a value the table does not map, is "
            "rejected; the component is never omitted and a reason is never inferred.",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, insulin)

    def test_mobile_healthkit_coverage_is_bidirectional(self) -> None:
        supported_rows: dict[str, list[str]] = {}
        for row in self.catalog["rows"]:
            if row["status"] != "supported":
                continue
            for measurement_id in row["measurementIDs"]:
                supported_rows.setdefault(measurement_id, []).append(
                    row["sourceTypeIdentifier"]
                )
        shared = {item["id"]: item for item in self.mobile["measurements"]}
        for measurement_id, measurement in shared.items():
            if measurement["coverage"]["healthkit"] == "supported":
                self.assertIn(measurement_id, supported_rows)
        adapter_only = (
            set(self.catalog["standardAdapterClaims"])
            | set(self.catalog["sensorAdapterClaims"])
        )
        self.assertEqual(set(supported_rows) - set(shared), adapter_only)
        for measurement_id in set(supported_rows) & set(shared):
            self.assertEqual(shared[measurement_id]["coverage"]["healthkit"], "supported")


if __name__ == "__main__":
    unittest.main()
