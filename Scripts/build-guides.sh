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
readonly FHIR_TOOL_HOME="$REPOSITORY_ROOT/.build/fhir-home"
readonly FHIR_PACKAGE_CACHE="$FHIR_TOOL_HOME/.fhir/packages"
JAVA_COMMAND="java"
if [[ -x "$REPOSITORY_ROOT/.build/jdk21/Contents/Home/bin/java" ]]; then
  JAVA_COMMAND="$REPOSITORY_ROOT/.build/jdk21/Contents/Home/bin/java"
fi
readonly JAVA_COMMAND
readonly JAVA_MEMORY_ARGUMENTS=("-Xmx768m" "-XX:MaxMetaspaceSize=256m")

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
  publisher_arguments=(-ig ig.ini -tx n/a -no-network)
  guide_package_directory="$REPOSITORY_ROOT/.build/guide-packages/$guide"
  if [[ -d "$guide_package_directory" ]]; then
    find "$guide_package_directory" -depth -delete
  fi
  mkdir -p "$guide_package_directory"
  has_local_guide_packages=false
  if grep -q '^  org\.grovealliance\.fhir\.mobile:' "$guide/sushi-config.yaml"; then
    test -f "$REPOSITORY_ROOT/mobile/output/package.tgz"
    node "$REPOSITORY_ROOT/Scripts/cache-fhir-package.cjs" \
      --cache-root "$FHIR_PACKAGE_CACHE" \
      "$REPOSITORY_ROOT/mobile/output/package.tgz"
    cp "$REPOSITORY_ROOT/mobile/output/package.tgz" \
      "$guide_package_directory/org.grovealliance.fhir.mobile-0.2.0.tgz"
    has_local_guide_packages=true
  fi
  if grep -q '^  org\.grovealliance\.fhir\.sensor:' "$guide/sushi-config.yaml"; then
    test -f "$REPOSITORY_ROOT/sensor/output/package.tgz"
    node "$REPOSITORY_ROOT/Scripts/cache-fhir-package.cjs" \
      --cache-root "$FHIR_PACKAGE_CACHE" \
      "$REPOSITORY_ROOT/sensor/output/package.tgz"
    cp "$REPOSITORY_ROOT/sensor/output/package.tgz" \
      "$guide_package_directory/org.grovealliance.fhir.sensor-0.2.0.tgz"
    has_local_guide_packages=true
  fi
  if [[ "$has_local_guide_packages" == "true" ]]; then
    publisher_arguments+=(
      -packages
      "$guide_package_directory"
    )
  fi
  (
    cd "$guide"
    GROVE_FHIR_TOOL_HOME="$FHIR_TOOL_HOME" \
    NODE_OPTIONS="--require=$REPOSITORY_ROOT/Scripts/sushi-cache-home.cjs" \
      "$JAVA_COMMAND" "${JAVA_MEMORY_ARGUMENTS[@]}" -Djava.awt.headless=true \
      -Duser.home="$FHIR_TOOL_HOME" -jar "$TOOLS_DIRECTORY/publisher.jar" \
      "${publisher_arguments[@]}"
  ) || {
    # Publisher 2.3.x can report a transient combined-package write failure before
    # Jekyll creates output/, or return nonzero for the pinned offline MIME defect
    # even though every finding is an exact reviewed suppression. Accept only a
    # fully materialized package whose raw/exact/unsuppressed QA ledger passes the
    # same fail-closed audit used below; every other nonzero exit remains fatal.
    test -f "$REPOSITORY_ROOT/$guide/output/package.tgz"
    test -f "$REPOSITORY_ROOT/$guide/output/qa.json"
    python3 "$REPOSITORY_ROOT/Scripts/check-guide-qa.py" "$REPOSITORY_ROOT/$guide"
  }
done

python3 Scripts/check-guide-qa.py "${guides[@]}"
