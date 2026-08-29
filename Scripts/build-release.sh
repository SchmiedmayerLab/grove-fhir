#!/usr/bin/env bash
#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly REPOSITORY_ROOT

if [[ "$#" -ne 0 && "$#" -ne 2 ]]; then
  echo "Usage: $0 [--output <directory-under-.build>]" >&2
  exit 2
fi
if [[ "$#" -eq 2 && "$1" != "--output" ]]; then
  echo "Usage: $0 [--output <directory-under-.build>]" >&2
  exit 2
fi

cd "$REPOSITORY_ROOT"
if [[ -n "$(git status --porcelain=v1 --untracked-files=all)" ]]; then
  echo "Release candidates must be built from a clean source tree." >&2
  exit 1
fi
version="$(python3 -c 'import json; print(json.load(open("catalog/release-manifest.json"))["releaseVersion"])')"
readonly version
output="${2:-$REPOSITORY_ROOT/.build/release-candidate-$version}"
readonly output
source_revision="$(git rev-parse HEAD)"
readonly source_revision

case "$(python3 -c 'from pathlib import Path; import sys; root=Path(".build").resolve(); target=Path(sys.argv[1]).resolve(); print(target.is_relative_to(root) and target != root)' "$output")" in
  True) ;;
  *) echo "Release output must be a dedicated directory under .build: $output" >&2; exit 2 ;;
esac

# Phase 1 is the only network-enabled phase. npm and Bundler are integrity/checksum locked, while
# download-fhir-tools.sh verifies explicit SHA-256 pins for Publisher, Validator, the template,
# and every external FHIR package before admitting them to the bootstrap cache.
echo "Bootstrapping the checksum-pinned release dependency closure (network enabled)"
npm ci
export BUNDLE_FROZEN=true
bundle config set --local path "$REPOSITORY_ROOT/.build/bundle"
bundle config set --local bin "$REPOSITORY_ROOT/.build/bin"
bundle install --jobs 4 --retry 3
./Scripts/download-fhir-tools.sh "$REPOSITORY_ROOT/.build/fhir-tools"

# Phase 2 consumes only that bootstrap. npm must reconstruct node_modules from its local cache;
# Bundler and every FHIR archive are rechecked locally by build-guides.sh; Publisher itself gets
# both -tx n/a and -no-network. No online terminology claim can be produced by this lane.
echo "Replaying the verified dependency closure in the offline structural/package lane"
npm ci --offline
export npm_config_offline=true
export GROVE_TX_OFFLINE=1
bundle check
./Scripts/download-fhir-tools.sh --offline "$REPOSITORY_ROOT/.build/fhir-tools"
npm run inventory:check
npm run pages:build
npm test
python3 Scripts/validate-questionnaire-fhir.py
python3 Scripts/validate-producer.py \
  --manifest Conformance/corpora/mobile-exchange/official-validator-manifest.json \
  --validator .build/fhir-tools/validator_cli.jar \
  --package mobile=mobile/output/package.tgz \
  --package questionnaire=questionnaire/output/package.tgz \
  --allow-example-urls
python3 Scripts/check-publication.py \
  --site .build/pages \
  --repository-root . \
  --config publication/config.json \
  --base-url https://schmiedmayerlab.github.io/grove-fhir
python3 Scripts/collect-release-evidence.py \
  --output "$output" \
  --source-revision "$source_revision" \
  --lane offline-structural
(cd "$output" && shasum -a 256 --check SHA256SUMS)

echo "Release-candidate evidence collected at $output"
echo "No canonical publication was performed."
