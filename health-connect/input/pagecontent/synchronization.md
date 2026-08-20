<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

FHIR conversion and Health Connect synchronization are one consistency problem. The
converter must retain enough state to replace every output from an updated source Record,
remove every output after a deletion or filter change, and resume without losing changes.

### Scope the synchronization state

A synchronization scope consists of:

- one stable repository scope used by the record-identifier algorithm;
- one Health Connect Record class;
- every DataOrigin filter, collection time range, and client-side predicate; and
- the conversion-contract version.

Persist an explicit fingerprint of that configuration with the token and baseline cursor. A
change to any member creates a new baseline operation; never reuse a token under a different
fingerprint. Keep the exported-output ledger separate, keyed by repository scope, Record
class, and raw Record id, with its current owning fingerprint. A baseline takes exclusive
ownership of that ledger while it reconciles the old projection; concurrent fingerprints
must not publish competing views. Persist the current owning fingerprint for each repository
scope and Record class. Every ownership change, including a return to a previously used
fingerprint, requires a new baseline; a saved token does not prove that its projection still
owns the ledger. Serialize ownership changes with a durable lease or generation and stop and
join the prior collector before the successor can publish. The repository scope remains
stable when filters change so the baseline can tombstone exclusions and a later re-inclusion
produces the same identifiers.

### Keep a conversion journal and durable outbox

Persist one exported-output ledger entry per repository scope, Record class, and raw Record
id. It contains:

- the raw `metadata.id` and Record class for local Health Connect access;
- the derived Health Connect Record Identifier exchanged in FHIR;
- every Health Connect Output Identifier emitted from the source Record;
- the exact source `metadata.lastModifiedTime` as an epoch-nanosecond decimal string;
- the latest positive decimal `eventSequence` when an exchange event exists;
- the exact compact UTF-8 Bundle JSON and its SHA-256 digest while delivery is pending; and
- the configuration fingerprint and conversion-contract version.

The raw id, repository scope, configuration fingerprint, journal, and change token are
operational state, not FHIR data. Do not serialize them as Observation metadata, Provenance
entities, or study facts. The FHIR resources carry only the scoped record identifier.

Persist the journal transition and an outbox entry atomically before advancing a change
token. Deliver the exact stored Bundle bytes from the outbox; a retry must not reserialize or
reconstruct a different payload. A destination acknowledgement retires the outbox entry but
does not define Health Connect source versioning. Pending transitions remain enumerable by
repository scope and Record class until local completion; baseline and expiry recovery must
drain or reconcile them even when the source Record no longer appears in a full read.

### Use explicit replacement and deletion Bundles

Every exchange event carries the exact UTF-8 JSON for one FHIR R4 `collection` Bundle with
an `entry` array and at least one Observation. The boundary accepts at most 16 MiB, 50,000
Observations, and 80,000 distinct complete Observation identifier tokens per Bundle. These
limits prevent unbounded intake without forcing a normal Health Connect Record to be split.
Every active or `entered-in-error` Observation in the Bundle must contain the envelope's
exact complete Health Connect Record Identifier. A missing or different source pair rejects
the whole event; one Bundle cannot mix outputs from different source Records.

An `upsert` Bundle is a complete replacement for one source Record. It contains every active
Observation produced by the new Record and an `entered-in-error` form of every previously
active Observation that is no longer produced. Retained outputs keep their complete
identifiers. A source Record that has no usable outputs creates no active Observation. On
first sight this is a durable active, zero-output journal transition with no Bundle or outbox
event; it is not a deletion, conversion error, or quarantine state. If a prior version had
outputs, its upsert consists of their tombstones.

Preflight both the exact active Bundle and the minimal all-tombstone form that may be needed
to retire it later. If old tombstones and new active outputs each fit the receiver limits but
their combined replacement does not, emit two consecutive durable `upsert` events: first a
tombstone-only complete empty projection, then the complete active projection at a higher
event sequence. Both events must be durable before the source callback completes or its
change token advances, and crash recovery retries their exact stored bytes in order. Mark a
Record `UNSUPPORTED_LIMIT` only when its current active projection or its guaranteed future
tombstone cannot fit individually. This state is durable and operator-visible; a later
baseline or conversion-contract change retries it. A first-seen unsupported Record sends no
event. For a previously published Record, send its preflighted tombstone projection before
the unsupported state becomes current so the receiver never retains stale active output.

A `delete` Bundle contains an `entered-in-error` form of every currently active Observation
for the deleted source Record. A Health Connect deletion supplies no new last-modified time,
so it reuses the journaled source timestamp. Deleting an unknown or already deleted Record
is a durable no-op and does not invent a FHIR resource.

Patient, ResearchStudy, Device, DeviceMetric, Provenance, and other non-Observation entries
are not lifecycle identity records. The receiver preserves and delivers them byte-for-byte
with the Bundle; it does not filter or reserialize them. The newest source head points to the
newest complete Bundle, while prior Bundles remain immutable delivery and audit history. A
downstream sink applies the event sequence as a complete source event and must not merge an
older companion resource back into the current projection. Package validation of a producer
fixture proves profile conformance; this operational receiver does not replace that FHIR
validation.

The operational delivery envelope uses lowercase `upsert` or `delete`, the complete Health
Connect Record Identifier, `sourceVersion`, `eventSequence`, and the exact Bundle JSON.
`sourceVersion` is the Health Connect last-modified instant encoded as canonical decimal
epoch nanoseconds; it is source metadata and need not increase. `eventSequence` is the
synchronizer-owned positive decimal ordering and idempotency key. It increases strictly for
each source Record identity; a producer may allocate it from a wider repository sequence.
A higher sequence is a new event even when the source timestamp is equal or lower. Reusing
a sequence is valid only for an exact byte-for-byte retry of the same operation, source
version, and Bundle. A receiver rejects a lower sequence without changing state and treats
reuse of a sequence with different content as a conflict.

This envelope defines reliable delivery between a producer and receiver; it is not a FHIR
REST interaction or a CapabilityStatement. The Bundle is the exchanged FHIR payload.

### Keep authorization outside pseudonymous identifiers

The Record Identifier digest is not an authorization boundary. Before it invokes the
receiver, an authenticated intake adapter derives one trusted partition Identifier from
server-side account, study, or tenant authorization. Client input must not select or alter
that Identifier. Its `system` is a server-owned, allowlisted NamingSystem URI and its opaque,
stable `value` names the authorized storage scope without concatenating untrusted fields.

The trusted partition and complete Health Connect Record Identifier jointly scope lifecycle
ordering, identifier ownership, immutable payload storage, and downstream delivery. The
partition is trusted operational context: it is not a field in the producer envelope and is
not added to the FHIR Bundle. A downstream sink receives the same trusted context through
its authenticated delivery channel. Equal FHIR identifiers in different trusted partitions
remain operationally independent; within one partition, an Observation identifier cannot be
claimed by two active source Records.

### Process a change page durably

1. Request a page with the token for its exact synchronization scope.
2. For every upsertion, read the complete current Record and derive its complete replacement
   set. For every deletion, resolve all active outputs from the journal.
3. When the transition has active outputs or tombstones, allocate the next event sequence and
   persist the journal transition, exact Bundle bytes, digest, and durable outbox entry
   atomically. A first-ever zero-output Record persists only its local journal state.
4. Continue until every change and every page returned from the token has been processed.
5. In normal active-token processing, persist the returned next token only after the page
   transitions and outbox entries are durable. During baseline recovery, retain the original
   pending boundary as described below. Remote delivery may complete later from the outbox.

Retrying an interrupted page is safe because source and output identifiers are stable and
the journal records the exact event. Never advance a token merely because conversion began,
a Bundle was constructed, or a network request was sent.

Use separate tokens per supported Record class. Every DataOrigin filter, collection range,
and client-side predicate is part of the stored fingerprint. When a new filter excludes a
previously exported Record, baseline reconciliation emits its tombstones. A later filter
that includes it again may reactivate it with the same identifiers and a higher event
sequence.

### Establish or recover a token without a gap

Use the same baseline-and-replay procedure when no token exists and when a token expires:

1. acquire a new token for the exact Record class and DataOrigin scope, and durably store it
   as a pending baseline boundary;
2. reread the complete retained range (or a bounded range whose retention guarantee is
   documented), convert every Record, and reconcile stale journal entries only inside that
   scope;
3. request and durably process every changes page beginning at the pending boundary,
   including changes concurrent with the baseline read;
4. retain the original pending boundary while pages are drained, so a crash replays the
   same range through the idempotent journal; and
5. atomically replace it with the final returned token only after reconciliation and replay
   complete.

If the process stops, resume the same pending baseline rather than requesting a later token.
Persisting a fresh token without the baseline would omit all existing Records; completing a
baseline without draining changes from its boundary would lose concurrent updates.

Android recommends reading and deduplicating the data again after expiry. A bounded recovery
window is valid only when the deployment can prove that its retention and last-successful-read
policy covers every Record that may still exist. A token unused for 30 days can expire, so
background scheduling must not be the only recovery mechanism.

### Source timestamps are not revisions

`metadata.lastModifiedTime` becomes `Observation.issued` and the envelope's `sourceVersion`.
It states when Health Connect reports the source Record was modified; Health Connect does not
guarantee that it is a unique, strictly increasing revision. Ordering, replay detection, and
reactivation therefore use `eventSequence` plus exact payload identity. A receiving FHIR
server may create a `meta.versionId`; the adapter does not copy either source timestamp or
event sequence into that field.

`clientRecordId` and `clientRecordVersion` govern conflict resolution when an application
writes its own data into Health Connect. The highest client record version wins for a given
client record id. Those fields do not replace `metadata.id` in the read-side journal. If the
same application writes and reads Records, keep its write ledger and conversion journal as
distinct concerns.

The official Android [synchronization guide](https://developer.android.com/health-and-fitness/health-connect/sync-data)
defines changes tokens, upsertion and deletion changes, pagination, and token-expiry recovery.
The [write guide](https://developer.android.com/health-and-fitness/health-connect/write-data)
defines client record identity and version conflict behavior.
