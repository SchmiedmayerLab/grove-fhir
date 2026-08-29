<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Provider implementations pass already-obtained records to a mapper that consumes the exact contract in [`catalog/providers-adapter.json`](https://grovealliance.org/fhir/catalog/providers-adapter.json). Provider API clients, credentials, token refresh, subscriptions, and network retries belong to the calling application and are outside this package.

A producer must:

1. match an exact provider/source token and element in the closed catalog;
2. fail closed unless its status admits the listed output;
3. normalize units without changing the source interval or inventing an instant;
4. assign complete source and output business identifiers;
5. carry exactly one catalogued provider extension and provider-qualified source-type extension;
6. declare exactly the catalogued semantic-plus-provider profile pair for a structured Observation, or the catalogued Sensor-plus-Provider pair for a native Recording Document;
7. include one `providers-conversion-provenance` whose sole source entity is the complete connected-provider source-record Identifier and whose internal UUID targets cover every structured and raw output for that source record; and
8. exchange a complete resource graph in a Grove Mobile collection Bundle using deterministic `urn:uuid` full URLs for internal references.

### Provider scope and traceability

The provider-scope Identifier pair is a complete identity input.
Account-scoped rows require the catalog mode `deployment-scoped-account-pseudonym`; globally keyed rows require `documented-global-key-space`.
The Grove graph does not disclose either scope pair as a business Identifier.
A vendor email, account/member id, OAuth subject, token, or per-account value for a globally keyed row is not an interchangeable substitute for the catalogued scope.
If a deployment deliberately needs exact upstream traceability, the provider's own record key may additionally appear once as the governed source `Identifier` on the catalog-designated one-to-one primary output.
Its absolute non-Grove system defines the upstream namespace, its value is exact, and its disclosure policy belongs to the deployment.
This optional Identifier neither replaces the mandatory Grove HMAC identities nor belongs on child, artifact, or support nodes.

### Requirements for opaque provider payloads

An opaque native attachment can itself contain sensitive provider fields.
Before emission, the calling application must explicitly state either that the opaque payload is authorized for disclosure as supplied (`caller-authorized-opaque-payload`) or that it has been verified and sanitized (`verified-sanitized-input`).
Exactly one declaration is required; otherwise conversion fails.
These declarations are producer preconditions, not FHIR Consent or authorization records.
Grove format validation verifies required Attachment metadata for every payload and byte integrity for inline content; it does not fetch URL-backed content, inspect opaque payload semantics, or detect secrets.
The resulting identifier is business identity for deduplication and reference resolution, never a credential or authorization to fetch provider data.
The identifier, profile claim, and Attachment hash do not authorize disclosure; URL access control, consent, minimization, retention, and deletion remain deployment policy.

### Conversion and exchange identity

Provider source-record identity is the v0 HMAC over provider code, exact source type, the complete provider-scope Identifier pair, and stable native/import record id.
A documented global provider key space still supplies an explicit scope pair under mode `documented-global-key-space`; it never uses a per-account value.
An account-scoped row uses mode `deployment-scoped-account-pseudonym` and a deployment-governed pseudonymous account pair; scope is never inferred from the shape of an observed key.
If the provider supplies no native key, the connector assigns and persists an opaque import-record key before conversion rather than hashing measured values or serialized content.

Every output has its own `provider-output` identity under the FHIR Identifier role `source-output`.
A native Recording Document also carries a `provider-artifact` identity under the role `source-artifact` for its exact registered format and part.
These provider-specific HMAC kinds cannot alias the adapter-scoped `source-output` and `source-artifact` kinds.
Writer identity is emitted only when the payload supplies a complete writer-application pair and logical writer record id; provider code plus native id is not evidence that two ingestion channels name the same logical record.

The Bundle owns the event Identifier `e0:<producer-instance-uuid>:<positive-sequence>`; Provenance is an event-scoped entry node rather than a second event business identifier.
A byte-identical retry reuses the event identity, times, graph keys, and payload.
New or corrected content receives a new event sequence.
The protocol and language-independent conformance test vectors in [`catalog/exchange-protocol.json`](https://grovealliance.org/fhir/catalog/exchange-protocol.json) are normative.

Business identifiers are not copied into `Resource.id`.
Before exchange, follow the Mobile guide's [validation instructions](https://grovealliance.org/fhir/mobile/implementation.html#validate-a-resource), loading the Mobile, Sensor, Provider, and applicable vendor packages.
Validate emitted resources against their declared Grove profiles and the graph-level identity and reference requirements.

Canonical URLs identify artifacts.
They do not promise that Grove hosts a package or a FHIR endpoint at the canonical origin.

### Dependencies and terminology notices

The tables below list this guide's package dependencies and the notices for terminology used by its artifacts and examples.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
