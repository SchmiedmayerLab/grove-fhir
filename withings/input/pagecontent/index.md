<!--

This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

-->

The Grove FHIR Withings guide defines the Withings provider-lineage specialization and the semantic profiles for admitted Health Mate elements that no other inventoried source reports.

A measurement reported by two or more connected providers is source-neutral and belongs to the [Grove FHIR Connected Provider Adapter](https://grovealliance.org/fhir/providers), which this guide depends on.
Provider-specific content in this guide is limited to Withings-exclusive values produced by Withings' own algorithms over Withings' own inputs.

Each such value directly claims a Withings-scoped semantic profile rather than a shared one, together with the Withings Observation provider-lineage envelope.
A shared Withings result uses the same envelope but pairs it with the exact shared semantic profile.
Neither claim is inferred from the other.
A vendor score is not comparable across vendors even when two vendors give it the same name, so publishing it under a shared code would assert a comparability that does not exist.
The profile states what the value is and whose algorithm produced it, and asserts nothing further.

Withings rows use the catalog's `account` identifier scope and `deployment-scoped-account-pseudonym` mode because `grpid` is not documented as globally unique.
The complete provider-scope pair therefore contains a stable deployment-governed account pseudonym, even when an observed integer appears globally allocated.

### Implementation resources

The [Withings status matrix](status-matrix.html) lists every inventoried source field, its definitive status, and its admitted representation.
The shared [provider mapping](https://grovealliance.org/fhir/providers/mapping.html) and [implementation](https://grovealliance.org/fhir/providers/implementation.html) pages define the common conversion and exchange rules.
The [Withings blood-pressure walkthrough](https://grovealliance.org/fhir/providers/walkthrough.html) demonstrates an atomic grouped mapping from provider JSON to the emitted FHIR graph.

### Dependencies and terminology notices

The tables below list this guide's package dependencies and the notices for terminology used by its artifacts and examples.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
