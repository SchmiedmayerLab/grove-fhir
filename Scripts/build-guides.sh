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

cd "$REPOSITORY_ROOT"
export PATH="$REPOSITORY_ROOT/node_modules/.bin:$PATH"
bundle config set --local path "$REPOSITORY_ROOT/.build/bundle"
bundle config set --local bin "$REPOSITORY_ROOT/.build/bin"
bundle install --jobs 4 --retry 3
bundle binstubs jekyll
export PATH="$REPOSITORY_ROOT/.build/bin:$PATH"
./Scripts/download-fhir-tools.sh "$TOOLS_DIRECTORY"

if [[ "$#" -eq 0 ]]; then
  guides=()
  while IFS= read -r guide; do
    guides+=("$guide")
  done < <(python3 -c 'import json; print("\n".join(guide["source"] for guide in json.load(open("publication/config.json", encoding="utf-8"))["guides"]))')
else
  guides=("$@")
fi

clean_generated_guide_content() {
  local guide="$1"
  local directory
  for directory in fsh-generated output temp template translations; do
    local generated="$REPOSITORY_ROOT/$guide/$directory"
    if [[ -d "$generated" ]]; then
      find "$generated" -depth -delete
    fi
  done
}

for guide in "${guides[@]}"; do
  test -f "$guide/sushi-config.yaml"
  echo "Building $guide"
  clean_generated_guide_content "$guide"
  publisher_arguments=(-ig ig.ini)
  if grep -q '^  org\.grovealliance\.fhir\.mobile:' "$guide/sushi-config.yaml"; then
    test -f "$REPOSITORY_ROOT/mobile/output/package.tgz"
    node "$REPOSITORY_ROOT/Scripts/cache-fhir-package.cjs" \
      "$REPOSITORY_ROOT/mobile/output/package.tgz"
    publisher_arguments+=(
      -packages
      "$REPOSITORY_ROOT/mobile/output"
    )
  fi
  (cd "$guide" && java -jar "$TOOLS_DIRECTORY/publisher.jar" "${publisher_arguments[@]}")
done

python3 Scripts/check-guide-qa.py "${guides[@]}"
