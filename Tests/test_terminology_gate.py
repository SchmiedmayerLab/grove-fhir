#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "Scripts/check-terminology.py"

spec = importlib.util.spec_from_file_location(
    "ucum_expression", ROOT / "Scripts/ucum_expression.py"
)
ucum_expression = importlib.util.module_from_spec(spec)
sys.modules["ucum_expression"] = ucum_expression
spec.loader.exec_module(ucum_expression)
UcumTable = ucum_expression.UcumTable
UcumError = ucum_expression.UcumError

PINNED = json.loads(
    (ROOT / "catalog/terminology/ucum-units.json").read_text(encoding="utf-8")
)


class UcumExpressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.table = UcumTable(PINNED)

    def test_pin_records_its_source_and_version(self) -> None:
        self.assertEqual(PINNED["ucumVersion"], "2.2")
        self.assertEqual(len(PINNED["source"]["sha256"]), 64)
        self.assertEqual(
            PINNED["baseUnits"], ["C", "K", "cd", "g", "m", "rad", "s"]
        )
        self.assertGreater(len(PINNED["units"]), 300)

    def test_dimensions_of_the_grove_unit_inventory(self) -> None:
        cases = {
            "/min": {"s": -1},
            "mm[Hg]": {"g": 1, "m": -1, "s": -2},
            "kg": {"g": 1},
            "%": {},
            "km/h": {"m": 1, "s": -1},
            "10*3/uL": {"m": -3},
            "kg/m2": {"g": 1, "m": -2},
            "mL/min/{1.73_m2}": {"m": 3, "s": -1},
            "kcal": {"g": 1, "m": 2, "s": -2},
            "h": {"s": 1},
            "cm": {"m": 1},
        }
        for code, dimension in cases.items():
            self.assertEqual(
                dict(sorted(self.table.parse(code).dimension.items())),
                dict(sorted(dimension.items())),
                code,
            )

    def test_special_units_are_whole_expression_only(self) -> None:
        self.assertEqual(self.table.parse("Cel").dimension, {"K": 1})
        self.assertEqual(self.table.parse("Cel").special_atom, "Cel")
        self.assertEqual(
            self.table.parse("dB[SPL]").dimension, {"g": 1, "m": -1, "s": -2}
        )
        for bad in ("Cel/s", "Cel2", "s.Cel"):
            with self.assertRaises(UcumError, msg=bad):
                self.table.parse(bad)

    def test_prefixes_attach_only_to_metric_atoms(self) -> None:
        self.assertEqual(self.table.parse("mm[Hg]").dimension["m"], -1)
        with self.assertRaises(UcumError):
            self.table.parse("m[in_i]")

    def test_annotations_are_captured_and_dimensionless(self) -> None:
        parsed = self.table.parse("{steps}")
        self.assertEqual(parsed.dimension, {})
        self.assertEqual(parsed.annotations, ["steps"])

    def test_malformed_codes_are_rejected(self) -> None:
        for bad in ("", " kg", "kg//s", "xyz", "k{ann}", "(kg", "kg)"):
            with self.assertRaises(UcumError, msg=repr(bad)):
                self.table.parse(bad)


class TerminologyGateTests(unittest.TestCase):
    def run_gate(self, root: Path) -> tuple[int, str]:
        result = subprocess.run(
            [sys.executable, str(GATE), "--root", str(root)],
            capture_output=True,
            text=True,
        )
        return result.returncode, result.stdout

    def write_fixture(self, directory: Path, measurement: dict) -> Path:
        terminology = directory / "catalog/terminology"
        terminology.mkdir(parents=True)
        for name in ("ucum-units.json", "loinc-concepts.json", "ucum-annotations.json"):
            (terminology / name).write_text(
                (ROOT / "catalog/terminology" / name).read_text(encoding="utf-8")
            )
        (directory / "catalog/measurement-catalog.json").write_text(
            json.dumps({"measurements": [measurement]})
        )
        return directory

    def test_repository_passes(self) -> None:
        code, output = self.run_gate(ROOT)
        self.assertEqual(code, 0, output)
        self.assertIn("problems=0", output)

    def test_gate_rejects_each_defect_class(self) -> None:
        heart_rate = {
            "id": "heart-rate",
            "code": {"system": "http://loinc.org", "code": "8867-4"},
            "quantity": {"system": "http://unitsofmeasure.org", "code": "/min"},
        }
        defects = {
            "unpinned LOINC code": (
                {**heart_rate, "code": {"system": "http://loinc.org", "code": "0000-0"}},
                "LOINC 0000-0 is not pinned",
            ),
            "display drift": (
                {
                    **heart_rate,
                    "code": {
                        "system": "http://loinc.org",
                        "code": "8867-4",
                        "display": "Pulse",
                    },
                },
                "differs from the pinned",
            ),
            "unparseable unit": (
                {
                    **heart_rate,
                    "quantity": {
                        "system": "http://unitsofmeasure.org",
                        "code": "count/min",
                    },
                },
                "unknown UCUM atom 'count'",
            ),
            "unlisted annotation": (
                {
                    **heart_rate,
                    "quantity": {
                        "system": "http://unitsofmeasure.org",
                        "code": "{beats}/min",
                    },
                },
                "annotation {beats} is not allowlisted",
            ),
            "dimension contradiction": (
                {
                    **heart_rate,
                    "quantity": {"system": "http://unitsofmeasure.org", "code": "kg"},
                },
                "PROPERTY NRat requires",
            ),
        }
        for label, (measurement, expected) in defects.items():
            with self.subTest(label):
                with tempfile.TemporaryDirectory() as directory:
                    root = self.write_fixture(Path(directory), measurement)
                    code, output = self.run_gate(root)
                    self.assertEqual(code, 1, output)
                    self.assertIn(expected, output)

    def test_green_fixture_passes(self) -> None:
        heart_rate = {
            "id": "heart-rate",
            "code": {"system": "http://loinc.org", "code": "8867-4"},
            "quantity": {"system": "http://unitsofmeasure.org", "code": "/min"},
        }
        with tempfile.TemporaryDirectory() as directory:
            root = self.write_fixture(Path(directory), heart_rate)
            code, output = self.run_gate(root)
            self.assertEqual(code, 0, output)


if __name__ == "__main__":
    unittest.main()
