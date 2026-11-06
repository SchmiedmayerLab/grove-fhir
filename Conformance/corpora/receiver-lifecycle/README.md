<!--
SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
SPDX-License-Identifier: MIT
-->

# Receiver Lifecycle Sequences

These synthetic sequences exercise a declared receiver policy against grove-fhir 0.8.0.
They do not add a Bundle field, endpoint, receipt code, storage engine or universal disclosure policy to the IG.
`bundles.json` pins the contract, the exact bytes of the 22 fixture Bundles and the record-version Identifiers of their records. `sequences.json` covers fifteen single-output lifecycle sequences; `revision-sequences.json` adds forty-three complete-revision and version-selection sequences.
`identity-sequences.json` adds two arrival orders for a contradictory source-record claim under the same output identity, one Bundle that mixes an admitted and a rejected record, and two sequences in which a retraction binds nothing.
`source-record-target-retraction-sequences.json` adds five retraction sequences, the fifth a typed retraction that suppresses its whole record.

The fixtures are derived from the existing Mobile exchange bases with the reference identity algorithms and keyed by their record-version Identifiers.
Every record here is the base's `record-heart-001` record, or that record attributed to another source record; the base's second record is dropped.
Run `python3 -B -m Scripts.receiver_lifecycle_fixtures --check` to detect drift; omit `--check` to regenerate only this corpus's generated files, `sequences.json` included.
The retraction is the unchanged pinned example. Its typed target names the output in `original`, and it addresses `original`'s source record, even when no version of it has arrived.
The source-record target retraction is the unchanged pinned source-record target example: its one untyped target repeats the source-record Identifier of `original` and of every other version of `record-heart-001`.
Both pinned retraction Bundles also retract `record-heart-002`, the base's second record, of which no version arrives here.
The lock distinguishes the base source/catalog from this corpus's catalog, which carries the record-centric contract and its reproducible identity test vectors.

## Receiver Harness

Start each sequence with empty durable state and one verified participant/source binding.
Independently authorize purpose-a for the named output versions; purpose-b must never gain access.
After each delivery, compare every `expect` field and assert purpose-b remains empty.
An alias in `retracted` names an output of a retracted source record by its complete source-output Identifier; it names no version: the output's fullUrl is the same in every version, and a version is named by its record-version Identifier.
The correction/retraction sequences exercise both arrival orders and `restored-transport` replay.
The retraction of `record-heart-001` also suppresses `corrected`, another version of the same record with a higher writer version: a retraction suppresses every output of every version of its source record (`versionSelection.retraction`). Both immutable versions remain in history.
`current` is source-version selection, not disclosure: a selected version can still be pending.

Run each complete sequence again against the retained state, including after restarting the receiver.
The second pass must leave its final history, versions, selection, references and visibility unchanged and make no new access available.
State expectations on the first pass are not intermediate expectations for this replay pass.

`restored-transport` means another authenticated transport replaying the same record version, with the same key and the same tokens, under a verified restoration of the same source binding.
It does not prove source ownership or authorize an unrelated installation.
Test rejection of a foreign subject/source binding separately in the receiver's authentication suite.

## Ordering and References

Versions of one source record are selected by `lifecycle.active.versionSelection` in `catalog/exchange-protocol.json`: writer evidence first, then the later `Provenance.recorded`, then the bytewise-greater record-version Identifier.
The correction has writer version `9007199254740993`, greater than the original's `9007199254740992`, and the earlier `Provenance.recorded` (`17:30:01Z` against `17:30:02Z`): writer evidence beats `recorded`, so `corrected` is current in both arrival orders.
Both versions exceed the range in which adjacent integers are exactly representable as JavaScript Numbers.
Compare canonical decimal text without rounding, scoped to the complete writer-record Identifier pair.
The correction retains its source-output Identifier and fullUrl; neither alone identifies an immutable payload version. Its record-version Identifier does.
The two unordered fixtures deliberately lack writer identity/version evidence, so the later `recorded` decides: `unordered-a` (`17:30:05Z`) is current in both arrival orders, never the later arrival.
`reconverted` is `original` converted again at `17:31:02Z`: the same writer evidence, a later `recorded`, and so a new current version.

The pending record uses an identifier-only QuestionnaireResponse reference (decision 7).
A later target record carries that exact response and a distinct source record and output, so resolution cannot accidentally depend on replacing the referring record.
The harness must resolve under verified subject/source scope; matching an Identifier from another participant is not sufficient.

## Validation Boundaries

The structural producer validator checks 21 of the 22 Bundles: their records, keys, source-neutral semantic profile claims and closed references.
`altered-retry` is FHIR-valid but fails `mobile-exchange.record-version-key` under the test key, which a production receiver cannot run, so receivers still detect it only by history; it is therefore not in this corpus's producer manifest.
The all-fixtures manifest sends every generated Bundle through the official FHIR Validator with the exact Mobile and Questionnaire packages.

The corpus consistency tests verify fixture bytes and expected-state invariants, not a production receiver.
A receiver implementation must consume the sequences and prove its own persistence, authorization and restart behavior.
Retraction is not physical erasure, and no sequence authorizes deletion of retained evidence.

## Output-to-Record Binding

`multi-v2` and `changed-source-record` claim the same complete output Identifier under different complete source-record Identifiers.
Both graphs agree with their own Provenance, and the second has a higher writer version.
Standalone validation cannot recover the producer's secret HMAC preimage or detect a contradiction with previously received history.

This receiver policy binds an output to its source record when the first active record version claiming it is accepted.
Admission is per record: a contradictory record is rejected without receipt, custody or grants, and the other records of its Bundle are admitted (`mixed-admission`, which carries the `changed-source-record` record beside the `target` record). A rejected record does not replace the binding, hide the accepted record or enter version selection.
Both first-arrival orders are intentional: this preserves the first authenticated claim, not proof of its clinical correctness.
An identity correction must use the correctly derived new output identity, without rewriting retained history or bypassing independent authorization.

Only an active record version binds; a retraction binds nothing, because it addresses its source record and its targets are informative. In `typed-retraction-binds-no-output` the retraction is accepted and binds nothing, `changed-source-record` is accepted and binds the output to `another-record`, and `multi-v2` is rejected. In `retraction-after-contradictory-claim` the retraction is accepted after `changed-source-record` and suppresses `record-heart-001`, which holds nothing current, so `changed-source-record` stays current.

Each sequence repeats accepted and rejected submissions. `bindingBundle` names the Bundle whose record first bound the output, and is null while nothing binds it. `current` and `grants` name exact active-record Observations by their Bundle aliases, and `mixed-admission.target` names the output of `mixed-admission`'s target record; `retractionBundles` records accepted retractions. `receiptBundle` identifies the particular accepted/replayed Bundle, not always the binding Bundle, and is null for a rejection. `rejectedRecords` names the records a delivery rejected, by the alias of the Bundle that carries each one alone.
Purpose-b remains unauthorized. A receiver harness must also interleave concurrent first claims and interrupt the transaction: at most one contradictory claim may commit, and a failed transaction must not reserve the binding.
Replay after restart preserves the accepted binding and rejected outcome. This is a declared contextual admission policy, not a new FHIR profile constraint.

## Source-Record Target Retraction

`source-record-target-retraction-sequences.json` names each complete source-record Identifier by a record alias, and each output by a Bundle and the fullUrl its conversion Provenance targets.
`history` holds accepted Bundle aliases, `versions`, `current`, `visible` and `newlyVisible` hold output aliases, and `retractedRecords` holds record aliases.
A retraction addresses every output of every accepted record version whose source entity is that record, whether the version is accepted before or after the retraction; a typed target names an output the producer emitted and, like a source-record target, binds nothing.
A retraction that arrives first is accepted, matches nothing, and keeps later versions of its record from becoming current.
Outputs of every other source record stay current, a rejected record is never addressed, and an addressed output keeps its versions and history.
No retraction binds an output, whatever its targets name: in `source-record-target-retraction-binds-no-output`, as in `typed-retraction-binds-no-output` in `identity-sequences.json`, `changed-source-record` is accepted after the retraction and binds the shared output to `another-record`, so the later `multi-v2` claim is rejected.
In `typed-retraction-suppresses-whole-record`, the typed retraction names only the primary output, yet it suppresses `multi-v3.secondary` too, and a version that arrives after it; `typed-retraction-suppresses-whole-record-before-its-version` delivers the retraction first, and `multi-v3.secondary` never becomes current.
Every output version is authorized for purpose-a, so visibility follows current selection; purpose-b stays empty, and replay or rejection leaves the state unchanged.

## Complete Source-Record Revisions

The revision corpus addresses an output by an alias resolving to a record version and an output fullUrl.
The same output fullUrl recurs in every version of its record; it does not identify an immutable version alone.
`history` contains record-version aliases, while `versions`, `current`, `visible` and `newlyVisible` contain output aliases; `recordVersions` gives each alias's record-version Identifier.
`authorizedOutputs` grants only the listed exact versions to the named purpose, independently of selection.
These fixtures use a current-only view; they do not prescribe historical export policy.

`multi-v1` contains two readings from one source record. `multi-v2` contains only the primary reading, and `multi-v3` contains both again.
Comparable writer versions select the complete revision, not each output's independent maximum.
Both arrival orders therefore remove the old secondary from current selection while retaining its history.
Its absence from v2 is not a retraction: it may reappear in v3, but the v1 authorization does not grant access to the v3 version.

Selection follows `versionSelection` (`catalog/exchange-protocol.json`): drop every version that a greater writer version under the same complete writer-record pair beats, then select the latest `Provenance.recorded`, then the bytewise-greater record-version Identifier.
`reformatted-retry` repeats `original`'s tokens in another member order: the same record-version key, so it is the exact retry.
`lexeme-retry` repeats it with `72.0` in place of `72`: a new version with the same writer evidence and `recorded`, which the tie-break orders against `original`, so both arrival orders end on the same version.
`altered-retry` repeats `original`'s key with other tokens and stays a disregarded altered retry.
The writer W revisions are `multi-v1` (`…992`, `17:30:09Z`), `multi-v2` (`…993`, `:08Z`) and `multi-v3` (`…994`, `:07Z`), so writer evidence beats `recorded` throughout.
The five candidates are `equal-version-later-recorded` (`…993`, other content, `:10Z`), `equal-version-reconversion` (`…993`, `multi-v2`'s outputs, `:11Z`), `equal-version-equal-recorded` (`…993`, other content, `17:30:08.000Z`, the same instant as `multi-v2` in another lexeme, so the tie-break decides), `other-writer` (writer W′ `…994`, `:06Z`) and `missing-order` (no writer evidence, `17:30:07.500Z`).

### Selection over three versions

For each candidate, two sequences deliver it after and before `multi-v2`, and six sequences cover every arrival order of the older (`multi-v2`), candidate and newer (`multi-v3`) versions.
Each permutation then replays all three versions; final selection and exact grants must not change.
`multi-v3` supersedes `multi-v2` and every W candidate by writer version; `other-writer` has another writer and an earlier `recorded`, so `multi-v3` stays current.
`missing-order` is the set-rule case: it lies between `multi-v3` and `multi-v2` by `recorded`, has no writer evidence, and becomes current once `multi-v3` has dropped `multi-v2`, so a superseded writer version never returns.
Only explicitly authorized versions become visible; `multi-v3`'s secondary does not inherit `multi-v1`'s grant.
These are current-view decisions only; historical access to superseded versions needs its own receiver authorization policy.

The tests include a deliberately incorrect per-output maximum selector to show the obsolete-child failure.
That counterexample validates the fixture's purpose, not a production receiver; real storage, concurrency and restart assertions remain the adopting receiver's responsibility.
