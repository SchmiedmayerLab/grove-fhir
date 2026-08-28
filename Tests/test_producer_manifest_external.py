"""Domain regressions for Grove producer conformance."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from Scripts.producer_validation import (
    cli,
    context,
    diagnostics,
    external_validator,
    io,
    manifest as manifest_validation,
)
from Tests.producer_validation_test_support import (
    Path,
    ProducerValidationTestCase,
    ROOT,
    copy,
    json,
    mock,
    subprocess,
    tempfile,
)

class ProducerManifestExternalTests(ProducerValidationTestCase):
    def test_repository_example_is_structurally_valid(self) -> None:
        manifest, resources = manifest_validation.validate_manifest(self.example)
        self.assertEqual(manifest["fhirVersion"], "4.0.1")
        self.assertEqual([path.name for path in resources], ["exchange-bundle.json"])
        self.assertEqual(manifest["semanticVectors"][0]["id"], "heart-rate")

    def test_official_manifest_validates_both_normative_exchange_bases(self) -> None:
        path = (
            ROOT
            / "Conformance/corpora/mobile-exchange/official-validator-manifest.json"
        )
        manifest, resources = manifest_validation.validate_manifest(path)
        self.assertEqual(manifest["producer"]["version"], "0.6.0")
        self.assertEqual(
            [resource.name for resource in resources],
            ["exchange-bundle.json", "retraction-bundle.json"],
        )
        self.assertEqual(
            [resource.parent for resource in resources],
            [path.parent, path.parent],
        )

    def test_path_traversal_is_rejected(self) -> None:
        manifest = json.loads(self.example.read_text(encoding="utf-8"))
        manifest["resources"][0]["path"] = "../heart-rate.json"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(diagnostics.ProducerValidationError, "unsafe resource path"):
                manifest_validation.validate_manifest(path)

    def test_intermediate_symlink_component_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outside = root / "outside"
            outside.mkdir()
            (outside / "resource.json").write_text("{}", encoding="utf-8")
            (root / "linked").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(
                diagnostics.ProducerValidationError, "symlink component"
            ):
                io.safe_resource_path(root, "linked/resource.json")

    def test_manifest_leaf_and_intermediate_symlinks_are_rejected_before_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            leaf = root / "manifest-link.json"
            leaf.symlink_to(self.example)
            with self.subTest(kind="leaf"), self.assertRaisesRegex(
                diagnostics.ProducerValidationError, "manifest path contains a symlink"
            ):
                io.resolve_unlinked_regular_file(leaf, "manifest")

            linked_directory = root / "linked"
            linked_directory.symlink_to(self.example.parent, target_is_directory=True)
            with self.subTest(kind="intermediate"), self.assertRaisesRegex(
                diagnostics.ProducerValidationError, "manifest path contains a symlink"
            ):
                io.resolve_unlinked_regular_file(
                    linked_directory / "manifest.json", "manifest"
                )

    def test_package_leaf_and_intermediate_symlinks_are_rejected_before_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            real_directory = root / "real"
            real_directory.mkdir()
            package = real_directory / "package.tgz"
            package.write_bytes(b"package")
            leaf = root / "package-link.tgz"
            leaf.symlink_to(package)
            with self.subTest(kind="leaf"), self.assertRaisesRegex(
                diagnostics.ProducerValidationError, "mobile package path contains a symlink"
            ):
                manifest_validation.parse_package_arguments([f"mobile={leaf}"])

            linked_directory = root / "linked"
            linked_directory.symlink_to(real_directory, target_is_directory=True)
            with self.subTest(kind="intermediate"), self.assertRaisesRegex(
                diagnostics.ProducerValidationError, "mobile package path contains a symlink"
            ):
                manifest_validation.parse_package_arguments(
                    [f"mobile={linked_directory / 'package.tgz'}"]
                )

    def test_validator_leaf_and_intermediate_symlinks_are_rejected_before_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            real_directory = root / "real"
            real_directory.mkdir()
            validator = real_directory / "validator.jar"
            validator.write_bytes(b"jar")
            leaf = root / "validator-link.jar"
            leaf.symlink_to(validator)
            with self.subTest(kind="leaf"), self.assertRaisesRegex(
                diagnostics.ProducerValidationError, "Validator JAR path contains a symlink"
            ):
                external_validator.run_validator(leaf, [], [])

            linked_directory = root / "linked"
            linked_directory.symlink_to(real_directory, target_is_directory=True)
            with self.subTest(kind="intermediate"), self.assertRaisesRegex(
                diagnostics.ProducerValidationError, "Validator JAR path contains a symlink"
            ):
                external_validator.run_validator(linked_directory / "validator.jar", [], [])

    def test_validator_rejects_a_linked_private_fhir_home(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            validator = root / "validator.jar"
            validator.write_bytes(b"jar")
            real_home = root / "home"
            (real_home / ".fhir" / "packages").mkdir(parents=True)
            linked_home = root / "linked-home"
            linked_home.symlink_to(real_home, target_is_directory=True)
            with self.assertRaisesRegex(
                diagnostics.ProducerValidationError,
                "private FHIR home path contains a symlink",
            ):
                external_validator.run_validator(
                    validator, [], [], fhir_tool_home=linked_home
                )

    def test_duplicate_package_alias_is_rejected(self) -> None:
        manifest = json.loads(self.example.read_text(encoding="utf-8"))
        manifest["packages"].append(copy.deepcopy(manifest["packages"][0]))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "resources").mkdir()
            resource = self.example.parent / "resources/exchange-bundle.json"
            (root / "resources/exchange-bundle.json").write_bytes(resource.read_bytes())
            path = root / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(diagnostics.ProducerValidationError, "must be unique"):
                manifest_validation.validate_manifest(path)

    def test_cli_requires_official_validator_outside_structural_mode(self) -> None:
        self.assertEqual(cli.main(["--manifest", str(self.example)]), 1)

    def test_validator_runs_one_offline_batch_and_parses_attributed_outcomes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            validator = root / "validator.jar"
            validator.write_bytes(b"jar")
            resources = [root / "one.json", root / "two.json"]
            for resource in resources:
                resource.write_text('{"resourceType":"Patient"}', encoding="utf-8")
            commands: list[list[str]] = []

            def successful_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                commands.append(command)
                output = Path(command[command.index("-output") + 1])
                output.write_text(json.dumps({
                    "resourceType": "Bundle",
                    "type": "collection",
                    "entry": [
                        {"resource": self.outcome(resource, [
                            {"severity": "information", "code": "informational"}
                        ])}
                        for resource in sorted(resources)
                    ],
                }), encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, stdout="validated")

            with mock.patch.object(external_validator.subprocess, "run", side_effect=successful_run):
                external_validator.run_validator(
                    validator, [], resources, allow_example_urls=True
                )

            self.assertEqual(len(commands), 1)
            command = commands[0]
            self.assertIn(["-version", "4.0.1"], [command[index:index + 2] for index in range(len(command) - 1)])
            self.assertIn(["-tx", "n/a"], [command[index:index + 2] for index in range(len(command) - 1)])
            self.assertIn("-no-http-access", command)
            self.assertIn(
                ["-allow-example-urls", "true"],
                [command[index:index + 2] for index in range(len(command) - 1)],
            )
            self.assertIn(f"-Duser.home={context.FHIR_TOOL_HOME}", command)
            self.assertEqual(command[-2:], [str(resource) for resource in sorted(resources)])

    def test_validator_error_in_any_produced_outcome_fails_even_with_zero_exit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            validator = root / "validator.jar"
            validator.write_bytes(b"jar")
            resource = root / "resource.json"
            resource.write_text('{"resourceType":"Patient"}', encoding="utf-8")

            def error_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                output = Path(command[command.index("-output") + 1])
                output.write_text(json.dumps(self.outcome(resource, [
                    {"severity": "error", "code": "invalid", "diagnostics": "bad unit"}
                ])), encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, stdout="")

            with mock.patch.object(
                external_validator.subprocess, "run", side_effect=error_run
            ) as run:
                with self.assertRaisesRegex(diagnostics.ProducerValidationError, "bad unit"):
                    external_validator.run_validator(validator, [], [resource])
                self.assertEqual(run.call_count, 1)

    def test_validator_process_and_output_failures_are_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            validator = root / "validator.jar"
            validator.write_bytes(b"jar")
            resource = root / "resource.json"
            resource.write_text('{"resourceType":"Patient"}', encoding="utf-8")

            def nonzero_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                output = Path(command[command.index("-output") + 1])
                output.write_text(json.dumps(self.outcome(resource, [
                    {"severity": "information", "code": "informational"}
                ])), encoding="utf-8")
                return subprocess.CompletedProcess(command, 2, stdout="failed")

            with mock.patch.object(
                external_validator.subprocess, "run", side_effect=nonzero_run
            ) as run:
                with self.assertRaisesRegex(diagnostics.ProducerValidationError, "process failed"):
                    external_validator.run_validator(validator, [], [resource])
                self.assertEqual(run.call_count, 2)

            with mock.patch.object(
                external_validator.subprocess,
                "run",
                return_value=subprocess.CompletedProcess(
                    [], 0, stdout="no output " + "x" * 5000
                ),
            ) as run:
                with self.assertRaisesRegex(diagnostics.ProducerValidationError, "no trustworthy"):
                    external_validator.run_validator(validator, [], [resource])
                self.assertEqual(run.call_count, 2)

            with mock.patch.object(
                external_validator.subprocess,
                "run",
                side_effect=subprocess.TimeoutExpired(
                    cmd=["java"],
                    timeout=context.VALIDATOR_TIMEOUT_SECONDS,
                    output=b"partial validator log",
                ),
            ) as run:
                with self.assertRaisesRegex(
                    diagnostics.ProducerValidationError, "timed out after 180 seconds"
                ):
                    external_validator.run_validator(validator, [], [resource])
                self.assertEqual(run.call_count, 2)

    def test_validator_retries_wrong_batch_shape_once_and_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            validator = root / "validator.jar"
            validator.write_bytes(b"jar")
            resources = [root / "one.json", root / "two.json"]
            for resource in resources:
                resource.write_text('{"resourceType":"Patient"}', encoding="utf-8")

            def wrong_count(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                output = Path(command[command.index("-output") + 1])
                output.write_text(json.dumps({
                    "resourceType": "Bundle",
                    "type": "collection",
                    "entry": [{"resource": self.outcome(resources[0], [
                        {"severity": "information", "code": "informational"}
                    ])}],
                }), encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, stdout="wrong count")

            with mock.patch.object(
                external_validator.subprocess, "run", side_effect=wrong_count
            ) as run:
                with self.assertRaisesRegex(
                    diagnostics.ProducerValidationError, "output count does not match"
                ):
                    external_validator.run_validator(validator, [], resources)
                self.assertEqual(run.call_count, 2)
