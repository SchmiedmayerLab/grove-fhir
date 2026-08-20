"""Keep each published package limited to its explicitly reviewed artifact surface."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import re
import tarfile
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = ROOT / "publication/artifact-allowlist.json"
PUBLIC_DECLARATION = re.compile(
    r"^(Profile|Extension|Logical|Resource|CodeSystem|ValueSet|Instance):\s+(\S+)",
    re.MULTILINE,
)
INSTANCE_BLOCK = re.compile(
    r"^Instance:\s+(?P<name>\S+)(?P<body>.*?)(?=^(?:Profile|Extension|Logical|Resource|"
    r"CodeSystem|ValueSet|Instance|Invariant|RuleSet|Mapping|Alias):|\Z)",
    re.MULTILINE | re.DOTALL,
)
USAGE = re.compile(r"^Usage:\s+#(definition|example)\s*$", re.MULTILINE)
FHIR_ID = re.compile(r"^[A-Za-z0-9.-]{1,64}$")
ARTIFACT_KEYS = {"fshName", "fshType", "resourceType", "id", "classification"}
HEALTH_CONNECT_RECORD_SYSTEM = (
    "https://grovealliance.org/fhir/health-connect/"
    "NamingSystem/health-connect-record-id"
)
HEALTH_CONNECT_OUTPUT_SYSTEM = (
    "https://grovealliance.org/fhir/health-connect/"
    "NamingSystem/health-connect-output-id"
)


def scalar_configuration(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^([A-Za-z][A-Za-z0-9-]*):\s+(.+?)\s*$", line)
        if match:
            values[match.group(1)] = match.group(2).strip('"')
    return values


def fsh_declarations(source: str) -> dict[tuple[str, str], str]:
    declarations: dict[tuple[str, str], str] = {}
    for path in sorted((ROOT / source / "input/fsh").rglob("*.fsh")):
        text = path.read_text(encoding="utf-8")
        instance_usage = {}
        for match in INSTANCE_BLOCK.finditer(text):
            usage = USAGE.search(match.group("body"))
            if usage is None:
                raise AssertionError(
                    f"{path.relative_to(ROOT)} instance {match.group('name')} must declare Usage"
                )
            instance_usage[match.group("name")] = usage.group(1)
        for fsh_type, name in PUBLIC_DECLARATION.findall(text):
            key = (fsh_type, name)
            if key in declarations:
                raise AssertionError(f"duplicate FSH declaration in {source}: {fsh_type} {name}")
            declarations[key] = (
                instance_usage[name] if fsh_type == "Instance" else "definition"
            )
    return declarations


def package_contents(
    archive_path: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], set[tuple[str, str, str]]]:
    with tarfile.open(archive_path, "r:gz") as archive:
        metadata_file = archive.extractfile("package/package.json")
        index_file = archive.extractfile("package/.index.json")
        if metadata_file is None or index_file is None:
            raise AssertionError(f"{archive_path} has no FHIR package metadata and index")
        metadata = json.load(metadata_file)
        index = json.load(index_file)
        examples: set[tuple[str, str, str]] = set()
        for member in archive.getmembers():
            path = Path(member.name)
            if (
                not member.isfile()
                or path.parent.as_posix() != "package/example"
                or path.suffix != ".json"
                or path.name == ".index.json"
            ):
                continue
            resource_file = archive.extractfile(member)
            if resource_file is None:
                raise AssertionError(f"cannot read packaged example {member.name}")
            resource = json.load(resource_file)
            resource_type = resource.get("resourceType")
            resource_id = resource.get("id")
            if not isinstance(resource_type, str) or not isinstance(resource_id, str):
                raise AssertionError(f"packaged example {member.name} has no resourceType/id")
            identity = (resource_type, resource_id, path.name)
            if identity in examples:
                raise AssertionError(f"duplicate packaged example {identity}")
            examples.add(identity)
    if index.get("index-version") != 2 or not isinstance(index.get("files"), list):
        raise AssertionError(f"{archive_path} has an unsupported package index")
    return metadata, index["files"], examples


class ArtifactAllowlistTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.allowlist = json.loads(ALLOWLIST.read_text(encoding="utf-8"))
        cls.packages = cls.allowlist.get("packages")
        if cls.allowlist.get("schemaVersion") != 1 or not isinstance(cls.packages, list):
            raise AssertionError("artifact allowlist must use schemaVersion 1 and list packages")

    def test_packages_match_the_active_publication(self) -> None:
        publication = json.loads(
            (ROOT / "publication/config.json").read_text(encoding="utf-8")
        )
        publication_by_source = {
            guide["source"]: guide for guide in publication["guides"]
        }
        allowlist_by_source = {
            package["source"]: package for package in self.packages
        }
        self.assertEqual(
            len(publication_by_source),
            len(publication["guides"]),
            "duplicate active publication source",
        )
        self.assertEqual(len(allowlist_by_source), len(self.packages), "duplicate package source")
        self.assertEqual(allowlist_by_source.keys(), publication_by_source.keys())

        for source, package in allowlist_by_source.items():
            self.assertEqual(
                set(package), {"source", "packageId", "canonical", "artifacts"}
            )
            configuration = scalar_configuration(ROOT / source / "sushi-config.yaml")
            expected_canonical = (
                f"{publication['canonicalBaseUrl'].rstrip('/')}/"
                f"{publication_by_source[source]['canonicalPath']}"
            )
            self.assertEqual(package["packageId"], configuration.get("id"))
            self.assertEqual(package["canonical"], configuration.get("canonical"))
            self.assertEqual(package["canonical"], expected_canonical)
            representative = publication_by_source[source].get("representativeResource")
            self.assertIsInstance(representative, str)
            representative_parts = representative.split("/", 1)
            self.assertEqual(
                len(representative_parts),
                2,
                f"invalid representative resource for {source}",
            )
            definitions = {
                (artifact["resourceType"], artifact["id"])
                for artifact in package["artifacts"]
                if artifact["classification"] == "definition"
            }
            self.assertIn(
                tuple(representative_parts),
                definitions,
                f"representative resource for {source} is not an allowlisted definition",
            )

    def test_every_public_fsh_declaration_is_allowlisted_once(self) -> None:
        for package in self.packages:
            source = package["source"]
            artifacts = package.get("artifacts")
            self.assertIsInstance(artifacts, list)
            allowlisted: dict[tuple[str, str], str] = {}
            resource_identities: set[tuple[str, str]] = set()
            for artifact in artifacts:
                self.assertEqual(set(artifact), ARTIFACT_KEYS)
                key = (artifact["fshType"], artifact["fshName"])
                self.assertNotIn(key, allowlisted, f"duplicate allowlist declaration: {key}")
                self.assertIn(artifact["classification"], {"definition", "example"})
                self.assertRegex(artifact["id"], FHIR_ID)
                identity = (artifact["resourceType"], artifact["id"])
                self.assertNotIn(
                    identity,
                    resource_identities,
                    f"duplicate resource identity in {source}: {identity}",
                )
                allowlisted[key] = artifact["classification"]
                resource_identities.add(identity)

            self.assertEqual(allowlisted, fsh_declarations(source))
            self.assertTrue(allowlisted)

    def test_sushi_output_matches_the_allowlist_when_present(self) -> None:
        for package in self.packages:
            source = package["source"]
            index_path = ROOT / source / "fsh-generated/data/fsh-index.json"
            if not index_path.is_file():
                continue
            expected = {
                (artifact["fshType"], artifact["fshName"]): artifact
                for artifact in package["artifacts"]
            }
            actual = json.loads(index_path.read_text(encoding="utf-8"))
            self.assertEqual(
                {(entry["fshType"], entry["fshName"]) for entry in actual},
                expected.keys(),
            )
            for entry in actual:
                artifact = expected[(entry["fshType"], entry["fshName"])]
                expected_filename = f"{artifact['resourceType']}-{artifact['id']}.json"
                self.assertEqual(entry["outputFile"], expected_filename)
                resource = json.loads(
                    (ROOT / source / "fsh-generated/resources" / expected_filename).read_text(
                        encoding="utf-8"
                    )
                )
                self.assertEqual(resource.get("resourceType"), artifact["resourceType"])
                self.assertEqual(resource.get("id"), artifact["id"])

    def test_built_packages_contain_exactly_the_allowlisted_definitions(self) -> None:
        publication = json.loads(
            (ROOT / "publication/config.json").read_text(encoding="utf-8")
        )
        publication_by_source = {
            guide["source"]: guide for guide in publication["guides"]
        }
        for package in self.packages:
            source = package["source"]
            public_path = publication_by_source[source]["canonicalPath"]
            archives = (
                ROOT / source / "output/package.tgz",
                ROOT / ".build/pages" / public_path / "ci-build/package.tgz",
            )
            for archive in archives:
                if not archive.is_file():
                    continue
                metadata, entries, packaged_examples = package_contents(archive)
                configuration = scalar_configuration(ROOT / source / "sushi-config.yaml")
                self.assertEqual(metadata.get("name"), package["packageId"])
                self.assertEqual(metadata.get("version"), configuration.get("version"))
                self.assertEqual(metadata.get("canonical"), package["canonical"])
                implementation_guides = [
                    entry
                    for entry in entries
                    if entry.get("resourceType") == "ImplementationGuide"
                ]
                self.assertEqual(len(implementation_guides), 1)
                self.assertEqual(
                    implementation_guides[0].get("id"), package["packageId"]
                )
                expected = {
                    (
                        artifact["resourceType"],
                        artifact["id"],
                        f"{artifact['resourceType']}-{artifact['id']}.json",
                    )
                    for artifact in package["artifacts"]
                    if artifact["classification"] == "definition"
                }
                actual_rows = [
                    (entry.get("resourceType"), entry.get("id"), entry.get("filename"))
                    for entry in entries
                    if entry.get("resourceType") != "ImplementationGuide"
                ]
                actual = set(actual_rows)
                self.assertEqual(
                    len(actual), len(actual_rows), "duplicate package index entry"
                )
                self.assertEqual(actual, expected)
                expected_examples = {
                    (
                        artifact["resourceType"],
                        artifact["id"],
                        f"{artifact['resourceType']}-{artifact['id']}.json",
                    )
                    for artifact in package["artifacts"]
                    if artifact["classification"] == "example"
                }
                self.assertEqual(packaged_examples, expected_examples)

    def test_built_healthkit_package_carries_attribution_and_exact_mobile_dependency(
        self,
    ) -> None:
        archive_paths = (
            ROOT / "healthkit/output/package.tgz",
            ROOT / ".build/pages/fhir/healthkit/ci-build/package.tgz",
        )
        mobile_configuration = scalar_configuration(ROOT / "mobile/sushi-config.yaml")
        for archive_path in archive_paths:
            if not archive_path.is_file():
                continue
            with tarfile.open(archive_path, "r:gz") as archive:
                metadata_file = archive.extractfile("package/package.json")
                self.assertIsNotNone(metadata_file)
                metadata = json.load(metadata_file)
                self.assertEqual(
                    metadata.get("dependencies", {}).get(
                        mobile_configuration["id"]
                    ),
                    mobile_configuration["version"],
                )
                for resource_id in (
                    "healthkit-metadata-key",
                    "healthkit-heart-rate-motion-context",
                ):
                    resource_file = archive.extractfile(
                        f"package/CodeSystem-{resource_id}.json"
                    )
                    self.assertIsNotNone(resource_file)
                    resource = json.load(resource_file)
                    copyright_notice = resource.get("copyright", "")
                    self.assertIn("Apple Inc.", copyright_notice)
                    self.assertIn("MIT", copyright_notice)

    def test_healthkit_profile_is_result_shape_neutral(self) -> None:
        profile_path = (
            ROOT / "healthkit/output/StructureDefinition-healthkit-observation.json"
        )
        if not profile_path.is_file():
            self.skipTest("HealthKit Publisher output is not present")
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        constraints = {
            constraint["key"]: constraint["expression"]
            for element in profile["differential"]["element"]
            for constraint in element.get("constraint", [])
        }
        self.assertNotIn("healthkit-primary-result-1", constraints)
        self.assertIn("healthkit-sleep-stage-1", constraints)
        differential_ids = {
            element["id"] for element in profile["differential"]["element"]
        }
        self.assertNotIn("Observation.value[x]", differential_ids)
        self.assertNotIn("Observation.dataAbsentReason", differential_ids)

    def test_mobile_identifier_uniqueness_uses_an_unambiguous_pair(self) -> None:
        profile_path = (
            ROOT / "mobile/output/StructureDefinition-grove-mobile-observation.json"
        )
        if not profile_path.is_file():
            self.skipTest("Mobile Publisher output is not present")
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        constraints = {
            constraint["key"]: constraint["expression"]
            for element in profile["differential"]["element"]
            for constraint in element.get("constraint", [])
        }
        self.assertEqual(
            constraints.get("grove-identifier-token-1"),
            "identifier.select(system.length().toString() & ':' & system & "
            "value.length().toString() & ':' & value).isDistinct()",
        )

    def test_built_health_connect_package_has_exact_mobile_dependency(self) -> None:
        archive_paths = (
            ROOT / "health-connect/output/package.tgz",
            ROOT / ".build/pages/fhir/health-connect/ci-build/package.tgz",
        )
        mobile_configuration = scalar_configuration(ROOT / "mobile/sushi-config.yaml")
        for archive_path in archive_paths:
            if not archive_path.is_file():
                continue
            with tarfile.open(archive_path, "r:gz") as archive:
                metadata_file = archive.extractfile("package/package.json")
                self.assertIsNotNone(metadata_file)
                metadata = json.load(metadata_file)
                self.assertEqual(
                    metadata.get("dependencies", {}).get(mobile_configuration["id"]),
                    mobile_configuration["version"],
                )
                index_file = archive.extractfile("package/.index.json")
                self.assertIsNotNone(index_file)
                index = json.load(index_file)
                terminology = {
                    (entry["resourceType"], entry["id"])
                    for entry in index["files"]
                    if entry["resourceType"] in {"CodeSystem", "ValueSet"}
                }
                self.assertEqual(
                    terminology,
                    {
                        (resource_type, identifier)
                        for resource_type in ("CodeSystem", "ValueSet")
                        for identifier in (
                            "health-connect-meal-type",
                            "health-connect-record-type",
                            "health-connect-relation-to-meal",
                            "health-connect-sleep-stage",
                        )
                    },
                )

    def test_health_connect_profiles_preserve_both_identity_layers(self) -> None:
        profile_path = (
            ROOT
            / "health-connect/output/StructureDefinition-health-connect-observation.json"
        )
        provenance_path = (
            ROOT
            / "health-connect/output/StructureDefinition-health-connect-conversion-provenance.json"
        )
        if not profile_path.is_file() or not provenance_path.is_file():
            self.skipTest("Health Connect Publisher output is not present")

        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        differential = {
            element["id"]: element
            for element in profile["differential"]["element"]
        }
        self.assertEqual(
            differential["Observation.identifier:recordId"].get("min"), 1
        )
        self.assertEqual(
            differential["Observation.identifier:outputId"].get("min"), 1
        )
        self.assertEqual(differential["Observation.issued"].get("min"), 1)
        self.assertNotIn("Observation.value[x]", differential)
        self.assertNotIn("Observation.dataAbsentReason", differential)
        constraints = {
            constraint["key"]: constraint["expression"]
            for constraint in differential["Observation"].get("constraint", [])
        }
        self.assertEqual(
            constraints.get("health-connect-output-id-1"),
            "identifier.where(system = "
            "'https://grovealliance.org/fhir/health-connect/"
            "NamingSystem/health-connect-output-id').all("
            "value.matches('^v1:[0-9a-f]{64}$'))",
        )
        record_value_constraints = {
            constraint["key"]: constraint["expression"]
            for constraint in differential[
                "Observation.identifier:recordId.value"
            ].get("constraint", [])
        }
        self.assertEqual(
            record_value_constraints.get("health-connect-record-id-value-1"),
            "matches('^v1:[0-9a-f]{64}$')",
        )

        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        provenance_differential = {
            element["id"]: element
            for element in provenance["differential"]["element"]
        }
        source_system = provenance_differential[
            "Provenance.entity.what.identifier.system"
        ]
        self.assertEqual(
            source_system.get("patternUri"),
            "https://grovealliance.org/fhir/health-connect/"
            "NamingSystem/health-connect-record-id",
        )
        self.assertEqual(
            provenance_differential["Provenance.entity.what.reference"].get("max"),
            "0",
        )
        self.assertEqual(
            provenance_differential["Provenance.entity.agent.type"].get(
                "patternCodeableConcept"
            ),
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/"
                        "provenance-participant-type",
                        "code": "enterer",
                    }
                ]
            },
        )
        self.assertEqual(
            provenance_differential["Provenance.entity.agent.who"]["type"],
            [
                {
                    "code": "Reference",
                    "targetProfile": [
                        "http://hl7.org/fhir/StructureDefinition/Device"
                    ],
                }
            ],
        )

    def test_health_connect_heart_rate_outputs_share_only_source_identity(self) -> None:
        output = ROOT / "health-connect/output"
        paths = (
            output / "Observation-HealthConnectHeartRateSampleOneExample.json",
            output / "Observation-HealthConnectHeartRateSampleTwoExample.json",
        )
        if not all(path.is_file() for path in paths):
            self.skipTest("Health Connect Publisher examples are not present")
        observations = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
        by_system = [
            {identifier["system"]: identifier["value"] for identifier in observation["identifier"]}
            for observation in observations
        ]
        record_system = (
            "https://grovealliance.org/fhir/health-connect/"
            "NamingSystem/health-connect-record-id"
        )
        output_system = (
            "https://grovealliance.org/fhir/health-connect/"
            "NamingSystem/health-connect-output-id"
        )
        self.assertEqual(by_system[0][record_system], by_system[1][record_system])
        self.assertNotEqual(by_system[0][output_system], by_system[1][output_system])
        self.assertTrue(
            all(observation["effectiveDateTime"].endswith("Z") for observation in observations)
        )
        self.assertTrue(all("_effectiveDateTime" not in observation for observation in observations))

    def test_health_connect_provenance_uses_each_observations_source_identity(self) -> None:
        output = ROOT / "health-connect/output"
        cases = (
            (
                output / "Provenance-HealthConnectHeartRateProvenanceExample.json",
                (
                    output / "Observation-HealthConnectHeartRateSampleOneExample.json",
                    output / "Observation-HealthConnectHeartRateSampleTwoExample.json",
                ),
            ),
            (
                output / "Provenance-HealthConnectBodyWeightProvenanceExample.json",
                (output / "Observation-HealthConnectBodyWeightExample.json",),
            ),
            (
                output / "Provenance-HealthConnectStepCountProvenanceExample.json",
                (output / "Observation-HealthConnectStepCountExample.json",),
            ),
        )
        if not all(
            provenance_path.is_file()
            and all(observation_path.is_file() for observation_path in observation_paths)
            for provenance_path, observation_paths in cases
        ):
            self.skipTest("Health Connect Publisher examples are not present")

        for provenance_path, observation_paths in cases:
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            provenance_source = provenance["entity"][0]["what"]["identifier"]
            self.assertEqual(provenance_source["system"], HEALTH_CONNECT_RECORD_SYSTEM)
            for observation_path in observation_paths:
                observation = json.loads(observation_path.read_text(encoding="utf-8"))
                source_identifiers = [
                    identifier
                    for identifier in observation["identifier"]
                    if identifier["system"] == HEALTH_CONNECT_RECORD_SYSTEM
                ]
                self.assertEqual(source_identifiers, [provenance_source])

    def test_health_connect_does_not_invent_data_origin_metadata(self) -> None:
        path = ROOT / "health-connect/output/Device-HealthConnectSourceApplicationExample.json"
        if not path.is_file():
            self.skipTest("Health Connect Publisher examples are not present")
        source = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(
            source.get("identifier"),
            [
                {
                    "system": "https://grovealliance.org/fhir/"
                    "health-connect/NamingSystem/android-package-name",
                    "value": "com.example.wearable",
                }
            ],
        )
        self.assertNotIn("deviceName", source)
        self.assertNotIn("version", source)

if __name__ == "__main__":
    unittest.main()
