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

while IFS= read -r guide; do
  test -f "$REPOSITORY_ROOT/$guide/output/index.html"
done < <(python3 -c 'import json, sys; print("\n".join(guide["source"] for guide in json.load(open(sys.argv[1], encoding="utf-8"))["guides"]))' "$REPOSITORY_ROOT/publication/config.json")

if [[ -n "${PUBLISHED_SITE_ROOT:-}" ]]; then
  python3 "$REPOSITORY_ROOT/Scripts/prepare-pages.py" \
    --site "$SITE_DIRECTORY" \
    --repository-root "$REPOSITORY_ROOT" \
    --config "$REPOSITORY_ROOT/publication/config.json" \
    --base-url "${PAGES_BASE_URL:-https://schmiedmayerlab.github.io/grove-fhir}" \
    --published-root "$PUBLISHED_SITE_ROOT"
else
  python3 "$REPOSITORY_ROOT/Scripts/prepare-pages.py" \
    --site "$SITE_DIRECTORY" \
    --repository-root "$REPOSITORY_ROOT" \
    --config "$REPOSITORY_ROOT/publication/config.json" \
    --base-url "${PAGES_BASE_URL:-https://schmiedmayerlab.github.io/grove-fhir}"
fi

python3 "$REPOSITORY_ROOT/Scripts/check-publication.py" \
  --site "$SITE_DIRECTORY" \
  --repository-root "$REPOSITORY_ROOT" \
  --config "$REPOSITORY_ROOT/publication/config.json" \
  --base-url "${PAGES_BASE_URL:-https://schmiedmayerlab.github.io/grove-fhir}"
