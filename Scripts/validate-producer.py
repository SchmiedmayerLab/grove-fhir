#!/usr/bin/env python3
"""Validate producer-emitted R4 resources without executing the producer."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

try:
    from Scripts.producer_validation.cli import main
except ModuleNotFoundError:  # Direct `python Scripts/validate-producer.py` execution.
    from producer_validation.cli import main  # type: ignore[no-redef]


if __name__ == "__main__":
    raise SystemExit(main())
