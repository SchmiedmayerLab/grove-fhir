<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

A SensorKit-facing producer must match an exact source token in the published adapter contract and fail closed unless that row admits the requested representation.

For a source-neutral Observation it declares exactly two direct `meta.profile` values: the listed Sensor profile and `sensorkit-observation`.
For a native payload it declares exactly the Sensor Recording Document and `sensorkit-recording-document`.
Platform-specific on-wrist, device-usage, and visit summaries declare only their exact SensorKit profile, which inherits the adapter envelope.

### Durable source identity

Every output carries one complete SensorKit record business Identifier and one exact source-type extension whose URL and code system are fixed by the published adapter contract.
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

### Recording payload admission

The Recording Document represents exact bytes already supplied by the caller and exposes them either inline or at an immutable, resolvable attachment URL.
Before emission, the calling application must explicitly state either that the opaque payload is authorized for disclosure as supplied (`caller-authorized-opaque-payload`) or that it has been verified and sanitized (`verified-sanitized-input`).
Exactly one declaration is required; otherwise conversion fails.
These declarations are producer preconditions, not FHIR Consent or authorization records.
The mapper does not fetch attachment URLs, semantically reinterpret, sanitize, rewrite, or reserialize SensorKit data.
A conformant producer validates supplied bytes against the declared registry grammar before emission.
Grove format validation checks required Attachment metadata for URL-backed content without retrieving the bytes.
For inline content, it verifies size and hash integrity and, when applicable to the declared format, the generic native-JSON envelope or selected registered CSV grammar.
The CSV checks are structural and lexical; they do not enforce per-column source-domain ranges stated in column meanings.
These checks do not parse the PPG binary grammar, recompute summaries, or establish URL-backed payload integrity, clinical meaning, or authorization.

`native-recording` is strict UTF-8 JSON with an object or array root.
Byte-order marks, duplicate object member names, non-finite numeric values, scalar roots, malformed UTF-8, and malformed JSON are rejected.
Validation checks only this strict envelope; it does not reinterpret, sanitize, rewrite, or reserialize the bytes.
The carrying SensorKit source type supplies the source category and meaning; it does not select a per-stream JSON field schema in this guide, and a generic receiver treats payload members as opaque producer-defined data.

### Structured summaries with native recordings

The document preserves heterogeneous detail omitted from a structured summary.
A structured device-usage result retains only total unlock duration, screen wakes, and unlocks, so a conformant conversion contains both that Observation and the Recording Document in one collection Bundle.
The Observation has exactly one internal UUID `derivedFrom` reference to that document; both carry the same source-record identifier and distinct deterministic output identifiers.

Every SensorKit hybrid graph is bidirectional: the Observation's `derivedFrom` points to the Recording Document, the document's `context.related` points back, and both resources share one source-record identity.
The accelerometer, PPG, and wrist-temperature contracts additionally require caller-supplied acquisition or session bounds in `Observation.effectivePeriod` to contain every instant encoded in the accepted payload.
The same fail-closed containment check applies to a raw-only Recording Document's `context.period` whenever its registered inline payload grammar yields instant bounds; formats without derived bounds retain the producer's exact source-coverage assertion.
For those three registered-schema graphs, every summary count is derived by parsing that same payload; a separate caller-supplied count is never an authoritative input.
Generic `native-recording` links, such as keyboard metrics, define graph coherence without defining a per-stream JSON member schema or a generic summary algorithm.
The machine-readable `graphContract` on each catalog row states the exact resource pair, links, and, where applicable, coverage and derivation rules.

The linked Observation and DocumentReference examples illustrate individual resources rather than a complete exchange Bundle.
The catalog's `graphContract` defines the required resource pair, bidirectional references, coverage bounds, and derivation rules.
When those resources are assembled into a Mobile exchange event, every transformation graph includes one `sensorkit-conversion-provenance` for each source-record identifier.
Its sole source entity is that complete SensorKit record Identifier, and its internal UUID targets cover every structured and native output for the record.
A conversion that emits both a device-usage summary and its required native document uses one Provenance with both targets; omitting the raw target is nonconformant.

### Sensitive source context

SensorKit raw, visit, per-application, communication, face, and speech streams can be highly identifying even when participant and account identifiers are pseudonymous.
Profiles, canonicals, business identifiers, and Attachment hashes never grant access, express consent, or authorize disclosure.
The deployment separately governs consent and authorization, access control, pseudonym scope and linkability, data minimization, retention and deletion, and authorization for immutable attachment URLs.
A visit summary preserves a supplied `locationId` in `Observation.focus` as an identifier-only logical Location reference.
Its absolute Identifier system is owned by the deployment or exact source-store scope; the value is source context for recurrence analysis, not a Grove graph key, entry key, or retraction address.
It must not be incidentally copied into logs or object names.
The R4 SHA-1 Attachment hash is change detection only, not a signature, credential, or authorization token.

### Exchange Bundles

When resources are exchanged as a graph, the Mobile collection Bundle contract applies: internal references use deterministic `urn:uuid` full URLs, `Resource.id` remains optional/repository-assigned, and all business identifier pairs are complete.
No receiver capacity, authentication, storage, retention, or transport rule is defined here.

### Retracting a source record

Emit the dedicated Grove Mobile Retraction Bundle when the producer can establish that a prior SensorKit source record is no longer exposed.
Its sole source-record-retracted Provenance targets the exact prior structured outputs, artifacts, and device snapshot by complete typed Identifier pairs and only the target roles allowed by the retraction profile.
Do not copy prior clinical resources or relabel them `entered-in-error`; the receiving deployment defines identifier resolution, repeated and all-or-nothing event handling, retention, and deletion.

### Dependencies and terminology notices

The tables below list this guide's package dependencies and the notices for terminology used by its artifacts and examples.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
