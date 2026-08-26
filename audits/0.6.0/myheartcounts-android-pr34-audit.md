# MyHeartCounts Android PR #34 FHIR audit

- Audit date: 2026-08-26
- Pull request: [SchmiedmayerLab/MyHeartCounts-Android#34](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/pull/34)
- Head branch: `feature/health-connect-fhir-v020`
- Reviewed head: [`f09c745df627343f4ba51c2c4f3c5f934f589cdb`](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/tree/f09c745df627343f4ba51c2c4f3c5f934f589cdb)
- Base at review time: `9f497387c2306f1835824e103c7e39b762707fb6`
- Nested workspace checkout: `/Users/paulschmiedmayer/Developer/grove-fhir/stack/MyHeartCounts-Android` (clean at the reviewed HEAD)
- Scope: FHIR and Health Connect-to-FHIR behavior only. This is a read-only review; no PR code or comments were changed or posted.

## Executive assessment

PR #34 contains unusually strong foundations: a durable acknowledged outbox, deterministic event sequencing, defensive copies around mutable HAPI resources, explicit support/defer classification, exact graph construction, and an official FHIR R4 validator lane. Its current checks were green at the review snapshot.

It is nevertheless not ready to define Grove FHIR 0.6.0. The most serious issues are semantic rather than syntactic: retractions retain the result being retracted; `RestingHeartRateRecord` is given an invented daily-mean interval; materially significant source fields are silently discarded; and clear-text identity values are documented as digests. Passing the official validator does not detect those contradictions because the IG currently neither expresses nor tests them consistently.

Priority scale: **P0** is a 0.6.0 release blocker; **P1** is a high FHIR, data-integrity, privacy, or interoperability defect; **P2** is a material API/design/maintainability issue; **P3** is release hygiene.

Recommended disposition: retain the outbox architecture, but make the lifecycle and identity decisions in the IG first, regenerate a machine contract, and then refactor the converter against a shared cross-language conformance corpus.

## Selected highest-risk findings

| Priority | Finding | 0.6.0 disposition |
| --- | --- | --- |
| P0 | Retraction Bundles retain clinical values and contradict the IG; the IG's universal tombstone is itself not profile-conformant | Redesign lifecycle across IG and all SDKs |
| P0 | `RestingHeartRateRecord` is incorrectly represented as a daily mean over a zero-duration Period | Correct IG catalog/profile and Kotlin mapping |
| P0 | Source identifiers are emitted in clear text while code and README promise pseudonymous digests | Choose and implement one explicit privacy contract |
| P1 | Mindfulness type/title/notes and VO2 max measurement method are discarded | Add field-level source disposition and mappings |
| P1 | Valid supplementary Unicode characters are rejected as “isolated surrogates” | Use scalar-aware validation and shared vectors |
| P1 | Series identities are unstable under corrections at duplicate timestamps | Redesign per-sample identity or series representation |
| P1 | Acknowledgement and invalidation APIs erase `Identifier.system` | Carry a typed `(system, value)` key end-to-end |
| P1 | Writer identity rejects legal source strings with `|` through unchecked `require` | Replace delimiter composition with framed canonical input |
| P1 | README examples and contract-version claims are stale or contradictory | Generate documentation facts from the contract |
| P2 | One 2,200-line converter suppresses complexity rules | Split by source-record family after contract stabilization |

## Release blockers

### P0 — Retraction output retains the value being retracted

The coordinator's tombstone is only a copied Observation with `status = entered-in-error`:

- [`HealthConnectExportCoordinator.kt`, `invalidatedCopy`](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/blob/f09c745df627343f4ba51c2c4f3c5f934f589cdb/health-fhir/src/main/kotlin/org/grovealliance/health/fhir/HealthConnectExportCoordinator.kt#L381-L389)

Consequently, scalar `value[x]`, components, `hasMember`, device links, and any other clinical result from the active Observation remain in the deletion Bundle. The local tests assert the new status but do not assert removal of the old result. This contradicts the current Health Connect guide, which says a retraction retains identity/profile/code, removes the result, adds `dataAbsentReason`, and omits conversion Provenance ([IG implementation page](../../health-connect/input/pagecontent/implementation.md)).

There is a deeper IG defect: several Grove profiles require `value[x]` or component values and prohibit or cannot carry root `dataAbsentReason`; `DocumentReference` has no `dataAbsentReason` at all. Therefore, simply changing Kotlin to match the prose would make some tombstones violate their claimed profiles. Moreover, a source-platform deletion does not establish the resource-specific `entered-in-error` meaning even if the retained value were removed.

Required 0.6.0 change:

1. Adopt a dedicated profiled lifecycle `Provenance` in a new retraction exchange Bundle. A Health Connect removal triggers the event; use `http://terminology.hl7.org/CodeSystem/v3-DataOperation#DELETE` only if it asserts completed removal of the prior Grove output, and use `#NULLIFY` or `entered-in-error` only when their narrower/resource-specific meanings apply.
2. Target prior logical outputs through typed, complete, indexed `Reference.identifier` pairs; exact revisions need revision-specific identifiers or literal version references, and output role needs a discriminator/extension. Do not copy prior clinical resources or results into the transport event.
3. Implement the selected assertion in the coordinator and document idempotent sink application separately; a collection Bundle has no transaction semantics and the Provenance is not a delete command.
4. Add official-validator-positive fixtures for scalar, component-only, child/member graph, SampledData, hybrid, and DocumentReference-only retractions. Add negative semantic fixtures that retain forbidden results or mix conversion and retraction graphs.

Acceptance criterion: a source deletion cannot be interpreted as either a current clinical result or unsupported evidence of clinical error, and every lifecycle example conforms both to base R4 and to every profile it claims.

### P0 — `RestingHeartRateRecord` is not a daily mean

The converter takes the record's single `time`, creates a zero-duration `Period`, and asserts a Grove `daily-mean` method:

- [`HealthConnectConverter.kt` lines 477–505](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/blob/f09c745df627343f4ba51c2c4f3c5f934f589cdb/health-fhir/src/main/kotlin/org/grovealliance/health/fhir/HealthConnectConverter.kt#L477-L505)

AndroidX Health Connect 1.1 defines each `RestingHeartRateRecord` as one instantaneous measurement with a single time and BPM value, not a daily aggregate. See the [official `RestingHeartRateRecord` reference](https://developer.android.com/reference/kotlin/androidx/health/connect/client/records/RestingHeartRateRecord). The comment in the converter acknowledges that Health Connect supplies no estimation window, but the code fabricates both an interval and aggregation claim.

This originated in the IG measurement catalog, so it is not sufficient to patch Kotlin alone. For 0.6.0:

- represent the Health Connect value with `effectiveDateTime` at `record.time`;
- remove `daily-mean` unless a particular source explicitly supplies that aggregation meaning;
- separate the shared clinical concept “resting heart rate” from source-specific acquisition semantics;
- reassess the Swift/HealthKit route independently because Apple describes its resting-heart-rate samples differently and likewise does not provide a precise daily window in the sample API ([Apple HealthKit reference](https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/restingheartrate)); and
- add a source-semantics test that forbids a Period or aggregate method for Health Connect.

### P0 — Clear identifiers are falsely described as private digests

`HealthConnectSynchronizationScope` calls its output pseudonymous and says it exposes neither input:

- [`HealthConnectSynchronizationScope.kt` lines 54–60](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/blob/f09c745df627343f4ba51c2c4f3c5f934f589cdb/health-fhir/src/main/kotlin/org/grovealliance/health/fhir/HealthConnectSynchronizationScope.kt#L54-L60)

The actual identity helper explicitly performs no hashing or escaping and composes `v1:<repositoryScope>|<RecordClass>|<metadata.id>`:

- [`HealthConnectIdentity.kt` lines 191–202](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/blob/f09c745df627343f4ba51c2c4f3c5f934f589cdb/health-fhir/src/main/kotlin/org/grovealliance/health/fhir/HealthConnectIdentity.kt#L191-L202)

The README also says native IDs and repository scope are inputs to domain-separated digests and never appear on the wire:

- [`health-fhir/README.md` lines 113–123](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/blob/f09c745df627343f4ba51c2c4f3c5f934f589cdb/health-fhir/README.md#L113-L123)

This is a material privacy-description error. UUIDv5-derived Bundle `fullUrl` values are deterministic format conversions, not concealment, particularly because the originating business identifier is included on the resource.

Required decision for 0.6.0:

- If non-disclosure is required, use a versioned, domain-separated, deployment-keyed construction such as HMAC-SHA-256 over unambiguous length-framed UTF-8 components. Define key persistence/rotation, reinstall behavior, collision handling, and cross-language public test vectors. Never serialize the native ID or key/salt.
- If clear interoperability is the goal and a key cannot be governed, retain a clear versioned composition but explicitly document its disclosure and stop calling it a digest or pseudonym.

Do not use an unkeyed hash of a low-entropy native ID and call it private. Make the same choice in the IG, Swift, Kotlin, TypeScript, examples, NamingSystems, and threat model.

## High-priority correctness findings

### P1 — Material Health Connect fields are silently lost

The 1.1 dependency is current stable at the audit date (`androidx.health.connect:connect-client:1.1.0`), which is a good baseline ([AndroidX release notes](https://developer.android.com/jetpack/androidx/releases/health-connect)). However, “supported record type” currently means only that some result is emitted, not that all semantically material fields are represented or explicitly disposed.

Verified examples:

- `MindfulnessSessionRecord`: the converter emits only interval and duration and drops the required session `type` plus optional `title` and `notes` ([converter](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/blob/f09c745df627343f4ba51c2c4f3c5f934f589cdb/health-fhir/src/main/kotlin/org/grovealliance/health/fhir/HealthConnectConverter.kt#L807-L854), [official API](https://developer.android.com/reference/kotlin/androidx/health/connect/client/records/MindfulnessSessionRecord)). Dropping type collapses meditation, breathing, music, movement, unguided, and other sessions into the same meaning.
- `Vo2MaxRecord`: the converter emits the numeric result but drops `measurementMethod` ([converter](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/blob/f09c745df627343f4ba51c2c4f3c5f934f589cdb/health-fhir/src/main/kotlin/org/grovealliance/health/fhir/HealthConnectConverter.kt#L319-L340), [official API](https://developer.android.com/reference/kotlin/androidx/health/connect/client/records/Vo2MaxRecord)). Method materially qualifies comparability of the result.

Required 0.6.0 change:

1. Generate a field-level disposition table from the exact AndroidX API baseline for every supported Record: mapped path, intentionally omitted with rationale, rejected, or unavailable.
2. Make “supported” fail CI when a new public source field has no disposition.
3. Add adapter-specific coded mappings for mindfulness type and VO2 max method. Decide explicitly whether user-authored title/notes are retained, omitted for minimization, or exposed only by deployment policy; never drop them silently.
4. Repeat this audit for all 40 claimed supported types before release, rather than extrapolating from type coverage.

### P1 — Supplementary Unicode scalars are rejected

Both identity implementations reject any UTF-16 code unit for which `Char.isSurrogate()` is true:

- [`GroveExchangeIdentity.kt` lines 45–60](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/blob/f09c745df627343f4ba51c2c4f3c5f934f589cdb/health-fhir/src/main/kotlin/org/grovealliance/health/fhir/GroveExchangeIdentity.kt#L45-L60)
- [`HealthConnectIdentity.kt` lines 195–201](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/blob/f09c745df627343f4ba51c2c4f3c5f934f589cdb/health-fhir/src/main/kotlin/org/grovealliance/health/fhir/HealthConnectIdentity.kt#L195-L201)

A valid supplementary Unicode scalar is encoded in Kotlin as a *paired* high and low surrogate, so this test rejects valid emoji and non-BMP scripts while claiming to reject only isolated surrogates. `GroveCanonicalJson` already contains pair-aware logic and demonstrates the appropriate distinction.

Required change: centralize UTF-8/scalar validation; accept valid pairs and reject only unpaired code units. Add the same BMP, emoji, combining-mark, normalization-sensitive, and isolated-surrogate vectors to Kotlin, Swift, TypeScript, and the IG reference validator.

### P1 — Delimiter composition rejects valid platform values by throwing

Writer record identity is built as `v1:<package>|<clientRecordId>` and uses `require` if either input contains `|`:

- [`HealthConnectConverter.kt` lines 1772–1798](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/blob/f09c745df627343f4ba51c2c4f3c5f934f589cdb/health-fhir/src/main/kotlin/org/grovealliance/health/fhir/HealthConnectConverter.kt#L1772-L1798)

The platform does not make the IG's delimiter restriction part of the source API contract. A source value should not crash conversion through an unchecked precondition merely because it contains the IG's chosen separator.

Required change: use a canonical unambiguous input representation—length framing or JCS array followed by the chosen opaque/clear versioned encoding. Surface any genuinely unsupported record as the module's typed rejection result, not `IllegalArgumentException`. Remove arbitrary delimiter exclusions from source data.

### P1 — Per-sample identity is unstable under corrected duplicate timestamps

Heart-rate and generic series samples are sorted by `(time, value)` and then assigned an occurrence number based on time alone:

- [`convertHeartRate`](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/blob/f09c745df627343f4ba51c2c4f3c5f934f589cdb/health-fhir/src/main/kotlin/org/grovealliance/health/fhir/HealthConnectConverter.kt#L1406-L1433)
- [`convertSeries`](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/blob/f09c745df627343f4ba51c2c4f3c5f934f589cdb/health-fhir/src/main/kotlin/org/grovealliance/health/fhir/HealthConnectConverter.kt#L1600-L1637)

When multiple samples share a timestamp, changing a value can reorder the samples and reassign identities to different clinical results. Health Connect supplies no stable sample identifier that resolves this automatically.

Required decision: either represent the source series as one Observation/SampledData-style result, or define sample identity from the canonical clinical tuple `(source record, exact instant, canonical value, duplicate occurrence)`. With the latter, a corrected value becomes an explicit deletion plus insertion rather than silently taking another sample's identity. Publish collision and correction vectors.

### P1 — Sink APIs discard the identifier system

Comments require observations to be addressed by the exact `(Identifier.system, Identifier.value)` pair, but acknowledgement and invalidation collections use only strings:

- [`HealthConnectExportAcknowledgement.destinationReferences: Map<String, String>`](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/blob/f09c745df627343f4ba51c2c4f3c5f934f589cdb/health-fhir/src/main/kotlin/org/grovealliance/health/fhir/HealthConnectExportCoordinator.kt#L53-L75)
- [`invalidatedOutputIdentifiers: Set<String>`](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/blob/f09c745df627343f4ba51c2c4f3c5f934f589cdb/health-fhir/src/main/kotlin/org/grovealliance/health/fhir/HealthConnectExportCoordinator.kt#L17-L29)
- conversion to `.value` only ([coordinator lines 381–385](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/blob/f09c745df627343f4ba51c2c4f3c5f934f589cdb/health-fhir/src/main/kotlin/org/grovealliance/health/fhir/HealthConnectExportCoordinator.kt#L381-L385))

The current output systems may happen to be closed, but the public contract says the pair is authoritative. Introduce an immutable `IdentifierKey(system, value)` value type and use it in journal state, invalidations, acknowledgements, maps, and sink contracts. Validate absolute/nonblank system and nonblank value once at construction.

### P1 — Event granularity differs from the IG

The PR explicitly defines one sink-acknowledged Bundle/event per Health Connect source record ([`HealthConnectExportBatch`](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/blob/f09c745df627343f4ba51c2c4f3c5f934f589cdb/health-fhir/src/main/kotlin/org/grovealliance/health/fhir/HealthConnectExportCoordinator.kt#L17-L29)). Parts of the IG describe one conversion event as covering many source records. Event sequence identity, retry semantics, and Provenance meaning therefore differ even if every individual resource validates.

For 0.6.0, choose one normative granularity. Per-record events fit this implementation's atomic outbox and correction model well. If selected, update IG prose and golden Bundles accordingly. If batching is required, define ordering, partial failure, event identity, source-entity cardinality, and deletion behavior explicitly.

### P1 — Contract facts and examples are stale

The README and code contain mutually inconsistent facts:

- README and `HealthConnectIdentity` call the contract/IG `0.3.0`, while the reviewed integration is targeting the newer contract ([README](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/blob/f09c745df627343f4ba51c2c4f3c5f934f589cdb/health-fhir/README.md#L13-L15), [identity comment](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/blob/f09c745df627343f4ba51c2c4f3c5f934f589cdb/health-fhir/src/main/kotlin/org/grovealliance/health/fhir/HealthConnectIdentity.kt#L15)).
- The README first says `Observation.issued = convertedAt`, then correctly says it equals `metadata.lastModifiedTime`; code uses `lastModifiedTime` ([README lines 35–38](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/blob/f09c745df627343f4ba51c2c4f3c5f934f589cdb/health-fhir/README.md#L35-L38), [README lines 98–111](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/blob/f09c745df627343f4ba51c2c4f3c5f934f589cdb/health-fhir/README.md#L98-L111), [converter](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/blob/f09c745df627343f4ba51c2c4f3c5f934f589cdb/health-fhir/src/main/kotlin/org/grovealliance/health/fhir/HealthConnectConverter.kt#L1801-L1816)).
- The constructor example omits required `graphIdentifierSystem` ([README example](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/blob/f09c745df627343f4ba51c2c4f3c5f934f589cdb/health-fhir/README.md#L40-L58), [actual context](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/blob/f09c745df627343f4ba51c2c4f3c5f934f589cdb/health-fhir/src/main/kotlin/org/grovealliance/health/fhir/HealthConnectConversionContext.kt#L81-L97)).
- The README describes RFC 8785 input to UUIDv5, while `GroveExchangeIdentity` uses a simple `system + "|" + value` name ([implementation](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/blob/f09c745df627343f4ba51c2c4f3c5f934f589cdb/health-fhir/src/main/kotlin/org/grovealliance/health/fhir/GroveExchangeIdentity.kt#L42-L60)).

Required change: generate the supported-version string, identity algorithm summary, inventory, and runnable examples from the same machine contract/tests used by the converter. Treat documentation tests as a release gate.

## Maintainability and API design

### P2 — Preserve the architecture, split the converter

`HealthConnectConverter` is more than 2,200 lines and suppresses `LargeClass`, `TooManyFunctions`, and cyclomatic-complexity checks at class level. The result makes systematic field auditing and code review unnecessarily difficult.

After the 0.6.0 contract is stable, split it into record-family converters behind one exhaustive registry, for example:

- scalar quantities;
- coded/event observations;
- interval/session records;
- sampled series;
- exercise graph;
- nutrition fan-out;
- specimen-aware glucose; and
- graph/Provenance assembly shared infrastructure.

Generate specs for routine field mappings, but keep clinically meaningful transformations explicit and reviewable. Avoid a generic reflection converter that hides semantics.

### P2 — Return typed conversion outcomes at the public boundary

The coordinator converts several failures to a typed rejection path, which is good. The public `convert` path can still throw `InvalidHealthConnectRecord`, `require`, or `check` failures. A breaking release is an opportunity to expose a sealed outcome such as `Converted`, `Unsupported`, and `Rejected(reason, sourceField)` while reserving exceptions for programmer/configuration defects. This improves collector reliability and lets telemetry distinguish bad source data from a broken deployment graph.

### P2 — Revisit physical Device identity

The current conservative model/manufacturer identity avoids serial-number disclosure, but it can merge two physical units of the same model used by one participant. In FHIR, a `Device` represents an instance, not merely a product model. For 0.6.0, require an explicitly governed stable per-unit pseudonym when instance identity matters; otherwise omit the instance Device or use a clearly record-scoped representation. Do not silently treat manufacturer/model as globally sufficient identity.

## Strengths to retain

- `HealthConnectExportJournal` defines a durable, monotonically increasing producer-wide event sequence and atomically stages the exact payload before delivery ([journal contract](https://github.com/SchmiedmayerLab/MyHeartCounts-Android/blob/f09c745df627343f4ba51c2c4f3c5f934f589cdb/health-fhir/src/main/kotlin/org/grovealliance/health/fhir/HealthConnectExportJournal.kt#L16-L62)).
- The outbox stores exact compact FHIR JSON and verifies its SHA-256 and deep equality before replay. This is a strong idempotency boundary.
- HAPI resources are defensively copied and revalidated around caller callbacks, limiting mutation hazards.
- The support/defer inventory is exhaustive against `RecordType.all`, so an AndroidX inventory change fails closed.
- Source-class lineage, profile claims, Provenance, internal `fullUrl` references, and source/application Device separation are explicit.
- Nanosecond source instants are retained in technical identity even where FHIR clinical timestamps have narrower rounding policy.
- Current CI includes unit, instrumentation, Detekt, documentation, release-build, and official FHIR R4 validation lanes. The problem is corpus coverage and semantics, not lack of engineering discipline.

## Required 0.6.0 work package

1. **Freeze IG decisions first:** lifecycle/retraction representation, clear versus opaque source identity, event granularity, series correction semantics, and Device instance identity.
2. **Generate a Kotlin contract:** exact version, profile canonicals, code systems, source type inventory, output shapes, cardinality meaning, identity algorithms, and per-field dispositions.
3. **Correct source semantics:** begin with RestingHeartRate, MindfulnessSession, and Vo2Max, then complete all 40 supported Record audits.
4. **Change public key types:** carry complete identifiers; remove delimiter-driven source rejection; expose typed conversion outcomes.
5. **Refactor by record family:** only after behavior is fixed and protected by characterization vectors.
6. **Expand the corpus:** share positive and negative JSON/vector fixtures with the IG, Swift, and TypeScript implementations.
7. **Regenerate documentation:** fail CI on version, constructor, algorithm, inventory, or mapping drift.

## Acceptance gates

- Every AndroidX 1.1 public field on every claimed supported Record has a machine-readable disposition and test.
- Official R4 validation passes for every active and lifecycle fixture.
- The IG producer validator and Kotlin preflight accept/reject the same mutation corpus.
- Kotlin, Swift, TypeScript, and Python reproduce byte-identical identity vectors, including non-BMP Unicode.
- A deleted or superseded output contains no active clinical result under a lifecycle profile that promises otherwise.
- One duplicate-time correction suite proves stable, explicit output replacement semantics.
- Sink/journal interfaces never reduce an Identifier to an unqualified value.
- README code examples compile and all version/algorithm claims are generated.
- All existing PR checks remain green after the new semantic corpus is added.

## Review limits

This review examined the exact PR head and current IG worktree, not runtime behavior on a physical Android device. It focused only on FHIR-related code and did not assess general application UI, permissions UX, database performance, or non-FHIR Health Connect collection behavior. The official Android API references and AndroidX release notes were checked on 2026-08-26; pin exact documentation/API artifacts in the eventual release record.
