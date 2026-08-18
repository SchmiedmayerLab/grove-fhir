#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "make-canonical-redirects.py"


class CanonicalRedirectTests(unittest.TestCase):
    def test_generates_standard_and_special_url_redirects(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output"
            site = Path(directory) / "site"
            output.mkdir()
            (output / "StructureDefinition-standard.json").write_text(
                json.dumps({"resourceType": "StructureDefinition", "id": "standard"}), encoding="utf-8"
            )
            (output / "StructureDefinition-standard.html").write_text("standard", encoding="utf-8")
            (output / "StructureDefinition-special.json").write_text(
                json.dumps(
                    {
                        "resourceType": "StructureDefinition",
                        "id": "special",
                        "url": "https://example.org/StructureDefinition/parent/child",
                    }
                ),
                encoding="utf-8",
            )
            (output / "StructureDefinition-special.html").write_text("special", encoding="utf-8")

            result = subprocess.run(
                ["python3", str(SCRIPT), str(output), str(site)],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("generated 3 canonical redirect entries", result.stdout)
            self.assertTrue((site / "StructureDefinition" / "standard" / "index.html").is_file())
            special_redirect = site / "StructureDefinition" / "parent" / "child" / "index.html"
            self.assertIn("StructureDefinition-special.html", special_redirect.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
