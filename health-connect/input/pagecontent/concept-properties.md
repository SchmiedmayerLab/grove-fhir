<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

The Health Connect record-type code system carries one concept property.

### `documentation`
{: #documentation }

The canonical AndroidX reference page for the record class the code names, recorded from the published
artifact inventory in `health-connect/input/data/health-connect-inventory.json`.

### Membership and versioning

The concepts in this code system are exactly the concrete `Record` classes published by the AndroidX
artifact named in the code system description, excluding the abstract supertypes `Record`,
`InstantaneousRecord`, `IntervalRecord`, and `SeriesRecord`, which are not readable record types.
`content` is therefore `complete` for that artifact version. Moving to a later artifact is a version
change, not an in-place edit.

Whether the v0.3 adapter admits output for a record type is the `status` column of the
[status matrix](status-matrix.html), and never appears in terminology.

Each property is defined as a concept in [health-connect-concept-property](CodeSystem-health-connect-concept-property.html), which is what `CodeSystem.property.uri` names.
