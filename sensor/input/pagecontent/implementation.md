<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

The Sensor package depends on the Grove Mobile package. Validate producer output against both packages with the official HL7 FHIR Validator.
Resolve the exact Mobile and Sensor package versions from `catalog/release-manifest.json`; both packages target FHIR R4 `4.0.1`.

An adapter Observation declares exactly two profiles: one shared semantic profile from Mobile or Sensor and one adapter profile.
It never repeats the inherited Grove Mobile Observation, PHD RTSA, or a core profile unless the resource independently conforms to a distinct workflow that explicitly requires that profile.

Producer implementations consume [`catalog/sensor-catalog.json`](https://grovealliance.org/fhir/catalog/sensor-catalog.json) and [`catalog/profile-claims.json`](https://grovealliance.org/fhir/catalog/profile-claims.json) as normative machine-readable contracts.

A conformant producer validates supplied bytes against the declared registry grammar before emission and derives grammar-defined summary counts from the accepted payload.
Grove format validation checks required Attachment metadata for URL-backed content without retrieving the bytes.
For inline content, it verifies size and hash integrity and, when applicable to the declared format, its registered CSV grammar or defined JSON envelope.
It does not replace validation of embedded FHIR resources, binary-format validation, semantic review, authorization, or adapter-specific derivation requirements.

Structured Sensor Observations and Recording Documents use the same auditable conversion graph shape. `grove-sensor-conversion-provenance` identifies the assembler, targets every produced representation, and carries the complete source Identifier as a source entity.
When resources are exchanged in a Mobile collection Bundle, adapter packages require Provenance targets to be literal UUID-URN references that resolve to entries in that Bundle.

### Dependencies and terminology notices

The tables below list this guide's package dependencies and the notices for terminology used by its artifacts and examples.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
