<!--

This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

-->

The Grove FHIR Oura guide defines the Oura provider-lineage specialization and the semantic profiles for admitted Oura Ring elements that no other inventoried source reports.

A measurement reported by two or more connected providers is source-neutral and belongs to the [Grove FHIR Connected Provider Adapter](https://grovealliance.org/fhir/providers), which this guide depends on.
Provider-specific content in this guide is limited to Oura-exclusive values produced by Oura's own algorithms over Oura's own inputs.

Each such value directly claims an Oura-scoped semantic profile rather than a shared one, together with the Oura Observation provider-lineage envelope.
A shared Oura result uses the same envelope but pairs it with the exact shared semantic profile.
Neither claim is inferred from the other.
A vendor score is not comparable across vendors even when two vendors give it the same name, so publishing it under a shared code would assert a comparability that does not exist.
The profile states what the value is and whose algorithm produced it, and asserts nothing further.

Oura rows use the catalog's `global` identifier scope and `documented-global-key-space` mode: the complete provider-scope pair names the documented global document-id key space and never contains an account pseudonym.
The conformance examples use a deployment-owned test pair for that key space; deployments govern their own stable pair.

### Implementation resources

The [Oura status matrix](status-matrix.html) lists every inventoried source field, its definitive status, and its admitted representation.
The shared [provider mapping](https://grovealliance.org/fhir/providers/mapping.html) and [implementation](https://grovealliance.org/fhir/providers/implementation.html) pages define the common conversion, identity, and exchange rules.

### Dependencies and terminology notices

The tables below list this guide's package dependencies and the notices for terminology used by its artifacts and examples.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
