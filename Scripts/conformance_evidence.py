"""Deterministic build and verification primitives for conformance evidence."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import copy
import gzip
import hashlib
import html
import io
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import zlib
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

try:
    from fhir_fixture_corpus import canonical_json_bytes, strict_json_loads
    from fhir_package_semantic_snapshot import (
        create_snapshot,
        read_package_json_files,
        validate_snapshot,
    )
    from fhir_package_semantic_diff import semantic_diff
except ModuleNotFoundError:  # Imported as Scripts.conformance_evidence in tests.
    from Scripts.fhir_fixture_corpus import canonical_json_bytes, strict_json_loads
    from Scripts.fhir_package_semantic_snapshot import (
        create_snapshot,
        read_package_json_files,
        validate_snapshot,
    )
    from Scripts.fhir_package_semantic_diff import semantic_diff


LOCK_SCHEMA_VERSION = 1
LOCK_FILENAME = "evidence-lock.json"
ARCHIVE_PREFIX = "grove-fhir-conformance-evidence"
ARCHIVE_FILENAME = "corpus.tgz"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
GIT_OBJECT_ID = re.compile(r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")
ZERO_COMMIT = "0" * 40
IDENTIFIER = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
MACHINE_LOCAL_UNIX_PATH = re.compile(
    r"(?<![A-Za-z0-9._~:/?#%+\\-])/(?:Users|home/runner|private/tmp)/"
)
MACHINE_LOCAL_WINDOWS_PATH = re.compile(
    r"(?i)(?<![A-Za-z0-9_])(?:[A-Z]:\\+(?:Users|home\\+runner|private\\+tmp)\\+)"
)
TEXT_SUFFIXES = frozenset(
    {
        ".css",
        ".csv",
        ".fsh",
        ".html",
        ".ini",
        ".json",
        ".js",
        ".map",
        ".md",
        ".mjs",
        ".patch",
        ".py",
        ".rb",
        ".scss",
        ".sh",
        ".svg",
        ".toml",
        ".ttl",
        ".txt",
        ".xml",
        ".xhtml",
        ".yaml",
        ".yml",
    }
)


class EvidenceError(ValueError):
    """Raised when evidence inputs or generated artifacts are inconsistent."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
    except OSError as error:
        raise EvidenceError(f"unable to hash {path}: {error}") from error
    return digest.hexdigest()


def semantic_sha256(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def canonical_gzip_header(source_date_epoch: int) -> bytes:
    if (
        not isinstance(source_date_epoch, int)
        or isinstance(source_date_epoch, bool)
        or source_date_epoch < 0
        or source_date_epoch > 0xFFFFFFFF
    ):
        raise EvidenceError("source date epoch must fit the gzip timestamp field")
    return (
        b"\x1f\x8b\x08\x00"
        + source_date_epoch.to_bytes(4, "little")
        + b"\x02\xff"
    )


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = strict_json_loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as error:
        raise EvidenceError(f"unable to read {label} {path}: {error}") from error
    if not isinstance(value, dict):
        raise EvidenceError(f"{label} must be a JSON object: {path}")
    return value


def _json_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from _json_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _json_strings(item)


def validate_portable_text_bytes(data: bytes, label: str, suffix: str) -> None:
    """Reject terminal control output and machine-local paths from public text.

    JSON string values are inspected after decoding as well as in their encoded form so
    escaped Windows separators and an escaped U+001B cannot bypass the publication gate.
    HTTPS URL paths such as ``https://example.org/home/runner/reference`` are not treated
    as filesystem locations.
    """
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise EvidenceError(f"public text is not UTF-8 in {label}: {error}") from error
    candidates = [text]
    if suffix.lower() == ".json":
        try:
            decoded = strict_json_loads(text)
        except ValueError:
            decoded = None
        if decoded is not None:
            candidates.extend(_json_strings(decoded))
    if any("\x1b" in candidate for candidate in candidates):
        raise EvidenceError(f"ANSI escape data is not portable in {label}")
    if any(
        "file://" in candidate
        or MACHINE_LOCAL_UNIX_PATH.search(candidate)
        or MACHINE_LOCAL_WINDOWS_PATH.search(candidate)
        for candidate in candidates
    ):
        raise EvidenceError(f"machine-local filesystem path is not portable in {label}")


def validate_portable_package_bytes(data: bytes, label: str) -> None:
    """Inspect every UTF-8 text member of a sanitized FHIR package archive."""
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as package:
            for member in package.getmembers():
                name = PurePosixPath(member.name)
                if not member.isfile() or name.suffix.lower() not in TEXT_SUFFIXES:
                    continue
                extracted = package.extractfile(member)
                if extracted is None:
                    raise EvidenceError(
                        f"unable to inspect public package text {label}:{member.name}"
                    )
                validate_portable_text_bytes(
                    extracted.read(), f"{label}:{member.name}", name.suffix
                )
    except (EOFError, OSError, tarfile.TarError) as error:
        raise EvidenceError(f"unable to inspect public package {label}: {error}") from error


def validate_portable_public_bytes(data: bytes, label: str, name: str) -> None:
    suffix = PurePosixPath(name).suffix.lower()
    if suffix in TEXT_SUFFIXES:
        validate_portable_text_bytes(data, label, suffix)
    elif suffix == ".tgz":
        validate_portable_package_bytes(data, label)


def validate_portable_file(path: Path, label: str) -> None:
    validate_portable_public_bytes(path.read_bytes(), label, path.name)


def safe_relative_path(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise EvidenceError(f"{label} must be a nonempty repository-relative path")
    candidate = PurePosixPath(value)
    if candidate.is_absolute() or ".." in candidate.parts or "." in candidate.parts:
        raise EvidenceError(f"{label} escapes its root: {value!r}")
    return candidate.as_posix()


def resolve_path(root: Path, relative: Any, label: str) -> Path:
    normalized = safe_relative_path(relative, label)
    root = root.resolve()
    candidate = root.joinpath(*PurePosixPath(normalized).parts)
    current = root
    for part in PurePosixPath(normalized).parts:
        current = current / part
        if current.is_symlink():
            raise EvidenceError(f"{label} may not traverse a symlink: {normalized}")
    resolved = candidate.resolve(strict=False)
    if not resolved.is_relative_to(root):
        raise EvidenceError(f"{label} escapes its root: {normalized}")
    return candidate


def regular_files(root: Path, label: str) -> list[Path]:
    if root.is_symlink() or not root.is_dir():
        raise EvidenceError(f"{label} must be a non-symlink directory: {root}")
    files: list[Path] = []
    for directory, directory_names, filenames in os.walk(root, followlinks=False):
        directory_path = Path(directory)
        for name in sorted(directory_names):
            if (directory_path / name).is_symlink():
                raise EvidenceError(f"{label} contains a symlink: {directory_path / name}")
        for name in sorted(filenames):
            path = directory_path / name
            if path.is_symlink() or not path.is_file():
                raise EvidenceError(f"{label} contains a non-regular file: {path}")
            files.append(path)
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


def unique_by_id(values: Any, label: str) -> dict[str, dict[str, Any]]:
    if not isinstance(values, list):
        raise EvidenceError(f"{label} must be a list")
    result: dict[str, dict[str, Any]] = {}
    for value in values:
        identifier = value.get("id") if isinstance(value, dict) else None
        if not isinstance(identifier, str) or not IDENTIFIER.fullmatch(identifier):
            raise EvidenceError(f"{label} contains an invalid id: {identifier!r}")
        if identifier in result:
            raise EvidenceError(f"{label} contains duplicate id: {identifier}")
        result[identifier] = value
    return result


def validate_json_schema(
    repository: Path, schema_path: Path, instance_paths: Sequence[Path]
) -> None:
    validator = repository / "Scripts/validate-json-schema.cjs"
    command = ["node", str(validator), str(schema_path), *map(str, instance_paths)]
    try:
        subprocess.run(command, cwd=repository, check=True)
    except (OSError, subprocess.CalledProcessError) as error:
        raise EvidenceError(f"JSON Schema 2020-12 validation failed: {error}") from error


def _download_toolchain_spec(script: str) -> tuple[list[tuple[str, str, str]], dict[str, str]]:
    constants: dict[str, str] = {}
    for name in (
        "PUBLISHER_VERSION",
        "PUBLISHER_SHA256",
        "VALIDATOR_VERSION",
        "VALIDATOR_SHA256",
        "TEMPLATE_ID",
        "TEMPLATE_VERSION",
        "TEMPLATE_SHA256",
    ):
        match = re.search(rf'^readonly {name}="([^"]+)"$', script, re.MULTILINE)
        if match is None:
            raise EvidenceError(f"download-fhir-tools.sh does not declare {name}")
        constants[name] = match.group(1)
    packages = [
        (match.group(1), match.group(2), match.group(3))
        for match in re.finditer(
            r'^\s+"([^|"\n]+)\|([^|"\n]+)\|([0-9a-f]{64})"$',
            script,
            re.MULTILINE,
        )
    ]
    if not packages:
        raise EvidenceError("download-fhir-tools.sh has no checksummed FHIR packages")
    return packages, constants


def validate_toolchain(
    repository: Path, toolchain: Mapping[str, Any], package_json: Mapping[str, Any]
) -> None:
    artifacts = toolchain.get("artifacts")
    if not isinstance(artifacts, list):
        raise EvidenceError("toolchain artifacts must be a list")
    artifact_keys: set[tuple[str, str]] = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise EvidenceError("toolchain artifact must be an object")
        key = (artifact.get("id"), artifact.get("version"))
        if key in artifact_keys:
            raise EvidenceError(f"duplicate toolchain artifact: {key[0]}#{key[1]}")
        artifact_keys.add(key)
    download_script_path = repository / "Scripts/download-fhir-tools.sh"
    try:
        script = download_script_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise EvidenceError(f"unable to read {download_script_path}: {error}") from error
    packages, constants = _download_toolchain_spec(script)
    declared_packages = sorted(
        (artifact["id"], artifact["version"], artifact["sha256"])
        for artifact in artifacts
        if artifact.get("kind") == "fhir-package"
    )
    if declared_packages != sorted(packages):
        raise EvidenceError(
            "toolchain FHIR package checksums do not exactly match download-fhir-tools.sh"
        )
    jars = {artifact["id"]: artifact for artifact in artifacts if artifact.get("kind") == "jar"}
    expected_jars = {
        "fhir-ig-publisher": (
            constants["PUBLISHER_VERSION"],
            constants["PUBLISHER_SHA256"],
        ),
        "fhir-validator": (
            constants["VALIDATOR_VERSION"],
            constants["VALIDATOR_SHA256"],
        ),
    }
    if set(jars) != set(expected_jars):
        raise EvidenceError("toolchain must declare exactly the Publisher and Validator JARs")
    for identifier, (version, checksum) in expected_jars.items():
        if (jars[identifier].get("version"), jars[identifier].get("sha256")) != (
            version,
            checksum,
        ):
            raise EvidenceError(f"toolchain {identifier} does not match download script")
    templates = [
        artifact for artifact in artifacts if artifact.get("kind") == "fhir-template"
    ]
    if len(templates) != 1 or (
        templates[0].get("id"),
        templates[0].get("version"),
        templates[0].get("sha256"),
    ) != (
        constants["TEMPLATE_ID"],
        constants["TEMPLATE_VERSION"],
        constants["TEMPLATE_SHA256"],
    ):
        raise EvidenceError("toolchain Publisher template does not match download script")
    root_dependencies = package_json.get("devDependencies")
    npm_packages = toolchain.get("npmPackages", [])
    npm_names = [
        package.get("name") for package in npm_packages if isinstance(package, dict)
    ]
    if len(npm_names) != len(npm_packages) or len(npm_names) != len(set(npm_names)):
        raise EvidenceError("toolchain npmPackages must use unique package names")
    declared_npm = {package["name"]: package["version"] for package in npm_packages}
    if not isinstance(root_dependencies, dict) or declared_npm != root_dependencies:
        raise EvidenceError(
            "toolchain npmPackages must exactly match direct package.json devDependencies"
        )
    if root_dependencies.get("ajv") != "8.20.0":
        raise EvidenceError("Ajv 8.20.0 must be an exact direct devDependency")
    ruby_packages = toolchain.get("rubyPackages", [])
    ruby_names = [
        package.get("name") for package in ruby_packages if isinstance(package, dict)
    ]
    if len(ruby_names) != len(ruby_packages) or len(ruby_names) != len(set(ruby_names)):
        raise EvidenceError("toolchain rubyPackages must use unique package names")
    declared_ruby = {
        package["name"]: package["version"] for package in ruby_packages
    }
    try:
        gemfile = (repository / "Gemfile").read_text(encoding="utf-8")
        gemfile_lock = (repository / "Gemfile.lock").read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise EvidenceError(f"unable to read Ruby toolchain inputs: {error}") from error
    direct_ruby: dict[str, str] = {}
    gem_lines = [line.strip() for line in gemfile.splitlines() if line.strip().startswith("gem ")]
    for line in gem_lines:
        match = re.fullmatch(r'gem\s+"([A-Za-z0-9_.-]+)",\s*"([^"\s]+)"', line)
        if match is None:
            raise EvidenceError(f"Gemfile direct dependency is not exactly pinned: {line}")
        name, version = match.groups()
        if name in direct_ruby:
            raise EvidenceError(f"Gemfile has duplicate direct dependency: {name}")
        direct_ruby[name] = version
    if direct_ruby != declared_ruby:
        raise EvidenceError(
            "toolchain rubyPackages must exactly match direct pinned Gemfile dependencies"
        )
    for name, version in declared_ruby.items():
        if not re.search(
            rf"^    {re.escape(name)} \({re.escape(version)}\)$",
            gemfile_lock,
            re.MULTILINE,
        ) or not re.search(
            rf"^  {re.escape(name)} \(= {re.escape(version)}\)$",
            gemfile_lock,
            re.MULTILINE,
        ):
            raise EvidenceError(
                f"Gemfile.lock does not resolve exact direct dependency {name} {version}"
            )


def _command_output(
    command: Sequence[str],
    label: str,
    *,
    stderr: bool = False,
    environment: Mapping[str, str] | None = None,
) -> str:
    try:
        result = subprocess.run(
            list(command),
            check=True,
            capture_output=True,
            text=True,
            env=None if environment is None else dict(environment),
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise EvidenceError(f"unable to inspect {label} runtime: {error}") from error
    value = result.stderr if stderr else result.stdout
    return value.strip()


def _runtime_version_matches(actual: str, declared: str, precision: str) -> bool:
    if precision == "exact":
        return actual == declared
    if precision == "major-minor":
        return actual == declared or actual.startswith(f"{declared}.")
    raise EvidenceError(f"unsupported runtime version precision: {precision!r}")


def collect_runtime_environment(toolchain: Mapping[str, Any]) -> list[dict[str, Any]]:
    declarations = toolchain["runtimes"]
    commands: dict[str, tuple[list[str], re.Pattern[str], bool]] = {
        "node": (["node", "--version"], re.compile(r"^v([0-9]+(?:\.[0-9]+)+)$"), False),
        "npm": (["npm", "--version"], re.compile(r"^([0-9]+(?:\.[0-9]+)+)$"), False),
        "python": (
            ["python3", "--version"],
            re.compile(r"^Python ([0-9]+(?:\.[0-9]+)+)$"),
            False,
        ),
        "ruby": (
            ["ruby", "--version"],
            re.compile(r"^ruby ([0-9]+(?:\.[0-9]+)+)(?:\s|$)"),
            False,
        ),
        "bundler": (
            ["bundle", "--version"],
            re.compile(r"\A(?:Bundler version )?([0-9]+(?:\.[0-9]+)+)\Z"),
            False,
        ),
    }
    result: list[dict[str, Any]] = []
    for identifier in ("node", "npm", "python", "ruby", "bundler"):
        command, pattern, stderr = commands[identifier]
        raw = _command_output(command, identifier, stderr=stderr)
        match = pattern.search(raw)
        if match is None:
            raise EvidenceError(f"unable to parse {identifier} runtime version: {raw!r}")
        version = match.group(1)
        declaration = declarations[identifier]
        if not _runtime_version_matches(
            version, declaration["version"], declaration["precision"]
        ):
            raise EvidenceError(
                f"{identifier} runtime {version} does not match declared "
                f"{declaration['version']} ({declaration['precision']})"
            )
        entry: dict[str, Any] = {
            "id": identifier,
            "command": command,
            "declaredVersion": declaration["version"],
            "precision": declaration["precision"],
            "version": version,
            "canonicalOutput": f"{identifier} {version}",
        }
        if identifier == "python":
            entry["zlibVersion"] = zlib.ZLIB_RUNTIME_VERSION
            entry["canonicalOutput"] = (
                f"python {version}; zlib {zlib.ZLIB_RUNTIME_VERSION}"
            )
        entry["transitiveSha256"] = semantic_sha256(entry)
        result.append(entry)
    java_command = ["java", "-XshowSettings:properties", "-version"]
    java_raw = _command_output(java_command, "java", stderr=True)
    runtime_match = re.search(r"^\s*java\.runtime\.version = (\S+)\s*$", java_raw, re.MULTILINE)
    vendor_match = re.search(r"^\s*java\.vendor = (.+?)\s*$", java_raw, re.MULTILINE)
    if runtime_match is None or vendor_match is None:
        raise EvidenceError("unable to parse Java runtime version and vendor")
    java_version = runtime_match.group(1).removesuffix("-LTS")
    java_vendor = vendor_match.group(1)
    java_declaration = declarations["java"]
    if not _runtime_version_matches(
        java_version, java_declaration["version"], java_declaration["precision"]
    ):
        raise EvidenceError(
            f"java runtime {java_version} does not match declared "
            f"{java_declaration['version']} ({java_declaration['precision']})"
        )
    distribution = java_declaration.get("distribution")
    if distribution == "temurin" and java_vendor != "Eclipse Adoptium":
        raise EvidenceError(
            f"java distribution temurin requires Eclipse Adoptium, found {java_vendor!r}"
        )
    java_entry: dict[str, Any] = {
        "id": "java",
        "command": java_command,
        "declaredVersion": java_declaration["version"],
        "setupVersion": java_declaration["setupVersion"],
        "precision": java_declaration["precision"],
        "version": java_version,
        "distribution": distribution,
        "vendor": java_vendor,
        "canonicalOutput": f"java {java_version}; distribution={distribution}; vendor={java_vendor}",
    }
    java_entry["transitiveSha256"] = semantic_sha256(java_entry)
    result.append(java_entry)
    return sorted(result, key=lambda item: item["id"])


def _read_downloaded_package_manifest(path: Path, label: str) -> dict[str, Any]:
    """Read only the package identity from an arbitrary checksummed FHIR archive.

    Downloaded dependency packages may contain non-FHIR JSON assets (for example an
    OpenAPI document with a UTF-8 BOM). Those assets are irrelevant to embedded package
    identity and must not weaken the fail-closed semantic package reader used for the
    four guides. This narrow reader therefore inspects exactly package/package.json,
    while still rejecting unsafe names, archive links, special members, and duplicates.
    """
    manifests: list[bytes] = []
    try:
        with tarfile.open(path, "r:gz") as archive:
            for member in archive.getmembers():
                name = member.name
                candidate = PurePosixPath(name)
                if (
                    not name
                    or "\\" in name
                    or candidate.is_absolute()
                    or ".." in candidate.parts
                ):
                    raise EvidenceError(f"{label} contains an unsafe member name: {name!r}")
                if member.issym() or member.islnk():
                    raise EvidenceError(f"{label} contains an archive link: {name}")
                if not member.isfile() and not member.isdir():
                    raise EvidenceError(f"{label} contains an unsupported member: {name}")
                if name != "package/package.json":
                    continue
                if not member.isfile():
                    raise EvidenceError(f"{label} package manifest is not a regular file")
                extracted = archive.extractfile(member)
                if extracted is None:
                    raise EvidenceError(f"{label} package manifest cannot be read")
                manifests.append(extracted.read())
    except (EOFError, OSError, tarfile.TarError) as error:
        raise EvidenceError(f"unable to inspect {label}: {error}") from error
    if len(manifests) != 1:
        raise EvidenceError(f"{label} must contain one package/package.json")
    try:
        value = strict_json_loads(manifests[0].decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as error:
        raise EvidenceError(f"{label} package manifest is invalid JSON: {error}") from error
    if not isinstance(value, dict):
        raise EvidenceError(f"{label} package manifest must be an object")
    return value


def collect_tool_artifacts(
    repository: Path, toolchain: Mapping[str, Any]
) -> list[dict[str, Any]]:
    tools_root = resolve_path(repository, ".build/fhir-tools", "FHIR tools directory")
    result: list[dict[str, Any]] = []
    jar_names = {
        "fhir-ig-publisher": "publisher.jar",
        "fhir-validator": "validator_cli.jar",
    }
    for artifact in sorted(
        toolchain["artifacts"], key=lambda item: (item["kind"], item["id"], item["version"])
    ):
        filename = (
            jar_names[artifact["id"]]
            if artifact["kind"] == "jar"
            else f"{artifact['id']}-{artifact['version']}.tgz"
        )
        path = tools_root / filename
        if path.is_symlink() or not path.is_file():
            raise EvidenceError(f"downloaded tool artifact is missing or unsafe: {path}")
        actual = sha256_file(path)
        if actual != artifact["sha256"]:
            raise EvidenceError(
                f"downloaded tool artifact checksum drift: {artifact['id']}#{artifact['version']}"
            )
        entry: dict[str, Any] = {
            "id": artifact["id"],
            "kind": artifact["kind"],
            "version": artifact["version"],
            "url": artifact["url"],
            "path": path.relative_to(repository).as_posix(),
            "declaredSha256": artifact["sha256"],
            "sha256": actual,
            "size": path.stat().st_size,
        }
        if artifact["kind"] in {"fhir-package", "fhir-template"}:
            package = _read_downloaded_package_manifest(
                path, f"downloaded FHIR package {filename}"
            )
            if (
                package.get("name") != artifact["id"]
                or package.get("version") != artifact["version"]
            ):
                raise EvidenceError(
                    f"downloaded FHIR package identity drift: {artifact['id']}#{artifact['version']}"
                )
            entry["packageId"] = package["name"]
            entry["packageVersion"] = package["version"]
            if artifact["kind"] == "fhir-template":
                if package.get("type") != "fhir.template":
                    raise EvidenceError(
                        f"downloaded Publisher template type drift: {artifact['id']}"
                    )
                entry["packageType"] = package["type"]
        entry["transitiveSha256"] = semantic_sha256(entry)
        result.append(entry)
    return result


def collect_language_packages(
    repository: Path, toolchain: Mapping[str, Any]
) -> list[dict[str, Any]]:
    """Lock direct npm/Ruby resolutions and their registry integrity metadata."""
    package_lock = load_json_object(repository / "package-lock.json", "npm lockfile")
    locked_node_packages = package_lock.get("packages")
    if not isinstance(locked_node_packages, dict):
        raise EvidenceError("package-lock.json packages must be an object")
    npm_lock_sha256 = sha256_file(repository / "package-lock.json")
    result: list[dict[str, Any]] = []
    for declaration in sorted(toolchain["npmPackages"], key=lambda item: item["name"]):
        name = declaration["name"]
        lock_entry = locked_node_packages.get(f"node_modules/{name}")
        if not isinstance(lock_entry, dict):
            raise EvidenceError(f"npm lockfile is missing direct package {name}")
        version = lock_entry.get("version")
        integrity = lock_entry.get("integrity")
        if version != declaration["version"] or not isinstance(integrity, str):
            raise EvidenceError(f"npm lockfile direct package drift: {name}")
        installed = load_json_object(
            repository / "node_modules" / name / "package.json",
            f"installed npm package {name}",
        )
        if installed.get("name") != name or installed.get("version") != version:
            raise EvidenceError(f"installed npm direct package drift: {name}")
        entry: dict[str, Any] = {
            "ecosystem": "npm",
            "name": name,
            "declaredVersion": declaration["version"],
            "resolvedVersion": version,
            "integrity": integrity,
            "lockfileSha256": npm_lock_sha256,
        }
        if name == "firebase-tools":
            raw = _command_output(
                [str(repository / "node_modules/.bin/firebase"), "--version"],
                "Firebase CLI",
                environment={
                    **os.environ,
                    "CI": "true",
                    "FIREBASE_CLI_DISABLE_UPDATE_CHECK": "true",
                },
            )
            if raw != version:
                raise EvidenceError(
                    f"Firebase CLI executable {raw!r} does not match lock {version}"
                )
            entry["executableVersion"] = raw
        entry["transitiveSha256"] = semantic_sha256(entry)
        result.append(entry)
    try:
        gemfile_lock = (repository / "Gemfile.lock").read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise EvidenceError(f"unable to read Gemfile.lock: {error}") from error
    ruby_lock_sha256 = sha256_file(repository / "Gemfile.lock")
    for declaration in sorted(toolchain["rubyPackages"], key=lambda item: item["name"]):
        name = declaration["name"]
        version = declaration["version"]
        match = re.search(
            rf"^  {re.escape(name)} \({re.escape(version)}\) sha256=([0-9a-f]{{64}})$",
            gemfile_lock,
            re.MULTILINE,
        )
        if match is None:
            raise EvidenceError(f"Gemfile.lock checksum is missing for {name} {version}")
        entry = {
            "ecosystem": "rubygems",
            "name": name,
            "declaredVersion": version,
            "resolvedVersion": version,
            "integrity": f"sha256-{match.group(1)}",
            "lockfileSha256": ruby_lock_sha256,
        }
        entry["transitiveSha256"] = semantic_sha256(entry)
        result.append(entry)
    return sorted(result, key=lambda item: (item["ecosystem"], item["name"]))


def _integration_maps(
    integration: Mapping[str, Any]
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    if integration.get("schemaVersion") != 3:
        raise EvidenceError("Integration/sources.json schemaVersion must be 3")
    return (
        unique_by_id(integration.get("sources"), "integration sources"),
        unique_by_id(integration.get("proposals"), "integration proposals"),
    )


def validate_external_evidence_coverage(
    external_evidence: Mapping[str, Mapping[str, Any]],
    implementations: Mapping[str, Mapping[str, Any]],
    proposals: Mapping[str, Mapping[str, Any]],
) -> None:
    """Require generator-proposal ownership for every generated implementation."""
    artifact_coverage: set[str] = set()

    def proposal_closure(identifier: str) -> set[str]:
        result: set[str] = set()
        pending = list(
            proposals[identifier]["dependsOn"]
            + proposals[identifier]["appliesAfter"]
        )
        while pending:
            dependency = pending.pop()
            if dependency in result:
                continue
            if dependency not in proposals:
                raise EvidenceError(
                    f"proposal {identifier} references unknown dependency {dependency}"
                )
            result.add(dependency)
            pending.extend(
                proposals[dependency]["dependsOn"]
                + proposals[dependency]["appliesAfter"]
            )
        return result

    for artifact in external_evidence.values():
        implementation_id = artifact["implementation"]
        if implementation_id not in implementations:
            raise EvidenceError(
                f"generated artifact {artifact['id']} references unknown implementation "
                f"{implementation_id}"
            )
        implementation = implementations[implementation_id]
        proposal_ids = artifact["proposals"]
        if any(proposal_id not in proposals for proposal_id in proposal_ids):
            raise EvidenceError(
                f"external evidence {artifact['id']} references an unknown proposal"
            )
        if (
            artifact["source"] != implementation["source"]
            or artifact["classification"] != implementation["classification"]
            or proposals[proposal_ids[-1]]["source"] != implementation["source"]
        ):
            raise EvidenceError(
                f"external evidence {artifact['id']} provenance is inconsistent"
            )
        if any(
            earlier not in proposal_closure(later)
            for index, later in enumerate(proposal_ids)
            for earlier in proposal_ids[:index]
        ):
            raise EvidenceError(
                f"external evidence {artifact['id']} proposals are not dependency ordered"
            )
        generator = implementation.get("generator")
        if not isinstance(generator, dict):
            raise EvidenceError(
                f"external evidence {artifact['id']} implementation {implementation_id} "
                "has no generator proposal"
            )
        generator_proposal = generator.get("proposal")
        if generator_proposal not in proposal_ids:
            raise EvidenceError(
                f"external evidence {artifact['id']} does not include implementation "
                f"{implementation_id} generator proposal {generator_proposal}"
            )
        artifact_coverage.add(implementation_id)
    for implementation in implementations.values():
        if (
            implementation["classification"]
            in {"accepted-contract", "historical-writer", "legacy-candidate"}
            and implementation["id"] not in artifact_coverage
        ):
            raise EvidenceError(
                f"implementation {implementation['id']} has no declared generated artifact"
            )


def validate_semantic_baseline_inputs(
    repository: Path,
    manifest: Mapping[str, Any],
    toolchain: Mapping[str, Any],
) -> None:
    """Validate only declarations that can influence the four package snapshots."""
    guides = unique_by_id(manifest.get("guides"), "evidence guides")
    package_ids = {guide["packageId"]: guide for guide in guides.values()}
    if len(package_ids) != len(guides):
        raise EvidenceError("semantic baseline guides must use unique packageIds")
    templates = [
        artifact
        for artifact in toolchain["artifacts"]
        if artifact["kind"] == "fhir-template"
    ]
    if len(templates) != 1:
        raise EvidenceError("toolchain must declare exactly one Publisher template")
    expected_template = f"{templates[0]['id']}#{templates[0]['version']}"
    external_packages = {
        (artifact["id"], artifact["version"])
        for artifact in toolchain["artifacts"]
        if artifact["kind"] == "fhir-package"
    }
    for guide in guides.values():
        ini = resolve_path(
            repository, f"{guide['source']}/ig.ini", f"guide {guide['id']} ig.ini"
        ).read_text(encoding="utf-8")
        if re.findall(r"^template\s*=\s*(\S+)\s*$", ini, re.MULTILINE) != [
            expected_template
        ]:
            raise EvidenceError(
                f"guide {guide['id']} must select locked template {expected_template}"
            )
        for dependency in guide["dependencies"]:
            package_id = dependency["packageId"]
            version = dependency["version"]
            if package_id in package_ids:
                if package_ids[package_id]["version"] != version:
                    raise EvidenceError(
                        f"guide {guide['id']} has wrong internal dependency version"
                    )
            elif (package_id, version) not in external_packages:
                raise EvidenceError(
                    f"guide {guide['id']} dependency has no locked archive: "
                    f"{package_id}#{version}"
                )
    publication = load_json_object(
        resolve_path(repository, manifest["publicationConfig"], "publication config"),
        "publication config",
    )
    publication_guides = publication.get("guides", [])
    if [item["source"] for item in publication_guides] != [
        item["source"] for item in manifest["guides"]
    ]:
        raise EvidenceError("semantic baseline guides do not match publication order")
    publication_by_source = {item["source"]: item for item in publication_guides}
    for guide in manifest["guides"]:
        expected = (
            ".build/pages/"
            f"{publication_by_source[guide['source']]['canonicalPath']}"
            "/ci-build/package.tgz"
        )
        if guide["package"] != expected:
            raise EvidenceError(
                f"guide {guide['id']} package must use sanitized Pages bytes at {expected}"
            )


def _owned_structure_definition_owners(
    manifest: Mapping[str, Any],
) -> dict[str, str]:
    """Return the unique guide owner for every declared StructureDefinition."""
    owners: dict[str, str] = {}
    for guide in unique_by_id(manifest.get("guides"), "evidence guides").values():
        for canonical in guide["structureDefinitions"]:
            prior = owners.get(canonical)
            if prior is not None:
                raise EvidenceError(
                    f"StructureDefinition {canonical} is owned by both {prior} and "
                    f"{guide['id']}"
                )
            owners[canonical] = guide["id"]
    return owners


def validate_implementation_profile_claims(manifest: Mapping[str, Any]) -> None:
    """Keep package/profile claims producer-only and exactly owner-complete."""
    owners = _owned_structure_definition_owners(manifest)
    implementations = unique_by_id(
        manifest.get("implementations"), "implementation evidence"
    )
    for implementation in implementations.values():
        identifier = implementation["id"]
        direction = implementation["direction"]
        packages = implementation["packages"]
        profiles = implementation["profiles"]
        if direction in {"consume", "reference"}:
            if packages or profiles:
                raise EvidenceError(
                    f"non-producer implementation {identifier} may not claim packages "
                    "or profiles"
                )
            continue
        unknown = sorted(set(profiles) - set(owners))
        if unknown:
            raise EvidenceError(
                f"producer implementation {identifier} claims unowned "
                "StructureDefinitions: " + ", ".join(unknown)
            )
        expected_packages = {owners[profile] for profile in profiles}
        if set(packages) != expected_packages:
            raise EvidenceError(
                f"producer implementation {identifier} package owners are not exact; "
                f"declared={sorted(packages)}, expected={sorted(expected_packages)}"
            )


def validate_manifest_semantics(
    repository: Path,
    manifest: Mapping[str, Any],
    toolchain: Mapping[str, Any],
    integration: Mapping[str, Any],
) -> None:
    guides = unique_by_id(manifest.get("guides"), "evidence guides")
    corpora = unique_by_id(manifest.get("corpora"), "evidence corpora")
    validation_reports = unique_by_id(
        manifest.get("validationReports"), "validation reports"
    )
    external_evidence = unique_by_id(
        manifest.get("externalEvidence"), "external implementation evidence"
    )
    implementations = unique_by_id(
        manifest.get("implementations"), "implementation evidence"
    )
    sources, proposals = _integration_maps(integration)
    package_ids: dict[str, str] = {}
    for guide in guides.values():
        package_id = guide["packageId"]
        if package_id in package_ids:
            raise EvidenceError(f"duplicate evidence packageId: {package_id}")
        package_ids[package_id] = guide["id"]
    templates = [
        artifact
        for artifact in toolchain["artifacts"]
        if artifact["kind"] == "fhir-template"
    ]
    if len(templates) != 1:
        raise EvidenceError("toolchain must declare exactly one Publisher template")
    expected_template = f"{templates[0]['id']}#{templates[0]['version']}"
    for guide in guides.values():
        ini_path = resolve_path(
            repository,
            f"{guide['source']}/ig.ini",
            f"guide {guide['id']} ig.ini",
        )
        try:
            ini = ini_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            raise EvidenceError(f"unable to inspect {ini_path}: {error}") from error
        matches = re.findall(r"^template\s*=\s*(\S+)\s*$", ini, re.MULTILINE)
        if matches != [expected_template]:
            raise EvidenceError(
                f"guide {guide['id']} must select locked template {expected_template}"
            )
    external_artifacts = {
        (artifact["id"], artifact["version"])
        for artifact in toolchain["artifacts"]
        if artifact["kind"] == "fhir-package"
    }
    for guide in guides.values():
        dependencies = guide["dependencies"]
        keys = [(item["packageId"], item["version"]) for item in dependencies]
        if len(keys) != len(set(keys)):
            raise EvidenceError(f"guide {guide['id']} has duplicate dependencies")
        for package_id, version in keys:
            if package_id in package_ids:
                dependency_guide = guides[package_ids[package_id]]
                if dependency_guide["version"] != version:
                    raise EvidenceError(
                        f"guide {guide['id']} has wrong internal dependency version"
                    )
            elif (package_id, version) not in external_artifacts:
                raise EvidenceError(
                    f"guide {guide['id']} dependency has no checksummed toolchain archive: "
                    f"{package_id}#{version}"
                )
    for corpus in corpora.values():
        for package_id in corpus["packageIds"]:
            if package_id not in package_ids:
                raise EvidenceError(
                    f"corpus {corpus['id']} references unknown packageId {package_id}"
                )
        root = safe_relative_path(corpus["root"], f"corpus {corpus['id']} root")
        manifest_path = safe_relative_path(
            corpus["manifest"], f"corpus {corpus['id']} manifest"
        )
        if not PurePosixPath(manifest_path).is_relative_to(PurePosixPath(root)):
            raise EvidenceError(f"corpus {corpus['id']} manifest is outside its root")
    report_paths: set[str] = set()
    for report in validation_reports.values():
        relative = safe_relative_path(
            report["path"], f"validation report {report['id']} path"
        )
        if relative in report_paths:
            raise EvidenceError(f"duplicate validation report path: {relative}")
        report_paths.add(relative)
        producer = resolve_path(
            repository,
            report["producer"],
            f"validation report {report['id']} producer",
        )
        if not producer.is_file():
            raise EvidenceError(
                f"validation report {report['id']} producer is not a tracked file"
            )
    for evidence_set in external_evidence.values():
        declared_paths = {item["path"] for item in evidence_set["files"]}
        if len(declared_paths) != len(evidence_set["files"]):
            raise EvidenceError(
                f"external evidence {evidence_set['id']} has duplicate file paths"
            )
        fhir_paths = {
            item["path"]
            for item in evidence_set["files"]
            if item["format"] == "fhir-json"
        }
        expected_unknown = evidence_set.get("expectedUnknownExtensions")
        legacy = evidence_set["classification"] in {
            "historical-writer",
            "legacy-candidate",
        }
        if legacy:
            if not isinstance(expected_unknown, list) or not expected_unknown:
                raise EvidenceError(
                    f"legacy external evidence {evidence_set['id']} needs an exact "
                    "unknown-extension contract"
                )
            contract_paths = {item["path"] for item in expected_unknown}
            contract_locations = {
                (item["path"], item["expression"]) for item in expected_unknown
            }
            if (
                contract_paths != fhir_paths
                or len(contract_locations) != len(expected_unknown)
            ):
                raise EvidenceError(
                    f"legacy external evidence {evidence_set['id']} unknown-extension "
                    "contract does not exactly cover its FHIR files and locations"
                )
        elif expected_unknown is not None:
            raise EvidenceError(
                f"accepted external evidence {evidence_set['id']} may not expect "
                "FHIR Validator errors"
            )
        for file in evidence_set["files"]:
            input_names: set[str] = set()
            for reference in file.get("attestationInputs", []):
                if reference["name"] in input_names:
                    raise EvidenceError(
                        f"external evidence {evidence_set['id']} has duplicate "
                        f"attestation input {reference['name']}"
                    )
                input_names.add(reference["name"])
                target = external_evidence.get(reference["evidenceSet"])
                if target is None or reference["path"] not in {
                    item["path"] for item in target["files"]
                }:
                    raise EvidenceError(
                        f"external evidence {evidence_set['id']} references unknown "
                        f"attestation input {reference['evidenceSet']}:{reference['path']}"
                    )
    validate_implementation_profile_claims(manifest)
    for implementation in implementations.values():
        source_id = implementation["source"]
        if source_id not in sources:
            raise EvidenceError(
                f"implementation {implementation['id']} references unknown source {source_id}"
            )
        source = sources[source_id]
        if implementation["repository"] != source["repository"]:
            raise EvidenceError(
                f"implementation {implementation['id']} repository does not match source"
            )
        if implementation["commit"] != source["commit"]:
            raise EvidenceError(
                f"implementation {implementation['id']} commit does not match source"
            )
        for guide_id in implementation["packages"]:
            if guide_id not in guides:
                raise EvidenceError(
                    f"implementation {implementation['id']} references unknown guide {guide_id}"
                )
        generator = implementation["generator"]
        evidence_classifications = {
            "accepted-contract",
            "historical-writer",
            "legacy-candidate",
        }
        if implementation["classification"] in evidence_classifications:
            if not isinstance(generator, dict):
                raise EvidenceError(
                    f"{implementation['classification']} implementation "
                    f"{implementation['id']} needs an integration-proposal generator"
                )
            proposal_id = generator["proposal"]
            if proposal_id not in proposals or proposals[proposal_id]["source"] != source_id:
                raise EvidenceError(
                    f"implementation {implementation['id']} generator proposal is inconsistent"
                )
            proposal = proposals[proposal_id]
            entrypoint = generator["entrypoint"]
            normalized_entrypoint = entrypoint.removeprefix("./")
            declared_commands = {
                str(test["argv"][0]).removeprefix("./")
                for test in proposal.get("tests", [])
                if isinstance(test, dict)
                and isinstance(test.get("argv"), list)
                and test["argv"]
                and isinstance(test["argv"][0], str)
            }
            patch_path = resolve_path(
                repository, proposal["patch"], f"proposal {proposal_id} patch"
            )
            try:
                patch_text = patch_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as error:
                raise EvidenceError(
                    f"unable to inspect generator proposal {proposal_id}: {error}"
                ) from error
            if (
                normalized_entrypoint not in declared_commands
                and normalized_entrypoint not in patch_text
            ):
                raise EvidenceError(
                    f"implementation {implementation['id']} generator entrypoint is not "
                    f"declared or introduced by proposal {proposal_id}"
                )
        elif generator is not None:
            raise EvidenceError(
                f"reference implementation {implementation['id']} may not claim a generator"
            )
    validate_external_evidence_coverage(
        external_evidence, implementations, proposals
    )
    publication = load_json_object(
        resolve_path(repository, manifest["publicationConfig"], "publication config"),
        "publication config",
    )
    publication_guides = publication.get("guides", [])
    publication_sources = [guide["source"] for guide in publication_guides]
    if publication_sources != [guide["source"] for guide in manifest["guides"]]:
        raise EvidenceError(
            "evidence guides must match publication/config.json order and membership"
        )
    publication_by_source = {guide["source"]: guide for guide in publication_guides}
    for guide in manifest["guides"]:
        canonical_path = publication_by_source[guide["source"]]["canonicalPath"]
        expected_package = f".build/pages/{canonical_path}/ci-build/package.tgz"
        if guide["package"] != expected_package:
            raise EvidenceError(
                f"guide {guide['id']} package must use sanitized Pages bytes at "
                f"{expected_package}"
            )
    allowlist = load_json_object(
        resolve_path(repository, manifest["artifactAllowlist"], "artifact allowlist"),
        "artifact allowlist",
    )
    allowlist_by_source = {
        package["source"]: package for package in allowlist.get("packages", [])
    }
    for guide in manifest["guides"]:
        package = allowlist_by_source.get(guide["source"])
        if not isinstance(package, dict):
            raise EvidenceError(f"guide {guide['id']} is absent from artifact allowlist")
        expected_definitions = sorted(
            f"{guide['canonical']}/StructureDefinition/{artifact['id']}"
            for artifact in package.get("artifacts", [])
            if artifact.get("classification") == "definition"
            and artifact.get("resourceType") == "StructureDefinition"
            and artifact.get("fshType") in {"Extension", "Profile"}
        )
        if guide["structureDefinitions"] != expected_definitions:
            raise EvidenceError(
                f"guide {guide['id']} structureDefinitions do not exactly match "
                "the Profile and Extension allowlist"
            )


def _file_record(repository: Path, path: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(repository).as_posix(),
        "sha256": sha256_file(path),
        "size": path.stat().st_size,
    }


def _git_output(repository: Path, arguments: Sequence[str], label: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", *arguments],
            cwd=repository,
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise EvidenceError(f"unable to inspect {label}: {error}") from error
    return result.stdout


def _git_object_format(repository: Path) -> str:
    try:
        value = _git_output(
            repository,
            ["rev-parse", "--show-object-format"],
            "Git object format",
        ).decode("ascii").strip()
    except UnicodeDecodeError as error:
        raise EvidenceError("Git object format is not ASCII") from error
    if value not in {"sha1", "sha256"}:
        raise EvidenceError(f"unsupported Git object format: {value!r}")
    return value


def _decode_git_path(value: bytes, label: str) -> str:
    try:
        path = value.decode("utf-8")
    except UnicodeDecodeError as error:
        raise EvidenceError(f"{label} path is not UTF-8") from error
    return safe_relative_path(path, f"{label} path")


def _git_index_entries(repository: Path) -> dict[str, tuple[str, str]]:
    entries: dict[str, tuple[str, str]] = {}
    output = _git_output(
        repository,
        ["ls-files", "--stage", "-z"],
        "Git index",
    )
    for record in output.split(b"\0"):
        if not record:
            continue
        metadata, separator, encoded_path = record.partition(b"\t")
        try:
            parts = metadata.decode("ascii").split()
        except UnicodeDecodeError as error:
            raise EvidenceError("Git index metadata is not ASCII") from error
        if not separator or len(parts) != 3:
            raise EvidenceError("Git index record is malformed")
        mode, object_id, stage = parts
        path = _decode_git_path(encoded_path, "Git index")
        if (
            stage != "0"
            or not GIT_OBJECT_ID.fullmatch(object_id)
            or path in entries
        ):
            raise EvidenceError(f"Git index entry is not exact: {path}")
        entries[path] = (mode, object_id)
    return entries


def _git_tree_entries(
    repository: Path, revision: str
) -> dict[str, tuple[str, str]]:
    if not COMMIT.fullmatch(revision):
        raise EvidenceError("Git tree revision must be a full lowercase commit SHA")
    entries: dict[str, tuple[str, str]] = {}
    output = _git_output(
        repository,
        ["ls-tree", "-rz", "--full-tree", revision],
        f"Git tree {revision}",
    )
    for record in output.split(b"\0"):
        if not record:
            continue
        metadata, separator, encoded_path = record.partition(b"\t")
        try:
            parts = metadata.decode("ascii").split()
        except UnicodeDecodeError as error:
            raise EvidenceError("Git tree metadata is not ASCII") from error
        if not separator or len(parts) != 3:
            raise EvidenceError("Git tree record is malformed")
        mode, kind, object_id = parts
        path = _decode_git_path(encoded_path, "Git tree")
        expected_kind = "commit" if mode == "160000" else "blob"
        if (
            kind != expected_kind
            or not GIT_OBJECT_ID.fullmatch(object_id)
            or path in entries
        ):
            raise EvidenceError(f"Git tree entry is not exact: {path}")
        entries[path] = (mode, object_id)
    return entries


def _git_blob_id(data: bytes, object_format: str) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    if object_format == "sha1":
        return hashlib.sha1(header + data, usedforsecurity=False).hexdigest()
    if object_format == "sha256":
        return hashlib.sha256(header + data).hexdigest()
    raise EvidenceError(f"unsupported Git object format: {object_format!r}")


def _verify_committed_file(
    repository: Path,
    relative: str,
    entry: tuple[str, str],
    object_format: str,
    label: str,
) -> Path:
    mode, object_id = entry
    if mode not in {"100644", "100755"}:
        raise EvidenceError(f"{label} is not a regular Git file: {relative}")
    path = resolve_path(repository, relative, label)
    if path.is_symlink() or not path.is_file():
        raise EvidenceError(f"{label} is not a non-symlink regular file: {relative}")
    try:
        data = path.read_bytes()
        executable = bool(path.stat().st_mode & 0o111)
    except OSError as error:
        raise EvidenceError(f"unable to inspect {label} {relative}: {error}") from error
    if _git_blob_id(data, object_format) != object_id:
        raise EvidenceError(
            f"{label} working-tree bytes do not match the attributed source revision: "
            f"{relative}"
        )
    if executable != (mode == "100755"):
        raise EvidenceError(
            f"{label} working-tree mode does not match the attributed source revision: "
            f"{relative}"
        )
    return path


def _entries_under(
    entries: Mapping[str, tuple[str, str]], relative_root: str
) -> dict[str, tuple[str, str]]:
    prefix = f"{relative_root}/"
    return {
        path: entry
        for path, entry in entries.items()
        if path.startswith(prefix)
    }


def _collect_committed_root(
    repository: Path,
    relative_root: str,
    label: str,
    index_entries: Mapping[str, tuple[str, str]],
    tree_entries: Mapping[str, tuple[str, str]],
) -> set[str]:
    root = resolve_path(repository, relative_root, label)
    if root.is_symlink() or not root.is_dir():
        raise EvidenceError(f"{label} must be a non-symlink directory: {relative_root}")
    indexed = _entries_under(index_entries, relative_root)
    committed = _entries_under(tree_entries, relative_root)
    if indexed != committed:
        raise EvidenceError(
            f"{label} Git index does not exactly match the attributed source revision"
        )
    non_regular = sorted(
        path
        for path, (mode, _) in committed.items()
        if mode not in {"100644", "100755"}
    )
    if non_regular:
        raise EvidenceError(
            f"{label} contains non-regular Git entries: {', '.join(non_regular)}"
        )
    committed_paths = set(committed)
    actual_paths = {
        path.relative_to(repository).as_posix()
        for path in regular_files(root, label)
    }
    missing = sorted(committed_paths - actual_paths)
    extras = sorted(actual_paths - committed_paths)
    if missing or extras:
        raise EvidenceError(
            f"{label} working-tree inventory does not exactly match Git "
            f"(missing={missing}, untracked-or-ignored={extras})"
        )
    return committed_paths


def collect_input_paths(
    repository: Path,
    manifest: Mapping[str, Any],
    integration: Mapping[str, Any],
) -> list[Path]:
    repository = repository.resolve()
    sources, proposals = _integration_maps(integration)
    revision = git_revision(repository)
    object_format = _git_object_format(repository)
    index_entries = _git_index_entries(repository)
    tree_entries = _git_tree_entries(repository, revision)
    relative_paths = {
        safe_relative_path(path, "tracked evidence input")
        for path in manifest["trackedInputs"]
    }
    for relative_root in manifest["trackedInputRoots"]:
        normalized_root = safe_relative_path(
            relative_root, f"tracked input root {relative_root}"
        )
        relative_paths.update(
            _collect_committed_root(
                repository,
                normalized_root,
                f"tracked input root {normalized_root}",
                index_entries,
                tree_entries,
            )
        )
    for guide in manifest["guides"]:
        guide_source = safe_relative_path(
            guide["source"], f"guide {guide['id']} source"
        )
        for name in ("ig.ini", "sushi-config.yaml"):
            relative_paths.add((PurePosixPath(guide_source) / name).as_posix())
        input_root = (PurePosixPath(guide_source) / "input").as_posix()
        relative_paths.update(
            _collect_committed_root(
                repository,
                input_root,
                f"guide {guide['id']} input",
                index_entries,
                tree_entries,
            )
        )
    for corpus in manifest["corpora"]:
        corpus_root = safe_relative_path(
            corpus["root"], f"corpus {corpus['id']} root"
        )
        relative_paths.update(
            _collect_committed_root(
                repository,
                corpus_root,
                f"corpus {corpus['id']}",
                index_entries,
                tree_entries,
            )
        )
    for proposal in proposals.values():
        relative_paths.add(
            safe_relative_path(proposal["patch"], f"proposal {proposal['id']} patch")
        )

    for relative in relative_paths:
        indexed = index_entries.get(relative)
        committed = tree_entries.get(relative)
        if indexed is None or indexed != committed:
            raise EvidenceError(
                f"tracked evidence input is not exact in HEAD and the Git index: {relative}"
            )
    for implementation in manifest["implementations"]:
        source = sources[implementation["source"]]
        if not implementation["provenance"]["resolvedPackages"]:
            continue
        source_relative = safe_relative_path(
            source["path"], f"source {source['id']} path"
        )
        source_commit = source["commit"]
        if not COMMIT.fullmatch(source_commit):
            raise EvidenceError(f"source {source['id']} commit is invalid")
        source_root = resolve_path(
            repository, source_relative, f"source {source['id']} checkout"
        )
        if git_revision(source_root) != source_commit:
            raise EvidenceError(
                f"source {source['id']} checkout HEAD does not match its pinned gitlink"
            )
        source_format = _git_object_format(source_root)
        source_index = _git_index_entries(source_root)
        source_tree = _git_tree_entries(source_root, source_commit)
        for resolved in implementation["provenance"]["resolvedPackages"]:
            manifest_relative = safe_relative_path(
                resolved["manifest"],
                f"implementation {implementation['id']} resolved package manifest",
            )
            indexed = source_index.get(manifest_relative)
            committed = source_tree.get(manifest_relative)
            if indexed is None or indexed != committed:
                raise EvidenceError(
                    f"resolved package manifest is not exact in the pinned source "
                    f"index: {source_relative}/{manifest_relative}"
                )
            _verify_committed_file(
                source_root,
                manifest_relative,
                committed,
                source_format,
                f"implementation {implementation['id']} resolved package manifest",
            )
            relative_paths.add(
                (PurePosixPath(source_relative) / manifest_relative).as_posix()
            )
    paths: list[Path] = []
    for relative in sorted(relative_paths):
        if relative in index_entries:
            paths.append(
                _verify_committed_file(
                    repository,
                    relative,
                    tree_entries[relative],
                    object_format,
                    "tracked evidence input",
                )
            )
        else:
            path = resolve_path(
                repository, relative, f"gitlink-owned evidence input {relative}"
            )
            if path.is_symlink() or not path.is_file():
                raise EvidenceError(
                    f"gitlink-owned evidence input is not a regular file: {relative}"
                )
            paths.append(path)
    return paths


def collect_inputs(
    repository: Path,
    manifest: Mapping[str, Any],
    integration: Mapping[str, Any],
) -> list[dict[str, Any]]:
    return [_file_record(repository, path) for path in collect_input_paths(repository, manifest, integration)]


def git_revision(repository: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise EvidenceError(f"unable to resolve repository revision: {error}") from error
    revision = result.stdout.strip()
    if not COMMIT.fullmatch(revision):
        raise EvidenceError(f"repository revision is not a full commit SHA: {revision!r}")
    return revision


def git_commit_epoch(repository: Path, revision: str) -> int:
    if not COMMIT.fullmatch(revision):
        raise EvidenceError("source revision must be a full lowercase commit SHA")
    try:
        result = subprocess.run(
            ["git", "show", "-s", "--format=%ct", revision],
            cwd=repository,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise EvidenceError(f"unable to resolve source commit epoch: {error}") from error
    value = result.stdout.strip()
    if not re.fullmatch(r"0|[1-9][0-9]*", value):
        raise EvidenceError(f"source commit epoch is not canonical: {value!r}")
    return int(value)


def _gitlink_commit(repository: Path, relative: str, revision: str) -> str:
    relative = safe_relative_path(relative, "gitlink path")
    indexed = _git_index_entries(repository).get(relative)
    committed = _git_tree_entries(repository, revision).get(relative)
    if indexed is None or indexed != committed:
        raise EvidenceError(f"gitlink {relative} is absent or ambiguous")
    mode, commit = indexed
    if mode != "160000" or not COMMIT.fullmatch(commit):
        raise EvidenceError(f"index entry is not an exact gitlink: {relative}")
    return commit


def collect_gitlinks(
    repository: Path,
    manifest: Mapping[str, Any],
    integration: Mapping[str, Any],
    input_records: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    sources, _ = _integration_maps(integration)
    input_hashes = {record["path"]: record["sha256"] for record in input_records}
    gitmodules_hash = input_hashes.get(".gitmodules")
    integration_hash = input_hashes.get(manifest["integrationSources"])
    if not isinstance(gitmodules_hash, str) or not isinstance(integration_hash, str):
        raise EvidenceError("gitlink provenance inputs are not locked")
    result: list[dict[str, Any]] = []
    top_level_by_source: dict[str, dict[str, Any]] = {}
    repository_revision = git_revision(repository)
    for source_id in sorted(sources):
        source = sources[source_id]
        relative = safe_relative_path(source["path"], f"source {source_id} path")
        index_commit = _gitlink_commit(repository, relative, repository_revision)
        if index_commit != source["commit"]:
            raise EvidenceError(f"gitlink {relative} does not match Integration/sources.json")
        entry: dict[str, Any] = {
            "id": source_id,
            "path": relative,
            "repository": source["repository"],
            "expectedCommit": source["commit"],
            "indexCommit": index_commit,
        }
        entry["transitiveSha256"] = semantic_sha256(
            {
                **entry,
                "gitmodulesSha256": gitmodules_hash,
                "integrationSourcesSha256": integration_hash,
            }
        )
        result.append(entry)
        top_level_by_source[source_id] = entry
    nested_number = 0
    for implementation in manifest["implementations"]:
        source = sources[implementation["source"]]
        source_root = resolve_path(
            repository, source["path"], f"source {implementation['source']} checkout"
        )
        for nested in implementation["provenance"]["nestedGitlinks"]:
            nested_number += 1
            nested_relative = safe_relative_path(
                nested["path"], f"implementation {implementation['id']} nested gitlink"
            )
            if not (source_root / ".git").exists():
                raise EvidenceError(
                    f"nested provenance requires initialized source {implementation['source']}"
                )
            if git_revision(source_root) != source["commit"]:
                raise EvidenceError(
                    f"source {implementation['source']} checkout HEAD does not match "
                    "its pinned gitlink"
                )
            nested_commit = _gitlink_commit(
                source_root, nested_relative, source["commit"]
            )
            if nested_commit != nested["commit"]:
                raise EvidenceError(
                    f"nested gitlink {implementation['id']}:{nested_relative} has drifted"
                )
            combined_path = (
                PurePosixPath(source["path"]) / PurePosixPath(nested_relative)
            ).as_posix()
            entry = {
                "id": f"{implementation['id']}-nested-{nested_number}",
                "path": combined_path,
                "repository": nested["repository"],
                "expectedCommit": nested["commit"],
                "indexCommit": nested_commit,
            }
            entry["transitiveSha256"] = semantic_sha256(
                {
                    **entry,
                    "ownerGitlinkSha256": top_level_by_source[
                        implementation["source"]
                    ]["transitiveSha256"],
                }
            )
            result.append(entry)
    return sorted(result, key=lambda item: item["id"])


def collect_resolved_packages(
    repository: Path,
    manifest: Mapping[str, Any],
    integration: Mapping[str, Any],
    gitlinks: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    sources, _ = _integration_maps(integration)
    gitlink_by_id = {entry["id"]: entry for entry in gitlinks}
    result: list[dict[str, Any]] = []
    for implementation in manifest["implementations"]:
        source = sources[implementation["source"]]
        source_root = resolve_path(repository, source["path"], "implementation source")
        for expected in implementation["provenance"]["resolvedPackages"]:
            relative = (
                PurePosixPath(source["path"]) / PurePosixPath(expected["manifest"])
            ).as_posix()
            path = resolve_path(repository, relative, "resolved package manifest")
            document = load_json_object(path, "resolved package manifest")
            pins = document.get("pins")
            matches = [
                pin
                for pin in pins
                if isinstance(pin, dict) and pin.get("identity") == expected["identity"]
            ] if isinstance(pins, list) else []
            if len(matches) != 1:
                raise EvidenceError(
                    f"resolved package {expected['identity']} is absent or duplicated in {relative}"
                )
            pin = matches[0]
            state = pin.get("state")
            if (
                pin.get("location") != expected["repository"]
                or not isinstance(state, dict)
                or state.get("version") != expected["version"]
                or state.get("revision") != expected["revision"]
            ):
                raise EvidenceError(
                    f"resolved package {expected['identity']} does not match evidence manifest"
                )
            entry = {
                "implementation": implementation["id"],
                "source": implementation["source"],
                "path": relative,
                "identity": expected["identity"],
                "repository": expected["repository"],
                "version": expected["version"],
                "revision": expected["revision"],
                "sha256": sha256_file(path),
            }
            entry["transitiveSha256"] = semantic_sha256(
                {
                    **entry,
                    "sourceGitlinkSha256": gitlink_by_id[implementation["source"]][
                        "transitiveSha256"
                    ],
                }
            )
            result.append(entry)
    return sorted(result, key=lambda item: (item["implementation"], item["identity"]))


def collect_proposals(
    repository: Path, integration: Mapping[str, Any]
) -> list[dict[str, Any]]:
    _, proposals = _integration_maps(integration)
    complete: dict[str, dict[str, Any]] = {}
    visiting: set[str] = set()

    def visit(identifier: str) -> dict[str, Any]:
        if identifier in complete:
            return complete[identifier]
        if identifier in visiting:
            raise EvidenceError(f"proposal dependency cycle at {identifier}")
        visiting.add(identifier)
        proposal = proposals[identifier]
        dependencies = sorted(set(proposal["dependsOn"]))
        applies_after = sorted(set(proposal["appliesAfter"]))
        for dependency in dependencies + applies_after:
            if dependency not in proposals:
                raise EvidenceError(
                    f"proposal {identifier} references unknown dependency {dependency}"
                )
            visit(dependency)
        path = resolve_path(repository, proposal["patch"], f"proposal {identifier} patch")
        actual = sha256_file(path)
        if actual != proposal["sha256"]:
            raise EvidenceError(f"proposal patch checksum drift: {identifier}")
        entry: dict[str, Any] = {
            "id": identifier,
            "source": proposal["source"],
            "path": proposal["patch"],
            "expectedSha256": proposal["sha256"],
            "sha256": actual,
            "dependsOn": dependencies,
            "appliesAfter": applies_after,
        }
        entry["transitiveSha256"] = semantic_sha256(
            {
                **entry,
                "dependencies": [
                    complete[dependency]["transitiveSha256"]
                    for dependency in dependencies + applies_after
                ],
            }
        )
        complete[identifier] = entry
        visiting.remove(identifier)
        return entry

    for identifier in sorted(proposals):
        visit(identifier)
    return [complete[identifier] for identifier in sorted(complete)]


def _copy_file(source: Path, destination: Path) -> None:
    if source.is_symlink() or not source.is_file():
        raise EvidenceError(f"evidence source must be a regular file: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def _toolchain_archives(toolchain: Mapping[str, Any]) -> dict[tuple[str, str], str]:
    return {
        (artifact["id"], artifact["version"]): artifact["sha256"]
        for artifact in toolchain["artifacts"]
        if artifact["kind"] == "fhir-package"
    }


def collect_packages(
    repository: Path,
    evidence_root: Path,
    manifest: Mapping[str, Any],
    toolchain: Mapping[str, Any],
    overrides: Mapping[str, Path] | None = None,
    copy_packages: bool = True,
) -> list[dict[str, Any]]:
    overrides = overrides or {}
    guides = unique_by_id(manifest["guides"], "evidence guides")
    unknown_overrides = sorted(set(overrides) - set(guides))
    if unknown_overrides:
        raise EvidenceError("package overrides reference unknown guides: " + ", ".join(unknown_overrides))
    external_archives = _toolchain_archives(toolchain)
    raw: dict[str, dict[str, Any]] = {}
    for identifier, guide in guides.items():
        input_mode = "override" if identifier in overrides else "declared"
        source_archive = (
            overrides[identifier]
            if identifier in overrides
            else resolve_path(repository, guide["package"], f"guide {identifier} package")
        )
        if source_archive.is_symlink():
            raise EvidenceError(f"guide {identifier} package may not be a symlink")
        source_archive = source_archive.resolve()
        if not source_archive.is_file():
            raise EvidenceError(f"guide {identifier} package does not exist: {source_archive}")
        validate_portable_package_bytes(
            source_archive.read_bytes(), f"guide {identifier} sanitized package"
        )
        try:
            package_files = read_package_json_files(source_archive)
        except ValueError as error:
            raise EvidenceError(
                f"unable to inspect guide {identifier} package: {error}"
            ) from error
        package = package_files["package.json"]
        expected_metadata = {
            "name": guide["packageId"],
            "version": guide["version"],
            "canonical": guide["canonical"],
            "fhirVersions": [guide["fhirVersion"]],
        }
        for field, expected in expected_metadata.items():
            if package.get(field) != expected:
                raise EvidenceError(
                    f"guide {identifier} package {field} is {package.get(field)!r}, "
                    f"expected {expected!r}"
                )
        expected_dependencies = {
            dependency["packageId"]: dependency["version"]
            for dependency in guide["dependencies"]
        }
        if package.get("dependencies") != expected_dependencies:
            raise EvidenceError(f"guide {identifier} package dependencies have drifted")
        destination_relative = f"packages/{identifier}/package.tgz"
        destination = evidence_root / destination_relative
        if copy_packages:
            _copy_file(source_archive, destination)
        elif not destination.is_file():
            raise EvidenceError(f"packaged guide artifact is missing: {destination_relative}")
        elif input_mode == "declared" and sha256_file(source_archive) != sha256_file(destination):
            raise EvidenceError(
                f"packaged guide artifact does not match sanitized Pages bytes: {identifier}"
            )
        try:
            snapshot = create_snapshot(destination)
        except ValueError as error:
            raise EvidenceError(
                f"unable to snapshot guide {identifier} package: {error}"
            ) from error
        failures = validate_snapshot(snapshot)
        if failures:
            raise EvidenceError(
                f"guide {identifier} semantic snapshot is invalid:\n" + "\n".join(failures)
            )
        snapshot_relative = f"snapshots/{identifier}.json"
        snapshot_path = evidence_root / snapshot_relative
        snapshot_bytes = canonical_json_bytes(snapshot)
        if copy_packages:
            snapshot_path.parent.mkdir(parents=True, exist_ok=True)
            snapshot_path.write_bytes(snapshot_bytes)
        else:
            try:
                stored_snapshot = snapshot_path.read_bytes()
            except OSError as error:
                raise EvidenceError(f"semantic snapshot is missing: {snapshot_relative}") from error
            if stored_snapshot != snapshot_bytes:
                raise EvidenceError(f"semantic snapshot does not match package: {identifier}")
        raw[identifier] = {
            "id": identifier,
            "source": guide["source"],
            "declaredPath": guide["package"],
            "inputMode": input_mode,
            "path": destination_relative,
            "packageId": guide["packageId"],
            "version": guide["version"],
            "canonical": guide["canonical"],
            "fhirVersion": guide["fhirVersion"],
            "sha256": sha256_file(destination),
            "size": destination.stat().st_size,
            "semanticSnapshot": snapshot_relative,
            "semanticSha256": sha256_bytes(snapshot_bytes),
            "declaredDependencies": guide["dependencies"],
        }
    package_id_to_guide = {guide["packageId"]: identifier for identifier, guide in guides.items()}
    complete: dict[str, dict[str, Any]] = {}
    visiting: set[str] = set()

    def visit(identifier: str) -> dict[str, Any]:
        if identifier in complete:
            return complete[identifier]
        if identifier in visiting:
            raise EvidenceError(f"FHIR package dependency cycle at {identifier}")
        visiting.add(identifier)
        base = raw[identifier]
        dependencies: list[dict[str, Any]] = []
        for dependency in sorted(
            base["declaredDependencies"],
            key=lambda item: (item["packageId"], item["version"]),
        ):
            package_id = dependency["packageId"]
            version = dependency["version"]
            if package_id in package_id_to_guide:
                dependency_entry = visit(package_id_to_guide[package_id])
                dependency_hash = dependency_entry["sha256"]
                transitive_hash = dependency_entry["transitiveSha256"]
                kind = "internal"
            else:
                key = (package_id, version)
                if key not in external_archives:
                    raise EvidenceError(
                        f"package {identifier} dependency has no toolchain checksum: "
                        f"{package_id}#{version}"
                    )
                dependency_hash = external_archives[key]
                transitive_hash = dependency_hash
                kind = "external"
            dependencies.append(
                {
                    "packageId": package_id,
                    "version": version,
                    "kind": kind,
                    "sha256": dependency_hash,
                    "transitiveSha256": transitive_hash,
                }
            )
        entry = {key: value for key, value in base.items() if key != "declaredDependencies"}
        entry["dependencies"] = dependencies
        entry["transitiveSha256"] = semantic_sha256(
            {
                "packageSha256": entry["sha256"],
                "semanticSha256": entry["semanticSha256"],
                "dependencies": dependencies,
            }
        )
        complete[identifier] = entry
        visiting.remove(identifier)
        return entry

    for identifier in sorted(raw):
        visit(identifier)
    return [complete[identifier] for identifier in sorted(complete)]


def _canonical_reference(value: Any) -> tuple[str, str | None] | None:
    if not isinstance(value, str) or not value:
        return None
    canonical, separator, version = value.partition("|")
    if not canonical:
        return None
    return canonical, version if separator else None


def _validate_locked_canonical_version(
    canonical: str,
    version: str | None,
    definition: Mapping[str, Any],
    label: str,
) -> None:
    if version is None:
        return
    expected = definition["version"]
    if version != expected:
        raise EvidenceError(
            f"{label} references {canonical} version {version!r}, expected {expected!r}"
        )


def _owned_profile_closures(
    evidence_root: Path,
    manifest: Mapping[str, Any],
    packages: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, frozenset[str]]]:
    """Load the exact owned definitions and their transitive owned base closure."""
    guides = unique_by_id(manifest.get("guides"), "evidence guides")
    package_by_id = unique_by_id(list(packages), "locked guide packages")
    if set(package_by_id) != set(guides):
        raise EvidenceError(
            "locked guide package inventory is not exact; "
            f"locked={sorted(package_by_id)}, expected={sorted(guides)}"
        )
    definitions: dict[str, dict[str, Any]] = {}
    owned_namespaces = [
        f"{guide['canonical']}/StructureDefinition/" for guide in guides.values()
    ]
    for identifier, guide in guides.items():
        package = package_by_id[identifier]
        snapshot_path = resolve_path(
            evidence_root,
            package.get("semanticSnapshot"),
            f"guide {identifier} semantic snapshot",
        )
        snapshot = load_json_object(
            snapshot_path, f"guide {identifier} semantic snapshot"
        )
        metadata = snapshot.get("package")
        if not isinstance(metadata, dict) or (
            metadata.get("name") != guide["packageId"]
            or metadata.get("version") != guide["version"]
            or metadata.get("canonical") != guide["canonical"]
        ):
            raise EvidenceError(
                f"guide {identifier} semantic snapshot package ownership has drifted"
            )
        structure_definitions = snapshot.get("structureDefinitions")
        if not isinstance(structure_definitions, dict):
            raise EvidenceError(
                f"guide {identifier} semantic snapshot StructureDefinitions are invalid"
            )
        expected = set(guide["structureDefinitions"])
        if set(structure_definitions) != expected:
            raise EvidenceError(
                f"guide {identifier} semantic snapshot StructureDefinition inventory "
                "is not exact"
            )
        for canonical in sorted(expected):
            entry = structure_definitions[canonical]
            resource = entry.get("resource") if isinstance(entry, dict) else None
            if (
                not isinstance(resource, dict)
                or resource.get("resourceType") != "StructureDefinition"
                or resource.get("url") != canonical
                or not isinstance(resource.get("type"), str)
                or not isinstance(resource.get("version"), str)
                or not resource["version"]
            ):
                raise EvidenceError(
                    f"guide {identifier} StructureDefinition {canonical} is invalid"
                )
            definitions[canonical] = resource

    closures: dict[str, frozenset[str]] = {}
    visiting: set[str] = set()

    def visit(canonical: str) -> frozenset[str]:
        if canonical in closures:
            return closures[canonical]
        if canonical in visiting:
            raise EvidenceError(
                f"owned StructureDefinition baseDefinition cycle at {canonical}"
            )
        visiting.add(canonical)
        closure = {canonical}
        base_reference = _canonical_reference(
            definitions[canonical].get("baseDefinition")
        )
        if base_reference is not None:
            base, version = base_reference
            if base in definitions:
                _validate_locked_canonical_version(
                    base,
                    version,
                    definitions[base],
                    f"StructureDefinition {canonical} baseDefinition",
                )
                closure.update(visit(base))
            elif any(base.startswith(prefix) for prefix in owned_namespaces):
                raise EvidenceError(
                    f"StructureDefinition {canonical} has unresolved owned "
                    f"baseDefinition {base}"
                )
        visiting.remove(canonical)
        closures[canonical] = frozenset(closure)
        return closures[canonical]

    for canonical in sorted(definitions):
        visit(canonical)
    return definitions, closures


def _exercised_owned_profiles(
    evidence_root: Path,
    implementation_id: str,
    external_evidence: Sequence[Mapping[str, Any]],
    definitions: Mapping[str, Mapping[str, Any]],
    owned_namespaces: Sequence[str],
) -> set[str]:
    """Find owned profile assertions and Extension URLs in emitted FHIR JSON."""
    exercised: set[str] = set()

    def register(value: Any, usage: str, resource_type: str | None) -> None:
        if usage == "extension":
            reference = (value, None) if isinstance(value, str) and value else None
        else:
            reference = _canonical_reference(value)
        if reference is None:
            return
        canonical, version = reference
        definition = definitions.get(canonical)
        if definition is None:
            if any(canonical.startswith(prefix) for prefix in owned_namespaces):
                raise EvidenceError(
                    f"implementation {implementation_id} exercises undefined owned "
                    f"StructureDefinition {canonical}"
                )
            return
        _validate_locked_canonical_version(
            canonical,
            version,
            definition,
            f"implementation {implementation_id} {usage}",
        )
        expected_type = definition["type"]
        if usage == "meta.profile" and expected_type != resource_type:
            raise EvidenceError(
                f"implementation {implementation_id} applies {canonical} to "
                f"{resource_type!r}, expected {expected_type!r}"
            )
        if usage == "extension" and expected_type != "Extension":
            raise EvidenceError(
                f"implementation {implementation_id} uses non-Extension {canonical} "
                "as an Extension URL"
            )
        exercised.add(canonical)

    def walk(value: Any, resource_type: str | None = None) -> None:
        if isinstance(value, list):
            for item in value:
                walk(item, resource_type)
            return
        if not isinstance(value, dict):
            return
        local_resource_type = resource_type
        declared_type = value.get("resourceType")
        if isinstance(declared_type, str) and declared_type:
            local_resource_type = declared_type
            meta = value.get("meta")
            profiles = meta.get("profile") if isinstance(meta, dict) else None
            if isinstance(profiles, list):
                for profile in profiles:
                    register(profile, "meta.profile", local_resource_type)
        for field in ("extension", "modifierExtension"):
            extensions = value.get(field)
            if not isinstance(extensions, list):
                continue
            for extension in extensions:
                if isinstance(extension, dict):
                    register(extension.get("url"), "extension", local_resource_type)
        for child in value.values():
            walk(child, local_resource_type)

    for evidence_set in external_evidence:
        if evidence_set.get("implementation") != implementation_id:
            continue
        set_root = safe_relative_path(
            evidence_set.get("path"),
            f"implementation {implementation_id} evidence path",
        )
        for file in evidence_set.get("files", []):
            if not isinstance(file, dict) or file.get("format") != "fhir-json":
                continue
            relative = (
                PurePosixPath(set_root)
                / PurePosixPath(
                    safe_relative_path(
                        file.get("path"),
                        f"implementation {implementation_id} FHIR evidence file",
                    )
                )
            ).as_posix()
            path = resolve_path(
                evidence_root,
                relative,
                f"implementation {implementation_id} FHIR evidence file",
            )
            if not path.is_file():
                raise EvidenceError(
                    f"implementation {implementation_id} FHIR evidence is missing: "
                    f"{relative}"
                )
            walk(_strict_json_bytes(path.read_bytes(), relative))
    return exercised


def validate_implementation_profile_coverage(
    evidence_root: Path,
    manifest: Mapping[str, Any],
    packages: Sequence[Mapping[str, Any]],
    external_evidence: Sequence[Mapping[str, Any]],
) -> None:
    """Prove producer claims equal the emitted owned StructureDefinition closure."""
    validate_implementation_profile_claims(manifest)
    implementations = unique_by_id(
        manifest.get("implementations"), "implementation evidence"
    )
    definitions, closures = _owned_profile_closures(
        evidence_root, manifest, packages
    )
    owned_namespaces = [
        f"{guide['canonical']}/StructureDefinition/"
        for guide in unique_by_id(
            manifest.get("guides"), "evidence guides"
        ).values()
    ]
    for implementation in implementations.values():
        if implementation["direction"] not in {"produce", "round-trip"}:
            continue
        roots = _exercised_owned_profiles(
            evidence_root,
            implementation["id"],
            external_evidence,
            definitions,
            owned_namespaces,
        )
        actual: set[str] = set()
        for root in roots:
            actual.update(closures[root])
        claimed = set(implementation["profiles"])
        if claimed != actual:
            raise EvidenceError(
                f"producer implementation {implementation['id']} owned profile closure "
                f"is not exact; undeclared={sorted(actual - claimed)}, "
                f"unexercised={sorted(claimed - actual)}"
            )


def _semantic_baseline_from_packages(
    evidence_root: Path, packages: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for package in sorted(packages, key=lambda item: item["id"]):
        snapshot_path = evidence_root / package["semanticSnapshot"]
        snapshot = load_json_object(snapshot_path, f"semantic snapshot {package['id']}")
        failures = validate_snapshot(snapshot)
        if failures:
            raise EvidenceError(
                f"semantic snapshot {package['id']} is invalid:\n" + "\n".join(failures)
            )
        entries.append(
            {
                "id": package["id"],
                "packageId": package["packageId"],
                "version": package["version"],
                "snapshot": snapshot,
            }
        )
    return {
        "kind": "grove-fhir-semantic-baseline",
        "schemaVersion": 1,
        "packages": entries,
    }


def _validate_semantic_baseline(
    baseline: Mapping[str, Any], label: str
) -> dict[str, dict[str, Any]]:
    if (
        baseline.get("kind") != "grove-fhir-semantic-baseline"
        or baseline.get("schemaVersion") != 1
    ):
        raise EvidenceError(f"{label} has an unsupported semantic baseline contract")
    packages = unique_by_id(baseline.get("packages"), f"{label} packages")
    for identifier, package in packages.items():
        snapshot = package.get("snapshot")
        if not isinstance(snapshot, dict):
            raise EvidenceError(f"{label} package {identifier} snapshot must be an object")
        failures = validate_snapshot(snapshot)
        if failures:
            raise EvidenceError(
                f"{label} package {identifier} snapshot is invalid:\n"
                + "\n".join(failures)
            )
        metadata = snapshot.get("package", {})
        if (
            metadata.get("name") != package.get("packageId")
            or metadata.get("version") != package.get("version")
        ):
            raise EvidenceError(f"{label} package {identifier} identity has drifted")
    return packages


def _baseline_at_revision(
    repository: Path, relative: str, revision: str
) -> tuple[dict[str, Any], bool]:
    if revision == ZERO_COMMIT:
        return {
            "kind": "grove-fhir-semantic-baseline",
            "schemaVersion": 1,
            "packages": [],
        }, False
    if not COMMIT.fullmatch(revision):
        raise EvidenceError("semantic comparison base must be a full lowercase commit SHA")
    try:
        subprocess.run(
            ["git", "cat-file", "-e", f"{revision}^{{commit}}"],
            cwd=repository,
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise EvidenceError(
            f"semantic comparison base commit is unavailable: {revision}"
        ) from error
    present = subprocess.run(
        ["git", "cat-file", "-e", f"{revision}:{relative}"],
        cwd=repository,
        capture_output=True,
    ).returncode == 0
    if not present:
        return {
            "kind": "grove-fhir-semantic-baseline",
            "schemaVersion": 1,
            "packages": [],
        }, False
    try:
        result = subprocess.run(
            ["git", "show", f"{revision}:{relative}"],
            cwd=repository,
            check=True,
            capture_output=True,
            text=True,
        )
        value = strict_json_loads(result.stdout)
    except (OSError, UnicodeDecodeError, ValueError, subprocess.CalledProcessError) as error:
        raise EvidenceError(
            f"unable to read semantic baseline at exact revision {revision}: {error}"
        ) from error
    if not isinstance(value, dict):
        raise EvidenceError("prior semantic baseline must be a JSON object")
    return value, True


def _semantic_report(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    base_revision: str,
    base_present: bool,
    head_revision: str,
) -> dict[str, Any]:
    before_packages = _validate_semantic_baseline(before, "prior semantic baseline")
    after_packages = _validate_semantic_baseline(after, "current semantic baseline")
    reports: list[dict[str, Any]] = []
    for identifier in sorted(set(before_packages) | set(after_packages)):
        prior = before_packages.get(identifier)
        current = after_packages.get(identifier)
        if prior is None:
            reports.append(
                {
                    "id": identifier,
                    "status": "added",
                    "packageId": current["packageId"],
                    "version": current["version"],
                }
            )
        elif current is None:
            reports.append(
                {
                    "id": identifier,
                    "status": "removed",
                    "packageId": prior["packageId"],
                    "version": prior["version"],
                }
            )
        else:
            difference = semantic_diff(prior["snapshot"], current["snapshot"])
            reports.append(
                {
                    "id": identifier,
                    "status": (
                        "unchanged"
                        if difference["summary"]["total"] == 0
                        else "changed"
                    ),
                    "packageId": current["packageId"],
                    "version": current["version"],
                    "diff": difference,
                }
            )
    return {
        "kind": "grove-fhir-semantic-diff",
        "schemaVersion": 1,
        "baseRevision": base_revision,
        "baseBaselinePresent": base_present,
        "headRevision": head_revision,
        "packages": reports,
    }


def _markdown_value(value: Any) -> str:
    rendered = canonical_json_bytes(value).decode("utf-8").strip().replace("|", "\\|")
    return rendered if len(rendered) <= 240 else rendered[:237] + "..."


def _semantic_report_markdown(report: Mapping[str, Any]) -> bytes:
    lines = [
        "# FHIR package semantic diff",
        "",
        f"Base revision: `{report['baseRevision']}`",
        f"Head revision: `{report['headRevision']}`",
        "",
    ]
    for package in report["packages"]:
        lines.extend(
            [
                f"## {package['id']} — {package['status']}",
                "",
            ]
        )
        difference = package.get("diff")
        if not isinstance(difference, dict):
            lines.append(
                f"Package `{package['packageId']}#{package['version']}` was {package['status']}."
            )
            lines.append("")
            continue
        summary = difference["summary"]
        lines.append(
            f"{summary['total']} semantic change(s): {summary['added']} added, "
            f"{summary['removed']} removed, {summary['changed']} changed."
        )
        lines.append("")
        if difference["changes"]:
            lines.extend(
                [
                    "| Kind | Semantic path | Before | After |",
                    "| --- | --- | --- | --- |",
                ]
            )
            for change in difference["changes"]:
                lines.append(
                    f"| {change['kind']} | `{change['path'] or '/'}` | "
                    f"`{_markdown_value(change.get('before'))}` | "
                    f"`{_markdown_value(change.get('after'))}` |"
                )
            lines.append("")
    return ("\n".join(lines).rstrip() + "\n").encode("utf-8")


def collect_semantic_evidence(
    repository: Path,
    evidence_root: Path,
    manifest: Mapping[str, Any],
    packages: Sequence[Mapping[str, Any]],
    base_revision: str,
    head_revision: str,
    *,
    write_reports: bool,
) -> dict[str, Any]:
    baseline_relative = safe_relative_path(
        manifest["semanticBaseline"], "semantic baseline"
    )
    baseline_path = resolve_path(repository, baseline_relative, "semantic baseline")
    current = _semantic_baseline_from_packages(evidence_root, packages)
    current_bytes = canonical_json_bytes(current)
    try:
        checked_in_bytes = baseline_path.read_bytes()
    except OSError as error:
        raise EvidenceError(f"unable to read semantic baseline: {error}") from error
    if checked_in_bytes != current_bytes:
        raise EvidenceError(
            "Conformance/semantic-baseline.json does not byte-match generated head snapshots"
        )
    before, base_present = _baseline_at_revision(
        repository, baseline_relative, base_revision
    )
    report = _semantic_report(before, current, base_revision, base_present, head_revision)
    outputs = {
        "json": (
            evidence_root / "reports/semantic-diff.json",
            canonical_json_bytes(report),
        ),
        "markdown": (
            evidence_root / "reports/semantic-diff.md",
            _semantic_report_markdown(report),
        ),
    }
    records: list[dict[str, Any]] = []
    for kind, (path, data) in outputs.items():
        if write_reports:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        else:
            try:
                existing = path.read_bytes()
            except OSError as error:
                raise EvidenceError(f"semantic {kind} report is missing: {error}") from error
            if existing != data:
                raise EvidenceError(f"semantic {kind} report has drifted")
        records.append(
            {
                "kind": kind,
                "path": path.relative_to(evidence_root).as_posix(),
                "sha256": sha256_bytes(data),
                "size": len(data),
            }
        )
    entry = {
        "baseRevision": base_revision,
        "baseBaselinePresent": base_present,
        "baselinePath": baseline_relative,
        "baselineSha256": sha256_bytes(current_bytes),
        "reports": records,
    }
    entry["transitiveSha256"] = semantic_sha256(entry)
    return entry


def parse_external_evidence(values: Sequence[str]) -> dict[str, Path]:
    locations: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise EvidenceError("external evidence must use EVIDENCE_SET_ID=PATH")
        identifier, filename = value.split("=", 1)
        if not IDENTIFIER.fullmatch(identifier) or not filename:
            raise EvidenceError(f"invalid external evidence location: {value!r}")
        if identifier in locations:
            raise EvidenceError(f"duplicate external evidence location: {identifier}")
        locations[identifier] = Path(filename)
    return locations


def parse_validation_reports(values: Sequence[str]) -> dict[str, Path]:
    locations: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise EvidenceError("validation report must use REPORT_ID=PATH")
        identifier, filename = value.split("=", 1)
        if not IDENTIFIER.fullmatch(identifier) or not filename:
            raise EvidenceError(f"invalid validation report location: {value!r}")
        if identifier in locations:
            raise EvidenceError(f"duplicate validation report location: {identifier}")
        locations[identifier] = Path(filename)
    return locations


def _strict_json_bytes(data: bytes, label: str) -> dict[str, Any]:
    try:
        value = strict_json_loads(data.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as error:
        raise EvidenceError(f"{label} is not strict UTF-8 JSON: {error}") from error
    if not isinstance(value, dict):
        raise EvidenceError(f"{label} must be a JSON object")
    return value


def _validate_fhir_json(data: bytes, label: str) -> None:
    value = _strict_json_bytes(data, label)
    resource_type = value.get("resourceType")
    if not isinstance(resource_type, str) or not resource_type:
        raise EvidenceError(f"{label} must contain a FHIR resourceType")


def _validate_attestation(
    data: bytes,
    file_declaration: Mapping[str, Any],
    evidence_set: Mapping[str, Any],
    implementation: Mapping[str, Any],
    proposal: Mapping[str, Any],
    expected_inputs: Sequence[Mapping[str, Any]],
) -> None:
    value = _strict_json_bytes(data, f"external evidence {evidence_set['id']}")
    required = {
        "kind",
        "schemaVersion",
        "artifactId",
        "implementation",
        "producerProposal",
        "sourceCommit",
        "testGroup",
        "commands",
        "result",
        "inputs",
    }
    if set(value) != required:
        raise EvidenceError(
            f"external evidence {evidence_set['id']} attestation fields are not exact"
        )
    if (
        value["kind"] != "grove-fhir-test-attestation"
        or value["schemaVersion"] != 1
        or value["artifactId"] != evidence_set["id"]
        or value["implementation"] != evidence_set["implementation"]
        or value["producerProposal"] != evidence_set["proposals"][-1]
        or value["sourceCommit"] != implementation["commit"]
        or value["testGroup"] != file_declaration["testGroup"]
        or value["result"] != "passed"
    ):
        raise EvidenceError(
            f"external evidence {evidence_set['id']} attestation provenance is inconsistent"
        )
    expected_commands = [
        {"cwd": test["cwd"], "argv": test["argv"]}
        for test in proposal.get("tests", [])
        if test.get("group") == file_declaration["testGroup"]
    ]
    if not expected_commands or value["commands"] != expected_commands:
        raise EvidenceError(
            f"external evidence {evidence_set['id']} attestation commands do not "
            "match Integration/sources.json"
        )
    inputs = value["inputs"]
    if not isinstance(inputs, list):
        raise EvidenceError(f"external evidence {evidence_set['id']} inputs must be a list")
    seen: set[str] = set()
    for item in inputs:
        if not isinstance(item, dict) or set(item) != {"name", "sha256", "size"}:
            raise EvidenceError(
                f"external evidence {evidence_set['id']} has an invalid attestation input"
            )
        name = item["name"]
        if (
            not isinstance(name, str)
            or not name
            or "/" in name
            or "\\" in name
            or name in seen
            or not isinstance(item["sha256"], str)
            or not SHA256.fullmatch(item["sha256"])
            or not isinstance(item["size"], int)
            or isinstance(item["size"], bool)
            or item["size"] < 0
        ):
            raise EvidenceError(
                f"external evidence {evidence_set['id']} has invalid input provenance"
            )
        seen.add(name)
    if inputs != sorted(expected_inputs, key=lambda item: item["name"]):
        raise EvidenceError(
            f"external evidence {evidence_set['id']} attestation inputs do not "
            "match the declared evidence files"
        )


def _validate_external_file(
    data: bytes,
    file_declaration: Mapping[str, Any],
    evidence_set: Mapping[str, Any],
    implementation: Mapping[str, Any],
    proposal: Mapping[str, Any],
    expected_inputs: Sequence[Mapping[str, Any]] = (),
) -> None:
    label = f"external evidence {evidence_set['id']}:{file_declaration['path']}"
    if file_declaration["format"] == "fhir-json":
        validate_portable_text_bytes(
            data, label, PurePosixPath(file_declaration["path"]).suffix
        )
        _validate_fhir_json(data, label)
    elif file_declaration["format"] == "test-attestation-v1":
        validate_portable_text_bytes(
            data, label, PurePosixPath(file_declaration["path"]).suffix
        )
        _validate_attestation(
            data,
            file_declaration,
            evidence_set,
            implementation,
            proposal,
            expected_inputs,
        )
    else:
        raise EvidenceError(f"{label} has an unsupported external evidence format")


def _resolve_external_location(path: Path, label: str) -> Path:
    if path.is_symlink():
        raise EvidenceError(f"{label} may not be a symlink")
    absolute = path.absolute()
    resolved = path.resolve()
    if absolute != resolved:
        raise EvidenceError(f"{label} may not traverse a symlink")
    return resolved


def _external_source_files(
    evidence_root: Path,
    declarations: Mapping[str, Mapping[str, Any]],
    locations: Mapping[str, Path] | None,
    *,
    copy_evidence: bool,
) -> dict[str, dict[str, Path]]:
    result: dict[str, dict[str, Path]] = {}
    for identifier, evidence_set in sorted(declarations.items()):
        declared_files = {
            file["path"]: file for file in evidence_set["files"]
        }
        if len(declared_files) != len(evidence_set["files"]):
            raise EvidenceError(f"external evidence {identifier} has duplicate file paths")
        if copy_evidence:
            source = _resolve_external_location(
                (locations or {})[identifier], f"external evidence {identifier}"
            )
        else:
            source = (
                evidence_root
                / "implementations"
                / evidence_set["implementation"]
                / identifier
            )
        if evidence_set["kind"] == "file":
            if copy_evidence:
                if not source.is_file():
                    raise EvidenceError(f"external evidence {identifier} must be a file")
                source_by_path = {next(iter(declared_files)): source}
            else:
                relative = next(iter(declared_files))
                candidate = source / relative
                if candidate.is_symlink() or not candidate.is_file():
                    raise EvidenceError(
                        f"packaged external evidence file is missing: {identifier}:{relative}"
                    )
                source_by_path = {relative: candidate}
        else:
            if source.is_symlink() or not source.is_dir():
                raise EvidenceError(f"external evidence {identifier} must be a directory")
            actual_files = regular_files(source, f"external evidence {identifier}")
            source_by_path = {
                path.relative_to(source).as_posix(): path for path in actual_files
            }
            actual_paths = set(source_by_path)
            if actual_paths != set(declared_files):
                missing = sorted(set(declared_files) - actual_paths)
                extra = sorted(actual_paths - set(declared_files))
                raise EvidenceError(
                    f"external evidence {identifier} file allowlist mismatch; "
                    f"missing={missing}, extra={extra}"
                )
        result[identifier] = source_by_path
    return result


def collect_external_evidence(
    evidence_root: Path,
    manifest: Mapping[str, Any],
    integration: Mapping[str, Any],
    proposals: Sequence[Mapping[str, Any]],
    gitlinks: Sequence[Mapping[str, Any]],
    locations: Mapping[str, Path] | None,
    *,
    copy_evidence: bool,
) -> list[dict[str, Any]]:
    declarations = unique_by_id(
        manifest["externalEvidence"], "external implementation evidence"
    )
    if copy_evidence:
        supplied = set(locations or {})
        if supplied != set(declarations):
            missing = sorted(set(declarations) - supplied)
            unknown = sorted(supplied - set(declarations))
            details = []
            if missing:
                details.append("missing: " + ", ".join(missing))
            if unknown:
                details.append("unknown: " + ", ".join(unknown))
            raise EvidenceError(
                "external evidence locations must exactly match evidence.json ("
                + "; ".join(details)
                + ")"
            )
    source_files = _external_source_files(
        evidence_root,
        declarations,
        locations,
        copy_evidence=copy_evidence,
    )
    implementations = unique_by_id(manifest["implementations"], "implementations")
    _, proposal_declarations = _integration_maps(integration)
    proposal_locks = {proposal["id"]: proposal for proposal in proposals}
    gitlink_locks = {gitlink["id"]: gitlink for gitlink in gitlinks}
    result: list[dict[str, Any]] = []
    for identifier, evidence_set in sorted(declarations.items()):
        implementation = implementations[evidence_set["implementation"]]
        proposal_ids = evidence_set["proposals"]
        proposal_values = [proposal_declarations[item] for item in proposal_ids]
        if (
            evidence_set["source"] != implementation["source"]
            or proposal_values[-1]["source"] != implementation["source"]
            or evidence_set["classification"] != implementation["classification"]
        ):
            raise EvidenceError(f"external evidence {identifier} provenance has drifted")
        destination_relative = (
            f"implementations/{evidence_set['implementation']}/{identifier}"
        )
        destination_root = evidence_root / destination_relative
        declared_files = {
            file["path"]: file for file in evidence_set["files"]
        }
        if len(declared_files) != len(evidence_set["files"]):
            raise EvidenceError(f"external evidence {identifier} has duplicate file paths")
        source_by_path = source_files[identifier]
        records: list[dict[str, Any]] = []
        for relative, file_declaration in sorted(declared_files.items()):
            safe_relative_path(relative, f"external evidence {identifier} file")
            destination = destination_root / relative
            if copy_evidence:
                source_file = source_by_path[relative]
                data = source_file.read_bytes()
                expected_inputs = []
                input_names: set[str] = set()
                for reference in file_declaration.get("attestationInputs", []):
                    name = reference["name"]
                    target_set = reference["evidenceSet"]
                    target_path = reference["path"]
                    if name in input_names:
                        raise EvidenceError(
                            f"external evidence {identifier} has duplicate attestation input {name}"
                        )
                    input_names.add(name)
                    if (
                        target_set not in declarations
                        or target_path not in source_files.get(target_set, {})
                    ):
                        raise EvidenceError(
                            f"external evidence {identifier} references an unknown "
                            f"attestation input {target_set}:{target_path}"
                        )
                    input_data = source_files[target_set][target_path].read_bytes()
                    expected_inputs.append(
                        {
                            "name": name,
                            "sha256": sha256_bytes(input_data),
                            "size": len(input_data),
                        }
                    )
                _validate_external_file(
                    data,
                    file_declaration,
                    evidence_set,
                    implementation,
                    proposal_values[-1],
                    expected_inputs,
                )
                _copy_file(source_file, destination)
            else:
                if destination.is_symlink() or not destination.is_file():
                    raise EvidenceError(
                        f"packaged external evidence file is missing: {identifier}:{relative}"
                    )
                data = destination.read_bytes()
                expected_inputs = []
                for reference in file_declaration.get("attestationInputs", []):
                    input_data = source_files[reference["evidenceSet"]][
                        reference["path"]
                    ].read_bytes()
                    expected_inputs.append(
                        {
                            "name": reference["name"],
                            "sha256": sha256_bytes(input_data),
                            "size": len(input_data),
                        }
                    )
                _validate_external_file(
                    data,
                    file_declaration,
                    evidence_set,
                    implementation,
                    proposal_values[-1],
                    expected_inputs,
                )
            record = {
                "path": relative,
                "mediaType": file_declaration["mediaType"],
                "format": file_declaration["format"],
                "sha256": sha256_bytes(data),
                "size": len(data),
            }
            for field in (
                "testGroup",
                "attestationInputs",
            ):
                if field in file_declaration:
                    record[field] = file_declaration[field]
            records.append(record)
        if not copy_evidence:
            actual_paths = {
                path.relative_to(destination_root).as_posix()
                for path in regular_files(
                    destination_root, f"packaged external evidence {identifier}"
                )
            }
            if actual_paths != set(declared_files):
                raise EvidenceError(
                    f"packaged external evidence {identifier} has stale or extra files"
                )
        entry = {
            "id": identifier,
            "implementation": evidence_set["implementation"],
            "source": implementation["source"],
            "proposals": proposal_ids,
            "classification": evidence_set["classification"],
            "kind": evidence_set["kind"],
            "path": destination_relative,
            "files": records,
            "setDigest": semantic_sha256(records),
        }
        if "expectedUnknownExtensions" in evidence_set:
            entry["expectedUnknownExtensions"] = [
                dict(item) for item in evidence_set["expectedUnknownExtensions"]
            ]
        entry["transitiveSha256"] = semantic_sha256(
            {
                **entry,
                "sourceGitlinkSha256": gitlink_locks[implementation["source"]][
                    "transitiveSha256"
                ],
                "proposalSha256": [
                    proposal_locks[proposal_id]["transitiveSha256"]
                    for proposal_id in proposal_ids
                ],
                "proposalSourceGitlinkSha256": [
                    gitlink_locks[proposal_declarations[proposal_id]["source"]][
                        "transitiveSha256"
                    ]
                    for proposal_id in proposal_ids
                ],
            }
        )
        result.append(entry)
    return result


def _validate_domain_fhir_report(
    repository: Path,
    data: bytes,
    declaration: Mapping[str, Any],
    tool_artifacts: Sequence[Mapping[str, Any]],
    packages: Sequence[Mapping[str, Any]],
    external_evidence: Sequence[Mapping[str, Any]],
) -> None:
    label = f"validation report {declaration['id']}"
    validate_portable_text_bytes(data, label, ".json")
    report = _strict_json_bytes(data, label)
    expected_top_level = {
        "kind",
        "schemaVersion",
        "validator",
        "fhirPackageClosure",
        "guides",
        "coverage",
        "externalEvidence",
    }
    if set(report) != expected_top_level:
        raise EvidenceError(f"{label} has unsupported or missing top-level fields")
    if (
        report.get("kind") != "grove-domain-fhir-validation"
        or report.get("schemaVersion") != 1
        or not isinstance(report.get("validator"), dict)
        or not isinstance(report.get("guides"), list)
        or not isinstance(report.get("coverage"), list)
    ):
        raise EvidenceError(f"{label} has invalid identity or summary fields")

    validators = [item for item in tool_artifacts if item.get("id") == "fhir-validator"]
    if len(validators) != 1:
        raise EvidenceError(f"{label} tool closure has no unique FHIR Validator")
    validator = validators[0]
    expected_validator = {
        "id": "fhir-validator",
        "version": validator["version"],
        "sha256": validator["sha256"],
    }
    if report["validator"] != expected_validator:
        raise EvidenceError(f"{label} Validator identity has drifted")
    expected_package_closure = sorted(
        (
            {
                "id": item["id"],
                "version": item["version"],
                "sha256": item["sha256"],
            }
            for item in tool_artifacts
            if item.get("kind") == "fhir-package"
        ),
        key=lambda item: (item["id"], item["version"]),
    )
    if report.get("fhirPackageClosure") != expected_package_closure:
        raise EvidenceError(f"{label} FHIR package closure has drifted")

    corpus_index = load_json_object(
        repository / "Conformance/corpora/index.json", "domain corpus index"
    )
    domain_corpora = unique_by_id(
        corpus_index.get("domainCorpora"), "domain corpus index entries"
    )
    referenced_corpora = unique_by_id(
        corpus_index.get("referencedCorpora"),
        "referenced corpus index entries",
    )
    packages_by_id = {item["id"]: item for item in packages}
    expected_guides: dict[str, dict[str, Any]] = {}
    for identifier, corpus in sorted(domain_corpora.items()):
        if identifier not in packages_by_id:
            raise EvidenceError(f"{label} is missing locked package {identifier}")
        corpus_manifest = load_json_object(
            resolve_path(
                repository,
                corpus["manifest"],
                f"domain corpus {identifier} manifest",
            ),
            f"domain corpus {identifier} manifest",
        )
        package = packages_by_id[identifier]
        expected_guides[identifier] = {
            "id": identifier,
            "packageId": package["packageId"],
            "version": package["version"],
            "sha256": package["sha256"],
            "baseCount": len(corpus_manifest.get("bases", [])),
            "caseCount": len(corpus_manifest.get("cases", [])),
            "additionalValidCount": len(corpus.get("additionalValidResources", [])),
        }
    reported_guides = report["guides"]
    if [item.get("id") for item in reported_guides if isinstance(item, dict)] != sorted(
        expected_guides
    ):
        raise EvidenceError(f"{label} guide inventory is not sorted and exact")
    guide_fields = {
        "id",
        "packageId",
        "version",
        "sha256",
        "baseCount",
        "caseCount",
        "additionalValidCount",
        "warningCount",
    }
    for item in reported_guides:
        if not isinstance(item, dict) or set(item) != guide_fields:
            raise EvidenceError(f"{label} has an invalid guide result record")
        warning_count = item.get("warningCount")
        if (
            not isinstance(warning_count, int)
            or isinstance(warning_count, bool)
            or warning_count < 0
        ):
            raise EvidenceError(f"{label} guide warningCount is invalid")
        comparable = dict(item)
        comparable.pop("warningCount")
        if comparable != expected_guides[item["id"]]:
            raise EvidenceError(f"{label} guide package or corpus counts have drifted")

    coverage = load_json_object(
        resolve_path(
            repository,
            corpus_index["coverage"],
            "domain coverage inventory",
        ),
        "domain coverage inventory",
    )
    coverage_guides = coverage.get("guides")
    referenced_owners = {
        item.get("ownership")
        for item in referenced_corpora.values()
        if isinstance(item.get("ownership"), str) and item.get("ownership")
    }
    if (
        any(
            not isinstance(item.get("ownership"), str)
            or not item.get("ownership")
            for item in referenced_corpora.values()
        )
        or not isinstance(coverage_guides, dict)
        or set(coverage_guides) != set(domain_corpora) | referenced_owners
    ):
        raise EvidenceError(f"{label} source coverage inventory has drifted")
    expected_coverage = []
    for identifier, source in sorted(coverage_guides.items()):
        if not isinstance(source, dict):
            raise EvidenceError(f"{label} source coverage entry is invalid")
        expected_coverage.append(
            {
                "id": identifier,
                "structureDefinitionCount": len(source.get("structureDefinitions", {})),
                "invariantCount": len(source.get("invariants", {})),
                "computableRuleCount": len(source.get("sourceRules", {})),
                "invalidBoundaryCount": len(set(source.get("caseBoundaries", {}).values())),
                "nonInvalidBoundaryCount": len(source.get("nonInvalidBoundaries", {})),
                "validatorLimitationCount": len(source.get("validatorLimitations", {})),
            }
        )
    if report["coverage"] != expected_coverage:
        raise EvidenceError(f"{label} live-FSH coverage summary has drifted")
    external = report.get("externalEvidence")
    if not isinstance(external, dict) or set(external) != {
        "setCount",
        "fhirInputCount",
        "resourceCount",
        "warningCount",
        "expectedErrorCount",
        "sets",
    }:
        raise EvidenceError(f"{label} externalEvidence summary is not closed")

    expected_sets = {item["id"]: item for item in external_evidence}
    reported_sets = external.get("sets")
    if (
        not isinstance(reported_sets, list)
        or external.get("setCount") != len(expected_sets)
        or len(reported_sets) != len(expected_sets)
    ):
        raise EvidenceError(f"{label} external evidence set count has drifted")
    expected_fhir_count = sum(
        file["format"] == "fhir-json"
        for evidence_set in external_evidence
        for file in evidence_set["files"]
    )
    if external.get("fhirInputCount") != expected_fhir_count:
        raise EvidenceError(f"{label} external FHIR input count has drifted")
    expected_error_count = sum(
        len(evidence_set.get("expectedUnknownExtensions", []))
        for evidence_set in external_evidence
    )
    if external.get("expectedErrorCount") != expected_error_count:
        raise EvidenceError(f"{label} expected external error count has drifted")
    for field in ("resourceCount", "warningCount", "expectedErrorCount"):
        value = external.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise EvidenceError(f"{label} {field} must be a nonnegative integer")

    reported_ids: list[str] = []
    recursive_resource_count = 0
    for reported_set in reported_sets:
        if not isinstance(reported_set, dict) or set(reported_set) != {
            "id",
            "validationScope",
            "expectedErrorCount",
            "files",
        }:
            raise EvidenceError(f"{label} has an invalid external evidence set record")
        identifier = reported_set.get("id")
        files = reported_set.get("files")
        if identifier not in expected_sets or not isinstance(files, list):
            raise EvidenceError(f"{label} references an unknown external evidence set")
        reported_ids.append(identifier)
        expected_set = expected_sets[identifier]
        fhir_files = [
            file for file in expected_set["files"] if file["format"] == "fhir-json"
        ]
        expected_scope = (
            "none"
            if not fhir_files
            else "r4-core"
            if expected_set["classification"]
            in {"historical-writer", "legacy-candidate"}
            else "accepted-package-closure"
        )
        set_expected_error_count = len(
            expected_set.get("expectedUnknownExtensions", [])
        )
        reported_set_error_count = reported_set.get("expectedErrorCount")
        if (
            reported_set.get("validationScope") != expected_scope
            or not isinstance(reported_set_error_count, int)
            or isinstance(reported_set_error_count, bool)
            or reported_set_error_count < 0
            or reported_set_error_count != set_expected_error_count
        ):
            raise EvidenceError(
                f"{label} external validation contract has drifted for {identifier}"
            )
        expected_files = {
            file["path"]: file for file in expected_set["files"]
        }
        if len(files) != len(expected_files):
            raise EvidenceError(f"{label} file count has drifted for {identifier}")
        reported_paths: list[str] = []
        for file in files:
            if not isinstance(file, dict):
                raise EvidenceError(f"{label} has a non-object file record")
            path_value = file.get("path")
            if path_value not in expected_files:
                raise EvidenceError(
                    f"{label} references unknown file {identifier}:{path_value}"
                )
            expected = expected_files[path_value]
            is_fhir = expected["format"] == "fhir-json"
            expected_keys = {"path", "sha256", "size"}
            if is_fhir:
                expected_keys.update({"resourceCount", "expectedErrorCount"})
            if set(file) != expected_keys:
                raise EvidenceError(
                    f"{label} file record fields have drifted for {identifier}:{path_value}"
                )
            if (
                file.get("sha256") != expected["sha256"]
                or file.get("size") != expected["size"]
            ):
                raise EvidenceError(
                    f"{label} file bytes have drifted for {identifier}:{path_value}"
                )
            if is_fhir:
                resource_count = file.get("resourceCount")
                file_expected_error_count = sum(
                    expectation["path"] == path_value
                    for expectation in expected_set.get(
                        "expectedUnknownExtensions", []
                    )
                )
                reported_file_error_count = file.get("expectedErrorCount")
                if (
                    not isinstance(resource_count, int)
                    or isinstance(resource_count, bool)
                    or resource_count < 1
                    or not isinstance(reported_file_error_count, int)
                    or isinstance(reported_file_error_count, bool)
                    or reported_file_error_count < 0
                    or reported_file_error_count != file_expected_error_count
                ):
                    raise EvidenceError(
                        f"{label} FHIR resource or expected error count is invalid for "
                        f"{identifier}:{path_value}"
                    )
                recursive_resource_count += resource_count
            reported_paths.append(path_value)
        if reported_paths != sorted(expected_files):
            raise EvidenceError(f"{label} files are not sorted for {identifier}")
    if reported_ids != sorted(expected_sets):
        raise EvidenceError(f"{label} external evidence sets are not sorted and exact")
    if external.get("resourceCount") != recursive_resource_count:
        raise EvidenceError(f"{label} recursive FHIR resource count has drifted")


def collect_validation_reports(
    repository: Path,
    evidence_root: Path,
    manifest: Mapping[str, Any],
    input_records: Sequence[Mapping[str, Any]],
    tool_artifacts: Sequence[Mapping[str, Any]],
    packages: Sequence[Mapping[str, Any]],
    external_evidence: Sequence[Mapping[str, Any]],
    locations: Mapping[str, Path] | None,
    *,
    copy_reports: bool,
) -> list[dict[str, Any]]:
    declarations = unique_by_id(manifest["validationReports"], "validation reports")
    if copy_reports:
        supplied = set(locations or {})
        if supplied != set(declarations):
            missing = sorted(set(declarations) - supplied)
            unknown = sorted(supplied - set(declarations))
            raise EvidenceError(
                "validation report locations must exactly match evidence.json "
                f"(missing={missing}, unknown={unknown})"
            )
    inputs_by_path = {record["path"]: record for record in input_records}
    result: list[dict[str, Any]] = []
    for identifier, declaration in sorted(declarations.items()):
        producer = declaration["producer"]
        if producer not in inputs_by_path:
            raise EvidenceError(
                f"validation report {identifier} producer is absent from tracked inputs"
            )
        destination = evidence_root / "reports" / safe_relative_path(
            declaration["path"], f"validation report {identifier} path"
        )
        if copy_reports:
            source = _resolve_external_location(
                (locations or {})[identifier], f"validation report {identifier}"
            )
            if not source.is_file():
                raise EvidenceError(f"validation report {identifier} must be a file")
            data = source.read_bytes()
            _validate_domain_fhir_report(
                repository,
                data,
                declaration,
                tool_artifacts,
                packages,
                external_evidence,
            )
            _copy_file(source, destination)
        else:
            if destination.is_symlink() or not destination.is_file():
                raise EvidenceError(f"packaged validation report is missing: {identifier}")
            data = destination.read_bytes()
            _validate_domain_fhir_report(
                repository,
                data,
                declaration,
                tool_artifacts,
                packages,
                external_evidence,
            )
        input_closure = {
            "producer": inputs_by_path[producer],
            "sourceInputs": [
                item
                for item in input_records
                if item["path"].startswith(
                    (
                        "Conformance/corpora/",
                        "Conformance/study-graph/",
                        "mobile/input/fsh/",
                        "healthkit/input/fsh/",
                        "health-connect/input/fsh/",
                        "questionnaire/input/fsh/",
                        "questionnaire/fixtures/validator/",
                        "questionnaire/fixtures/pairs/",
                    )
                )
            ],
            "toolArtifacts": [
                {
                    "id": item["id"],
                    "version": item["version"],
                    "transitiveSha256": item["transitiveSha256"],
                }
                for item in tool_artifacts
            ],
            "packages": [
                {
                    "id": item["id"],
                    "transitiveSha256": item["transitiveSha256"],
                }
                for item in packages
            ],
            "externalEvidence": [
                {
                    "id": item["id"],
                    "transitiveSha256": item["transitiveSha256"],
                }
                for item in external_evidence
            ],
        }
        entry = {
            "id": identifier,
            "path": destination.relative_to(evidence_root).as_posix(),
            "mediaType": declaration["mediaType"],
            "format": declaration["format"],
            "producer": producer,
            "sha256": sha256_bytes(data),
            "size": len(data),
            "inputClosureSha256": semantic_sha256(input_closure),
        }
        entry["transitiveSha256"] = semantic_sha256(entry)
        result.append(entry)
    return result


def collect_corpora(
    repository: Path,
    evidence_root: Path,
    manifest: Mapping[str, Any],
    packages: Sequence[Mapping[str, Any]],
    copy_corpora: bool = True,
) -> list[dict[str, Any]]:
    package_by_id = {package["packageId"]: package for package in packages}
    result: list[dict[str, Any]] = []
    for corpus in sorted(manifest["corpora"], key=lambda item: item["id"]):
        source_root = resolve_path(repository, corpus["root"], f"corpus {corpus['id']} root")
        source_files = regular_files(source_root, f"corpus {corpus['id']}")
        if not source_files:
            raise EvidenceError(f"corpus {corpus['id']} is empty")
        for source in source_files:
            validate_portable_file(
                source,
                f"corpus {corpus['id']}:{source.relative_to(source_root).as_posix()}",
            )
        destination_root = evidence_root / "corpora" / corpus["id"]
        if copy_corpora:
            for source in source_files:
                relative = source.relative_to(source_root)
                _copy_file(source, destination_root / relative)
        destination_files = regular_files(destination_root, f"packaged corpus {corpus['id']}")
        records = [
            {
                "path": path.relative_to(destination_root).as_posix(),
                "sha256": sha256_file(path),
                "size": path.stat().st_size,
            }
            for path in destination_files
        ]
        source_records = [
            {
                "path": path.relative_to(source_root).as_posix(),
                "sha256": sha256_file(path),
                "size": path.stat().st_size,
            }
            for path in source_files
        ]
        if records != source_records:
            raise EvidenceError(f"packaged corpus {corpus['id']} does not match source")
        package_ids = sorted(corpus["packageIds"])
        missing_packages = sorted(set(package_ids) - set(package_by_id))
        if missing_packages:
            raise EvidenceError(
                f"corpus {corpus['id']} package closure is missing: "
                + ", ".join(missing_packages)
            )
        entry = {
            "id": corpus["id"],
            "path": f"corpora/{corpus['id']}",
            "format": corpus["format"],
            "packageIds": package_ids,
            "files": records,
            "sha256": semantic_sha256(records),
        }
        entry["transitiveSha256"] = semantic_sha256(
            {
                "corpusSha256": entry["sha256"],
                "packages": [
                    {
                        "packageId": package_id,
                        "transitiveSha256": package_by_id[package_id][
                            "transitiveSha256"
                        ],
                    }
                    for package_id in package_ids
                ],
            }
        )
        result.append(entry)
    return result


def output_file_records(evidence_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in regular_files(evidence_root, "conformance evidence"):
        relative = path.relative_to(evidence_root).as_posix()
        if relative == LOCK_FILENAME:
            continue
        records.append(
            {"path": relative, "sha256": sha256_file(path), "size": path.stat().st_size}
        )
    return records


def _toolchain_transitive_hash(
    manifest: Mapping[str, Any],
    input_records: Sequence[Mapping[str, Any]],
    runtimes: Sequence[Mapping[str, Any]],
    artifacts: Sequence[Mapping[str, Any]],
    language_packages: Sequence[Mapping[str, Any]],
) -> str:
    paths = {
        manifest["toolchain"],
        "Gemfile",
        "Gemfile.lock",
        "package.json",
        "package-lock.json",
        "Scripts/build-guides.sh",
        "Scripts/cache-fhir-package.cjs",
        "Scripts/download-fhir-tools.sh",
    }
    locked = [record for record in input_records if record["path"] in paths]
    if {record["path"] for record in locked} != paths:
        raise EvidenceError("toolchain transitive inputs are incomplete")
    return semantic_sha256(
        {
            "inputs": locked,
            "runtimes": list(runtimes),
            "artifacts": list(artifacts),
            "languagePackages": list(language_packages),
        }
    )


def _write_supporting_evidence(
    repository: Path,
    evidence_root: Path,
    manifest: Mapping[str, Any],
    integration: Mapping[str, Any],
    proposals: Sequence[Mapping[str, Any]],
) -> None:
    copies = {
        "README.md": "Conformance/README.md",
        "evidence.json": "Conformance/evidence.json",
        "evidence.schema.json": "Conformance/evidence.schema.json",
        "semantic-baseline.json": manifest["semanticBaseline"],
        "toolchain.json": manifest["toolchain"],
        "provenance/integration-sources.json": manifest["integrationSources"],
        "provenance/publication-config.json": manifest["publicationConfig"],
        "provenance/artifact-allowlist.json": manifest["artifactAllowlist"],
        "provenance/gitmodules.txt": ".gitmodules",
    }
    for destination, source in copies.items():
        source_path = resolve_path(
            repository, source, f"evidence support file {source}"
        )
        validate_portable_file(source_path, f"evidence support file {source}")
        _copy_file(
            source_path,
            evidence_root / destination,
        )
    proposal_by_id = {proposal["id"]: proposal for proposal in integration["proposals"]}
    for locked in proposals:
        proposal = proposal_by_id[locked["id"]]
        proposal_path = resolve_path(
            repository, proposal["patch"], f"proposal {locked['id']}"
        )
        validate_portable_file(proposal_path, f"proposal {locked['id']}")
        _copy_file(
            proposal_path,
            evidence_root / "proposals" / f"{locked['id']}.patch",
        )


def build_lock(
    repository: Path,
    evidence_root: Path,
    manifest: Mapping[str, Any],
    toolchain: Mapping[str, Any],
    integration: Mapping[str, Any],
    source_revision: str,
    source_date_epoch: int,
    semantic_base_revision: str,
    overrides: Mapping[str, Path] | None = None,
    external_locations: Mapping[str, Path] | None = None,
    validation_report_locations: Mapping[str, Path] | None = None,
) -> dict[str, Any]:
    inputs = collect_inputs(repository, manifest, integration)
    runtimes = collect_runtime_environment(toolchain)
    language_packages = collect_language_packages(repository, toolchain)
    tool_artifacts = collect_tool_artifacts(repository, toolchain)
    proposals = collect_proposals(repository, integration)
    gitlinks = collect_gitlinks(repository, manifest, integration, inputs)
    resolved_packages = collect_resolved_packages(
        repository, manifest, integration, gitlinks
    )
    _write_supporting_evidence(repository, evidence_root, manifest, integration, proposals)
    packages = collect_packages(
        repository, evidence_root, manifest, toolchain, overrides, copy_packages=True
    )
    semantic_comparison = collect_semantic_evidence(
        repository,
        evidence_root,
        manifest,
        packages,
        semantic_base_revision,
        source_revision,
        write_reports=True,
    )
    external_evidence = collect_external_evidence(
        evidence_root,
        manifest,
        integration,
        proposals,
        gitlinks,
        external_locations,
        copy_evidence=True,
    )
    validate_implementation_profile_coverage(
        evidence_root, manifest, packages, external_evidence
    )
    validation_reports = collect_validation_reports(
        repository,
        evidence_root,
        manifest,
        inputs,
        tool_artifacts,
        packages,
        external_evidence,
        validation_report_locations,
        copy_reports=True,
    )
    corpora = collect_corpora(
        repository, evidence_root, manifest, packages, copy_corpora=True
    )
    files = output_file_records(evidence_root)
    lock: dict[str, Any] = {
        "kind": "grove-fhir-conformance-evidence-lock",
        "schemaVersion": LOCK_SCHEMA_VERSION,
        "sourceRevision": source_revision,
        "sourceDateEpoch": source_date_epoch,
        "inputs": inputs,
        "runtimes": runtimes,
        "runtimeTransitiveSha256": semantic_sha256(runtimes),
        "languagePackages": language_packages,
        "languagePackagesTransitiveSha256": semantic_sha256(language_packages),
        "toolArtifacts": tool_artifacts,
        "toolArtifactsTransitiveSha256": semantic_sha256(tool_artifacts),
        "toolchainTransitiveSha256": _toolchain_transitive_hash(
            manifest, inputs, runtimes, tool_artifacts, language_packages
        ),
        "pathMatrixSha256": semantic_sha256(
            {
                "pathMatrix": manifest["pathMatrix"],
                "pathMatrixIgnored": manifest["pathMatrixIgnored"],
            }
        ),
        "semanticComparison": semantic_comparison,
        "externalEvidence": external_evidence,
        "validationReports": validation_reports,
        "proposals": proposals,
        "gitlinks": gitlinks,
        "resolvedPackages": resolved_packages,
        "packages": packages,
        "corpora": corpora,
        "files": files,
    }
    lock["lockDigest"] = semantic_sha256(lock)
    return lock


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def _validate_archive_sidecar_target(sidecar: Path) -> None:
    if sidecar.is_symlink() or (sidecar.exists() and not sidecar.is_file()):
        raise EvidenceError(f"archive checksum path is unsafe: {sidecar}")


def _write_archive_sidecar(archive: Path, checksum: str) -> None:
    sidecar = Path(f"{archive}.sha256")
    _validate_archive_sidecar_target(sidecar)
    descriptor, filename = tempfile.mkstemp(
        prefix=f".{sidecar.name}.", suffix=".tmp", dir=sidecar.parent
    )
    temporary = Path(filename)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            descriptor = -1
            stream.write(f"{checksum}  {archive.name}\n")
        # Replacing a name is safe even if it is swapped to a symlink after the
        # preflight check: os.replace replaces the link itself and never opens its target.
        os.replace(temporary, sidecar)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary.exists():
            temporary.unlink()


def create_deterministic_archive(
    evidence_root: Path, archive: Path, source_date_epoch: int
) -> str:
    if (
        not isinstance(source_date_epoch, int)
        or isinstance(source_date_epoch, bool)
        or source_date_epoch < 0
        or source_date_epoch > 0xFFFFFFFF
    ):
        raise EvidenceError("source date epoch must fit the gzip timestamp field")
    files = regular_files(evidence_root, "conformance evidence archive source")
    for path in files:
        validate_portable_file(
            path,
            f"conformance evidence {path.relative_to(evidence_root).as_posix()}",
        )
    archive.parent.mkdir(parents=True, exist_ok=True)
    if archive.is_symlink():
        raise EvidenceError(f"archive path may not be a symlink: {archive}")
    _validate_archive_sidecar_target(Path(f"{archive}.sha256"))
    try:
        with archive.open("wb") as raw:
            with gzip.GzipFile(
                filename="",
                mode="wb",
                fileobj=raw,
                compresslevel=9,
                mtime=source_date_epoch,
            ) as compressed:
                with tarfile.open(
                    fileobj=compressed, mode="w", format=tarfile.USTAR_FORMAT
                ) as bundle:
                    for path in files:
                        relative = path.relative_to(evidence_root).as_posix()
                        data = path.read_bytes()
                        member = tarfile.TarInfo(f"{ARCHIVE_PREFIX}/{relative}")
                        member.size = len(data)
                        member.mode = 0o644
                        member.mtime = source_date_epoch
                        member.uid = 0
                        member.gid = 0
                        member.uname = ""
                        member.gname = ""
                        member.linkname = ""
                        member.devmajor = 0
                        member.devminor = 0
                        member.pax_headers = {}
                        bundle.addfile(member, io.BytesIO(data))
    except (OSError, tarfile.TarError, ValueError) as error:
        raise EvidenceError(f"unable to create deterministic evidence archive: {error}") from error
    checksum = sha256_file(archive)
    _write_archive_sidecar(archive, checksum)
    return checksum


def parse_package_overrides(values: Sequence[str]) -> dict[str, Path]:
    overrides: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise EvidenceError("package override must use GUIDE=PATH")
        identifier, filename = value.split("=", 1)
        if not IDENTIFIER.fullmatch(identifier) or not filename:
            raise EvidenceError(f"invalid package override: {value!r}")
        if identifier in overrides:
            raise EvidenceError(f"duplicate package override: {identifier}")
        overrides[identifier] = Path(filename)
    return overrides


def build_evidence(
    repository: Path,
    manifest_path: Path,
    schema_path: Path,
    output: Path,
    archive: Path,
    overrides: Mapping[str, Path] | None = None,
    semantic_base_revision: str | None = None,
    external_locations: Mapping[str, Path] | None = None,
    validation_report_locations: Mapping[str, Path] | None = None,
    validate_schema: bool = True,
) -> dict[str, Any]:
    if manifest_path.is_symlink() or schema_path.is_symlink():
        raise EvidenceError("evidence manifest and schema may not be symlinks")
    if output.is_symlink() or archive.is_symlink():
        raise EvidenceError("evidence output targets may not be symlinks")
    repository = repository.resolve()
    manifest_path = manifest_path.resolve()
    schema_path = schema_path.resolve()
    manifest = load_json_object(manifest_path, "evidence manifest")
    toolchain_path = resolve_path(repository, manifest["toolchain"], "toolchain")
    toolchain = load_json_object(toolchain_path, "toolchain")
    integration_path = resolve_path(
        repository, manifest["integrationSources"], "integration sources"
    )
    integration = load_json_object(integration_path, "integration sources")
    baseline_path = resolve_path(
        repository, manifest["semanticBaseline"], "semantic baseline"
    )
    package_json = load_json_object(repository / "package.json", "package manifest")
    if validate_schema:
        validate_json_schema(
            repository, schema_path, [manifest_path, toolchain_path, baseline_path]
        )
    validate_toolchain(repository, toolchain, package_json)
    validate_manifest_semantics(repository, manifest, toolchain, integration)
    revision = git_revision(repository)
    source_date_epoch = git_commit_epoch(repository, revision)
    if semantic_base_revision is None:
        semantic_base_revision = revision
    if semantic_base_revision != ZERO_COMMIT and not COMMIT.fullmatch(
        semantic_base_revision
    ):
        raise EvidenceError("semantic comparison base must be a full lowercase commit SHA")
    output = output.resolve()
    archive = archive.resolve()
    if output == repository or output == Path(output.anchor) or archive == repository:
        raise EvidenceError("evidence output targets are unsafe")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = Path(
        tempfile.mkdtemp(prefix=".conformance-evidence-", dir=output.parent)
    )
    try:
        lock = build_lock(
            repository,
            temporary,
            manifest,
            toolchain,
            integration,
            revision,
            source_date_epoch,
            semantic_base_revision,
            overrides,
            external_locations,
            validation_report_locations,
        )
        write_json(temporary / LOCK_FILENAME, lock)
        if validate_schema:
            validate_json_schema(repository, schema_path, [temporary / LOCK_FILENAME])
        if output.exists():
            if output.is_symlink() or not output.is_dir():
                raise EvidenceError(f"existing evidence output is unsafe: {output}")
            shutil.rmtree(output)
        os.replace(temporary, output)
        temporary = None
        create_deterministic_archive(output, archive, source_date_epoch)
        return lock
    finally:
        if temporary is not None and temporary.exists():
            shutil.rmtree(temporary)


def update_semantic_baseline(
    repository: Path,
    manifest_path: Path,
    schema_path: Path,
    overrides: Mapping[str, Path] | None = None,
    validate_schema: bool = True,
) -> dict[str, Any]:
    """Atomically update the reviewed baseline from exact sanitized package bytes.

    This is deliberately separate from ``build_evidence``. Normal builds only verify
    the checked-in baseline and never update it as a side effect.
    """
    if manifest_path.is_symlink() or schema_path.is_symlink():
        raise EvidenceError("evidence manifest and schema may not be symlinks")
    repository = repository.resolve()
    manifest_path = manifest_path.resolve()
    schema_path = schema_path.resolve()
    manifest = load_json_object(manifest_path, "evidence manifest")
    toolchain_path = resolve_path(repository, manifest["toolchain"], "toolchain")
    baseline_path = resolve_path(
        repository, manifest["semanticBaseline"], "semantic baseline"
    )
    if baseline_path.is_symlink():
        raise EvidenceError("semantic baseline may not be a symlink")
    toolchain = load_json_object(toolchain_path, "toolchain")
    integration = load_json_object(
        resolve_path(repository, manifest["integrationSources"], "integration sources"),
        "integration sources",
    )
    if validate_schema:
        validate_json_schema(repository, schema_path, [manifest_path, toolchain_path])
    validate_toolchain(
        repository,
        toolchain,
        load_json_object(repository / "package.json", "package manifest"),
    )
    validate_semantic_baseline_inputs(repository, manifest, toolchain)
    temporary_root = Path(
        tempfile.mkdtemp(prefix=".semantic-baseline-", dir=baseline_path.parent)
    )
    temporary_file: Path | None = None
    try:
        packages = collect_packages(
            repository,
            temporary_root,
            manifest,
            toolchain,
            overrides,
            copy_packages=True,
        )
        baseline = _semantic_baseline_from_packages(temporary_root, packages)
        _validate_semantic_baseline(baseline, "generated semantic baseline")
        if validate_schema:
            candidate = temporary_root / "semantic-baseline.json"
            candidate.write_bytes(canonical_json_bytes(baseline))
            validate_json_schema(repository, schema_path, [candidate])
        descriptor, filename = tempfile.mkstemp(
            prefix=".semantic-baseline.", suffix=".json", dir=baseline_path.parent
        )
        os.close(descriptor)
        temporary_file = Path(filename)
        temporary_file.write_bytes(canonical_json_bytes(baseline))
        os.replace(temporary_file, baseline_path)
        temporary_file = None
        return baseline
    finally:
        if temporary_file is not None and temporary_file.exists():
            temporary_file.unlink()
        shutil.rmtree(temporary_root)


def _expected_output_records(evidence_root: Path) -> list[dict[str, Any]]:
    return output_file_records(evidence_root)


def verify_archive(
    evidence_root: Path, archive: Path, source_date_epoch: int
) -> list[str]:
    failures: list[str] = []
    if archive.is_symlink() or not archive.is_file():
        return [f"evidence archive is missing or unsafe: {archive}"]
    sidecar = Path(f"{archive}.sha256")
    expected_sidecar = f"{sha256_file(archive)}  {archive.name}\n"
    try:
        header = archive.read_bytes()[:10]
    except OSError as error:
        failures.append(f"unable to read evidence archive header: {error}")
        return failures
    if header != canonical_gzip_header(source_date_epoch):
        failures.append("evidence archive gzip header is not canonical")
    if sidecar.is_symlink() or not sidecar.is_file():
        failures.append(f"evidence archive checksum is missing or unsafe: {sidecar}")
    else:
        try:
            actual_sidecar = sidecar.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            failures.append(f"unable to read evidence archive checksum: {error}")
        else:
            if actual_sidecar != expected_sidecar:
                failures.append("evidence archive checksum sidecar does not match")
    try:
        expected = {
            f"{ARCHIVE_PREFIX}/{path.relative_to(evidence_root).as_posix()}": path.read_bytes()
            for path in regular_files(evidence_root, "conformance evidence")
        }
    except EvidenceError as error:
        failures.append(str(error))
        return failures
    found: dict[str, bytes] = {}
    try:
        with tarfile.open(archive, "r:gz") as bundle:
            member_names: list[str] = []
            for member in bundle.getmembers():
                member_names.append(member.name)
                if (
                    member.mode != 0o644
                    or member.mtime != source_date_epoch
                    or member.uid != 0
                    or member.gid != 0
                    or member.uname
                    or member.gname
                    or member.pax_headers
                    or member.linkname
                    or member.devmajor != 0
                    or member.devminor != 0
                ):
                    failures.append(f"evidence archive metadata is not canonical: {member.name}")
                if not member.isfile():
                    failures.append(f"evidence archive has a non-file member: {member.name}")
                    continue
                extracted = bundle.extractfile(member)
                if extracted is None:
                    failures.append(f"unable to read evidence archive member: {member.name}")
                    continue
                if member.name in found:
                    failures.append(f"duplicate evidence archive member: {member.name}")
                payload = extracted.read()
                found[member.name] = payload
                try:
                    validate_portable_public_bytes(
                        payload, f"evidence archive member {member.name}", member.name
                    )
                except EvidenceError as error:
                    failures.append(str(error))
            if member_names != sorted(member_names) or len(member_names) != len(
                set(member_names)
            ):
                failures.append("evidence archive members are not sorted and unique")
    except (EOFError, OSError, tarfile.TarError) as error:
        failures.append(f"unable to inspect evidence archive: {error}")
        return failures
    if found != expected:
        failures.append("evidence archive members do not exactly match the evidence directory")
    return failures


def verify_evidence(
    repository: Path,
    manifest_path: Path,
    schema_path: Path,
    evidence_root: Path,
    archive: Path | None = None,
    expected_revision: str | None = None,
    validate_schema: bool = True,
) -> list[str]:
    repository = repository.resolve()
    evidence_root = evidence_root.resolve()
    failures: list[str] = []
    try:
        manifest = load_json_object(manifest_path.resolve(), "evidence manifest")
        toolchain_path = resolve_path(repository, manifest["toolchain"], "toolchain")
        toolchain = load_json_object(toolchain_path, "toolchain")
        baseline_path = resolve_path(
            repository, manifest["semanticBaseline"], "semantic baseline"
        )
        integration = load_json_object(
            resolve_path(repository, manifest["integrationSources"], "integration sources"),
            "integration sources",
        )
        lock_path = evidence_root / LOCK_FILENAME
        lock = load_json_object(lock_path, "evidence lock")
        if validate_schema:
            validate_json_schema(
                repository,
                schema_path.resolve(),
                [manifest_path.resolve(), toolchain_path, baseline_path, lock_path],
            )
        validate_toolchain(
            repository,
            toolchain,
            load_json_object(repository / "package.json", "package manifest"),
        )
        validate_manifest_semantics(repository, manifest, toolchain, integration)
        revision = git_revision(repository)
        source_date_epoch = git_commit_epoch(repository, revision)
        if expected_revision is not None:
            if not COMMIT.fullmatch(expected_revision):
                failures.append("expected revision must be a full lowercase commit SHA")
            elif revision != expected_revision:
                failures.append(
                    f"checked-out revision {revision} does not match expected {expected_revision}"
                )
        if lock.get("sourceRevision") != revision:
            failures.append("evidence lock sourceRevision does not match checkout HEAD")
        if lock.get("sourceDateEpoch") != source_date_epoch:
            failures.append("evidence lock sourceDateEpoch does not match checkout HEAD")
        digest_source = dict(lock)
        actual_digest = digest_source.pop("lockDigest", None)
        if actual_digest != semantic_sha256(digest_source):
            failures.append("evidence lock digest does not match its content")
        expected_inputs = collect_inputs(repository, manifest, integration)
        if lock.get("inputs") != expected_inputs:
            failures.append("evidence lock source inputs have drifted")
        runtimes = collect_runtime_environment(toolchain)
        if lock.get("runtimes") != runtimes:
            failures.append("evidence runtime provenance has drifted")
        if lock.get("runtimeTransitiveSha256") != semantic_sha256(runtimes):
            failures.append("evidence runtime transitive hash has drifted")
        language_packages = collect_language_packages(repository, toolchain)
        if lock.get("languagePackages") != language_packages:
            failures.append("evidence language-package provenance has drifted")
        if lock.get("languagePackagesTransitiveSha256") != semantic_sha256(
            language_packages
        ):
            failures.append("evidence language-package transitive hash has drifted")
        tool_artifacts = collect_tool_artifacts(repository, toolchain)
        if lock.get("toolArtifacts") != tool_artifacts:
            failures.append("evidence downloaded tool artifacts have drifted")
        if lock.get("toolArtifactsTransitiveSha256") != semantic_sha256(tool_artifacts):
            failures.append("evidence tool-artifact transitive hash has drifted")
        if lock.get("toolchainTransitiveSha256") != _toolchain_transitive_hash(
            manifest,
            expected_inputs,
            runtimes,
            tool_artifacts,
            language_packages,
        ):
            failures.append("evidence toolchain transitive hash has drifted")
        if lock.get("pathMatrixSha256") != semantic_sha256(
            {
                "pathMatrix": manifest["pathMatrix"],
                "pathMatrixIgnored": manifest["pathMatrixIgnored"],
            }
        ):
            failures.append("evidence path matrix hash has drifted")
        proposals = collect_proposals(repository, integration)
        if lock.get("proposals") != proposals:
            failures.append("evidence proposal closure has drifted")
        gitlinks = collect_gitlinks(repository, manifest, integration, expected_inputs)
        if lock.get("gitlinks") != gitlinks:
            failures.append("evidence gitlink closure has drifted")
        resolved = collect_resolved_packages(repository, manifest, integration, gitlinks)
        if lock.get("resolvedPackages") != resolved:
            failures.append("evidence resolved-package provenance has drifted")
        external_evidence = collect_external_evidence(
            evidence_root,
            manifest,
            integration,
            proposals,
            gitlinks,
            None,
            copy_evidence=False,
        )
        if lock.get("externalEvidence") != external_evidence:
            failures.append("external implementation evidence has drifted")
        input_modes = {
            package["id"]: package.get("inputMode")
            for package in lock.get("packages", [])
            if isinstance(package, dict) and isinstance(package.get("id"), str)
        }
        packages = collect_packages(
            repository,
            evidence_root,
            manifest,
            toolchain,
            overrides={
                identifier: evidence_root / f"packages/{identifier}/package.tgz"
                for identifier, mode in input_modes.items()
                if mode == "override"
            },
            copy_packages=False,
        )
        for package in packages:
            package["inputMode"] = input_modes.get(package["id"], "declared")
        if lock.get("packages") != packages:
            failures.append("evidence package or dependency closure has drifted")
        validate_implementation_profile_coverage(
            evidence_root, manifest, packages, external_evidence
        )
        validation_reports = collect_validation_reports(
            repository,
            evidence_root,
            manifest,
            expected_inputs,
            tool_artifacts,
            packages,
            external_evidence,
            None,
            copy_reports=False,
        )
        if lock.get("validationReports") != validation_reports:
            failures.append("evidence validation reports have drifted")
        semantic_lock = lock.get("semanticComparison")
        if not isinstance(semantic_lock, dict) or not isinstance(
            semantic_lock.get("baseRevision"), str
        ):
            failures.append("evidence semantic comparison metadata is missing")
        else:
            semantic_comparison = collect_semantic_evidence(
                repository,
                evidence_root,
                manifest,
                packages,
                semantic_lock["baseRevision"],
                revision,
                write_reports=False,
            )
            if semantic_lock != semantic_comparison:
                failures.append("evidence semantic baseline or diff has drifted")
        corpora = collect_corpora(
            repository, evidence_root, manifest, packages, copy_corpora=False
        )
        if lock.get("corpora") != corpora:
            failures.append("evidence corpus closure has drifted")
        actual_files = _expected_output_records(evidence_root)
        if lock.get("files") != actual_files:
            failures.append("evidence artifact files are stale, missing, or modified")
        if archive is not None:
            failures.extend(
                verify_archive(evidence_root, archive.resolve(), source_date_epoch)
            )
    except EvidenceError as error:
        failures.append(str(error))
    return failures


def render_evidence_index(lock: Mapping[str, Any]) -> bytes:
    revision = html.escape(lock["sourceRevision"])
    packages = "\n".join(
        "<li><code>"
        + html.escape(package["packageId"])
        + "#"
        + html.escape(package["version"])
        + "</code> — <code>sha256:"
        + html.escape(package["sha256"])
        + "</code></li>"
        for package in lock["packages"]
    )
    index = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Grove FHIR conformance evidence</title></head>
<body>
<main>
<h1>Grove FHIR conformance evidence</h1>
<p>Repository revision: <code>{revision}</code></p>
<ul>{packages}</ul>
<p><a href="{ARCHIVE_FILENAME}">Download the deterministic evidence bundle</a>
and <a href="{ARCHIVE_FILENAME}.sha256">its SHA-256 checksum</a>.</p>
<p>The <a href="{LOCK_FILENAME}">generated lock</a>,
<a href="evidence.json">declarative manifest</a>,
<a href="evidence.schema.json">JSON Schema</a>, and
<a href="toolchain.json">toolchain pins</a> are available separately.</p>
<p>Review the package <a href="semantic-diff.md">semantic diff</a>
or its <a href="semantic-diff.json">machine-readable form</a>.</p>
</main>
</body>
</html>
"""
    return index.encode("utf-8")


def _safe_pages_destination(site: Path) -> tuple[Path, Path]:
    """Resolve the Pages evidence destination without traversing child symlinks."""
    if site.is_symlink() or not site.is_dir():
        raise EvidenceError(f"Pages site must be a non-symlink directory: {site}")
    resolved_site = site.resolve()
    current = resolved_site
    for component in ("conformance", "ci-build"):
        current = current / component
        if current.is_symlink():
            raise EvidenceError(f"Pages evidence path may not be a symlink: {current}")
        if current.exists() and not current.is_dir():
            raise EvidenceError(f"Pages evidence path must be a directory: {current}")
    resolved_destination = current.resolve(strict=False)
    if (
        resolved_destination == resolved_site
        or not resolved_destination.is_relative_to(resolved_site)
    ):
        raise EvidenceError("Pages evidence destination escapes the Pages site")
    return resolved_site, current


def inject_pages(
    evidence_root: Path,
    archive: Path,
    site: Path,
) -> None:
    if evidence_root.is_symlink() or archive.is_symlink():
        raise EvidenceError("Pages injection paths may not be symlinks")
    site, destination = _safe_pages_destination(site)
    evidence_root = evidence_root.resolve()
    archive = archive.resolve()
    if archive.name != ARCHIVE_FILENAME:
        raise EvidenceError(
            f"public evidence archive must be named {ARCHIVE_FILENAME}"
        )
    lock = load_json_object(evidence_root / LOCK_FILENAME, "evidence lock")
    archive_failures = verify_archive(
        evidence_root, archive, lock.get("sourceDateEpoch")
    )
    if archive_failures:
        raise EvidenceError("invalid evidence archive:\n" + "\n".join(archive_failures))
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    _copy_file(archive, destination / archive.name)
    sidecar = Path(f"{archive}.sha256")
    _copy_file(sidecar, destination / sidecar.name)
    _copy_file(evidence_root / LOCK_FILENAME, destination / LOCK_FILENAME)
    _copy_file(evidence_root / "evidence.json", destination / "evidence.json")
    _copy_file(evidence_root / "evidence.schema.json", destination / "evidence.schema.json")
    _copy_file(evidence_root / "toolchain.json", destination / "toolchain.json")
    _copy_file(
        evidence_root / "reports/semantic-diff.json",
        destination / "semantic-diff.json",
    )
    _copy_file(
        evidence_root / "reports/semantic-diff.md",
        destination / "semantic-diff.md",
    )
    (destination / "index.html").write_bytes(render_evidence_index(lock))


def verify_site_evidence(site: Path, expected_revision: str) -> list[str]:
    """Verify a downloaded Pages artifact without rebuilding any guide."""
    failures: list[str] = []
    try:
        if not COMMIT.fullmatch(expected_revision):
            raise EvidenceError("expected revision must be a full lowercase commit SHA")
        site, destination = _safe_pages_destination(site)
        lock_path = destination / LOCK_FILENAME
        lock = load_json_object(lock_path, "Pages evidence lock")
        if lock.get("sourceRevision") != expected_revision:
            failures.append(
                "Pages evidence lock sourceRevision does not match the workflow revision"
            )
        source_date_epoch = lock.get("sourceDateEpoch")
        if (
            not isinstance(source_date_epoch, int)
            or isinstance(source_date_epoch, bool)
            or source_date_epoch < 0
            or source_date_epoch > 0xFFFFFFFF
        ):
            failures.append("Pages evidence lock sourceDateEpoch is invalid")
            source_date_epoch = -1
        digest_source = dict(lock)
        actual_digest = digest_source.pop("lockDigest", None)
        if actual_digest != semantic_sha256(digest_source):
            failures.append("Pages evidence lock digest does not match its content")
        archive = destination / ARCHIVE_FILENAME
        sidecar = Path(f"{archive}.sha256")
        if archive.is_symlink() or not archive.is_file():
            failures.append(f"Pages evidence archive is missing or unsafe: {archive}")
            return failures
        expected_sidecar = f"{sha256_file(archive)}  {archive.name}\n"
        try:
            header = archive.read_bytes()[:10]
        except OSError as error:
            failures.append(f"unable to read Pages evidence archive header: {error}")
            header = b""
        if header != canonical_gzip_header(source_date_epoch):
            failures.append("Pages evidence archive gzip header is not canonical")
        if sidecar.is_symlink() or not sidecar.is_file():
            failures.append(f"Pages evidence checksum is missing or unsafe: {sidecar}")
        else:
            try:
                actual_sidecar = sidecar.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as error:
                failures.append(f"unable to read Pages evidence checksum: {error}")
            else:
                if actual_sidecar != expected_sidecar:
                    failures.append("Pages evidence archive checksum sidecar does not match")
        names: set[str] = set()
        ordered_names: list[str] = []
        archive_members: dict[str, bytes] = {}
        with tarfile.open(archive, "r:gz") as bundle:
            for member in bundle.getmembers():
                ordered_names.append(member.name)
                name = PurePosixPath(member.name)
                if (
                    name.is_absolute()
                    or ".." in name.parts
                    or not member.isfile()
                    or not member.name.startswith(f"{ARCHIVE_PREFIX}/")
                ):
                    failures.append(
                        f"Pages evidence archive has an unsafe member: {member.name}"
                    )
                    continue
                if member.name in names:
                    failures.append(
                        f"Pages evidence archive has a duplicate member: {member.name}"
                    )
                names.add(member.name)
                if (
                    member.mode != 0o644
                    or member.mtime != source_date_epoch
                    or member.uid != 0
                    or member.gid != 0
                    or member.uname
                    or member.gname
                    or member.pax_headers
                    or member.linkname
                    or member.devmajor != 0
                    or member.devminor != 0
                ):
                    failures.append(
                        f"Pages evidence archive metadata is not canonical: {member.name}"
                    )
                extracted = bundle.extractfile(member)
                if extracted is None:
                    failures.append(
                        f"Pages evidence archive member cannot be read: {member.name}"
                    )
                    continue
                relative = member.name[len(ARCHIVE_PREFIX) + 1 :]
                payload = extracted.read()
                archive_members[relative] = payload
                try:
                    validate_portable_public_bytes(
                        payload,
                        f"Pages evidence archive member {member.name}",
                        relative,
                    )
                except EvidenceError as error:
                    failures.append(str(error))
        if ordered_names != sorted(ordered_names) or len(ordered_names) != len(
            set(ordered_names)
        ):
            failures.append("Pages evidence archive members are not sorted and unique")
        file_records = lock.get("files")
        if not isinstance(file_records, list):
            failures.append("Pages evidence lock files must be a list")
            file_records = []
        expected_archive_files: dict[str, Mapping[str, Any]] = {}
        for record in file_records:
            if not isinstance(record, dict) or not isinstance(record.get("path"), str):
                failures.append("Pages evidence lock has an invalid file record")
                continue
            if record["path"] in expected_archive_files:
                failures.append("Pages evidence lock has duplicate file records")
            expected_archive_files[record["path"]] = record
        expected_archive_names = set(expected_archive_files) | {LOCK_FILENAME}
        if set(archive_members) != expected_archive_names:
            failures.append(
                "Pages evidence archive member set does not exactly match evidence lock files"
            )
        for relative, record in expected_archive_files.items():
            payload = archive_members.get(relative)
            if payload is None:
                continue
            if (
                sha256_bytes(payload) != record.get("sha256")
                or len(payload) != record.get("size")
            ):
                failures.append(
                    f"Pages evidence archive member does not match lock: {relative}"
                )
        lock_bytes = lock_path.read_bytes()
        if archive_members.get(LOCK_FILENAME) != lock_bytes:
            failures.append("Pages evidence lock does not match the bundled lock")
        loose_to_archive = {
            LOCK_FILENAME: LOCK_FILENAME,
            "evidence.json": "evidence.json",
            "evidence.schema.json": "evidence.schema.json",
            "toolchain.json": "toolchain.json",
            "semantic-diff.json": "reports/semantic-diff.json",
            "semantic-diff.md": "reports/semantic-diff.md",
        }
        for loose, bundled in loose_to_archive.items():
            path = destination / loose
            if path.is_symlink() or not path.is_file():
                failures.append(f"Pages conformance file is missing or unsafe: {loose}")
                continue
            if path.read_bytes() != archive_members.get(bundled):
                failures.append(
                    f"Pages conformance file does not match bundled evidence: {loose}"
                )
        index_path = destination / "index.html"
        if index_path.is_symlink() or not index_path.is_file():
            failures.append("Pages conformance file is missing or unsafe: index.html")
        elif index_path.read_bytes() != render_evidence_index(lock):
            failures.append("Pages conformance index does not match the evidence lock")
        allowed_public = set(loose_to_archive) | {
            "index.html",
            ARCHIVE_FILENAME,
            f"{ARCHIVE_FILENAME}.sha256",
        }
        actual_public = {
            path.relative_to(destination).as_posix()
            for path in regular_files(destination, "Pages conformance publication")
        }
        if actual_public != allowed_public:
            failures.append("Pages conformance publication has extra or missing files")
        for package in lock.get("packages", []):
            if not isinstance(package, dict):
                failures.append("Pages evidence lock has an invalid package record")
                continue
            declared = package.get("declaredPath")
            prefix = ".build/pages/"
            if not isinstance(declared, str) or not declared.startswith(prefix):
                failures.append("Pages package declaredPath is not rooted in .build/pages")
                continue
            relative = declared[len(prefix) :]
            try:
                package_path = resolve_path(site, relative, "Pages package")
            except EvidenceError as error:
                failures.append(str(error))
                continue
            if package_path.is_symlink() or not package_path.is_file():
                failures.append(f"Pages package is missing or unsafe: {relative}")
                continue
            if (
                sha256_file(package_path) != package.get("sha256")
                or package_path.stat().st_size != package.get("size")
            ):
                failures.append(f"Pages package bytes do not match the lock: {relative}")
                continue
            try:
                validate_portable_package_bytes(
                    package_path.read_bytes(), f"Pages package {relative}"
                )
            except EvidenceError as error:
                failures.append(str(error))
                continue
            try:
                metadata = read_package_json_files(package_path)["package.json"]
            except ValueError as error:
                failures.append(f"Pages package cannot be inspected: {relative}: {error}")
                continue
            dependencies = {
                item["packageId"]: item["version"]
                for item in package.get("dependencies", [])
                if isinstance(item, dict)
                and isinstance(item.get("packageId"), str)
                and isinstance(item.get("version"), str)
            }
            if (
                metadata.get("name") != package.get("packageId")
                or metadata.get("version") != package.get("version")
                or metadata.get("canonical") != package.get("canonical")
                or metadata.get("fhirVersions") != [package.get("fhirVersion")]
                or metadata.get("dependencies") != dependencies
            ):
                failures.append(f"Pages package identity has drifted: {relative}")
    except (EOFError, EvidenceError, OSError, tarfile.TarError, ValueError) as error:
        failures.append(str(error))
    return failures
