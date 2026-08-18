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
