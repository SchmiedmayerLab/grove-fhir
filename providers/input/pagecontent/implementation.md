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
6. include one `providers-conversion-provenance` whose sole source entity is the
   complete connected-provider source-record Identifier and whose internal UUID targets
   cover every structured and raw output for that source record; and
7. exchange a complete resource graph in a Grove Mobile collection Bundle using
   deterministic `urn:uuid` full URLs for internal references.

`providerAccountIdentifier` is a complete, deployment-scoped pseudonymous Identifier.
A vendor email, account/member id, OAuth subject, or token is prohibited unless an
explicit deployment privacy policy separately authorizes that disclosure; this package
does not. The provider's own record key travels in the identifier value: it is a vendor row key,
not participant data, and the identical value is already public whenever the vendor's own
application writes it into HealthKit or Health Connect.
An opaque native attachment can itself contain sensitive provider fields. Before
emission, the producer therefore requires exactly one explicit caller assertion:
`caller-authorized-opaque-payload` or `verified-sanitized-input`; absent, ambiguous, or
unsupported assertions fail closed. This producer preflight is not encoded as FHIR
consent or authorization. The generic conformance kit validates metadata and byte integrity but does not
claim to inspect opaque payload semantics or secrets. The resulting identifier is business
identity for deduplication and reference resolution, never a credential or authorization
to fetch provider data. The identifier, profile claim, and Attachment hash do not authorize
disclosure; URL access control, consent, minimization, retention, and deletion remain
deployment policy.

`Resource.id` remains optional and repository-assigned. Business identifiers are never copied
into it. ### Conversion and exchange identity

A conversion Provenance and an exchange Bundle record an export event rather than anything read
from the provider, so they are named in the namespace the deployment owns rather than one this
guide owns, and they carry no scheme version from this guide.
The value is the provider code, the durable event sequence and the role, joined by vertical bars:
`withings|1|conversion-provenance` and `withings|1|exchange-bundle`.
`positiveEventSequence` is the durable positive event sequence of the identified event written as a non-zero ASCII digit followed by zero or more ASCII digits; no sign, no leading zero, no other characters.
A byte-identical retry reuses the sequence; changed content allocates a higher value.
One export event produces one conversion and one Bundle, so the two values name the same event and differ only in the role they carry.
Two deployments converting the same provider record agree on every identifier derived from that record and are expected to differ on these.
The published vectors in [`catalog/providers-adapter.json`](https://grovealliance.org/fhir/catalog/providers-adapter.json) are normative.

Business identifiers are not copied into `Resource.id`. Implementations validate their own emitted
resources with the generic producer kit under `Scripts/validate-producer.py`; this
repository does not run consumer implementations.

Canonical URLs identify artifacts. They do not promise that Grove hosts a package or a
FHIR endpoint at the canonical origin.

## Dependencies and terminology notices

The generated tables identify this guide's package dependencies and the notices for terminology used by its artifacts and examples.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
