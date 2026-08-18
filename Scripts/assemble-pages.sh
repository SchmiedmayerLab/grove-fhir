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
readonly SITE_DIRECTORY="$REPOSITORY_ROOT/.build/pages"

for guide in \
  "$REPOSITORY_ROOT/ig/output" \
  "$REPOSITORY_ROOT/platforms/output" \
  "$REPOSITORY_ROOT/archive/v0-healthkit-shaped/output"; do
  test -f "$guide/index.html"
done

rm -rf "$SITE_DIRECTORY"
mkdir -p \
  "$SITE_DIRECTORY/platforms" \
  "$SITE_DIRECTORY/archive/v0-healthkit-shaped"

cp -R "$REPOSITORY_ROOT/ig/output/." "$SITE_DIRECTORY/"
cp -R "$REPOSITORY_ROOT/platforms/output/." "$SITE_DIRECTORY/platforms/"
cp -R \
  "$REPOSITORY_ROOT/archive/v0-healthkit-shaped/output/." \
  "$SITE_DIRECTORY/archive/v0-healthkit-shaped/"

# GitHub Pages should serve Publisher output verbatim, including underscore-prefixed assets.
touch "$SITE_DIRECTORY/.nojekyll"

python3 "$REPOSITORY_ROOT/Scripts/prepare-pages.py" \
  --site "$SITE_DIRECTORY" \
  --repository-root "$REPOSITORY_ROOT" \
  --base-url "${PAGES_BASE_URL:-https://schmiedmayerlab.github.io/grove-fhir}"

echo "Assembled GitHub Pages site at $SITE_DIRECTORY"
