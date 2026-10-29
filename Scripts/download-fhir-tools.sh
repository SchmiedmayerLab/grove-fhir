#!/usr/bin/env bash
#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#

set -euo pipefail

offline=false
if [[ "${1:-}" == "--offline" ]]; then
  offline=true
  shift
fi
if (( $# > 1 )); then
  echo "Usage: $0 [--offline] [tools-directory]" >&2
  exit 2
fi

readonly OFFLINE="$offline"
readonly TOOLS_DIRECTORY="${1:-.build/fhir-tools}"
REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly REPOSITORY_ROOT
# Honours the same override as the guide build: concurrent builds each seed their own clone, and
# two of them warming one cache is what corrupts it.
readonly FHIR_PACKAGE_CACHE="${GROVE_FHIR_HOME_OVERRIDE:-$REPOSITORY_ROOT/.build/fhir-home}/.fhir/packages"
readonly PUBLISHER_VERSION="2.3.3"
readonly PUBLISHER_SHA256="7821631325c60b17b8832a15ed4299563265e72cfe5af12457ab7f23628400d2"
readonly VALIDATOR_VERSION="6.10.4"
readonly VALIDATOR_SHA256="1106b9d58f9e363e47bea7c4fc065841e5fc91fe9d062775c3bfdd212bd653cc"
readonly TEMPLATE_ID="fhir2.base.template"
readonly TEMPLATE_VERSION="0.1.0"
readonly TEMPLATE_SHA256="b351fa5fcc8edd76f491e129de4aeb35c888265ae0f7b33ea2af0571a7533fed"

# Validator 6.10.4 loads the R4 bootstrap packages and the current universal
# terminology/extension packages before it can honor a fully offline
# validation request. Keep the complete, checksum-pinned dependency closure in
# one place so a fresh runner never depends on mutable package-server state.
readonly FHIR_PACKAGE_ARCHIVES=(
  "hl7.fhir.pubpack|0.2.5|ce55f91c9e4ca723711a9c6a55aee22368278b73e3c4e0c6408bf90488a1a360"
  "hl7.fhir.r4.core|4.0.1|ebd7731df7d36b5b7d39d5fb6c9d77b44bb7fe5742f1a2e87f164738c3289d44"
  "hl7.fhir.r5.core|5.0.0|74b27cd1bfce9e80eaceac431edf230b0945a443564fbf5512f82e5fa50a80d4"
  "hl7.fhir.xver-extensions|0.1.0|f3bb9fa2083402e88a02b41f433655274e8a1cca563211c8f7ba6fd0badf537a"
  "hl7.terminology.r4|6.2.0|79404c9cc95491fc0155627cd039c401a6eb4748175328131e91b709a41300e2"
  "hl7.fhir.uv.extensions.r4|5.2.0|b406e75575f05676559d0759770c5939d023ee72fb2ef38e0b3259328487720a"
  "hl7.fhir.uv.extensions.r5|5.2.0|e02fc6eff0f37c1611a35aa93ef9aaa3b55ab7371a5c96f4d2a5834106a13170"
  "hl7.terminology.r5|7.1.0|473303108b5607aad7b910581739e8bbf3e61a625ed9e739c66e0ca597d4aefe"
  "hl7.terminology.r5|7.5.0|cabae9ff7828c05173369bd2244ab6eabafe19d65b02c140a76638c1f3a56bf9"
  "hl7.fhir.uv.extensions.r5|5.4.0|79ceb16622794579a905d019890644887e070db7df640b6f98483a390ee3f598"
  "hl7.terminology|7.5.0|c54ebe534cd3f2474459eaed68e54c34f09b003766605b19e5552db376f2cc42"
  "hl7.fhir.uv.extensions|5.4.0|9e72cb92118a3e64babf442394fdc300b97f5d53b295469aee5ed34f216a830e"
  "hl7.terminology.r4|7.1.0|1cb0cd5601972925fcd04f2c175d9cc63a9ecd9346a91a6e735f1a865dc5fba1"
  "hl7.fhir.uv.extensions.r4|5.4.0|e93eb1ece7d14e6b3dfaa7af5ac510577957cb5fd2b61ef95cdcfbbdca81c96d"
  "hl7.terminology.r4|7.5.0|1da3004587602c3f5120061abc2309fef1f96668a477a9964354fa9af6fa6e60"
  "hl7.fhir.uv.sdc|4.0.0|d785be8474c7ec7988e32e326430d9ca4aeb2cac4a1f195022e4d6f7dc5c5291"
  # SDC 4.0.0 declares this exact ballot build as its dependency; the guides themselves pin 5.4.0.
  "hl7.fhir.uv.extensions.r4|5.3.0-ballot-tc1|5f5d1e88052d615453e6b7a1eb4f885df36590f14b52974e5860485d16819bd9"
  "hl7.fhir.r4.examples|4.0.1|e18b31e7a52145a31f1f3f409cf6847583b08b7306cc4e9460a95a7b5efba930"
  "hl7.fhir.uv.xver-r5.r4|0.1.0|7ee6f04d78ced803dd567559a0d178bafbd2d3b71db61bbbf6b15c796a1a664d"
  "hl7.fhir.uv.tools.r4|1.1.2|a1f166f8808629a40c4acabc16a4fbfd164d9f38f9db95b6f4b38bb69155dfe4"
  "hl7.terminology.r4|6.5.0|a28b638483a11df696ed92198276236d759e41c7a3a8960c9e7e7d0a1185bd06"
)

mkdir -p "$TOOLS_DIRECTORY" "$FHIR_PACKAGE_CACHE"

download_and_verify() {
  local url="$1"
  local destination="$2"
  local expected_sha="$3"

  if [[ -f "$destination" && ! -L "$destination" ]] \
      && printf '%s  %s\n' "$expected_sha" "$destination" | shasum -a 256 --check --status; then
    return
  fi
  if [[ "$OFFLINE" == "true" ]]; then
    echo "Offline FHIR tool cache is missing or invalid: $destination" >&2
    exit 1
  fi

  local temporary_file="${destination}.download"
  if [[ -L "$destination" || -L "$temporary_file" ]]; then
    echo "FHIR tool destination must not be a symlink: $destination" >&2
    exit 1
  fi
  # --retry alone skips connection failures, which is how the package host usually fails.
  curl --fail --location --retry 3 --retry-all-errors --retry-delay 5 \
    --connect-timeout 30 --output "$temporary_file" "$url"
  printf '%s  %s\n' "$expected_sha" "$temporary_file" | shasum -a 256 --check
  mv "$temporary_file" "$destination"
}

download_and_verify \
  "https://github.com/HL7/fhir-ig-publisher/releases/download/${PUBLISHER_VERSION}/publisher.jar" \
  "$TOOLS_DIRECTORY/publisher.jar" \
  "$PUBLISHER_SHA256"
download_and_verify \
  "https://github.com/hapifhir/org.hl7.fhir.core/releases/download/${VALIDATOR_VERSION}/validator_cli.jar" \
  "$TOOLS_DIRECTORY/validator_cli.jar" \
  "$VALIDATOR_SHA256"

template_archive="$TOOLS_DIRECTORY/${TEMPLATE_ID}-${TEMPLATE_VERSION}.tgz"
download_and_verify \
  "https://packages.fhir.org/${TEMPLATE_ID}/${TEMPLATE_VERSION}" \
  "$template_archive" \
  "$TEMPLATE_SHA256"
node "$(dirname "$0")/cache-fhir-package.cjs" \
  --cache-root "$FHIR_PACKAGE_CACHE" \
  "$template_archive"

for package_specification in "${FHIR_PACKAGE_ARCHIVES[@]}"; do
  IFS='|' read -r package_id package_version package_sha256 <<< "$package_specification"
  package_archive="$TOOLS_DIRECTORY/${package_id}-${package_version}.tgz"
  download_and_verify \
    "https://packages.fhir.org/${package_id}/${package_version}" \
    "$package_archive" \
    "$package_sha256"
  node "$(dirname "$0")/cache-fhir-package.cjs" \
    --cache-root "$FHIR_PACKAGE_CACHE" \
    "$package_archive"
done
