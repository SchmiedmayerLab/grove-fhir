<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Health Connect change-token handling is application code, not a FHIR transport protocol.
This page defines only the producer-owned durability boundary needed to avoid losing source
changes while converting already-read Records.

### Durable producer state

Keep a durable synchronization scope for one Health Connect repository, Record class,
source filter, retained time range, and conversion-contract version. Persist its opaque
repository scope, change token, and a ledger keyed by the raw Record id. The ledger retains
the derived source identifier and every output identifier previously produced for that
Record. Raw ids, tokens, filter fingerprints, and repository scope are local operational
state; they are never copied into FHIR resources except through the derived identifiers
defined by `catalog/health-connect-identity.json`.

When a Record maps to several Observations, derive the complete replacement set before
publishing it. An update can add, retain, or remove output identifiers. A deletion resolves
the prior set from the ledger because Health Connect supplies only the deleted Record id.
The exchange representation of a retraction is defined by the shared contract: publish the prior output set as `entered-in-error` stubs with no conversion Provenance, as described under "Retracting an entered-in-error record" on the implementation page.
Receiver projection and storage lifecycle remain deployment policy.

### Token advancement boundary

For each change page:

1. Convert every already-read upsertion and resolve every deletion against the ledger.
2. Persist the new ledger state and any caller-owned durable outbox item atomically.
3. Advance the change token only after that local transaction is durable.
4. Retire an outbox item only after the caller-selected sink acknowledges it.

A retry reuses the same source and output identifiers. If the caller assigns a durable
positive `eventSequence`, preserve it for byte-identical retries and allocate a higher value
for a new source event. The identity catalog uses that sequence to derive conversion and
exchange business identifiers; it does not prescribe an external message format.

### New or expired tokens

When no token exists, or a token expires, establish a fresh token boundary, perform a full
read for the documented retained range, reconcile it with the ledger, and then drain every
change page from that boundary. Persist the final token only after reconciliation and replay
are durable. Reusing a token with a different Record class, filter, range, or contract
version is invalid.

The calling Android application owns Health Connect permissions, Record fetching,
pagination, scheduling, and its retention guarantee. A Grove mapping library accepts typed
Records or normalized inputs and emits FHIR; it does not call Health Connect APIs.

### Explicit non-goals

Version 0.2.0 defines no receiver, authenticated intake, tenant partition, Firebase or cloud
storage model, Bundle byte or count limit, replay endpoint, transport acknowledgement
schema, or downstream merge behavior. Those policies may wrap a conformant Bundle without
changing its FHIR identities or profile claims.
