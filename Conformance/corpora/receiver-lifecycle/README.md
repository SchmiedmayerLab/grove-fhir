<!--
SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
SPDX-License-Identifier: MIT
-->

# Receiver Lifecycle Sequences

These synthetic sequences exercise a declared receiver policy against grove-fhir 0.6.0.
They do not add a Bundle field, endpoint, receipt code, storage engine or universal disclosure policy to the IG.
`events.json` pins the contract and exact fixture bytes. `sequences.json` covers nine single-output lifecycle sequences; `revision-sequences.json` adds thirty-five complete-revision and ordering-conflict sequences.
`identity-sequences.json` adds two arrival orders for a contradictory source-record claim under the same output identity.

The events are derived from the existing Mobile exchange bases using the reference identity algorithms.
Run `python3 -B -m Scripts.receiver_lifecycle_fixtures --check` to detect drift; omit `--check` to regenerate only this corpus's generated files.
The retraction is the unchanged pinned example. Its complete target Identifier addresses the output in `original`, even when that event has not arrived.
The lock distinguishes the base source/catalog from this corpus's catalog, whose only additions are reproducible identity test vectors.

## Receiver Harness

Start each sequence with empty durable state and one verified participant/source binding.
Independently authorize purpose-a for the named output versions; purpose-b must never gain access.
After each delivery, compare every `expect` field and assert purpose-b remains empty.
An alias in `retracted` identifies the complete source-output Identifier, not an event-specific FHIR `id` or fullUrl.
The correction/retraction sequences exercise both arrival orders and restored replay.
The `original` tombstone also suppresses `corrected`, which has the same logical output
identity but a distinct event and writer version. Both immutable versions remain in history.
`current` is source-version selection, not disclosure: a selected version can still be pending.

Run each complete sequence again against the retained state, including after restarting the receiver.
The second pass must leave its final history, versions, selection, references and visibility unchanged and make no new access available.
State expectations on the first pass are not intermediate expectations for this replay pass.

`restored-producer` means another authenticated transport instance replaying the original immutable event under a verified restoration of the same source binding.
It does not remint the event's producer UUID, prove source ownership, or authorize an unrelated installation.
Test rejection of a foreign subject/source binding separately in the receiver's authentication suite.

## Ordering and References

The correction has writer version `9007199254740993`, greater than the original's `9007199254740992`, but a lower producer sequence and earlier `issued`.
Both versions exceed the range in which adjacent integers are exactly representable as JavaScript Numbers.
Compare canonical decimal text without rounding, scoped to the complete writer-record Identifier pair.
The correction retains its source-output Identifier and fullUrl; neither alone identifies an immutable payload version. Preserve its distinct event and payload history.
The two unordered fixtures deliberately lack writer identity/version evidence; their sequence numbers must not silently resolve their conflict.

The pending event uses a logical QuestionnaireResponse reference.
The later target event carries that exact response and a distinct source record/output, so resolution cannot accidentally depend on replacing the referring event.
The harness must resolve under verified subject/source scope; matching an Identifier from another participant is not sufficient.

## Validation Boundaries

The structural producer validator checks the sixteen graphs, identities, source-neutral semantic profile claims and closed references.
The all-fixtures manifest sends every generated Bundle through the official FHIR Validator with the exact Mobile and Questionnaire packages.
The changed-content retry is intentionally profile-valid: only receiver history can identify its conflict.

The corpus consistency tests verify fixture bytes and expected-state invariants, not a production receiver.
A receiver implementation must consume the sequences and prove its own persistence, authorization and restart behavior.
Retraction is not physical erasure, and no sequence authorizes deletion of retained evidence.

## Output-to-Record Binding

`multi-v2` and `changed-source-record` claim the same complete output Identifier under different complete source-record Identifiers.
Both graphs agree with their own Provenance, and the second has a higher writer version.
Standalone validation cannot recover the producer's secret HMAC preimage or detect a contradiction with previously received history.

This receiver policy binds an output to its source record in the first accepted event transaction.
A later contradictory event is rejected without receipt, custody or grants; it does not replace the binding, hide the accepted event or enter ordinary revision selection.
Both first-arrival orders are intentional: this preserves the first authenticated claim, not proof of its clinical correctness.
An identity correction must use the correctly derived new output identity, without rewriting retained history or bypassing independent authorization.

The first binding may come from an active event or a retraction assertion. The two cross-kind sequences reuse the same validated Bundles: a retraction first rejects the contradictory active claim and suppresses the later matching target; the contradictory active claim first causes the retraction to be rejected without suppressing accepted data.

Each sequence repeats accepted and rejected submissions. `bindingEvent` names the first accepted claiming event, which need not contain an Observation. `current` and `grants` name exact active-event Observations; `retractionEvents` records accepted restrictive assertions in the cross-kind cases. A later matching target can have a retained grant but no current disclosure because of its earlier retraction. `receiptEvent` identifies the particular accepted/replayed event, not always the binding event, and is null for a rejection.
Purpose-b remains unauthorized. A receiver harness must also interleave concurrent first claims and interrupt the transaction: at most one contradictory claim may commit, and a failed transaction must not reserve the binding.
Replay after restart preserves the accepted binding and rejected outcome. This is a declared contextual admission policy, not a new FHIR profile constraint.

## Complete Source-Record Revisions

The revision corpus addresses an output by an alias resolving to both its event and entry fullUrl.
The same fullUrl can recur in several events; it does not identify an immutable version alone.
`history` and `conflicts` contain event aliases, while `versions`, `current`, `visible` and `newlyVisible` contain output aliases.
`conflicts` retains historical conflict evidence; it is not a boolean that blocks every later comparable revision.
`authorizedOutputs` grants only the listed exact versions to the named purpose, independently of selection.
These fixtures use a current-only view; they do not prescribe historical export policy.

`multi-v1` contains two readings from one source record. `multi-v2` contains only the primary reading, and `multi-v3` contains both again.
Comparable writer versions select the complete revision, not each output's independent maximum.
Both arrival orders therefore remove the old secondary from current selection while retaining its history.
Its absence from v2 is not a retraction: it may reappear in v3, but the v1 authorization does not grant access to the v3 version.

Distinct events claiming equal writer versions remain unresolved under this conservative receiver policy, including a reassembly whose displayed measurements agree.
Exact event replay proves equality; comparing a few clinical fields or stripping event-scoped metadata does not establish cross-event content equivalence.
Different writer identities and missing comparable writer evidence also leave unresolved candidates; all four conflict cases cover both arrival orders.
No new access is available during these conflicts, and replay cannot resolve them.
This is an explicit fixture policy, not a new normative IG rejection rule or a requirement to discard valid events.

### Higher Revisions After Conflicts

A unique higher complete revision from the same writer can become current without deciding which of two conflicting older events was correct.
For example, v3 supersedes both competing v2 events, but those v2 events and their conflict remain in history.
Only v3's explicitly authorized primary reading becomes visible; its secondary does not inherit v1's grant.
A higher numeric version does not resolve a candidate with a different writer identity or no ordering evidence: those cases still have no current disclosure.

For each of the four conflict candidates, six sequences cover every arrival order of the older, competing and newer events.
Each sequence then replays all three events; final selection, exact grants and conflict history must not change.
This includes receiving v3 before discovering the older conflict, so a late v2 cannot incorrectly revoke v3's current selection.
These are current-view decisions only; historical access to disputed versions needs its own receiver authorization policy.

The tests include a deliberately incorrect per-output maximum selector to show the obsolete-child failure.
That counterexample validates the fixture's purpose, not a production receiver; real storage, concurrency and restart assertions remain the adopting receiver's responsibility.
