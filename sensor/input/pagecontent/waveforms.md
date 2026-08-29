<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

This page defines the two source-neutral representations for sampled sensor data: inline uniform series and registered recording documents.
The selected representation must preserve the source timing, channel identity, and payload without inventing regularity or clinical meaning.

### Uniform sampled data

`grove-sensor-sampled-data-observation` carries one uniformly sampled numeric series. `SampledData.period` is the strictly positive number of milliseconds between frames, and `dimensions` is the strictly positive number of interlaced decimal values in each frame.
At least two complete frames are required.
The Grove FHIR contracts admit direct numeric values only: `factor`, `lowerLimit`, and `upperLimit` are absent, and `E`, `U`, `L`, and omitted-value tokens are not admitted.
The data token count is an exact multiple of `dimensions`.

`effectivePeriod.start` is the first frame instant.
If there are `F` frames, `effectivePeriod.end` is exactly `start + (F - 1) × period` milliseconds.
Both bounds are mandatory and carry offsets.
A producer that cannot prove uniform timing, complete numeric frames, and this exact end instant emits a Recording Document instead of a SampledData Observation.

### ECG

`grove-sensor-ecg-observation` fixes the recording code to LOINC `11524-6` and uses one component per lead.
Each component identifies its lead using one or more complete established-terminology codings and contains a one-dimensional millivolt SampledData series.
The unordered set of exact `(Coding.system, Coding.code)` pairs identifies the channel, which permits standard and adapter translations without depending on coding order. Duplicate pairs within a component and duplicate identity sets across components are prohibited; `Coding.display` is presentation text and never contributes to identity.
The example uses ISO/IEEE 11073 MDC `131329` for Lead I.
A producer does not relabel an unknown channel as a known lead.

### Recording documents

`grove-sensor-recording-document` carries exactly one embedded payload or retrievable URL per attachment. `contentType`, byte size, and the FHIR R4 Attachment SHA-1 hash are mandatory. `title` is an optional presentation label; consumers must not use its presence or wording as recording identity or semantics.
For embedded data, size and hash match the decoded bytes exactly.
A retrievable URL is immutable and version-specific; changed bytes use a new URL and business identity.
The R4 SHA-1 hash detects changed content only: it is not a digital signature, authorization decision, or security credential. `context.related` can link a parsed or summary Observation.
There is deliberately no universal inline-size cutoff: transport and repository capacity are deployment policy, while the FHIR representation remains stable.

The Grove ValueSet admits the registered media types used by the payload formats and carries a closed expansion for offline membership checks.
`Attachment.contentType` identifies the serialization using an IANA-registered type such as `text/csv`, `application/fhir+json`, `application/json`, or `application/octet-stream`.
`DocumentReference.content.format` separately identifies the exact Grove payload contract, so two formats may share one media type without losing their distinct semantics.
The IANA registry remains authoritative for media types: Grove neither publishes nor versions that external CodeSystem and does not define or reassign its codes.

Before emitting any Recording Document, a producer requires exactly one explicit caller assertion: either `caller-authorized-opaque-payload` or `verified-sanitized-input`.
An absent, ambiguous, or unsupported assertion fails closed.
This is a producer preflight input, not a FHIR consent or authorization claim.
A conformant producer validates supplied bytes against the declared registry grammar and derives any grammar-defined summary counts from the accepted payload.
For URL payloads, the bundled validator checks required Attachment metadata only and does not fetch or verify the bytes.
For inline payloads, it verifies size/hash integrity, validates registered CSV grammars, and applies the documented strict JSON checks to native, provider, and FHIR formats; the FHIR collection format also receives its Bundle-envelope and resource-shape checks.
Its CSV checks are structural and lexical; they do not enforce per-column source-domain ranges stated in column meanings.
It does not execute the official FHIR Validator over embedded resources, parse every binary grammar, recompute summaries, reinterpret, sanitize, rewrite, or reserialize the bytes.
Passing it alone does not prove URL-backed payload integrity, embedded-resource FHIR/profile conformance, or the remaining payload and derivation obligations, clinical meaning, or authorization.
