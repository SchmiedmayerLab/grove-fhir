#!/usr/bin/env python3
"""Collect checksum-bound release-candidate evidence without publishing it."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import datetime
import gzip
import hashlib
import io
import json
import os
import platform
import subprocess
import tarfile
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "catalog/release-manifest.json"
MOBILE_SEMANTICS = ROOT / "publication/mobile-semantic-baseline.json"
RELEASE_MANIFEST_SCHEMA = ROOT / "catalog/schemas/release-manifest.schema.json"
RELEASE_EVIDENCE_SCHEMA = ROOT / "catalog/schemas/release-evidence.schema.json"
TERMINOLOGY_EVIDENCE_SCHEMA = ROOT / "catalog/schemas/terminology-evidence.schema.json"
RELEASE_EVIDENCE_SCHEMA_URL = (
    "https://grovealliance.org/fhir/catalog/schemas/release-evidence.schema.json"
)
TERMINOLOGY_EVIDENCE_SCHEMA_URL = (
    "https://grovealliance.org/fhir/catalog/schemas/terminology-evidence.schema.json"
)
ALLOWED_LANES = {"offline-structural", "online-terminology"}
NORMATIVE_CORPUS_ROOTS = (
    "Conformance/corpora/mobile-exchange",
    "Conformance/corpora/mobile-semantics",
    "questionnaire/fixtures/pairs",
    "questionnaire/fixtures/validator",
)


class EvidenceError(ValueError):
    """Release evidence is incomplete, inconsistent, or would be overwritten."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def display_path(path: Path, root: Path = ROOT) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def require_regular_file(path: Path, *, root: Path = ROOT) -> None:
    if path.is_symlink() or not path.is_file():
        raise EvidenceError(f"missing or unsafe release input: {display_path(path, root)}")


def copy_new(source: Path, destination: Path) -> None:
    require_regular_file(source)
    if destination.exists() or destination.is_symlink():
        raise EvidenceError(f"release evidence is immutable; refusing to replace {destination}")
    destination.write_bytes(source.read_bytes())


def package_metadata(path: Path) -> dict[str, object]:
    require_regular_file(path)
    try:
        with tarfile.open(path, "r:gz") as archive:
            package_member = archive.getmember("package/package.json")
            if not package_member.isfile() or package_member.issym() or package_member.islnk():
                raise EvidenceError(f"{path} has an unsafe package/package.json")
            member = archive.extractfile(package_member)
            if member is None:
                raise EvidenceError(f"{path} contains no package/package.json")
            metadata = json.load(member)
    except (KeyError, json.JSONDecodeError, tarfile.TarError) as error:
        raise EvidenceError(f"cannot read FHIR package metadata from {path}: {error}") from error
    if not isinstance(metadata, dict):
        raise EvidenceError(f"{path} package/package.json is not an object")
    return metadata


def git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def git_status() -> str:
    return subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def command_version(command: list[str]) -> str:
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise EvidenceError(f"cannot record runtime version for {command[0]}: {error}") from error
    output = (result.stdout or result.stderr).strip()
    if not output:
        raise EvidenceError(f"runtime version command produced no output: {command}")
    return output.splitlines()[0]


def repository_file(root: Path, relative_path: str) -> Path:
    relative = Path(relative_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise EvidenceError(f"unsafe repository path in release manifest: {relative_path!r}")
    path = root / relative
    require_regular_file(path, root=root)
    return path


def normative_contract_paths(
    root: Path, manifest: dict[str, Any]
) -> tuple[Path, ...]:
    """Return the complete, sorted machine-contract closure for the release."""

    relative_paths = {
        "catalog/release-manifest.json",
        "catalog/schemas/release-manifest.schema.json",
        "catalog/schemas/release-evidence.schema.json",
        "catalog/schemas/terminology-evidence.schema.json",
    }
    catalogs = manifest.get("normativeCatalogs")
    if not isinstance(catalogs, list) or not catalogs:
        raise EvidenceError("release manifest declares no normative catalogs")
    for catalog in catalogs:
        if not isinstance(catalog, dict):
            raise EvidenceError("release manifest normativeCatalogs entry is not an object")
        for key in ("path", "schema"):
            value = catalog.get(key)
            if not isinstance(value, str) or not value:
                raise EvidenceError(f"normative catalog has no {key}")
            relative_paths.add(value)

    # The manifest identifies the normative catalog instances, but the release archive carries
    # the entire catalog JSON surface (including local terminology evidence and every schema) so
    # consumers never have to guess which transitive machine input was omitted.
    catalog_root = root / "catalog"
    if catalog_root.is_symlink() or not catalog_root.is_dir():
        raise EvidenceError("missing or unsafe catalog root")
    for path in sorted(catalog_root.rglob("*.json")):
        if path.is_symlink() or not path.is_file():
            raise EvidenceError(f"catalog contains an unsafe JSON path: {path}")
        relative_paths.add(path.relative_to(root).as_posix())

    for relative_root in NORMATIVE_CORPUS_ROOTS:
        corpus_root = root / relative_root
        if corpus_root.is_symlink() or not corpus_root.is_dir():
            raise EvidenceError(f"missing or unsafe normative corpus root: {relative_root}")
        files = sorted(path for path in corpus_root.rglob("*") if path.is_file())
        if not files:
            raise EvidenceError(f"normative corpus root is empty: {relative_root}")
        for path in files:
            if path.is_symlink():
                raise EvidenceError(
                    f"normative corpus contains a symlink: {path.relative_to(root)}"
                )
            if path.suffix != ".json":
                raise EvidenceError(
                    "normative machine-contract roots may contain only JSON files: "
                    f"{path.relative_to(root)}"
                )
            relative_paths.add(path.relative_to(root).as_posix())

    paths = tuple(repository_file(root, path) for path in sorted(relative_paths))
    for path in paths:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise EvidenceError(
                f"machine contract is not valid UTF-8 JSON: {path.relative_to(root)}: {error}"
            ) from error
    return paths


def machine_contract_index(
    root: Path,
    manifest: dict[str, Any],
    source_revision: str,
) -> tuple[dict[str, Any], tuple[Path, ...]]:
    paths = normative_contract_paths(root, manifest)
    index = {
        "$schema": RELEASE_EVIDENCE_SCHEMA_URL,
        "schemaVersion": 1,
        "kind": "machine-contract-index",
        "releaseVersion": manifest["releaseVersion"],
        "fhirVersion": manifest["fhirVersion"],
        "sourceRevision": source_revision,
        "artifacts": {
            path.relative_to(root).as_posix(): {
                "sha256": sha256(path),
                "size": path.stat().st_size,
            }
            for path in paths
        },
    }
    return index, paths


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_tar_entry(archive: tarfile.TarFile, name: str, content: bytes) -> None:
    member = tarfile.TarInfo(name)
    member.size = len(content)
    member.mtime = 0
    member.mode = 0o644
    member.uid = 0
    member.gid = 0
    member.uname = ""
    member.gname = ""
    archive.addfile(member, io.BytesIO(content))


def write_machine_contract_archive(
    destination: Path,
    root: Path,
    index: dict[str, Any],
    paths: tuple[Path, ...],
) -> None:
    """Write a byte-reproducible gzip/tar archive of the normative contracts."""

    if destination.exists() or destination.is_symlink():
        raise EvidenceError(f"refusing to replace {destination}")
    with destination.open("xb") as destination_stream:
        with gzip.GzipFile(
            filename="",
            mode="wb",
            fileobj=destination_stream,
            compresslevel=9,
            mtime=0,
        ) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.USTAR_FORMAT) as archive:
                write_tar_entry(archive, "machine-contract-index.json", json_bytes(index))
                for path in paths:
                    write_tar_entry(
                        archive,
                        path.relative_to(root).as_posix(),
                        path.read_bytes(),
                    )


def validate_json_schema(schema: Path, instance: Path) -> None:
    require_regular_file(schema)
    require_regular_file(instance)
    command = [
        "node",
        str(ROOT / "Scripts/validate-json-schema.cjs"),
        str(schema),
        str(instance),
    ]
    try:
        subprocess.run(
            command,
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        details = (error.stderr or error.stdout).strip()
        raise EvidenceError(
            f"{display_path(instance)} does not satisfy {display_path(schema)}: {details}"
        ) from error


def validate_terminology_evidence(
    evidence: dict[str, Any],
    *,
    manifest: dict[str, Any],
    source_revision: str,
    package_digests: dict[str, str],
) -> None:
    """Enforce cross-file bindings that JSON Schema cannot express."""

    expected_scalars = {
        "$schema": TERMINOLOGY_EVIDENCE_SCHEMA_URL,
        "releaseVersion": manifest["releaseVersion"],
        "fhirVersion": manifest["fhirVersion"],
        "sourceRevision": source_revision,
    }
    for key, expected in expected_scalars.items():
        if evidence.get(key) != expected:
            raise EvidenceError(
                f"terminology evidence {key} is {evidence.get(key)!r}, expected {expected!r}"
            )

    expected_tool = manifest["toolchain"]["fhirValidator"]
    tool = evidence["tool"]
    if tool["version"] != expected_tool["version"] or tool["sha256"] != expected_tool["sha256"]:
        raise EvidenceError("terminology evidence is not bound to the release FHIR Validator")
    endpoint = evidence["endpoint"]["url"]
    parsed_endpoint = urlsplit(endpoint)
    if (
        parsed_endpoint.scheme != "https"
        or not parsed_endpoint.hostname
        or parsed_endpoint.username
        or parsed_endpoint.password
        or parsed_endpoint.query
        or parsed_endpoint.fragment
    ):
        raise EvidenceError("terminology evidence endpoint is not a credential-free HTTPS URL")
    arguments = tool["arguments"]
    if endpoint not in arguments or not any(
        argument in {"-tx", "--tx", "-terminology"} for argument in arguments
    ):
        raise EvidenceError(
            "terminology evidence Validator arguments do not select the declared endpoint"
        )

    expected_packages = {
        guide["packageId"]: {
            "version": manifest["releaseVersion"],
            "sha256": package_digests[guide["packageId"]],
        }
        for guide in manifest["guides"]
    }
    actual_packages: dict[str, dict[str, str]] = {}
    for package in evidence["packages"]:
        package_id = package["packageId"]
        if package_id in actual_packages:
            raise EvidenceError(f"terminology evidence repeats package {package_id}")
        actual_packages[package_id] = {
            "version": package["version"],
            "sha256": package["sha256"],
        }
    if actual_packages != expected_packages:
        missing = sorted(expected_packages.keys() - actual_packages.keys())
        extra = sorted(actual_packages.keys() - expected_packages.keys())
        drifted = sorted(
            package_id
            for package_id in expected_packages.keys() & actual_packages.keys()
            if expected_packages[package_id] != actual_packages[package_id]
        )
        raise EvidenceError(
            "terminology evidence package closure does not match built release packages; "
            f"missing={missing}, extra={extra}, drifted={drifted}"
        )

    systems = [edition["system"] for edition in evidence["terminologyEditions"]]
    if len(systems) != len(set(systems)):
        raise EvidenceError("terminology evidence repeats a terminology edition system")
    try:
        validation_date = datetime.date.fromisoformat(evidence["validationDate"])
        completed_at = datetime.datetime.fromisoformat(
            evidence["result"]["completedAt"].replace("Z", "+00:00")
        )
    except ValueError as error:
        raise EvidenceError(f"terminology evidence has an invalid date: {error}") from error
    if completed_at.date() != validation_date:
        raise EvidenceError(
            "terminology evidence validationDate does not match result.completedAt"
        )
    if (
        evidence["policy"]["warningDisposition"] == "fail"
        and evidence["result"]["warningCount"] != 0
    ):
        raise EvidenceError(
            "terminology evidence policy fails warnings but the result contains warnings"
        )


def terminology_report_input(
    evidence_path: Path, evidence: dict[str, Any]
) -> Path:
    report_name = evidence["result"]["report"]["file"]
    if Path(report_name).name != report_name:
        raise EvidenceError("terminology evidence report must be a sibling JSON filename")
    report = evidence_path.parent / report_name
    require_regular_file(report)
    expected_digest = evidence["result"]["report"]["sha256"]
    actual_digest = sha256(report)
    if actual_digest != expected_digest:
        raise EvidenceError(
            "terminology validation report checksum does not match evidence; "
            f"expected {expected_digest}, found {actual_digest}"
        )
    try:
        json.loads(report.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise EvidenceError(f"terminology validation report is not JSON: {error}") from error
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--lane", choices=sorted(ALLOWED_LANES), required=True)
    parser.add_argument(
        "--terminology-evidence",
        type=Path,
        help="Required only for the online-terminology lane; validated and copied.",
    )
    arguments = parser.parse_args()

    revision = git_head()
    if arguments.source_revision != revision:
        raise EvidenceError(
            f"source revision {arguments.source_revision!r} is not checked-out HEAD {revision!r}"
        )
    if status := git_status():
        first = status.splitlines()[0]
        raise EvidenceError(
            "release evidence must be bound to a clean source tree; first change: "
            f"{first}"
        )
    if (arguments.lane == "online-terminology") != bool(arguments.terminology_evidence):
        raise EvidenceError(
            "online-terminology requires exactly one --terminology-evidence input; "
            "offline-structural prohibits it"
        )

    unresolved_output = arguments.output.absolute()
    if unresolved_output.is_symlink():
        raise EvidenceError(f"release evidence path must not be a symlink: {unresolved_output}")
    output = unresolved_output.resolve()
    build_root = (ROOT / ".build").resolve()
    if not output.is_relative_to(build_root) or output == build_root:
        raise EvidenceError("release evidence output must be a dedicated directory under .build")
    if output.exists() or output.is_symlink():
        raise EvidenceError(f"release evidence path already exists: {output}")

    validate_json_schema(RELEASE_MANIFEST_SCHEMA, MANIFEST)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for catalog in manifest["normativeCatalogs"]:
        validate_json_schema(ROOT / catalog["schema"], ROOT / catalog["path"])
    require_regular_file(MOBILE_SEMANTICS)
    try:
        json.loads(MOBILE_SEMANTICS.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise EvidenceError(f"Mobile semantic snapshot is invalid: {error}") from error
    version = manifest["releaseVersion"]
    guide_inputs: list[dict[str, Any]] = []
    package_digests: dict[str, str] = {}
    for guide in manifest["guides"]:
        source = guide["source"]
        package_id = guide["packageId"]
        package_source = ROOT / source / "output/package.tgz"
        metadata = package_metadata(package_source)
        expected = {
            "name": package_id,
            "version": version,
            "canonical": guide["canonical"],
        }
        for key, value in expected.items():
            if metadata.get(key) != value:
                raise EvidenceError(
                    f"{source} package {key} is {metadata.get(key)!r}, expected {value!r}"
                )
        qa_json = ROOT / source / "output/qa.json"
        qa_html = ROOT / source / "output/qa.html"
        require_regular_file(qa_json)
        require_regular_file(qa_html)
        try:
            qa = json.loads(qa_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise EvidenceError(f"{source} qa.json is invalid: {error}") from error
        package_digests[package_id] = sha256(package_source)
        guide_inputs.append(
            {
                "source": source,
                "packageId": package_id,
                "package": package_source,
                "qaJson": qa_json,
                "qaHtml": qa_html,
                "qa": qa,
            }
        )

    index, contract_paths = machine_contract_index(ROOT, manifest, revision)
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".json") as index_input:
        index_input.write(json_bytes(index))
        index_input.flush()
        validate_json_schema(RELEASE_EVIDENCE_SCHEMA, Path(index_input.name))
    terminology_source: Path | None = None
    terminology_report_source: Path | None = None
    if arguments.terminology_evidence:
        terminology_source = arguments.terminology_evidence.absolute()
        require_regular_file(terminology_source)
        validate_json_schema(TERMINOLOGY_EVIDENCE_SCHEMA, terminology_source)
        terminology = json.loads(terminology_source.read_text(encoding="utf-8"))
        validate_terminology_evidence(
            terminology,
            manifest=manifest,
            source_revision=revision,
            package_digests=package_digests,
        )
        terminology_report_source = terminology_report_input(
            terminology_source, terminology
        )
    dependency_paths = (
        Path("package-lock.json"),
        Path("Gemfile.lock"),
        Path("Scripts/download-fhir-tools.sh"),
    )
    dependency_inputs = {}
    for path in dependency_paths:
        source = ROOT / path
        require_regular_file(source)
        dependency_inputs[path.as_posix()] = sha256(source)
    bundled_java = ROOT / ".build/jdk21/Contents/Home/bin/java"
    java_command = str(bundled_java) if os.access(bundled_java, os.X_OK) else "java"

    # All validation above is preflight. Nothing is copied until the source, package,
    # contract, and (when selected) terminology closures have passed together.
    output.mkdir(parents=True)
    copied: list[Path] = []
    qa_by_guide: dict[str, Any] = {}
    for guide in guide_inputs:
        package_id = guide["packageId"]
        package_target = output / f"{package_id}-{version}.tgz"
        copy_new(guide["package"], package_target)
        copied.append(package_target)
        for suffix, source_key in (("json", "qaJson"), ("html", "qaHtml")):
            qa_target = output / f"{package_id}-{version}-qa.{suffix}"
            copy_new(guide[source_key], qa_target)
            copied.append(qa_target)
        qa_by_guide[guide["source"]] = guide["qa"]

    manifest_target = output / f"release-manifest-{version}.json"
    copy_new(MANIFEST, manifest_target)
    copied.append(manifest_target)
    semantic_target = output / f"mobile-semantic-snapshot-{version}.json"
    copy_new(MOBILE_SEMANTICS, semantic_target)
    copied.append(semantic_target)

    index_target = output / f"machine-contract-index-{version}.json"
    index_target.write_bytes(json_bytes(index))
    copied.append(index_target)
    contracts_target = output / f"grove-fhir-machine-contracts-{version}.tar.gz"
    write_machine_contract_archive(contracts_target, ROOT, index, contract_paths)
    copied.append(contracts_target)

    terminology_target: Path | None = None
    terminology_report_target: Path | None = None
    if terminology_source:
        terminology_target = output / f"terminology-validation-{version}.json"
        copy_new(terminology_source, terminology_target)
        copied.append(terminology_target)
        assert terminology_report_source is not None
        terminology_report_target = output / f"terminology-validation-report-{version}.json"
        copy_new(terminology_report_source, terminology_report_target)
        copied.append(terminology_report_target)

    provenance = {
        "schemaVersion": 2,
        "releaseVersion": version,
        "fhirVersion": manifest["fhirVersion"],
        "sourceRevision": revision,
        "lane": arguments.lane,
        "canonicalPublicationPerformed": False,
        "canonicalPublicationBlocker": (
            "Canonical-host ownership, live HTTPS verification, and release governance "
            "require separate approval; this evidence set is not a canonical publication."
        ),
        "releaseManifestSha256": sha256(MANIFEST),
        "machineContracts": {
            "archive": contracts_target.name,
            "archiveSha256": sha256(contracts_target),
            "index": index_target.name,
            "indexSha256": sha256(index_target),
            "entryCount": len(index["artifacts"]),
        },
        "dependencyBootstrap": {
            "phase": "online-checksum-pinned",
            "offlineReplay": [
                "npm ci --offline",
                "bundle install --local",
                "download-fhir-tools.sh --offline",
                "FHIR Publisher -tx n/a -no-network",
            ],
            "lockSha256": dependency_inputs,
        },
        "toolchain": manifest["toolchain"],
        "runtime": {
            "operatingSystem": platform.platform(),
            "node": command_version(["node", "--version"]),
            "npm": command_version(["npm", "--version"]),
            "python": platform.python_version(),
            "java": command_version([java_command, "-version"]),
            "ruby": command_version(["ruby", "--version"]),
            "bundler": command_version(["bundle", "--version"]),
        },
        "packages": [
            {
                "packageId": package_id,
                "version": version,
                "sha256": digest,
            }
            for package_id, digest in sorted(package_digests.items())
        ],
        "qa": qa_by_guide,
    }
    if terminology_target:
        assert terminology_report_target is not None
        provenance["terminologyEvidence"] = {
            "file": terminology_target.name,
            "sha256": sha256(terminology_target),
            "report": terminology_report_target.name,
            "reportSha256": sha256(terminology_report_target),
        }
    provenance_target = output / f"build-provenance-{version}.json"
    provenance_target.write_bytes(json_bytes(provenance))
    copied.append(provenance_target)

    checksum_target = output / "SHA256SUMS"
    checksum_target.write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in sorted(copied)),
        encoding="utf-8",
    )
    print(
        f"Collected {len(copied)} checksum-bound artifacts for {version} "
        f"at source revision {revision}."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EvidenceError as error:
        raise SystemExit(f"release evidence failed: {error}") from error
