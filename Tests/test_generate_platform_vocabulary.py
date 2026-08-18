#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "generate-platform-vocabulary.py"
SPEC = importlib.util.spec_from_file_location("generate_platform_vocabulary", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PlatformVocabularyTests(unittest.TestCase):
    def test_class_name_is_stable(self) -> None:
        self.assertEqual(MODULE.class_name("healthkit-state-of-mind-property"), "HealthkitStateOfMindPropertyCS")

    def test_workout_display_splits_initialisms_and_words(self) -> None:
        self.assertEqual(MODULE.workout_display("swimBikeRun"), "swim bike run")
        self.assertEqual(MODULE.workout_display("HIIT"), "HIIT")

    def test_code_system_declares_complete_case_sensitive_content(self) -> None:
        output = "\n".join(MODULE.code_system("sample-system", "Sample", "Definition", [("one", "One")]))
        self.assertIn("* ^caseSensitive = true", output)
        self.assertIn("* ^content = #complete", output)
        self.assertIn('* #one "One"', output)


if __name__ == "__main__":
    unittest.main()
