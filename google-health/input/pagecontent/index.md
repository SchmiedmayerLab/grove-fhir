<!--

This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

-->

Every Google Health API element this adapter admits that no other source reports.

A measurement two or more connected providers report is source-neutral and belongs to the [Grove FHIR Connected Provider Adapter](https://grovealliance.org/fhir/providers), which this guide depends on.
What remains here is Google Health-exclusive: a value produced by Google Health's own algorithm over Google Health's own inputs.

Such a value directly claims a Google Health-scoped semantic profile rather than a shared one, together with the Google Health Observation provider-lineage envelope.
A shared Google Health result uses the same envelope but pairs it with the exact shared semantic profile.
Neither claim is inferred from the other.
A vendor score is not comparable across vendors even when two vendors give it the same name, so publishing it under a shared code would assert a comparability that does not exist.
The profile states what the value is and whose algorithm produced it, and asserts nothing further.

Google Health rows use the catalog's `account` identifier scope and `deployment-scoped-account-pseudonym` mode because record names are not documented as globally unique.
The complete provider-scope pair therefore contains a stable deployment-governed account pseudonym, never a value inferred from the record key.

## Dependencies and terminology notices

The generated tables identify this guide's package dependencies and the notices for terminology used by its artifacts and examples.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
