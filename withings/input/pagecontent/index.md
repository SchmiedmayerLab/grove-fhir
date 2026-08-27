<!--

This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

-->

Every Withings Health Mate element this adapter admits that no other source reports.

A measurement two or more connected providers report is source-neutral and belongs to the
[Grove FHIR Connected Provider Adapter](https://grovealliance.org/fhir/providers), which this guide depends on.
What remains here is Withings-exclusive: a value produced by Withings's own algorithm over Withings's own inputs.

Such a value is carried under a Withings-scoped profile rather than a shared one, and never under a code another
vendor also uses.
A vendor score is not comparable across vendors even when two vendors give it the same name, so publishing it
under a shared code would assert a comparability that does not exist.
The profile states what the value is and whose algorithm produced it, and asserts nothing further.

## Dependencies and terminology notices

The generated tables identify this guide's package dependencies and the notices for terminology used by its artifacts and examples.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
