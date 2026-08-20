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
readonly TOOLS_DIRECTORY="$REPOSITORY_ROOT/.build/fhir-tools"

if [[ "$#" -ne 1 || ("$1" != "mobile" && "$1" != "healthkit" && "$1" != "health-connect" && "$1" != "questionnaire") ]]; then
  echo "Usage: $0 <mobile|healthkit|health-connect|questionnaire>" >&2
  exit 2
fi

readonly GUIDE="$1"
readonly REQUEST="$REPOSITORY_ROOT/$GUIDE/publication-request.json"
if [[ ! -f "$REQUEST" ]]; then
  echo "$GUIDE has no reviewed publication-request.json" >&2
  exit 1
fi

cd "$REPOSITORY_ROOT"
if [[ "$GUIDE" == "mobile" ]]; then
  ./Scripts/build-guides.sh mobile
elif grep -q '^  org\.grovealliance\.fhir\.mobile:' "$GUIDE/sushi-config.yaml"; then
  ./Scripts/build-guides.sh mobile "$GUIDE"
else
  ./Scripts/build-guides.sh "$GUIDE"
fi

publication_path="$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["path"])' "$REQUEST")"
readonly publication_path
if [[ "$publication_path" != https://schmiedmayerlab.github.io/grove-fhir/fhir/* ]]; then
  echo "publication request path is outside the configured draft canonical host" >&2
  exit 1
fi

export PATH="$REPOSITORY_ROOT/node_modules/.bin:$REPOSITORY_ROOT/.build/bin:$PATH"
echo "Building publication-mode output for $GUIDE at $publication_path"
(cd "$GUIDE" && java -jar "$TOOLS_DIRECTORY/publisher.jar" \
  -ig ig.ini \
  -publish "$publication_path")

python3 Scripts/check-guide-qa.py "$GUIDE"
