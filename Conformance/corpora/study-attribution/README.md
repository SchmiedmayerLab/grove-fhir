<!--
SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
SPDX-License-Identifier: MIT
-->

# Multi-Study Attribution and Protocol History

`source-event.json` contains one record, one Observation and its conversion Provenance, with study A's revision-1 context.
Its PlanDefinition, ResearchStudy and ResearchSubject are shared nodes keyed by their content: each carries a `context-snapshot` Identifier minted over its complete content, so a protocol revision gives a new snapshot and never mutates the node another record references.
`repository-b.json` supplies B's revision-3 context later, outside that immutable record version.
`history.json` specifies one stored record version and source payload, two independent exact-version grants, publication of A revision 2, withdrawal from A, and restart/replay without renewed A access.
These are expectations for a receiver harness, not an implementation of storage or authorization.

`context-two-studies.json` separately demonstrates a valid Mobile exchange Bundle whose producer already knows both study contexts.
Its record has a different record version, because the Observation references both studies, and it is an alternative producer example, not a second delivery in the late-attribution sequence.
The current Mobile profile already admits the connected ResearchStudy, ResearchSubject and PlanDefinition entries; no new profile or extension is required.

## Harness Inputs and Assertions

Start with a verified participant/source binding and no accepted record versions or grants.
For every step, assert the counts and permissions in `history.json`, retain the exact bytes/digest and the record-version Identifier in `event-lock.json`, and bind grants to its Observation version rather than a mutable “latest output.”
`authority.json` supplies explicit synthetic server-owned consent receipts and a verified source binding, separately from both Bundles; the binding names the participant and the source-record NamingSystem of the source's records.
Each grant names its exact consent receipt, enrollment, protocol URL/version, participant and source binding.
The receipt's half-open collection interval must include the Observation's point-in-time measurement; consent must already have been accepted at that instant.
Study B's association is late, but its consent and collection authority predate this sample.
This example does not impose an upload deadline or generalize point samples to interval/correction semantics.
These harness records are never trusted assertions from an uploaded Bundle and introduce no FHIR Consent profile or wire-format fields.
The repository Study B input must match the verified participant before it can contribute an association.
The illustrated withdrawal policy denies A's current export; it does not delete B's custody or invent a universal retention rule.
`activeGrants` lists present access. `retainedGrantDecisions` preserves the original exact-version decisions; A becomes `revoked` at withdrawal while B remains `active`.
The original A receipt, source bytes and decision remain historical evidence. Neither a new grant attempt nor exact source replay may reactivate A after withdrawal.
Collection eligibility is a historical prerequisite, not a replacement for the current enrollment/withdrawal check.

`export-a.json` and `export-b.json` are authorized, derived repository collections.
Each closes its literal references, includes only its study/enrollment/protocol, retains the clinical representation, and carries derivation Provenance with a study-scoped opaque custody identifier.
The receiver maps that identifier to the exact original record version and output internally; it is neither a raw-data URL nor an access capability.
The exports have new identifiers, carry no entry keys and do not claim the Mobile exchange Bundle profile.
Their clinical copies are example export representations, not a requirement to store another clinical payload per study.

## Negative Cases and Validation Layers

`negative-cases.json` uses the existing one-mutation corpus format:

- A canonical string in ResearchStudy.protocol fails the structural Reference-shape rule.
- A different ResearchSubject individual, rekeyed so its content snapshot still recomputes, remains structurally/profile valid but must fail the receiver's verified-subject check.
- Replacing an export's historical protocol version with the latest version remains valid FHIR but violates its exact grant.
- Repeating the source's record-version Identifier on the export's Provenance for filtered export bytes remains valid base FHIR but cannot be accepted as an exact record retry.

`receiver-study.*` labels describe these example harness assertions, not new normative producer diagnostics or HTTP status codes.
All profile-valid counterexamples are included in the official all-fixtures Validator lane, so FHIR validation cannot accidentally become their supposed authorization check.
The fixture tests separately assert the counterexample's relevant identity, revision or retry mismatch.

`authority-negative-cases.json` keeps the FHIR graph unchanged while removing or mismatching B's receipt, protocol revision, participant, source binding or collection window.
Every rejection preserves A's access and decision, creates no B grant/decision and stores no duplicate clinical payload.
The focused tests evaluate these records with a small point-sample predicate and verify the unchanged producer graph still passes structural validation.
They do not establish authenticated database access, transaction isolation or durable replay in a running server; the receiver harness must assert the declared after-state against its own implementation.

Regenerate with `python3 -B -m Scripts.study_attribution_fixtures`, which also writes `negative-cases.json`, whose subject-mismatch patch carries a rekeyed node; add `--check` to detect drift without writes.
The existing producer validator checks both Mobile source shapes, and the all-fixtures lane validates every FHIR resource example with the pinned packages.
The checks demonstrate coherent examples; a consuming receiver must still execute the history against real transactions, permissions and durable restart behavior.
