#!/usr/bin/env python3
"""Write a canonical passed-test attestation for one generated evidence artifact."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from fhir_fixture_corpus import canonical_json_bytes
from conformance_evidence import (
    COMMIT,
    EvidenceError,
    IDENTIFIER,
    load_json_object,
    sha256_file,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--implementation", required=True)
    parser.add_argument("--proposal", required=True)
    parser.add_argument("--test-group", required=True)
    parser.add_argument(
        "--source-commit",
        help="optional assertion; the emitted commit is always derived from sources.json",
    )
    parser.add_argument(
        "--integration-sources",
        type=Path,
        default=Path("Integration/sources.json"),
    )
    parser.add_argument(
        "--input",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="hash one concrete input without recording its machine-specific path",
    )
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    try:
        for label, value in (
            ("artifact", arguments.artifact),
            ("implementation", arguments.implementation),
            ("proposal", arguments.proposal),
        ):
            if not IDENTIFIER.fullmatch(value):
                raise EvidenceError(f"{label} must be a lowercase identifier")
        if not IDENTIFIER.fullmatch(arguments.test_group):
            raise EvidenceError("test group must be a lowercase identifier")
        integration = load_json_object(
            arguments.integration_sources, "integration sources"
        )
        proposals = {
            proposal["id"]: proposal
            for proposal in integration.get("proposals", [])
            if isinstance(proposal, dict) and isinstance(proposal.get("id"), str)
        }
        proposal = proposals.get(arguments.proposal)
        if not isinstance(proposal, dict):
            raise EvidenceError("attestation proposal is absent from Integration/sources.json")
        sources = {
            source["id"]: source
            for source in integration.get("sources", [])
            if isinstance(source, dict) and isinstance(source.get("id"), str)
        }
        source = sources.get(proposal.get("source"))
        source_commit = source.get("commit") if isinstance(source, dict) else None
        if not isinstance(source_commit, str) or not COMMIT.fullmatch(source_commit):
            raise EvidenceError("attestation proposal source has no exact commit")
        if (
            arguments.source_commit is not None
            and arguments.source_commit != source_commit
        ):
            raise EvidenceError("asserted source commit does not match sources.json")
        commands = [
            {"cwd": test["cwd"], "argv": test["argv"]}
            for test in proposal.get("tests", [])
            if isinstance(test, dict) and test.get("group") == arguments.test_group
        ]
        if not commands:
            raise EvidenceError("proposal has no commands in the selected test group")
        inputs = []
        names: set[str] = set()
        for value in arguments.input:
            if "=" not in value:
                raise EvidenceError("attestation input must use NAME=PATH")
            name, filename = value.split("=", 1)
            if (
                not name
                or "/" in name
                or "\\" in name
                or name in names
                or not filename
            ):
                raise EvidenceError(f"invalid or duplicate attestation input: {name!r}")
            names.add(name)
            path = Path(filename)
            if path.is_symlink() or not path.is_file():
                raise EvidenceError(f"attestation input is missing or unsafe: {filename}")
            inputs.append(
                {"name": name, "sha256": sha256_file(path), "size": path.stat().st_size}
            )
        document = {
            "kind": "grove-fhir-test-attestation",
            "schemaVersion": 1,
            "artifactId": arguments.artifact,
            "implementation": arguments.implementation,
            "producerProposal": arguments.proposal,
            "sourceCommit": source_commit,
            "testGroup": arguments.test_group,
            "commands": commands,
            "result": "passed",
            "inputs": sorted(inputs, key=lambda item: item["name"]),
        }
        if arguments.output.is_symlink():
            raise EvidenceError("attestation output may not be a symlink")
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_bytes(canonical_json_bytes(document))
        return 0
    except (EvidenceError, OSError, ValueError) as error:
        parser.exit(1, f"error: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
