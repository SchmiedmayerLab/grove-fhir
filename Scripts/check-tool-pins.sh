#!/usr/bin/env bash
#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#
# A GitHub release asset can be deleted and re-uploaded under a tag that already shipped, so a
# checksum pinned against it silently stops matching what upstream now serves. The build caches the
# tools by the content of download-fhir-tools.sh, so a cache hit never re-downloads and never
# notices. This compares each pinned checksum against the digest GitHub reports for the asset, which
# costs one API call and no download.

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly REPOSITORY_ROOT
readonly DOWNLOAD_SCRIPT="$REPOSITORY_ROOT/Scripts/download-fhir-tools.sh"

pinned_value() {
  sed -n "s/^readonly $1=\"\(.*\)\"$/\1/p" "$DOWNLOAD_SCRIPT"
}

# The pins live in download-fhir-tools.sh so the build and this check can never disagree.
PUBLISHER_VERSION="$(pinned_value PUBLISHER_VERSION)"
PUBLISHER_SHA256="$(pinned_value PUBLISHER_SHA256)"
VALIDATOR_VERSION="$(pinned_value VALIDATOR_VERSION)"
VALIDATOR_SHA256="$(pinned_value VALIDATOR_SHA256)"
readonly PUBLISHER_VERSION PUBLISHER_SHA256 VALIDATOR_VERSION VALIDATOR_SHA256

api() {
  local url="$1"
  if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    curl --fail --silent --show-error --location \
      --header "Authorization: Bearer $GITHUB_TOKEN" \
      --header "X-GitHub-Api-Version: 2022-11-28" "$url"
  else
    curl --fail --silent --show-error --location \
      --header "X-GitHub-Api-Version: 2022-11-28" "$url"
  fi
}

status=0

check_asset() {
  local repository="$1" tag="$2" asset="$3" expected_sha="$4"
  local release digest created published

  if ! release="$(api "https://api.github.com/repos/$repository/releases/tags/$tag")"; then
    echo "error: cannot read $repository release $tag" >&2
    status=1
    return
  fi
  digest="$(printf '%s' "$release" | node -e '
    const release = JSON.parse(require("fs").readFileSync(0, "utf8"));
    const asset = release.assets.find((candidate) => candidate.name === process.argv[1]);
    process.stdout.write(asset ? [asset.digest || "", asset.created_at, release.published_at].join("\t") : "");
  ' "$asset")"
  if [[ -z "$digest" ]]; then
    echo "error: $repository $tag has no asset named $asset" >&2
    status=1
    return
  fi
  IFS=$'\t' read -r digest created published <<< "$digest"

  if [[ -z "$digest" ]]; then
    # Assets uploaded before GitHub recorded digests cannot be checked without downloading them.
    echo "warning: $repository $tag $asset reports no digest; pin not verifiable from the API" >&2
    return
  fi
  if [[ "$digest" != "sha256:$expected_sha" ]]; then
    echo "error: $repository $tag $asset no longer matches its pin" >&2
    echo "  pinned:   sha256:$expected_sha" >&2
    echo "  upstream: $digest" >&2
    echo "  asset uploaded $created, release published $published" >&2
    echo "  An asset replaced under a released tag is a supply-chain event: establish why it changed" >&2
    echo "  before repinning, and prefer a later release whose asset was never replaced." >&2
    status=1
    return
  fi
  # An asset uploaded well after its release was published was replaced rather than published with it.
  if [[ "$created" > "$published" ]]; then
    local created_day="${created%%T*}" published_day="${published%%T*}"
    if [[ "$created_day" != "$published_day" ]]; then
      echo "warning: $repository $tag $asset was uploaded on $created_day but the release was published on $published_day" >&2
    fi
  fi
  echo "ok: $repository $tag $asset matches its pin"
}

check_asset "HL7/fhir-ig-publisher" "$PUBLISHER_VERSION" "publisher.jar" "$PUBLISHER_SHA256"
check_asset "hapifhir/org.hl7.fhir.core" "$VALIDATOR_VERSION" "validator_cli.jar" "$VALIDATOR_SHA256"

exit "$status"
