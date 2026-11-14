#!/usr/bin/env python3
"""Refresh build dependencies from stable upstream releases; leave all changes for review."""

# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
# SPDX-License-Identifier: MIT

from __future__ import annotations

import hashlib
import io
import tarfile
import json
import re
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def github(path: str) -> dict:
    return json.loads(subprocess.check_output(["gh", "api", path], cwd=ROOT, text=True))


def latest_binary(repository: str, name: str) -> dict:
    release = github(f"repos/{repository}/releases/latest")
    version = release["tag_name"].removeprefix("v")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError(f"not a stable release: {repository} {version}")
    asset = next(item for item in release["assets"] if item["name"] == name)
    digest = asset.get("digest") or ""
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise ValueError(f"GitHub has no SHA-256 for {repository} {name}")
    return {"version": version, "sha256": digest.removeprefix("sha256:")}


def checked_release(previous: dict, candidate: dict, label: str) -> dict:
    """An update may select a new release, never re-bless changed bytes of an old one."""
    if not re.fullmatch(r"\d+\.\d+\.\d+", candidate["version"]):
        raise ValueError(f"not a stable release: {label} {candidate['version']}")
    if previous["version"] == candidate["version"] and previous["sha256"] != candidate["sha256"]:
        raise ValueError(f"released asset changed upstream: {label}#{candidate['version']}")
    return candidate


def replace_constant(text: str, name: str, value: str, *, shell: bool = False) -> str:
    prefix = "readonly " if shell else ""
    assignment = f'{prefix}{name}="{value}"' if shell else f'{name} = "{value}"'
    result, count = re.subn(rf'(?m)^{prefix}{name}\s*=.*$', lambda _: assignment, text)
    if count != 1:
        raise ValueError(f"expected one {name} declaration")
    return result


def refresh_guide_dependencies(manifest: dict) -> None:
    versions = {}
    for guide in manifest["guides"]:
        configuration = ROOT / guide["source"] / "sushi-config.yaml"
        text = configuration.read_text()
        updated = []
        for dependency in guide["directDependencies"]:
            package, previous = dependency.split("#", 1)
            if package.startswith("org.grovealliance."):
                updated.append(dependency)
                continue
            if package not in versions:
                with urllib.request.urlopen(f"https://packages.fhir.org/{package}", timeout=60) as response:
                    versions[package] = json.load(response)["dist-tags"]["latest"]
                if not re.fullmatch(r"\d+\.\d+\.\d+", versions[package]):
                    raise ValueError(f"no stable latest release for {package}")
            version = versions[package]
            text, count = re.subn(r"(?m)^  " + re.escape(package) + r": [^\s]+$", f"  {package}: {version}", text)
            if count != 1:
                raise ValueError(f"expected one declared dependency: {configuration} {package}")
            updated.append(f"{package}#{version}")
            if package == "hl7.fhir.uv.extensions.r4" and previous != version:
                for source in (configuration.parent / "input/fsh").glob("*.fsh"):
                    source.write_text(re.sub(
                        r"(?m)^(Alias: [^\n]+ = http://hl7\.org/fhir/StructureDefinition/[^|\s]+\|)" + re.escape(previous) + r"$",
                        lambda match: match[1] + version, source.read_text()))
                expectations = configuration.parent / "fixtures/validator/validator-expectations.json"
                if expectations.is_file():
                    text_expectations = expectations.read_text()
                    text_expectations = text_expectations.replace(f"|{previous})", f"|{version})")
                    text_expectations = text_expectations.replace(f" v{previous} is not allowed", f" v{version} is not allowed")
                    expectations.write_text(text_expectations)
        guide["directDependencies"] = updated
        configuration.write_text(text)
    graph_path = ROOT / "catalog/package-graph.json"
    graph = json.loads(graph_path.read_text())
    by_source = {guide["source"]: guide["directDependencies"] for guide in manifest["guides"]}
    for package in graph["packages"]:
        package["dependencies"] = by_source[package["source"]]
    graph_path.write_text(json.dumps(graph, indent=2) + "\n")


def refresh_package_closure(text: str, manifest: dict) -> str:
    """Refresh implicit tool packages and include the declared transitive closure."""
    archives = {(package, version): checksum for package, version, checksum in re.findall(
        r'"([a-z0-9.-]+)\|([^|"\n]+)\|([0-9a-f]{64})"', text)}
    roots = set()
    for package in ("hl7.fhir.pubpack", "hl7.fhir.uv.tools.r4", "hl7.terminology", "hl7.fhir.uv.extensions"):
        with urllib.request.urlopen(f"https://packages.fhir.org/{package}") as response:
            roots.add((package, json.load(response)["dist-tags"]["latest"]))
    for guide in manifest["guides"]:
        for dependency in guide["directDependencies"]:
            package, version = dependency.split("#", 1)
            if not package.startswith("org.grovealliance."):
                roots.add((package, version))
    visited = set()
    while roots:
        package, version = roots.pop()
        if (package, version) in visited:
            continue
        visited.add((package, version))
        cached = ROOT / ".build/fhir-tools" / f"{package}-{version}.tgz"
        expected = archives.get((package, version))
        if expected and cached.is_file() and hashlib.sha256(cached.read_bytes()).hexdigest() == expected:
            payload = cached.read_bytes()
        else:
            print(f"Resolving {package}#{version}", flush=True)
            with urllib.request.urlopen(f"https://packages.fhir.org/{package}/{version}", timeout=60) as response:
                payload = response.read()
        checksum = hashlib.sha256(payload).hexdigest()
        if expected and checksum != expected:
            raise ValueError(f"released package changed upstream: {package}#{version}")
        archives[package, version] = checksum
        cached.parent.mkdir(parents=True, exist_ok=True)
        cached.write_bytes(payload)
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
            stream = archive.extractfile("package/package.json")
            if stream is None:
                raise ValueError(f"missing package metadata: {package}#{version}")
            metadata = json.load(stream)
        if metadata["name"] != package or metadata["version"] != version:
            raise ValueError(f"package identity mismatch: {package}#{version}")
        roots.update(metadata.get("dependencies", {}).items())
    declaration = "readonly FHIR_PACKAGE_ARCHIVES=(\n" + "".join(
        f'  "{package}|{version}|{checksum}"\n' for (package, version), checksum in sorted(archives.items())) + ")"
    updated, count = re.subn(r"readonly FHIR_PACKAGE_ARCHIVES=\(.*?\n\)", lambda _: declaration, text, flags=re.S)
    if count != 1:
        raise ValueError("expected one FHIR package closure declaration")
    return updated


def main() -> None:
    manifest_path = ROOT / "catalog/release-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    toolchain = manifest["toolchain"]
    toolchain["igPublisher"] = checked_release(toolchain["igPublisher"],
        latest_binary("HL7/fhir-ig-publisher", "publisher.jar"), "Publisher")
    toolchain["fhirValidator"] = checked_release(toolchain["fhirValidator"],
        latest_binary("hapifhir/org.hl7.fhir.core", "validator_cli.jar"), "Validator")
    template = dict(toolchain["template"])
    with urllib.request.urlopen(f"https://packages.fhir.org/{template['packageId']}") as response:
        template["version"] = json.load(response)["dist-tags"]["latest"]
    with urllib.request.urlopen(f"https://packages.fhir.org/{template['packageId']}/{template['version']}") as response:
        template["sha256"] = hashlib.sha256(response.read()).hexdigest()
    toolchain["template"] = checked_release(toolchain["template"], template, template["packageId"])
    history_revision = github("repos/HL7/fhir-ig-history-template/commits/HEAD")["sha"]
    with urllib.request.urlopen(f"https://api.github.com/repos/HL7/fhir-ig-history-template/tarball/{history_revision}") as response:
        history_sha = hashlib.sha256(response.read()).hexdigest()
    staging = ROOT / "Scripts/stage-publication.py"
    staging_text = staging.read_text()
    if (f'HISTORY_REVISION = "{history_revision}"' in staging_text
            and f'HISTORY_SHA256 = "{history_sha}"' not in staging_text):
        raise ValueError("history template changed upstream at its pinned revision")

    package = json.loads((ROOT / "package.json").read_text())
    subprocess.run(["npm", "install", "--save-dev", "--save-exact=false",
                    *(f"{name}@latest" for name in package["devDependencies"])], cwd=ROOT, check=True)
    subprocess.run(["bundle", "update", "--all"], cwd=ROOT, check=True)
    lock = json.loads((ROOT / "package-lock.json").read_text())
    toolchain["sushi"]["version"] = lock["packages"]["node_modules/fsh-sushi"]["version"]

    refresh_guide_dependencies(manifest)
    download = ROOT / "Scripts/download-fhir-tools.sh"
    text = download.read_text()
    text = replace_constant(text, "TEMPLATE_ID", template["packageId"], shell=True)
    for prefix, tool in (("PUBLISHER", toolchain["igPublisher"]), ("VALIDATOR", toolchain["fhirValidator"]),
                         ("TEMPLATE", template)):
        for field in ("version", "sha256"):
            text = replace_constant(text, f"{prefix}_{field.upper()}", tool[field], shell=True)
    download.write_text(refresh_package_closure(text, manifest))
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    for guide in manifest["guides"]:
        ini = ROOT / guide["source"] / "ig.ini"
        text, count = re.subn(r"(?m)^template\s*=.*$", f"template = {template['packageId']}#{template['version']}", ini.read_text())
        if count != 1:
            raise ValueError(f"expected one template declaration: {ini}")
        ini.write_text(text)
    text = replace_constant(staging_text, "HISTORY_REVISION", history_revision)
    staging.write_text(replace_constant(text, "HISTORY_SHA256", history_sha))
    print("Dependencies refreshed locally. Review the diff, run npm test, and build the guides before publishing.")


if __name__ == "__main__":
    main()
