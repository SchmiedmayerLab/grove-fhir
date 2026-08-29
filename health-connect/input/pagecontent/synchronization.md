<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Health Connect change-token handling is application code, not a FHIR transport protocol.
This page defines only the producer-owned durability boundary needed to avoid losing source changes while converting already-read Records.

### Durable producer state

Keep a durable synchronization scope for one Health Connect repository, Record class, source filter, retained time range, and conversion-contract version.
Persist its opaque repository scope, change token, and a ledger keyed by the raw Record id.
The ledger retains the derived source identifier and every output identifier previously produced for that Record.
Change tokens and filter fingerprints remain local operational state.
Grove's mandatory graph identities are the opaque identifiers defined by [`catalog/exchange-protocol.json`](https://grovealliance.org/fhir/catalog/exchange-protocol.json) and the Health Connect adapter binding; they are stable for equality and reconciliation but are not reversible.
When a deployment has an explicit traceability need, the exact raw Record id may additionally appear once as the governed source `Identifier` on the catalog-designated one-to-one primary output.
That optional Identifier uses an absolute, deployment-governed, non-Grove system and never replaces the mandatory graph identity.
It is not copied to child or support resources, entry addressing, retraction keys, arbitrary components, or untyped metadata.

When a Record maps to several Observations, derive the complete replacement set before publishing it.
An update can add, retain, or remove output identifiers.
A deletion resolves the prior set from the ledger because Health Connect supplies only the deleted Record id.
The exchange representation is the dedicated Retraction Bundle: resolve the exact prior target Identifier pairs and roles from the ledger and emit one source-record-retracted Provenance.
Do not copy or mutate the prior clinical resources.
Receiver projection and storage lifecycle remain deployment policy.

### Token advancement boundary

For each change page:

1. Convert every already-read upsertion and resolve every deletion against the ledger.
2. Persist the new ledger state and any caller-owned durable outbox item atomically.
3. Advance the change token only after that local transaction is durable.
4. Retire an outbox item only after the caller-selected sink acknowledges it.

A retry reuses the same source and output identifiers.
If the caller assigns a durable positive `eventSequence`, preserve it for byte-identical retries and allocate a higher value for a new source event.
The exchange protocol uses that sequence in the Bundle's `e2:` event Identifier; it does not prescribe an external message format.

### New or expired tokens

When no token exists, or a token expires, establish a fresh token boundary, perform a full read for the documented retained range, reconcile it with the ledger, and then drain every change page from that boundary.
Persist the final token only after reconciliation and replay are durable.
Reusing a token with a different Record class, filter, range, or contract version is invalid.

The calling Android application owns Health Connect permissions, Record fetching, pagination, scheduling, and its retention guarantee.
A Grove mapping library accepts typed Records or normalized inputs and emits FHIR; it does not call Health Connect APIs.

### Explicit non-goals

Version 0.6.0 defines no receiver, authenticated intake, tenant partition, Firebase or cloud storage model, Bundle byte or count limit, replay endpoint, transport acknowledgement schema, or downstream merge behavior.
Those policies may wrap a conformant Bundle without changing its FHIR identities or profile claims.
