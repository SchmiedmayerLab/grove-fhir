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
# Overridable so concurrent builds can each own a cloned cache; two Publishers writing one cache
# corrupt it. Defaults to the shared warm cache for an ordinary single-guide build.
readonly FHIR_TOOL_HOME="${GROVE_FHIR_HOME_OVERRIDE:-$REPOSITORY_ROOT/.build/fhir-home}"
readonly FHIR_PACKAGE_CACHE="$FHIR_TOOL_HOME/.fhir/packages"
JAVA_COMMAND="java"
if [[ -x "$REPOSITORY_ROOT/.build/jdk21/Contents/Home/bin/java" ]]; then
  JAVA_COMMAND="$REPOSITORY_ROOT/.build/jdk21/Contents/Home/bin/java"
fi
readonly JAVA_COMMAND
readonly JAVA_MEMORY_ARGUMENTS=("-Xmx4g" "-XX:MaxMetaspaceSize=512m")

cd "$REPOSITORY_ROOT"
export PATH="$REPOSITORY_ROOT/node_modules/.bin:$PATH"
bundle config set --local path "$REPOSITORY_ROOT/.build/bundle"
bundle config set --local bin "$REPOSITORY_ROOT/.build/bin"
case "${GROVE_TX_OFFLINE:-0}" in
  0|"") offline_build=false ;;
  1) offline_build=true ;;
  *) echo "GROVE_TX_OFFLINE must be 0 or 1" >&2; exit 2 ;;
esac
readonly offline_build
if [[ "$offline_build" == "true" ]]; then
  if [[ -n "${GROVE_TX_SERVER:-}" ]]; then
    echo "GROVE_TX_SERVER is prohibited when GROVE_TX_OFFLINE=1" >&2
    exit 2
  fi
  export BUNDLE_FROZEN=true
  # Release builds bootstrap these dependencies in an explicit online phase. Re-resolve the
  # complete bundle locally here so a missing gem fails instead of falling back to RubyGems.
  bundle install --local --jobs 4
  bundle check
else
  bundle install --jobs 4 --retry 3
fi
bundle binstubs jekyll
export PATH="$REPOSITORY_ROOT/.build/bin:$PATH"
if [[ "$offline_build" == "true" ]]; then
  # This re-hashes Publisher, Validator, the template, and the external FHIR package closure,
  # then seeds the isolated package cache exclusively from those verified local archives.
  ./Scripts/download-fhir-tools.sh --offline "$TOOLS_DIRECTORY"
else
  ./Scripts/download-fhir-tools.sh "$TOOLS_DIRECTORY"
fi

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
  # The Publisher writes the combined package before Jekyll creates output/, so the clean
  # above leaves it nowhere to write and the package is silently never produced.
  mkdir -p "$REPOSITORY_ROOT/$guide/output"
  # The Publisher validates codings against a terminology server. The server's cache lives in
  # each guide's input-cache, which is never committed: it holds thousands of SNOMED and LOINC
  # concepts this project has no licence to redistribute, and it is not ours to relicense under
  # the repository's MIT terms.
  #
  # GROVE_TX_OFFLINE=1 builds without a server. That cannot validate every external coding, so it
  # is the structural/package lane only; an approved online terminology attestation is separate.
  if [[ "$offline_build" == "true" ]]; then
    publisher_arguments=(-ig ig.ini -tx n/a -no-network)
  else
    publisher_arguments=(-ig ig.ini -tx "${GROVE_TX_SERVER:-https://tx.fhir.org}")
  fi
  guide_package_directory="$REPOSITORY_ROOT/.build/guide-packages/$guide"
  if [[ -d "$guide_package_directory" ]]; then
    find "$guide_package_directory" -depth -delete
  fi
  mkdir -p "$guide_package_directory"
  has_local_guide_packages=false
  # The dependencies, and the version each one is pinned at, come from the guide's own
  # sushi-config.yaml. A name or a version written here as well would be a second place to
  # forget: the staged file has to carry the pinned version, or the Publisher ignores it and
  # falls back to the network, where these packages are not published.
  while read -r dependency version; do
    [[ -z "$dependency" ]] && continue
    test -f "$REPOSITORY_ROOT/$dependency/output/package.tgz"
    node "$REPOSITORY_ROOT/Scripts/cache-fhir-package.cjs" \
      --cache-root "$FHIR_PACKAGE_CACHE" \
      "$REPOSITORY_ROOT/$dependency/output/package.tgz"
    cp "$REPOSITORY_ROOT/$dependency/output/package.tgz" \
      "$guide_package_directory/org.grovealliance.fhir.$dependency-$version.tgz"
    has_local_guide_packages=true
  done < <(python3 "$REPOSITORY_ROOT/Scripts/guide-build-plan.py" --dependencies "$guide")
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
  # The exact SUSHI index is ignored and remains only on the runner that built
  # this guide. Verify it here so local, draft, release, and deployment builds
  # all enforce the same reviewed artifact surface before output can be reused.
  python3 "$REPOSITORY_ROOT/Scripts/render-artifact-allowlist.py" \
    --check-generated "$guide"
  if [[ "$guide" == "mobile" ]]; then
    python3 "$REPOSITORY_ROOT/Scripts/check-semantic-baseline.py"
  fi
done

python3 Scripts/check-guide-qa.py "${guides[@]}"
