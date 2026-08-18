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
readonly DEFAULT_GUIDES=("archive/v0-healthkit-shaped" "platforms" "ig")

cd "$REPOSITORY_ROOT"
export PATH="$REPOSITORY_ROOT/node_modules/.bin:$PATH"
bundle config set --local path "$REPOSITORY_ROOT/.build/bundle"
bundle config set --local bin "$REPOSITORY_ROOT/.build/bin"
bundle install --jobs 4 --retry 3
bundle binstubs jekyll
export PATH="$REPOSITORY_ROOT/.build/bin:$PATH"
./Scripts/download-fhir-tools.sh "$TOOLS_DIRECTORY"

if [[ "$#" -eq 0 ]]; then
  guides=("${DEFAULT_GUIDES[@]}")
else
  guides=("$@")
fi

install_package() {
  local guide="$1"
  local package_id="$2"
  local package_version="$3"
  local package_archive="$guide/output/package.tgz"
  local package_directory="$HOME/.fhir/packages/${package_id}#${package_version}"

  test -f "$package_archive"
  rm -rf "$package_directory"
  mkdir -p "$package_directory"
  tar -xzf "$package_archive" -C "$package_directory"
}

for guide in "${guides[@]}"; do
  test -f "$guide/sushi-config.yaml"
  echo "Building $guide"
  (cd "$guide" && java -jar "$TOOLS_DIRECTORY/publisher.jar" -ig ig.ini)

  case "$guide" in
    platforms)
      install_package "$guide" "org.grovealliance.fhir.platforms" "0.1.0"
      ;;
    ig)
      install_package "$guide" "org.grovealliance.fhir.core" "0.5.0"
      ;;
  esac
done

python3 Scripts/check-guide-qa.py "${guides[@]}"
