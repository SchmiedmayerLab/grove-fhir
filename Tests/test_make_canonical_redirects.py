#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#

from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "make-canonical-redirects.py"
SPEC = importlib.util.spec_from_file_location("make_canonical_redirects", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
ROUTES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ROUTES)


class CanonicalRedirectTests(unittest.TestCase):
    canonical = "https://pages.example/repository/fhir/mobile"

    def add_resource(
        self,
        output: Path,
        site: Path,
        *,
        resource_type: str,
        resource_id: str,
        url: str,
        target_prefix: str = "ci-build",
        copy_human: bool = True,
        machine_formats: tuple[str, ...] = ("json", "xml", "ttl"),
    ) -> None:
        stem = f"{resource_type}-{resource_id}"
        resource = {
            "resourceType": resource_type,
            "id": resource_id,
            "url": url,
        }
        if "json" in machine_formats:
            (output / f"{stem}.json").write_text(
                json.dumps(resource, sort_keys=True), encoding="utf-8"
            )
        if "xml" in machine_formats:
            (output / f"{stem}.xml").write_text(f"<{resource_type}/>", encoding="utf-8")
        if "ttl" in machine_formats:
            (output / f"{stem}.ttl").write_text(
                f"@prefix fhir: <http://hl7.org/fhir/> . # {resource_id}\n",
                encoding="utf-8",
            )
        (output / f"{stem}.html").write_text(f"<h1>{resource_id}</h1>", encoding="utf-8")
        if copy_human:
            destination = site / target_prefix / f"{stem}.html"
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(f"<h1>{resource_id}</h1>", encoding="utf-8")

    def test_generates_standard_and_nested_routes_with_sibling_formats(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "output"
            site = root / "site"
            output.mkdir()
            site.mkdir()
            self.add_resource(
                output,
                site,
                resource_type="StructureDefinition",
                resource_id="standard",
                url=f"{self.canonical}/StructureDefinition/standard",
            )
            self.add_resource(
                output,
                site,
                resource_type="StructureDefinition",
                resource_id="special",
                url=f"{self.canonical}/StructureDefinition/parent/child",
            )
            self.add_resource(
                output,
                site,
                resource_type="CodeSystem",
                resource_id="external",
                url="https://vendor.example/CodeSystem/external",
            )
            self.add_resource(
                output,
                site,
                resource_type="CodeSystem",
                resource_id="prefix-trap",
                url=f"{self.canonical}-other/CodeSystem/prefix-trap",
            )

            rows = ROUTES.generate_routes(output, site, self.canonical, "ci-build")

            self.assertEqual(
                [row["canonical"] for row in rows],
                [
                    f"{self.canonical}/StructureDefinition/parent/child",
                    f"{self.canonical}/StructureDefinition/standard",
                ],
            )
            for suffix in ("json", "xml", "ttl"):
                self.assertTrue((site / f"StructureDefinition/standard.{suffix}").is_file())
                self.assertTrue(
                    (site / f"StructureDefinition/parent/child.{suffix}").is_file()
                )
            self.assertFalse(
                (site / "StructureDefinition/standard/standard.json").exists(),
                "canonical + .json must be the sibling standard.json",
            )
            self.assertTrue(
                (site / "StructureDefinition/standard/index.html").is_file()
            )
            self.assertTrue((site / "StructureDefinition/standard.html").is_file())
            self.assertTrue(
                (site / "StructureDefinition/parent/child/index.html").is_file()
            )
            self.assertTrue((site / "StructureDefinition/parent/child.html").is_file())
            directory_redirect = (
                site / "StructureDefinition/parent/child/index.html"
            ).read_text(encoding="utf-8")
            html_redirect = (site / "StructureDefinition/parent/child.html").read_text(
                encoding="utf-8"
            )
            self.assertIn("../../../ci-build/StructureDefinition-special.html", directory_redirect)
            self.assertIn("../../ci-build/StructureDefinition-special.html", html_redirect)
            self.assertIn("../child.json", directory_redirect)
            self.assertIn('rel="canonical"', directory_redirect)

            manifest = json.loads(
                (site / ROUTES.MANIFEST_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["schemaVersion"], 1)
            self.assertEqual(manifest["canonical"], self.canonical)
            self.assertEqual(manifest["routes"], rows)
            self.assertNotIn("external", json.dumps(manifest))
            self.assertNotIn("prefix-trap", json.dumps(manifest))

    def test_generation_is_deterministic_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "output"
            site = root / "site"
            output.mkdir()
            site.mkdir()
            self.add_resource(
                output,
                site,
                resource_type="Questionnaire",
                resource_id="example",
                url=f"{self.canonical}/Questionnaire/example",
            )

            first = ROUTES.generate_routes(output, site, f"{self.canonical}/", "ci-build")
            first_manifest = (site / ROUTES.MANIFEST_NAME).read_bytes()
            first_redirect = (site / "Questionnaire/example/index.html").read_bytes()
            second = ROUTES.generate_routes(output, site, self.canonical, "ci-build")

            self.assertEqual(first, second)
            self.assertEqual(first_manifest, (site / ROUTES.MANIFEST_NAME).read_bytes())
            self.assertEqual(
                first_redirect, (site / "Questionnaire/example/index.html").read_bytes()
            )

    def test_ignores_bom_prefixed_non_fhir_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "output"
            site = root / "site"
            output.mkdir()
            site.mkdir()
            self.add_resource(
                output,
                site,
                resource_type="StructureDefinition",
                resource_id="example",
                url=f"{self.canonical}/StructureDefinition/example",
            )
            (output / "receiver.openapi.json").write_bytes(
                b"\xef\xbb\xbf" + json.dumps({"openapi": "3.0.0"}).encode("utf-8")
            )

            rows = ROUTES.generate_routes(output, site, self.canonical, "ci-build")

            self.assertEqual(
                [row["canonical"] for row in rows],
                [f"{self.canonical}/StructureDefinition/example"],
            )

    def test_uses_guide_landing_for_a_resource_without_a_dedicated_page(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "output"
            site = root / "site"
            output.mkdir()
            site.mkdir()
            self.add_resource(
                output,
                site,
                resource_type="ImplementationGuide",
                resource_id="example",
                url=f"{self.canonical}/ImplementationGuide/example",
            )
            (output / "ImplementationGuide-example.html").unlink()
            (site / "ci-build/ImplementationGuide-example.html").unlink()
            (output / "index.html").write_text("guide landing", encoding="utf-8")
            (site / "ci-build/index.html").write_text("guide landing", encoding="utf-8")

            rows = ROUTES.generate_routes(output, site, self.canonical, "ci-build")

            self.assertEqual(rows[0]["human"], "ci-build/index.html")
            redirect = (site / "ImplementationGuide/example/index.html").read_text(
                encoding="utf-8"
            )
            self.assertIn("../../ci-build/index.html", redirect)

    def test_rejects_traversal_and_ambiguous_paths_before_writing(self) -> None:
        unsafe_urls = (
            f"{self.canonical}/StructureDefinition/../escape",
            f"{self.canonical}/StructureDefinition/%2e%2e/escape",
            f"{self.canonical}/StructureDefinition/back\\slash",
            f"{self.canonical}/StructureDefinition//ambiguous",
        )
        for index, url in enumerate(unsafe_urls):
            with self.subTest(url=url), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                output = root / "output"
                site = root / "site"
                output.mkdir()
                site.mkdir()
                self.add_resource(
                    output,
                    site,
                    resource_type="StructureDefinition",
                    resource_id=f"unsafe-{index}",
                    url=url,
                )

                with self.assertRaises(ROUTES.UnsafeRouteError):
                    ROUTES.generate_routes(output, site, self.canonical, "ci-build")

                self.assertFalse((site / ROUTES.MANIFEST_NAME).exists())

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "output"
            site = root / "site"
            output.mkdir()
            site.mkdir()
            with self.assertRaises(ROUTES.UnsafeRouteError):
                ROUTES.generate_routes(output, site, self.canonical, "../ci-build")

    def test_rejects_duplicate_and_file_directory_collisions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "output"
            site = root / "site"
            output.mkdir()
            site.mkdir()
            self.add_resource(
                output,
                site,
                resource_type="StructureDefinition",
                resource_id="first",
                url=f"{self.canonical}/StructureDefinition/shared",
            )
            self.add_resource(
                output,
                site,
                resource_type="StructureDefinition",
                resource_id="second",
                url=f"{self.canonical}/StructureDefinition/shared",
            )
            with self.assertRaises(ROUTES.RouteCollisionError):
                ROUTES.generate_routes(output, site, self.canonical, "ci-build")
            self.assertFalse((site / ROUTES.MANIFEST_NAME).exists())

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "output"
            site = root / "site"
            output.mkdir()
            site.mkdir()
            self.add_resource(
                output,
                site,
                resource_type="CodeSystem",
                resource_id="short",
                url=f"{self.canonical}/CodeSystem/value",
            )
            self.add_resource(
                output,
                site,
                resource_type="CodeSystem",
                resource_id="nested",
                url=f"{self.canonical}/CodeSystem/value.html/nested",
            )
            with self.assertRaises(ROUTES.RouteCollisionError):
                ROUTES.generate_routes(output, site, self.canonical, "ci-build")
            self.assertFalse((site / ROUTES.MANIFEST_NAME).exists())

    def test_rejects_missing_or_conflicting_representations(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "output"
            site = root / "site"
            output.mkdir()
            site.mkdir()
            self.add_resource(
                output,
                site,
                resource_type="ValueSet",
                resource_id="missing-ttl",
                url=f"{self.canonical}/ValueSet/missing-ttl",
                machine_formats=("json", "xml"),
            )
            with self.assertRaises(ROUTES.MissingRepresentationError):
                ROUTES.generate_routes(output, site, self.canonical, "ci-build")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "output"
            site = root / "site"
            output.mkdir()
            site.mkdir()
            self.add_resource(
                output,
                site,
                resource_type="ValueSet",
                resource_id="existing",
                url=f"{self.canonical}/ValueSet/existing",
            )
            conflict = site / "ValueSet/existing.json"
            conflict.parent.mkdir(parents=True)
            conflict.write_text("not the generated resource", encoding="utf-8")
            with self.assertRaises(ROUTES.RouteCollisionError):
                ROUTES.generate_routes(output, site, self.canonical, "ci-build")

    def test_cli_writes_manifest_and_reports_route_count(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "output"
            site = root / "site"
            output.mkdir()
            site.mkdir()
            self.add_resource(
                output,
                site,
                resource_type="CapabilityStatement",
                resource_id="client",
                url=f"{self.canonical}/CapabilityStatement/client",
            )

            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    str(output),
                    str(site),
                    "--canonical",
                    self.canonical,
                    "--target-prefix",
                    "ci-build",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("generated 1 canonical routes", result.stdout)
            self.assertTrue((site / ROUTES.MANIFEST_NAME).is_file())


if __name__ == "__main__":
    unittest.main()
