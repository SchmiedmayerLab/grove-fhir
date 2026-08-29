<!--

This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

-->

The Grove FHIR Google Health guide defines the Google Health provider-lineage specialization and any semantic profiles for admitted API elements that no other inventoried source reports.

A measurement reported by two or more connected providers is source-neutral and belongs to the [Grove FHIR Connected Provider Adapter](https://grovealliance.org/fhir/providers), which this guide depends on.
Provider-specific content in this guide is limited to Google Health-exclusive values produced by Google Health's own algorithms over Google Health's own inputs.

Each such value directly claims a Google Health-scoped semantic profile rather than a shared one, together with the Google Health Observation provider-lineage envelope.
A shared Google Health result uses the same envelope but pairs it with the exact shared semantic profile.
Neither claim is inferred from the other.
A vendor score is not comparable across vendors even when two vendors give it the same name, so publishing it under a shared code would assert a comparability that does not exist.
The profile states what the value is and whose algorithm produced it, and asserts nothing further.

Google Health rows use the catalog's `account` identifier scope and `deployment-scoped-account-pseudonym` mode because record names are not documented as globally unique.
The complete provider-scope pair therefore contains a stable deployment-governed account pseudonym, never a value inferred from the record key.

### Implementation resources

The [Google Health status matrix](status-matrix.html) lists every inventoried source field, its definitive status, and its admitted representation.
The shared [provider mapping](https://grovealliance.org/fhir/providers/mapping.html) and [implementation](https://grovealliance.org/fhir/providers/implementation.html) pages define the common conversion, identity, and exchange rules.

### Dependencies and terminology notices

The tables below list this guide's package dependencies and the notices for terminology used by its artifacts and examples.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
