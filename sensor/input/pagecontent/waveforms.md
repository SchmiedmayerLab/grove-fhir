<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

## Uniform sampled data

`grove-sensor-sampled-data-observation` carries one uniformly sampled numeric series.
`SampledData.period` is the strictly positive number of milliseconds between frames,
and `dimensions` is the strictly positive number of interlaced decimal values in each
frame. At least two complete frames are required. Version 0.5.0 admits direct numeric values only: `factor`, `lowerLimit`, and
`upperLimit` are absent, and `E`, `U`, `L`, and omitted-value tokens are not admitted.
The data token count is an exact multiple of `dimensions`.

`effectivePeriod.start` is the first frame instant. If there are `F` frames,
`effectivePeriod.end` is exactly `start + (F - 1) × period` milliseconds. Both bounds
are mandatory and carry offsets. A producer that cannot prove uniform timing, complete
numeric frames, and this exact end instant emits a Recording Document instead of a
SampledData Observation.

## ECG

`grove-sensor-ecg-observation` fixes the recording code to LOINC `11524-6` and uses one
component per lead. Each component identifies its lead using established terminology
and contains a one-dimensional millivolt SampledData series. The example uses ISO/IEEE
11073 MDC `131329` for Lead I. A producer does not relabel an unknown channel as a
known lead.

## Native and large recordings

`grove-sensor-recording-document` carries exactly one embedded payload or retrievable
URL per attachment. `contentType`, title, byte size, and the FHIR R4 Attachment SHA-1
hash are mandatory. For embedded data, size and hash match the decoded bytes exactly.
A retrievable URL is immutable and version-specific; changed bytes use a new URL and
business identity. The R4 SHA-1 hash detects changed content only: it is not a digital
signature, authorization decision, or security credential. `context.related` can link a parsed or summary
Observation. There is deliberately no universal inline-size cutoff: transport and
repository capacity are deployment policy, while the FHIR representation remains
stable.

The Grove ValueSet admits one media type per registered payload format and carries a
closed expansion for offline membership checks. Standard types such as `text/csv` and
`application/fhir+json` are identified by their IANA registration; the formats Grove
defines itself use the vendor tree, and those are Grove's own types rather than
registered ones. The IANA registry remains authoritative for the standard types: Grove
neither publishes nor versions that external CodeSystem and does not define or reassign
its codes.

Before emitting any native Recording Document, a producer requires exactly one explicit
caller assertion: either `caller-authorized-opaque-payload` or
`verified-sanitized-input`. An absent, ambiguous, or unsupported assertion fails closed.
This is a producer preflight input, not a FHIR consent or authorization claim. The guide
does not inspect, fetch, or sanitize opaque bytes.
