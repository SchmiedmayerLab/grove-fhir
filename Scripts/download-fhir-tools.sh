#!/usr/bin/env bash
#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#

set -euo pipefail

readonly TOOLS_DIRECTORY="${1:-.build/fhir-tools}"
readonly PUBLISHER_VERSION="2.3.2"
readonly PUBLISHER_SHA256="07c576024df917cc1f879b6b5a64147cd0222d5b4129688e8f0ad9ccce58b1d5"
readonly VALIDATOR_VERSION="6.10.2"
readonly VALIDATOR_SHA256="a3addadfa18dfa23146a0a243b6ede68eaad92157a5407738c468bb3d7e4ccd6"

# Validator 6.10.2 loads the R4 bootstrap packages and the current universal
# terminology/extension packages before it can honor a fully offline
# validation request. Keep the complete, checksum-pinned dependency closure in
# one place so a fresh runner never depends on mutable package-server state.
readonly FHIR_PACKAGE_ARCHIVES=(
  "hl7.fhir.r4.core|4.0.1|ebd7731df7d36b5b7d39d5fb6c9d77b44bb7fe5742f1a2e87f164738c3289d44"
  "hl7.fhir.r5.core|5.0.0|74b27cd1bfce9e80eaceac431edf230b0945a443564fbf5512f82e5fa50a80d4"
  "hl7.fhir.xver-extensions|0.1.0|f3bb9fa2083402e88a02b41f433655274e8a1cca563211c8f7ba6fd0badf537a"
  "hl7.terminology.r4|6.2.0|79404c9cc95491fc0155627cd039c401a6eb4748175328131e91b709a41300e2"
  "hl7.fhir.uv.extensions.r4|5.2.0|b406e75575f05676559d0759770c5939d023ee72fb2ef38e0b3259328487720a"
  "hl7.fhir.uv.extensions.r5|5.2.0|e02fc6eff0f37c1611a35aa93ef9aaa3b55ab7371a5c96f4d2a5834106a13170"
  "hl7.terminology.r5|7.1.0|473303108b5607aad7b910581739e8bbf3e61a625ed9e739c66e0ca597d4aefe"
  "hl7.fhir.uv.extensions.r5|5.3.0|f1039cac888d79ebd29878d7debe5e647ffe7ed962a9033da095258a03a06105"
  "hl7.terminology|7.3.0|8318f87cdcb44a6dfc5c197ca569c9b0499b06f45522324bfc4b4b810d51d4b9"
  "hl7.fhir.uv.extensions|5.3.0|6e3a3f9929e05d2b813a3f98fa1ad2f5122fb6b2819fa73e6c5520002fb2c5b0"
  "hl7.terminology.r4|7.1.0|1cb0cd5601972925fcd04f2c175d9cc63a9ecd9346a91a6e735f1a865dc5fba1"
  "hl7.fhir.uv.extensions.r4|5.3.0|dfbc3ac95df91ed845cc6b60920d2875f679361fa0e16f227cee93c4a9ab2104"
  "hl7.terminology.r4|7.3.0|1a1ef2aa22ecc820341267f2bdba3b2d1f4adafb9bdddfc9e51c611cd64f3b54"
)

mkdir -p "$TOOLS_DIRECTORY"

download_and_verify() {
  local url="$1"
  local destination="$2"
  local expected_sha="$3"

  if [[ -f "$destination" ]] && printf '%s  %s\n' "$expected_sha" "$destination" | shasum -a 256 --check --status; then
    return
  fi

  local temporary_file="${destination}.download"
  curl --fail --location --retry 3 --output "$temporary_file" "$url"
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

for package_specification in "${FHIR_PACKAGE_ARCHIVES[@]}"; do
  IFS='|' read -r package_id package_version package_sha256 <<< "$package_specification"
  package_archive="$TOOLS_DIRECTORY/${package_id}-${package_version}.tgz"
  download_and_verify \
    "https://packages.fhir.org/${package_id}/${package_version}" \
    "$package_archive" \
    "$package_sha256"
  node "$(dirname "$0")/cache-fhir-package.cjs" "$package_archive"
done
