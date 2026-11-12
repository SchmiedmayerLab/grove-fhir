#!/usr/bin/env bash
#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#

# Builds the guides in dependency waves, running each wave concurrently.
#
# The Publisher keeps its package cache under one `-Duser.home`, and two builds writing that cache
# at once corrupt it. Each concurrent build therefore gets its own home, cloned from the warm one:
# on APFS `cp -c` is a copy-on-write clone, so the clone costs neither the copy time nor the disk.
# Elsewhere it is a real copy, so a home is removed as soon as its guide has built.
#
# The Bundler setup and the checksum-pinned tools are bootstrapped once, before any wave, in the
# mode GROVE_TX_OFFLINE selects; the concurrent builds then skip that bootstrap rather than race it.

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly REPOSITORY_ROOT
readonly WARM_HOME="$REPOSITORY_ROOT/.build/fhir-home"
readonly WAVE_ROOT="$REPOSITORY_ROOT/.build/parallel-homes"

# The waves come from Scripts/guide-build-plan.py, which derives them from each guide's own
# dependencies. Writing them here as well would be a second place to forget when a guide is added.

# Another Publisher writing the shared cache while these clones are made is the corruption this
# script exists to avoid, so refuse rather than race it.
if pgrep -f "publisher.jar" > /dev/null 2>&1; then
  echo "error: a guide build is already running; wait for it to finish" >&2
  exit 2
fi

"$REPOSITORY_ROOT/Scripts/build-guides.sh" --bootstrap-only

if [[ ! -d "$WARM_HOME/.fhir/packages" ]]; then
  echo "error: the bootstrap left no package cache at $WARM_HOME" >&2
  exit 2
fi

rm -rf "$WAVE_ROOT"
mkdir -p "$WAVE_ROOT"

build_one() {
  local guide="$1"
  local home="$WAVE_ROOT/$guide"
  # Everything, including the clone, writes to the guide's log, so a failed copy is reported too.
  {
    mkdir -p "$home"
    # -c clones on APFS and falls back to a real copy elsewhere, so this stays correct off macOS.
    # A failed clone may leave a partial tree, which the copy would then nest itself inside.
    if ! cp -Rc "$WARM_HOME/.fhir" "$home/.fhir" 2>/dev/null; then
      rm -rf "$home/.fhir"
      cp -R "$WARM_HOME/.fhir" "$home/.fhir"
    fi
    GROVE_SKIP_BOOTSTRAP=1 GROVE_FHIR_HOME_OVERRIDE="$home" \
      "$REPOSITORY_ROOT/Scripts/build-guides.sh" "$guide"
    rm -rf "$home"
  } > "$WAVE_ROOT/$guide.log" 2>&1
}

run_wave() {
  local -a wave=("$@")
  local -a pids=()
  local -a names=()
  for guide in "${wave[@]}"; do
    build_one "$guide" &
    pids+=("$!")
    names+=("$guide")
  done
  local failed=0
  local -a results=()
  for index in "${!pids[@]}"; do
    if wait "${pids[$index]}"; then
      results+=("built")
    else
      results+=("FAILED")
      failed=1
    fi
  done
  for index in "${!names[@]}"; do
    # On GitHub Actions the per-guide logs are not otherwise visible, so fold each into the job log.
    if [[ "${GITHUB_ACTIONS:-}" == "true" ]]; then
      echo "::group::${names[$index]} (${results[$index]})"
      cat "$WAVE_ROOT/${names[$index]}.log" || echo "(no log was written)"
      echo "::endgroup::"
    fi
    if [[ "${results[$index]}" == "built" ]]; then
      echo "  ${names[$index]}: built"
    else
      echo "  ${names[$index]}: FAILED (see $WAVE_ROOT/${names[$index]}.log)" >&2
    fi
  done
  return "$failed"
}

wave_number=0
while IFS= read -r wave_line; do
  [[ -z "$wave_line" ]] && continue
  wave_number=$((wave_number + 1))
  read -r -a wave <<< "$wave_line"
  echo "==> wave $wave_number: ${wave[*]}"
  run_wave "${wave[@]}"
done < <(python3 "$REPOSITORY_ROOT/Scripts/guide-build-plan.py")

echo "==> QA ledger"
if [[ "${GROVE_TX_OFFLINE:-0}" == "1" ]]; then
  # shellcheck disable=SC2046 # the plan prints one bare guide name per field, which is the argument list.
  python3 "$REPOSITORY_ROOT/Scripts/check-guide-qa.py" \
    --offline-terminology \
    $(python3 "$REPOSITORY_ROOT/Scripts/guide-build-plan.py" | tr '\n' ' ')
else
  # shellcheck disable=SC2046 # the plan prints one bare guide name per field, which is the argument list.
  python3 "$REPOSITORY_ROOT/Scripts/check-guide-qa.py" \
    $(python3 "$REPOSITORY_ROOT/Scripts/guide-build-plan.py" | tr '\n' ' ')
fi
