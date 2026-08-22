#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#

import json
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
    "catalog/measurement-catalog.json",
    "mobile/input/data/terminology-reviews.json",
    "mobile/input/fsh/aliases.fsh",
    "mobile/input/fsh/profiles.fsh",
    "mobile/input/fsh/generated-measurement-profiles.fsh",
)


class MeasurementProfileProjectionTests(unittest.TestCase):
    def run_renderer(self, root: Path, *extra: str) -> tuple[int, str]:
        result = subprocess.run(
            [sys.executable, str(RENDERER), "--root", str(root), *extra],
            capture_output=True,
            text=True,
        )
        return result.returncode, result.stdout

    def make_fixture(self, directory: Path) -> Path:
        for name in FIXTURE_FILES:
            destination = directory / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)
        return directory

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
            ],
        )

    def test_generated_profiles_are_current(self) -> None:
        code, output = self.run_renderer(ROOT, "--check")
        self.assertEqual(code, 0, output)
        self.assertIn("13 emitted, 0 parity-checked, problems=0", output)

    def test_projection_still_reproduces_hand_written_profiles(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_fixture(Path(directory))
            self.demote_to_hand_written(root)
            code, output = self.run_renderer(root, "--check")
            self.assertEqual(code, 0, output)
            self.assertIn("13 parity-checked, problems=0", output)

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
