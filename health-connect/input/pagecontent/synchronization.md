<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Health Connect change tokens are application state, not part of FHIR transport.
The following durability rules prevent source changes from being lost while already-read Records are converted.

### Durable producer state

Keep a durable synchronization scope for one Health Connect repository, Record class, source filter, retained time range, and conversion-contract marker.
The marker identifies the conversion behavior used for the ledger and is independent of package metadata.
Persist its opaque repository scope, change token, and a ledger keyed by the raw Record id.
The ledger retains the derived source identifier and every output identifier previously produced for that Record.
Change tokens and filter fingerprints remain local operational state.
Grove's mandatory graph identities are the opaque identifiers defined by [`catalog/exchange-protocol.json`](https://grovealliance.org/fhir/catalog/exchange-protocol.json) and the Health Connect adapter binding; they are stable for equality and reconciliation but are not reversible.
When a deployment has an explicit traceability need, the exact raw Record id may additionally appear once as the governed source `Identifier` on the catalog-designated one-to-one primary output.
That optional Identifier uses an absolute, deployment-governed, non-Grove system and never replaces the mandatory graph identity.
It is not copied to child or support resources, entry addressing, retraction keys, arbitrary components, or untyped metadata.

When a Record maps to several Observations, derive the complete replacement set before publishing it.
An update can add, retain, or remove output identifiers.
A deletion supplies only the deleted Record id, and that is enough: the retraction addresses the deleted Record's whole source record, whose `source-record` Identifier derives from that id.
The exchange representation is one source-record-retracted Provenance in a Retraction Bundle; its source-record target needs no ledger, and typed targets, when the ledger names the prior outputs, are informative.
Do not copy or mutate the prior clinical resources.
Receiver projection and storage lifecycle remain deployment policy.

### When to advance the change token

For each change page:

1. Convert every created or updated Record already read from Health Connect and resolve every deletion against the ledger.
2. Persist the new ledger state and any caller-owned durable outbox item atomically.
3. Advance the change token only after that local transaction is durable.
4. Retire an outbox item only after the caller-selected sink acknowledges it.

A retry reuses the same source and output identifiers.
An exact retry repeats each record's record-version key and content, in whatever Bundle the caller packs it; a changed Record, or one converted again with a new `Provenance.recorded`, is a new version of its source record.
The exchange protocol does not prescribe an external message format.

### New or expired tokens

When no token exists, or a token expires, establish a fresh token boundary, perform a full read for the documented retained range, reconcile it with the ledger, and then drain every change page from that boundary.
Persist the final token only after reconciliation and replay are durable.
Reusing a token with a different Record class, filter, range, or contract marker is invalid.

The calling Android application owns Health Connect permissions, Record fetching, pagination, scheduling, and its retention guarantee.
A Grove mapping library accepts typed Records or normalized inputs and emits FHIR; it does not call Health Connect APIs.

### Scope boundaries

The Grove FHIR contracts define no receiver, authenticated intake, tenant partition, cloud storage model, Bundle byte or count limit, replay endpoint, transport acknowledgement schema, or downstream merge behavior.
Those policies may wrap a conformant Bundle without changing its FHIR identities or profile claims.
