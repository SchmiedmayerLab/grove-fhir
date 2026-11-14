#!/usr/bin/env python3
"""Stage all guides with the pinned HL7 Publisher's standard -go-publish process.

All mutations are confined to a fresh workspace under .build. No website, tag,
release, or upstream registry is changed by this command.
"""

# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import gzip
import html
import importlib.util
import json
import os
import re
import shutil
import subprocess
import tarfile
import urllib.request
from datetime import date
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
HISTORY_REVISION = "8a90b35a2d839cc463eaf3d1c04a02ea60abb998"
HISTORY_SHA256 = "4ec7696b16e32334d7b33b2c96132b51da6c4b4f3b4b59eed2d2423e05237146"


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "Scripts" / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PREPARE = load_module("prepare_publication", "prepare-pages.py")
CHECK = load_module("check_publication", "check-publication.py")
PLAN = load_module("publication_plan", "guide-build-plan.py")


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def checked_extract(archive: Path, target: Path, *, strip_root: bool = False) -> None:
    """Only regular files/directories; never allow archives to escape the fresh stage."""
    with tarfile.open(archive, "r:gz") as source:
        for member in source:
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or not (member.isfile() or member.isdir()):
                raise ValueError(f"unsafe publication archive member: {member.name}")
            parts = path.parts[1:] if strip_root else path.parts
            if not parts:
                continue
            destination = target.joinpath(*parts)
            if member.isdir():
                destination.mkdir(parents=True, exist_ok=True)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                stream = source.extractfile(member)
                assert stream is not None
                with destination.open("xb") as output:
                    shutil.copyfileobj(stream, output)


def publication_request(guide: dict, metadata: dict, configuration: dict,
                        release: dict, first: bool) -> dict:
    canonical = CHECK.canonical_for_guide(configuration, guide)
    request = {
        "package-id": metadata["name"], "version": metadata["version"],
        "path": f"{canonical}/{metadata['version']}", "mode": "milestone",
        "status": release["status"], "sequence": release["sequence"],
        "desc": release["description"], "first": first,
    }
    if first:
        request.update({
            "category": "Infrastructure", "title": metadata["title"],
            "introduction": metadata.get("description", metadata["title"]),
            "ci-build": f"{configuration['previewBaseUrl']}/{guide['canonicalPath']}/ci-build",
            "registry-description": metadata.get("description", metadata["title"]),
            "registry-country": "us", "registry-authority": "Schmiedmayer Lab",
        })
    return request


def check_published_guide(web: Path, guide: dict, configuration: dict, version: str) -> Path:
    """Publisher can report an error without a failing exit code: verify its outputs."""
    canonical = CHECK.canonical_for_guide(configuration, guide)
    guide_root = web / CHECK.safe_path(guide["canonicalPath"])
    published = guide_root / version
    for path in (published / "index.html", published / "package.tgz",
                 published / "qa.json", guide_root / "history.html",
                 guide_root / "index.html", guide_root / "package.tgz", guide_root / "qa.json"):
        if not path.is_file():
            raise ValueError(f"Publisher did not produce {path}")
    metadata = CHECK.package_metadata(published / "package.tgz")
    if (metadata.get("version") != version or metadata.get("canonical") != canonical
            or metadata.get("url") != f"{canonical}/{version}"):
        raise ValueError("published package identity does not match the release")
    current = CHECK.package_metadata(guide_root / "package.tgz")
    if any(current.get(key) != metadata.get(key) for key in ("name", "version", "canonical", "url")):
        raise ValueError("current package identity does not match the published version")
    history = json.loads((guide_root / "package-list.json").read_text())
    entries = [row for row in history["list"] if row.get("version") == version]
    if len(entries) != 1 or entries[0].get("path") != f"{canonical}/{version}" or not entries[0].get("current"):
        raise ValueError("Publisher did not register the current version at its permanent URL")
    page = (published / "index.html").read_text()
    if 'id="publish-box"' not in page or "Publication Build: This will be filled" in page:
        raise ValueError("Publisher did not populate the release publish box")
    return published


def sanitize_site(web: Path, source_url: str, public_urls: dict[str, str]) -> None:
    """Remove private build metadata, retaining the Publisher's package bytes."""
    for database in web.rglob("package.db"):
        database.unlink()
    for path in web.rglob("*"):
        if not path.is_file() or path.suffix not in PREPARE.TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        text = PREPARE.replace_build_locations(text, ROOT, public_urls, source_url)
        # Publication runs use nested temporary guide copies, all within this checkout.
        text = text.replace("file://" + source_url, source_url)
        PREPARE.validate_portable_text(text, str(path.relative_to(web)), path.suffix)
        path.write_text(text, encoding="utf-8")


def verify_evidence(evidence: Path) -> None:
    checksums = evidence / "SHA256SUMS"
    if not checksums.is_file() or not checksums.read_text().strip():
        raise ValueError("checksum-bound source-build evidence is required")
    listed = set()
    for line in checksums.read_text().splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9._-]+)", line)
        if not match:
            raise ValueError("invalid evidence checksum entry")
        checksum, name = match.groups()
        if name in listed or name == "SHA256SUMS":
            raise ValueError(f"duplicate or self-referential evidence checksum: {name}")
        listed.add(name)
        asset = evidence / name
        if asset.is_symlink() or not asset.is_file() or CHECK.digest(asset) != checksum:
            raise ValueError(f"source evidence checksum mismatch: {name}")
    if {path.name for path in evidence.iterdir()} != listed | {"SHA256SUMS"}:
        raise ValueError("source evidence contains entries not covered by SHA256SUMS")


def check_previous_publication(previous: dict | None, releases: list[dict]) -> None:
    """Never assemble a replacement website that silently drops published history."""
    published = []
    for release in releases:
        tag = release.get("tag_name", "")
        if release.get("draft") or release.get("prerelease") or not re.fullmatch(r"\d+\.\d+\.\d+", tag):
            continue
        if any(asset["name"] == f"grove-fhir-publication-{tag}.tar.gz" for asset in release.get("assets", [])):
            published.append(tag)
    latest = max(published, key=lambda v: tuple(map(int, v.split('.'))), default=None)
    if (previous or {}).get("tag") != latest:
        raise ValueError(f"previousPublication must pin the latest published website archive: {latest}")


def restore_history(web: Path, previous_web: Path, guides: list[dict]) -> None:
    # Upstream refreshes historical banners. Restore sealed version directories
    # after all publication and sanitation steps to preserve their exact bytes.
    for guide in guides:
        old_root = previous_web / CHECK.safe_path(guide["canonicalPath"])
        if not (old_root / "package-list.json").exists():
            continue
        for entry in json.loads((old_root / "package-list.json").read_text())["list"]:
            old_version = entry.get("version", "")
            if old_version == "current":
                continue
            if not re.fullmatch(r"\d+\.\d+\.\d+", old_version):
                raise ValueError("unsupported historical version path")
            destination = web / CHECK.safe_path(guide["canonicalPath"]) / old_version
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(old_root / old_version, destination)


def check_package_portability(package: Path) -> None:
    with tarfile.open(package, "r:gz") as archive:
        for member in archive:
            if member.isfile() and PurePosixPath(member.name).suffix in PREPARE.TEXT_SUFFIXES:
                content = archive.extractfile(member)
                assert content is not None
                try:
                    text = content.read().decode("utf-8")
                except UnicodeDecodeError:
                    continue
                PREPARE.validate_portable_text(text, f"{package}:{member.name}", PurePosixPath(member.name).suffix)


def archive_site(web: Path, output: Path) -> None:
    """Stable archive metadata; source content remains exactly as validated."""
    with output.open("xb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode="w") as archive:
            for path in sorted(web.rglob("*")):
                if path.is_symlink():
                    raise ValueError(f"publication contains a symlink: {path}")
                if not path.is_file():
                    continue
                info = tarfile.TarInfo(path.relative_to(web).as_posix())
                info.size, info.mode, info.mtime = path.stat().st_size, 0o644, 0
                with path.open("rb") as content:
                    archive.addfile(info, content)


def stage(*, output: Path, evidence: Path, publication_date: str) -> Path:
    date.fromisoformat(publication_date)
    configuration = PREPARE.load_configuration(ROOT / "publication/config.json")
    release = json.loads((ROOT / "publication/release.json").read_text())
    if release["status"] not in {"draft", "release", "trial-use"}:
        raise ValueError("publication status must be draft, release, or trial-use")
    for key in ("sequence", "description"):
        if not isinstance(release[key], str) or not release[key].strip():
            raise ValueError(f"publication {key} is required")
    version = json.loads((ROOT / "catalog/release-manifest.json").read_text())["releaseVersion"]
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("publication requires a stable numeric version")
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip():
        raise ValueError("publication requires a clean source revision")
    subprocess.run([str(ROOT / "Scripts/download-fhir-tools.sh"), "--offline"], cwd=ROOT, check=True)
    workspace = ROOT / ".build" / f"publication-{version}"
    if workspace.exists():
        raise ValueError(f"publication workspace already exists: {workspace}")
    if (not output.resolve().is_relative_to((ROOT / ".build").resolve())
            or output.exists() or output.is_symlink()):
        raise ValueError("output must be a fresh directory under .build")
    verify_evidence(evidence)
    provenance = json.loads((evidence / f"build-provenance-{version}.json").read_text())
    if (provenance.get("sourceRevision") != revision or provenance.get("releaseVersion") != version
            or provenance.get("releaseManifestSha256") != CHECK.digest(ROOT / "catalog/release-manifest.json")):
        raise ValueError("source evidence must match this revision and release manifest")
    archive_path = output / f"grove-fhir-publication-{version}.tar.gz"
    workspace.mkdir(parents=True)
    web = workspace / "web"
    web.mkdir()
    previous = release.get("previousPublication")
    release_pages = json.loads(subprocess.check_output([
        "gh", "api", "--paginate", "--slurp", "repos/SchmiedmayerLab/grove-fhir/releases?per_page=100",
    ], text=True))
    check_previous_publication(previous, [item for page in release_pages for item in page])
    if previous:
        tag, checksum = previous["tag"], previous["sha256"]
        if not re.fullmatch(r"\d+\.\d+\.\d+", tag) or not re.fullmatch(r"[0-9a-f]{64}", checksum):
            raise ValueError("previous publication must pin a release tag and SHA-256")
        if tuple(map(int, tag.split('.'))) >= tuple(map(int, version.split('.'))):
            raise ValueError("previous publication must precede the new version")
        asset = f"grove-fhir-publication-{tag}.tar.gz"
        subprocess.run(["gh", "release", "download", tag, "--repo", "SchmiedmayerLab/grove-fhir",
                        "--pattern", asset, "--dir", str(workspace)], check=True)
        if CHECK.digest(workspace / asset) != checksum:
            raise ValueError("previous publication archive checksum mismatch")
        checked_extract(workspace / asset, web)
        previous_manifest = json.loads((web / "publication-manifest.json").read_text())
        if (previous_manifest.get("releaseVersion") != tag
                or previous_manifest.get("canonicalBaseUrl") != configuration["canonicalBaseUrl"]):
            raise ValueError("previous publication manifest does not match its tag and canonical host")
    previous_web = workspace / "previous"
    shutil.copytree(web, previous_web)
    setup = json.loads((ROOT / "publication/publish-setup.json").read_text())
    if setup["website"]["url"] != configuration["canonicalBaseUrl"]:
        raise ValueError("publication website and canonical base disagree")
    write_json(web / "publish-setup.json", setup)
    registry = workspace / "ig-registry.json"
    write_json(registry, {"guides": []})  # Local only; no upstream registry writes.
    feed_date = date.fromisoformat(publication_date).strftime("%a, %d %b %Y 00:00:00 GMT")
    for name in ("package-feed.xml", "publication-feed.xml"):
        if not (web / name).exists():
            (web / name).write_text(
                '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0" '
                'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:fhir="http://hl7.org/fhir/feed"><channel>'
                '<title>Grove FHIR</title><description>Grove FHIR publications</description>'
                f'<link>{configuration["canonicalBaseUrl"]}</link>'
                f'<lastBuildDate>{feed_date}</lastBuildDate><pubDate>{feed_date}</pubDate></channel></rss>'
            )
    tools = ROOT / ".build/publication-tools"
    tools.mkdir(parents=True, exist_ok=True)
    history_archive = tools / f"history-{HISTORY_REVISION}.tar.gz"
    if not history_archive.exists():
        urllib.request.urlretrieve(
            f"https://api.github.com/repos/HL7/fhir-ig-history-template/tarball/{HISTORY_REVISION}",
            history_archive,
        )
    if CHECK.digest(history_archive) != HISTORY_SHA256:
        raise ValueError("history template checksum mismatch")
    history = workspace / "history"
    checked_extract(history_archive, history, strip_root=True)
    home = ROOT / ".build/fhir-home"
    java = str(ROOT / ".build/jdk21/Contents/Home/bin/java")
    if not Path(java).is_file():
        java = "java"
    publisher = [java, "-Xmx4g", "-Djava.awt.headless=true", f"-Duser.home={home}",
                 "-jar", str(ROOT / ".build/fhir-tools/publisher.jar")]
    env = dict(os.environ, GROVE_FHIR_TOOL_HOME=str(home),
               NODE_OPTIONS=f"--require={ROOT / 'Scripts/sushi-cache-home.cjs'}")
    env["PATH"] = f"{ROOT / 'node_modules/.bin'}:{ROOT / '.build/bin'}:{env['PATH']}"
    subprocess.run([*publisher, "-generate-package-registry", str(web)], env=env, check=True)
    by_source = {g["source"]: g for g in configuration["guides"]}
    packages = {}
    for source_name in [name for wave in PLAN.waves() for name in wave]:
        guide = by_source[source_name]
        source = workspace / "sources" / source_name
        shutil.copytree(ROOT / source_name, source,
                        ignore=shutil.ignore_patterns("temp", "template", "translations"))
        metadata = CHECK.package_metadata(source / "output/package.tgz")
        if metadata["version"] != version:
            raise ValueError(f"{source_name} has not been built at {version}")
        guide_root = web / CHECK.safe_path(guide["canonicalPath"])
        if (guide_root / version).exists():
            raise ValueError(f"publication version already exists: {guide_root / version}")
        request = publication_request(guide, metadata, configuration, release,
                                      not (guide_root / "package-list.json").exists())
        write_json(source / "publication-request.json", request)
        sushi = source / "sushi-config.yaml"
        text = re.sub(r"(?m)^releaseLabel:.*$", f"releaseLabel: {release['status']}", sushi.read_text())
        sushi.write_text(text)
        # -go-publish rebuilds twice and only forwards -tx, not -no-network.
        # This is publication rendering, not the offline structural evidence lane.
        temp = workspace / "temp" / source_name
        temp.mkdir(parents=True)
        subprocess.run([*publisher, "-go-publish", "-source", str(source), "-web", str(web),
                        "-registry", str(registry), "-history", str(history),
                        "-templates", str(ROOT / "publication/templates"),
                        "-temp", str(temp), "-zips", str(workspace / "build-zips"),
                        "-date", publication_date, "-tx", "n/a"], cwd=ROOT, env=env, check=True)
        published = check_published_guide(web, guide, configuration, version)
        check_package_portability(published / "package.tgz")
        # Audit the actual release output, not only the earlier development build.
        qa_root = workspace / "qa" / source_name
        qa_root.mkdir(parents=True)
        shutil.copytree(published, qa_root / "output")
        shutil.copytree(ROOT / source_name / "input", qa_root / "input")
        built_source = temp / "ig-builds" / f"{metadata['name']}#{version}"
        shutil.copytree(built_source / "fsh-generated", qa_root / "fsh-generated")
        shutil.copy2(source / "sushi-config.yaml", qa_root / "sushi-config.yaml")
        subprocess.run(["python3", str(ROOT / "Scripts/check-guide-qa.py"),
                        "--offline-terminology", str(qa_root)], check=True)
        # Published dependencies must be used by subsequent adapter publication builds.
        subprocess.run(["node", str(ROOT / "Scripts/cache-fhir-package.cjs"),
                        "--cache-root", str(home / ".fhir/packages"), str(published / "package.tgz")], check=True)
        packages[metadata["name"]] = {
            "version": version, "path": f"{guide['canonicalPath']}/{version}/package.tgz",
            "sha256": CHECK.digest(published / "package.tgz"),
        }
        # Freeze a version-specific notice before sealing the archive. It never claims
        # that an old version is still current, and requires no historical HTML edits.
        canonical = CHECK.canonical_for_guide(configuration, guide)
        notice = ('<!--ReleaseHeader--><p id="publish-box">'
                  f'Published version {version} ({html.escape(release["status"])}), {publication_date}. '
                  f'<a href="{canonical}/">Current publication</a> · '
                  f'<a href="{canonical}/history.html">Publication history</a>.'
                  '</p><!--EndReleaseHeader-->')
        for page in published.rglob("*.html"):
            text = page.read_text(encoding="utf-8")
            page.write_text(re.sub(r"<!--ReleaseHeader-->.*?<!--EndReleaseHeader-->",
                                  lambda _: notice, text, flags=re.S), encoding="utf-8")
    # Validate producer corpora against the final published packages too.
    package_args = []
    for name in ("mobile", "questionnaire", "sensor", "healthkit"):
        package_args += ["--package", f"{name}={web / by_source[name]['canonicalPath'] / version / 'package.tgz'}"]
    subprocess.run(["python3", "Scripts/validate-fixtures.py", "--validator",
                    ".build/fhir-tools/validator_cli.jar", *package_args], cwd=ROOT, check=True)
    subprocess.run(["python3", "Scripts/validate-producer.py", "--manifest",
                    "Conformance/corpora/mobile-exchange/official-validator-manifest.json",
                    "--validator", ".build/fhir-tools/validator_cli.jar", *package_args[:4],
                    "--allow-example-urls"], cwd=ROOT, check=True)
    subprocess.run(["python3", "Scripts/validate-questionnaire-fhir.py", "--package",
                    str(web / by_source['questionnaire']['canonicalPath'] / version / 'package.tgz')],
                   cwd=ROOT, check=True)
    links = "".join(f'<li><a href="{html.escape(g["canonicalPath"])}/">{html.escape(g["source"])}</a></li>'
                    for g in configuration["guides"])
    (web / "index.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8">'
                                  '<title>Grove FHIR</title><body><h1>Grove FHIR guides</h1>'
                                  f'<ul>{links}</ul></body></html>')
    shutil.copytree(ROOT / "catalog", web / "catalog", dirs_exist_ok=True)
    (web / ".nojekyll").touch()
    public_urls = {}
    for guide in configuration["guides"]:
        name = guide["source"]
        public_url = f"{CHECK.canonical_for_guide(configuration, guide)}/{version}"
        package_id = CHECK.package_metadata(ROOT / name / "output/package.tgz")["name"]
        for source in (ROOT / name, workspace / "sources" / name,
                       workspace / "temp" / name / "ig-builds" / f"{package_id}#{version}"):
            public_urls[source.relative_to(ROOT).as_posix()] = public_url
    sanitize_site(web, f"{configuration['sourceRepository']}/tree/{revision}", public_urls)
    restore_history(web, previous_web, configuration["guides"])
    write_json(web / "publication-manifest.json", {
        "schemaVersion": 1, "releaseVersion": version, "sourceRevision": revision,
        "canonicalBaseUrl": configuration["canonicalBaseUrl"], "publicationDate": publication_date,
        "status": release["status"], "previousPublication": previous,
        "publisherVersion": json.loads((ROOT / "catalog/release-manifest.json").read_text())["toolchain"]["igPublisher"]["version"], "historyTemplateRevision": HISTORY_REVISION,
        "packages": packages,
        "terminologyValidation": "offline-structural; no online terminology attestation",
    })
    output.mkdir(parents=True)
    # Offload only the new version and current copy. Sealed historical versions
    # remain byte-for-byte intact, including their original download locations.
    release_url = f"{configuration['sourceRepository']}/releases/download/{version}"
    for guide in configuration["guides"]:
        guide_root = web / guide["canonicalPath"]
        canonical = CHECK.canonical_for_guide(configuration, guide)
        PREPARE.offload_downloads(
            guide_root / version, output, public_url=f"{canonical}/{version}",
            asset_prefix=f"grove-{guide['source']}-{version}-", release_url=release_url)
        # The native current build can have different bundle bytes from the
        # versioned build, so preserve both under distinct release asset names.
        PREPARE.offload_downloads(
            guide_root, output, public_url=canonical,
            asset_prefix=f"grove-{guide['source']}-{version}-current-", release_url=release_url,
            excluded_directories={p.name for p in guide_root.iterdir()
                                  if p.is_dir() and re.fullmatch(r"\d+\.\d+\.\d+", p.name)})
    # Keep source-build evidence separate: -go-publish has rebuilt the packages,
    # and the primary release assets must be the bytes served by the website.
    archive_site(evidence, output / f"grove-fhir-source-evidence-{version}.tar.gz")
    for name in (f"grove-fhir-machine-contracts-{version}.tar.gz", f"machine-contract-index-{version}.json",
                 f"release-manifest-{version}.json"):
        shutil.copy2(evidence / name, output / name)
    subprocess.run(["python3", "Scripts/fhir_package_semantic_snapshot.py",
                    str(web / by_source['mobile']['canonicalPath'] / version / 'package.tgz'),
                    "--output", str(output / f"mobile-semantic-snapshot-{version}.json")],
                   cwd=ROOT, check=True)
    for package_id, details in packages.items():
        published = web / details["path"]
        shutil.copy2(published, output / f"{package_id}-{version}.tgz")
        for suffix in ("json", "html"):
            shutil.copy2(published.parent / f"qa.{suffix}", output / f"{package_id}-{version}-qa.{suffix}")
    shutil.copy2(web / "publication-manifest.json", output / f"publication-manifest-{version}.json")
    archive_site(web, archive_path)
    with (output / "SHA256SUMS").open("x") as checksums:
        for asset in sorted(output.iterdir()):
            if asset.name != "SHA256SUMS":
                checksums.write(f"{CHECK.digest(asset)}  {asset.name}\n")
    return archive_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--date", required=True, help="Publication date (YYYY-MM-DD)")
    args = parser.parse_args()
    print(stage(output=args.output, evidence=args.evidence, publication_date=args.date))


if __name__ == "__main__":
    main()
