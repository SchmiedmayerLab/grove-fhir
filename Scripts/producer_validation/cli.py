"""Command-line orchestration for Grove producer conformance."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .diagnostics import ProducerValidationError
from .external_validator import run_validator
from .io import resolve_unlinked_regular_file
from .manifest import parse_package_arguments, validate_manifest, validate_packages


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate producer-emitted R4 resources without executing the producer."
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--package", action="append", default=[])
    parser.add_argument("--validator", type=Path)
    parser.add_argument("--structural-only", action="store_true")
    parser.add_argument(
        "--allow-example-urls",
        action="store_true",
        help=(
            "allow example.org identifiers in demonstration fixtures; omitted by "
            "default so producer validation fails closed"
        ),
    )
    arguments = parser.parse_args(argv)
    try:
        manifest_path = resolve_unlinked_regular_file(arguments.manifest, "manifest")
        manifest, resources = validate_manifest(manifest_path)
        if arguments.structural_only:
            if (
                arguments.package
                or arguments.validator is not None
                or arguments.allow_example_urls
            ):
                raise ProducerValidationError(
                    "--structural-only cannot be combined with package, Validator, "
                    "or example-URL arguments"
                )
        else:
            if arguments.validator is None:
                raise ProducerValidationError(
                    "--validator is required unless --structural-only is used"
                )
            supplied = parse_package_arguments(arguments.package)
            packages = validate_packages(manifest, supplied)
            run_validator(
                arguments.validator,
                packages,
                resources,
                allow_example_urls=arguments.allow_example_urls,
            )
    except ProducerValidationError as error:
        print(f"Producer conformance failed: {error}", file=sys.stderr)
        return 1
    print(f"Validated {len(resources)} producer resource(s) against FHIR R4")
    return 0
