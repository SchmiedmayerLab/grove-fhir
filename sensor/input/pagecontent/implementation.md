<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

The Sensor package depends on Mobile and is built after it. Producer output is validated with the official HL7 FHIR Validator.
Resolve the exact Mobile and Sensor package versions from `catalog/release-manifest.json`; both packages target FHIR R4 `4.0.1`.

An adapter Observation declares exactly two profiles: one shared semantic profile from Mobile or Sensor and one adapter profile.
It never repeats the inherited Grove Mobile Observation, PHD RTSA, or a core profile unless the resource independently conforms to a distinct workflow that explicitly requires that profile.

Producer implementations consume [`catalog/sensor-catalog.json`](https://grovealliance.org/fhir/catalog/sensor-catalog.json) and [`catalog/profile-claims.json`](https://grovealliance.org/fhir/catalog/profile-claims.json) as normative machine-readable contracts.

A conformant producer validates supplied bytes against the declared registry grammar before emission and derives grammar-defined summary counts from the accepted payload.
For URL payloads, the bundled producer validator checks required Attachment metadata only and does not fetch or verify the bytes.
For inline payloads, it verifies size/hash integrity, validates registered CSV grammars, and applies the documented strict JSON checks to native, provider, and FHIR formats; the FHIR collection format also receives its Bundle-envelope and resource-shape checks.
Its CSV checks are structural and lexical; they do not enforce per-column source-domain ranges stated in column meanings.
It does not execute the official FHIR Validator over embedded resources, parse every binary grammar, recompute summaries, semantically reinterpret, sanitize, rewrite, or reserialize bytes.
Passing this validation alone therefore does not prove embedded-resource FHIR/profile conformance or the remaining payload and derivation obligations, clinical meaning, or authorization.

Structured Sensor Observations and Recording Documents use the same auditable conversion graph shape. `grove-sensor-conversion-provenance` identifies the assembler, targets every produced representation, and carries the complete source Identifier as a source entity.
Adapter packages narrow that source identity and require internal UUID targets when the resources are exchanged in a Mobile collection Bundle.

### Dependencies and terminology notices

The tables below list this guide's package dependencies and the notices for terminology used by its artifacts and examples.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
