<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

A SensorKit-facing producer must match an exact source token in the closed machine
catalog and fail closed unless that row admits the requested representation.

For a source-neutral Observation it declares exactly two direct `meta.profile` values:
the listed Sensor profile and `sensorkit-observation`. For a native payload it declares
exactly the Sensor Recording Document and `sensorkit-recording-document`.
Provider-specific on-wrist, device-usage, and visit summaries declare only their exact
SensorKit profile, which inherits the adapter envelope.

Every output carries one complete SensorKit record business Identifier and one exact
source-type extension. Because SensorKit publishes no durable sample identifier, the
SensorKit-facing producer assigns a stable lowercase UUID: re-fetching unchanged content
reuses it, while distinct or changed records use different values. It is not copied into
`Resource.id`, and it does not assert equality across independent producers.

The native Recording Document contains bytes already supplied by the caller, either
inline or through a resolvable attachment URL. Before emission, the producer requires
exactly one explicit caller assertion: `caller-authorized-opaque-payload` or
`verified-sanitized-input`; absent, ambiguous, or unsupported assertions fail closed.
The assertion is producer input and is not encoded as FHIR consent or authorization.
The mapper does not fetch, inspect, sanitize, or serialize SensorKit data. The document preserves heterogeneous detail omitted from a structured
summary. A structured device-usage result retains only total unlock duration, screen
wakes, and unlocks, so a conformant conversion contains both that Observation and the
native Recording Document in one collection Bundle. The Observation has exactly one
internal UUID `derivedFrom` reference to that document; both carry the same source-record
identifier and distinct deterministic output identifiers.

Every transformation graph includes one `sensorkit-conversion-provenance` for each
source-record identifier. Its sole source entity is that complete SensorKit record
Identifier, and its internal UUID targets cover every structured and native output for
the record. A conversion that emits both a device-usage summary and its required native
document uses one Provenance with both targets; omitting the raw target is nonconformant.

SensorKit raw, visit, per-application, communication, face, and speech streams can be
highly identifying even when participant and account identifiers are pseudonymous.
Profiles, canonicals, business identifiers, and Attachment hashes never
grant access, express consent, or authorize disclosure. The deployment separately
governs consent and authorization, access control, pseudonym scope and linkability,
data minimization, retention and deletion, and authorization for immutable attachment
URLs. A visit summary deliberately omits `locationId`; its related native attachment
can still contain that and other sensitive source fields. The R4 SHA-1 Attachment hash
is change detection only, not a signature, credential, or authorization token.

When resources are exchanged as a graph, the Mobile collection Bundle contract applies:
internal references use deterministic `urn:uuid` full URLs, `Resource.id` remains
optional/repository-assigned, and all business identifier pairs are complete. No
receiver capacity, authentication, storage, retention, or transport rule is defined
here.

### Retracting an entered-in-error record

When a previously converted source record is retracted, publish a bundle whose outputs for that source are all `entered-in-error` stubs.
Each stub keeps the profile claims, the normative code, and the complete business identifiers of the output it retracts, sets `status` to `entered-in-error`, and carries `dataAbsentReason` in place of a value.
A bundle whose outputs for a source record are all entered-in-error records a retraction rather than a conversion and carries no conversion Provenance.
The repository conformance validator enforces both directions: a retraction claiming a conversion Provenance and a conversion missing one are each rejected.
