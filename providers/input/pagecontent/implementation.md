<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Pass already-obtained provider records into a mapper that consumes the exact contract in
[`catalog/providers-adapter.json`](https://grovealliance.org/fhir/catalog/providers-adapter.json). Provider API clients, credentials, token refresh,
subscriptions, and network retries belong to the calling application and are outside this
package.

A producer must:

1. match an exact provider/source token and element in the closed catalog;
2. fail closed unless its status admits the listed output;
3. normalize units without changing the source interval or inventing an instant;
4. assign complete source and output business identifiers;
5. declare exactly the catalogued profile pair for a shared Observation or native Recording Document; and
6. include one `provider-conversion-provenance` whose sole source entity is the
   complete connected-provider source-record Identifier and whose internal UUID targets
   cover every structured and raw output for that source record; and
7. exchange a complete resource graph in a Grove Mobile collection Bundle using
   deterministic `urn:uuid` full URLs for internal references.

`providerAccountIdentifier` is a complete, deployment-scoped pseudonymous Identifier.
A vendor email, account/member id, OAuth subject, or token is prohibited unless an
explicit deployment privacy policy separately authorizes that disclosure; this package
does not. The exact `sourceNativeId` and provider-account pair are digest inputs only and
must not appear in FHIR metadata, identifiers, URLs, titles, displays, or Provenance text.
An opaque native attachment can itself contain sensitive provider fields. Before
emission, the producer therefore requires exactly one explicit caller assertion:
`caller-authorized-opaque-payload` or `verified-sanitized-input`; absent, ambiguous, or
unsupported assertions fail closed. This producer preflight is not encoded as FHIR
consent or authorization. The generic conformance kit validates metadata and byte integrity but does not
claim to inspect opaque payload semantics or secrets. The resulting digest is business
identity for deduplication and reference resolution, never a credential or authorization
to fetch provider data. The digest, profile claim, and Attachment hash do not authorize
disclosure; URL access control, consent, minimization, retention, and deletion remain
deployment policy.

`Resource.id` remains optional and repository-assigned. Provider-native keys and derived
### Conversion and exchange identity

The conversion and exchange identifier values are v1 digests over one flat RFC 8785/JCS string array.
Collect the source-record Identifier pairs in scope: for a conversion identifier, the sole `entity.what` Identifier of that conversion Provenance; for an exchange identifier, every distinct source-record Identifier carried by the Bundle's provider conversion Provenance source entities.
Serialize each pair as the canonical two-string array `["<system>","<value>"]` and sort the pairs by unsigned lexicographic UTF-8 byte order of those serializations; duplicate pairs are rejected.
The preimage is the canonical serialization of one flat string array holding, in sorted pair order, each pair's system then value, followed by exactly one trailing `positiveEventSequence` element.
`positiveEventSequence` is the durable positive event sequence of the identified event written as a non-zero ASCII digit followed by zero or more ASCII digits; no sign, no leading zero, no other characters.
A byte-identical retry reuses the sequence; changed content allocates a higher value.
When the Bundle carries exactly one conversion event, the exchange event is that conversion's emission and reuses its sequence; the exchange value then equals the conversion value byte for byte, and only the NamingSystem distinguishes them.
The identifier value is `v1:` followed by the lowercase hexadecimal SHA-256 of the UTF-8 bytes of the preimage, encoded without a byte-order mark.
The published conversion and exchange vectors in [`catalog/providers-adapter.json`](https://grovealliance.org/fhir/catalog/providers-adapter.json) are normative.

digests are not copied into `Resource.id`. Implementations validate their own emitted
resources with the generic producer kit under `Scripts/validate-producer.py`; this
repository does not run consumer implementations.

Canonical URLs identify artifacts. They do not promise that Grove hosts a package or a
FHIR endpoint at the canonical origin.
