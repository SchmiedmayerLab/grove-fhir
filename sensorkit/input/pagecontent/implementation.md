<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

A SensorKit-facing producer must match an exact source token in the closed machine catalog and fail closed unless that row admits the requested representation.

For a source-neutral Observation it declares exactly two direct `meta.profile` values: the listed Sensor profile and `sensorkit-observation`.
For a native payload it declares exactly the Sensor Recording Document and `sensorkit-recording-document`.
Platform-specific on-wrist, device-usage, and visit summaries declare only their exact SensorKit profile, which inherits the adapter envelope.

Every output carries one complete SensorKit record business Identifier and one exact source-type extension whose URL and code system are fixed by the machine catalog.
Because SensorKit publishes no durable sample identifier, the producer maintains a durable acquisition ledger per authorized SensorKit stream.
Before conversion it atomically assigns an opaque record key to `[reset generation, monotonic delivery ordinal]`.
The generation changes only for an explicit cursor reset after the prior generation has no unresolved delivery; the ordinal increases across callback batches and never restarts for equal timestamps.
Before yielding records, persist the exact pending start ordinal and count, ordered keys and verification evidence, source bytes, and pre-yield cursor boundary.
The cursor advances only after the whole pending delivery is handed off durably.
Retrying that delivery reuses the same coordinates even if SensorKit splits or combines callback batches differently; a different acquisition receives a different key even when its bytes and source timestamp are identical.

Measured values, serialized-content hashes, and sorting by measured timestamps are prohibited as identity inputs.
Callback order and multiplicity are preserved: no `Set`, payload-based deduplication, or `compactMap` may collapse byte-equal records.
A payload digest may verify retry consistency for an existing coordinate, but a mismatch fails closed and never selects a different identity.
The opaque key is not copied into `Resource.id`, and it does not assert equality across independent producers.

The native Recording Document contains bytes already supplied by the caller, either inline or through a resolvable attachment URL.
Before emission, the producer requires exactly one explicit caller assertion: `caller-authorized-opaque-payload` or `verified-sanitized-input`; absent, ambiguous, or unsupported assertions fail closed.
The assertion is producer input and is not encoded as FHIR consent or authorization.
The mapper does not fetch, inspect, sanitize, or serialize SensorKit data.
The document preserves heterogeneous detail omitted from a structured summary.
A structured device-usage result retains only total unlock duration, screen wakes, and unlocks, so a conformant conversion contains both that Observation and the native Recording Document in one collection Bundle.
The Observation has exactly one internal UUID `derivedFrom` reference to that document; both carry the same source-record identifier and distinct deterministic output identifiers.

Every transformation graph includes one `sensorkit-conversion-provenance` for each source-record identifier.
Its sole source entity is that complete SensorKit record Identifier, and its internal UUID targets cover every structured and native output for the record.
A conversion that emits both a device-usage summary and its required native document uses one Provenance with both targets; omitting the raw target is nonconformant.

SensorKit raw, visit, per-application, communication, face, and speech streams can be highly identifying even when participant and account identifiers are pseudonymous.
Profiles, canonicals, business identifiers, and Attachment hashes never grant access, express consent, or authorize disclosure.
The deployment separately governs consent and authorization, access control, pseudonym scope and linkability, data minimization, retention and deletion, and authorization for immutable attachment URLs.
A visit summary preserves a supplied `locationId` in `Observation.focus` as an identifier-only logical Location reference.
Its absolute Identifier system is owned by the deployment or exact source-store scope; the value is source context for recurrence analysis, not a Grove graph key, entry key, or retraction address.
It must not be incidentally copied into logs or object names.
The R4 SHA-1 Attachment hash is change detection only, not a signature, credential, or authorization token.

When resources are exchanged as a graph, the Mobile collection Bundle contract applies: internal references use deterministic `urn:uuid` full URLs, `Resource.id` remains optional/repository-assigned, and all business identifier pairs are complete.
No receiver capacity, authentication, storage, retention, or transport rule is defined here.

### Retracting a source record

Emit the dedicated Grove Mobile Retraction Bundle when the producer can establish that a prior SensorKit source record is no longer exposed.
Its sole source-record-retracted Provenance targets the exact prior structured outputs, artifacts, and device snapshot by complete typed Identifier pairs and closed roles.
Do not copy prior clinical resources or relabel them `entered-in-error`; receiver lifecycle application is separate sink policy.

## Dependencies and terminology notices

The generated tables identify this guide's package dependencies and the notices for terminology used by its artifacts and examples.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
