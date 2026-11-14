"""The fallback registry must preserve pinned bytes and offline behavior."""

# This source file is part of the Grove FHIR open-source project
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
# SPDX-License-Identifier: MIT

import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).parents[1]


class DownloadFHIRToolsTests(unittest.TestCase):
    def test_registry_fallback_keeps_checksum_and_offline_guards(self):
        source = (ROOT / "Scripts/download-fhir-tools.sh").read_text()
        start = source.index("download_and_verify() {")
        function = source[start:source.index("\n}\n", start) + 3]
        checksum = hashlib.sha256(b"pinned package").hexdigest()
        for mode in ("fallback", "changed", "offline", "cached", "github"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                destination = root / "package.tgz"
                if mode == "cached":
                    destination.write_bytes(b"pinned package")
                script = r'''
set -euo pipefail
cd "$1"
mode="$2"
OFFLINE=false
[[ "$mode" != offline ]] || OFFLINE=true
curl() {
  local url="${!#}" output
  printf '%s\n' "$url" >> calls
  while [[ $# -gt 0 ]]; do
    if [[ "$1" == --output ]]; then output="$2"; shift; fi
    shift
  done
  [[ "$url" == https://packages2.fhir.org/* ]] || return 6
  if [[ "$mode" == changed ]]; then
    printf '%s' 'changed package' > "$output"
  else
    printf '%s' 'pinned package' > "$output"
  fi
}
'''
                url = ("https://github.com/example/tool.jar" if mode == "github"
                       else "https://packages.fhir.org/example/1.0.0")
                script += function + f'\ndownload_and_verify "{url}" package.tgz "{checksum}"\n'
                result = subprocess.run(["bash", "-c", script, "test", directory, mode],
                                        capture_output=True, text=True)
                calls = (root / "calls").read_text().splitlines() if (root / "calls").exists() else []
                if mode in {"cached", "fallback"}:
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(destination.read_bytes(), b"pinned package")
                else:
                    self.assertNotEqual(result.returncode, 0)
                    self.assertFalse(destination.exists())
                if mode in {"offline", "cached"}:
                    self.assertEqual(calls, [])
                elif mode == "github":
                    self.assertEqual(calls, [url])
                else:
                    self.assertEqual(calls, [url, "https://packages2.fhir.org/packages/example/1.0.0"])
