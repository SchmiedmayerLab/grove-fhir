<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

A HealthKit source-type code is the identifier the platform hands back at runtime, which is what a
producer reads from a sample. It is not always the name of the constant that holds it: Apple can rename a
constant while keeping its value, and two sample types are published with no constant at all. The catalog
records every declaring name alongside the identifier; only the identifier is a code.

### `documentation`
{: #documentation }

The canonical Apple documentation page for the source type, recorded verbatim from Apple's published
symbol index. Apple nests a member page beneath its owning type, so a path assembled from the identifier
alone does not resolve.

### Membership and versioning

The concepts in this code system are exactly the source-type identifiers of the SDK baseline named in the
code system description, read by resolving every declared constant inside an iOS simulator on that
baseline and verified against `healthkit/input/data/healthkit-inventory.json`. `content` is therefore
`complete` for that baseline. Moving to a later SDK baseline is a version change, not an in-place edit.

Whether the v0.2 adapter admits output for a source type is the `status` column of the
[status matrix](status-matrix.html), and never appears in terminology.

Each property is defined as a concept in [healthkit-concept-property](CodeSystem-healthkit-concept-property.html), which is what `CodeSystem.property.uri` names.
