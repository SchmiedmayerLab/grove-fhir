"""Test the trunk and leaf split the CI wave jobs are built from."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location(
    "guide_build_plan", ROOT / "Scripts/guide-build-plan.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
# The number of wave levels build-and-test.yml provides jobs for.
LEVELS = 6


class GuideBuildPlanTests(unittest.TestCase):
    def test_every_guide_is_built_exactly_once(self) -> None:
        outputs = MODULE.ci_outputs(LEVELS)
        built = [
            guide
            for name, guides in outputs.items()
            if name.startswith(("trunk", "leaf"))
            for guide in guides
        ]
        self.assertEqual(sorted(built), sorted(MODULE.guides()))

    def test_each_job_restores_every_dependency_from_a_finished_trunk_job(self) -> None:
        outputs = MODULE.ci_outputs(LEVELS)
        for level in range(1, LEVELS + 1):
            # Wave N waits only for trunk N-1, which itself waited for every earlier trunk.
            available = set(outputs[f"built{level - 1}"]) if level > 1 else set()
            trunk = set(outputs.get(f"trunk{level}", []))
            for guide in trunk | set(outputs[f"leaf{level}"]):
                with self.subTest(guide=guide):
                    self.assertLessEqual(MODULE.dependencies(guide), available)

    def test_no_leaf_is_a_dependency(self) -> None:
        outputs = MODULE.ci_outputs(LEVELS)
        depended_on = set().union(*(MODULE.dependencies(guide) for guide in MODULE.guides()))
        leaves = {guide for name, guides in outputs.items() if name.startswith("leaf") for guide in guides}
        self.assertFalse(leaves & depended_on)

    def test_slow_leaves_do_not_gate_unrelated_guides(self) -> None:
        # The reason for the split: healthkit is the slowest build, and nothing reads it.
        outputs = MODULE.ci_outputs(LEVELS)
        self.assertNotIn("healthkit", {guide for name, guides in outputs.items() if name.startswith("trunk") for guide in guides})

    def test_a_plan_deeper_than_the_jobs_fails_loudly(self) -> None:
        plan = [[f"guide-{index}"] for index in range(LEVELS + 1)]
        with mock.patch.object(MODULE, "waves", return_value=plan):
            with self.assertRaisesRegex(SystemExit, "add a trunk and a leaf job"):
                MODULE.ci_outputs(LEVELS)


if __name__ == "__main__":
    unittest.main()
