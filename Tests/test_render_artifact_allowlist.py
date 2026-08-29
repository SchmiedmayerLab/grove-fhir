"""Tests for clean and post-SUSHI artifact allowlist verification."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "Scripts/render-artifact-allowlist.py"
PACKAGE = SCRIPT.parents[1] / "package.json"
SPECIFICATION = importlib.util.spec_from_file_location(
    "render_artifact_allowlist", SCRIPT
)
assert SPECIFICATION is not None and SPECIFICATION.loader is not None
RENDERER = importlib.util.module_from_spec(SPECIFICATION)
SPECIFICATION.loader.exec_module(RENDERER)


class RenderArtifactAllowlistTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "publication").mkdir()
        (self.root / "mobile/input/fsh").mkdir(parents=True)
        (self.root / "publication/config.json").write_text(
            json.dumps(
                {
                    "canonicalBaseUrl": "https://grove.example/fhir",
                    "guides": [
                        {
                            "source": "mobile",
                            "canonicalPath": "mobile",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (self.root / "mobile/sushi-config.yaml").write_text(
            "id: org.example.fhir.mobile\n"
            "canonical: https://grove.example/fhir/mobile\n",
            encoding="utf-8",
        )
        self.fsh = self.root / "mobile/input/fsh/artifacts.fsh"
        self.fsh.write_text(
            "Profile: MiniObservation\n"
            "Parent: Observation\n\n"
            "Instance: MiniExample\n"
            "InstanceOf: MiniObservation\n"
            "Usage: #example\n",
            encoding="utf-8",
        )
        self.allowlist = self.root / "publication/artifact-allowlist.json"
        self.allowlist.write_text(
            json.dumps(
                {
                    "schemaVersion": 0,
                    "packages": [
                        {
                            "source": "mobile",
                            "packageId": "org.example.fhir.mobile",
                            "canonical": "https://grove.example/fhir/mobile",
                            "artifacts": [
                                {
                                    "fshName": "MiniExample",
                                    "fshType": "Instance",
                                    "resourceType": "Observation",
                                    "id": "MiniExample",
                                    "classification": "example",
                                },
                                {
                                    "fshName": "MiniObservation",
                                    "fshType": "Profile",
                                    "resourceType": "StructureDefinition",
                                    "id": "mini-observation",
                                    "classification": "definition",
                                },
                            ],
                        }
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_renderer(self, *arguments: str) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output):
            status = RENDERER.main(list(arguments), root=self.root)
        return status, output.getvalue()

    def write_generated_output(self, *, example_id: str = "MiniExample") -> None:
        data = self.root / "mobile/fsh-generated/data"
        resources = self.root / "mobile/fsh-generated/resources"
        data.mkdir(parents=True)
        resources.mkdir(parents=True)
        (data / "fsh-index.json").write_text(
            json.dumps(
                [
                    {
                        "fshName": "MiniObservation",
                        "fshType": "Profile",
                        "outputFile": "StructureDefinition-mini-observation.json",
                    },
                    {
                        "fshName": "MiniExample",
                        "fshType": "Instance",
                        "outputFile": "Observation-MiniExample.json",
                    },
                ]
            ),
            encoding="utf-8",
        )
        (resources / "StructureDefinition-mini-observation.json").write_text(
            json.dumps(
                {"resourceType": "StructureDefinition", "id": "mini-observation"}
            ),
            encoding="utf-8",
        )
        (resources / "Observation-MiniExample.json").write_text(
            json.dumps({"resourceType": "Observation", "id": example_id}),
            encoding="utf-8",
        )

    def test_clean_check_does_not_require_ignored_generated_output(self) -> None:
        status, output = self.run_renderer("--check")

        self.assertEqual(status, 0, output)
        self.assertFalse((self.root / "mobile/fsh-generated").exists())
        self.assertIn("matches authored FSH declarations", output)

    def test_standalone_check_validates_schema_before_cross_references(self) -> None:
        scripts = json.loads(PACKAGE.read_text(encoding="utf-8"))["scripts"]

        self.assertEqual(
            scripts["artifacts:check"],
            "npm run artifacts:schema && "
            "python3 Scripts/render-artifact-allowlist.py --check",
        )

    def test_clean_check_still_rejects_authored_declaration_drift(self) -> None:
        self.fsh.write_text(
            self.fsh.read_text(encoding="utf-8")
            + "\nValueSet: NewlyAuthoredValueSet\n",
            encoding="utf-8",
        )

        status, output = self.run_renderer("--check")

        self.assertEqual(status, 1)
        self.assertIn("differ from authored FSH", output)

    def test_generated_check_requires_exact_output_to_exist(self) -> None:
        status, output = self.run_renderer("--check-generated", "mobile")

        self.assertEqual(status, 1)
        self.assertIn("is absent; run SUSHI first", output)

    def test_generated_check_accepts_exact_sushi_projection(self) -> None:
        self.write_generated_output()

        status, output = self.run_renderer("--check-generated", "mobile")

        self.assertEqual(status, 0, output)
        self.assertIn("matches exact generated SUSHI output for: mobile", output)

    def test_generated_check_rejects_generated_resource_identity_drift(self) -> None:
        self.write_generated_output(example_id="DifferentExample")

        status, output = self.run_renderer("--check-generated", "mobile")

        self.assertEqual(status, 1)
        self.assertIn("generated SUSHI projection differs", output)


if __name__ == "__main__":
    unittest.main()
