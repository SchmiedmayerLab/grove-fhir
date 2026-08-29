<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

A HealthKit source-type code is the identifier returned by the platform at runtime and read by a producer from a sample.
It is not always the name of the constant that holds it: Apple can rename a constant while keeping its value, and two sample types are published with no constant at all.
The catalog records every declaring name alongside the identifier; only the identifier is a code.

### `documentation`
{: #documentation }

The canonical Apple documentation page for the source type, recorded verbatim from Apple's published symbol index.
Apple nests a member page beneath its owning type, so a path assembled from the identifier alone does not resolve.

### Membership and versioning

The code system contains every source-type identifier in the SDK baseline named in its description.
`content` is therefore `complete` for that baseline.
Moving to a later SDK baseline is a version change, not an in-place edit.

The `status` column of the [status matrix](status-matrix.html) defines whether the Grove FHIR contracts admit output for a source type. Admission status is not part of the terminology.

Each property is defined as a concept in [healthkit-concept-property](CodeSystem-healthkit-concept-property.html), which is what `CodeSystem.property.uri` names.
