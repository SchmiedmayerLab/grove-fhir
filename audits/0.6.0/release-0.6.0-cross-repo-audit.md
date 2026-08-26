# Grove FHIR 0.6.0 cross-repository audit and release blueprint

- Audit date: 2026-08-26
- Scope: Grove FHIR R4 implementation guides and the FHIR-related portions of Grove Swift PR #67, MyHeartCounts Android PR #34, grove-ts PR #47, and MyHeartCounts iOS PR #204.
- Change policy: every prior IG, wire, identity, storage, and language API contract may break.
- Action taken: documentation only. No implementation, PR comment, commit, or remote state was changed.

Repository-specific evidence is in:

- [Grove FHIR IG audit](grove-fhir-ig-audit.md)
- [Grove Swift PR #67 audit](grove-swift-pr67-audit.md)
- [MyHeartCounts Android PR #34 audit](myheartcounts-android-pr34-audit.md)
- [grove-ts PR #47 audit](grove-ts-pr47-audit.md)
- [MyHeartCounts iOS PR #204 audit](myheartcounts-ios-pr204-audit.md)

## Executive verdict

Do not release the current IG worktree or merge the four PRs as the 0.6.0 contract. The overall architecture is promising, and several parts are substantially better than typical early-stage mobile FHIR work, but the repositories do not yet implement one wire protocol.

The central problem is authority: prose, JSON catalogs, NamingSystems, FSH, examples, Python validation, and language code each decide parts of identity, lifecycle, and output shape. This produces resources that may be valid base FHIR while still carrying false source semantics, different stable identifiers, incomplete graphs, or irreproducible payload bytes.

The cleanest breaking release is a re-foundation around:

1. one release manifest;
2. closed, schema-versioned machine catalogs;
3. structured identity and lifecycle contracts;
4. one-source-record-per-event exchange graphs;
5. explicit semantic versus source-preservation output modes;
6. a language-neutral positive/negative corpus; and
7. three named conformance levels: base R4, Grove profile, and Grove producer.

Do not begin by mechanically updating the SDKs to the current dirty catalog. Several current catalog decisions are themselves wrong or unresolved.

## Current release evidence

| Surface | Reviewed revision | Evidence at audit snapshot | Release status |
| --- | --- | --- | --- |
| Grove FHIR IG | `7e6ec8cdd5a1c562a586607c803b53e123edaf52` plus active dirty 0.6 worktree | Pinned `npm test`: 260-test suite green, with 1 skip because HealthKit Publisher output was absent at that instant; other concurrent-build observations had no skip | Green local gate, red semantic/release decisions |
| Grove Swift #67 | `eca40191935c5612ec2660792f01d0195d4cb992` | FHIR Output Conformance and SwiftLint failed; most platform builds passed or were still running | Red |
| MHC Android #34 | `f09c745df627343f4ba51c2c4f3c5f934f589cdb` | All reported checks passed, including official R4 validation | Green CI, red semantics |
| grove-ts #47 | `5a5b225220b7c10cf8ee7f73206cf48b7d529d68` | 434 FHIR tests passed; browser/readiness failed before official validator ran | Red |
| MHC iOS #204 | `2fbc1fa921628e01838406d6237b37acb9cec04a` | App unit/UI builds, SwiftLint, and Periphery failed | Red |

Android's green validator lane is an important warning: it validates the generated resources syntactically, but does not catch that deleted Observations retain their old results, that an instantaneous Health Connect record was reinterpreted as a daily mean, or that source fields were dropped. The 0.6.0 gate must test semantics and graph contracts, not only profile syntax.

The IG row is a pinned observation of a moving dirty worktree, not a release candidate. Its detailed report records the timestamp, SHA-256 fingerprints, and Publisher-output presence at that instant; all release gates must be rerun against one committed manifest and exact package/SDK digests.

The nested Grove Swift checkout also contained an uncommitted post-PR delta. The Swift report fingerprints and audits it separately; its retained-metadata and workout-segment work is not attributed to PR HEAD and does not yet close the corresponding IG/graph findings. The other three nested implementation checkouts were clean at their reviewed heads.

## Decisions that must precede implementation

### D1 — Use a dedicated retraction event, not a universal mutilated resource stub

Recommended target: a profiled retraction `Provenance` inside a profiled Grove retraction exchange Bundle. The contract should:

- give the enclosing Bundle a new durable `Bundle.identifier`; give Provenance only its typed entry node key, and distinguish `Provenance.occurred[x]` activity time, mandatory `Provenance.recorded` recording time, and profiled `Bundle.timestamp` assembly time;
- identify the producer/assembler agent;
- use a Coding from `http://terminology.hl7.org/CodeSystem/v3-DataOperation`: uppercase `DELETE` only when the recorded activity actually removed the target logical/output object, and uppercase `NULLIFY` only for its narrower v3 meaning of treating an Act-like object as though it never existed; otherwise use a reviewed Grove lifecycle code or a separate application operation;
- target the exact prior logical output, revision, or source-derived graph—whichever 0.6.0 explicitly selects—through a typed Reference. A logical `Reference.identifier` must be a complete, indexed pair; an exact revision additionally needs a revision-specific business identifier or version-specific literal reference. Encode output role in the identity discriminator or a profiled extension because it is not a base Reference field;
- optionally identify the source record/version that triggered retraction;
- contain no copied active clinical result; and
- be translated into repository-specific delete/status behavior only at the sink boundary.

FHIR R4 explicitly describes Provenance as tracking activities that create, revise, **delete**, or sign resource versions, and permits unresolvable references when they still identify targets unambiguously ([official R4 Provenance](https://hl7.org/fhir/R4/provenance.html)). This append-only assertion avoids weakening every active Observation profile and avoids pretending `DocumentReference` has `dataAbsentReason`. It is not a delete command: if Grove intends the receiver to perform a future operation, define that application protocol explicitly or use an appropriate operation/Task/transaction design.

Do not retain the current universal rule that copies an output, sets `entered-in-error`, removes its value, and adds root `dataAbsentReason`. It is impossible for required component/SampledData profiles, and `DocumentReference` has no such element. More importantly, a platform deletion does not establish the resource-specific error meaning: for Observation it can concern the result assertion, while `DocumentReference.status = entered-in-error` means the reference was created in error, not necessarily that its underlying document is clinically false. If a repository stores an `entered-in-error` projection, define it per resource and keep it separate from the transport assertion. R4 DocumentReference still requires at least one `content` element in this status, while Grove's profiles impose the stronger payload metadata requirements ([official R4 DocumentReference](https://hl7.org/fhir/R4/documentreference.html)).

The sink contract must say whether logical identifier references are supported and indexed, how ambiguity/version conflicts fail, and whether the event records an already completed output deletion or requests later application behavior.

Required owner: FHIR profiling lead plus backend/storage owner. This is principally a technical decision, but retention/deletion policy needs privacy/legal review.

### D2 — Make source identity opaque by default and deployment-scoped

Recommended target for Health Connect and provider-native identifiers:

- caller supplies a stable deployment identity system and managed key/key identifier;
- input is a typed, domain-separated tuple, never a delimiter-joined free string;
- canonical preimage uses length-framed UTF-8 fields with explicit version and role;
- wire value is `v2:<key-id-key-epoch-or-scope>:<base64url(HMAC-SHA-256(...))>` or an equivalent reviewed keyed construction;
- provider account identity includes both `Identifier.system` and `.value` in the preimage;
- provider code and exact source key-space/source type are always included;
- output identity adds the closed catalog output discriminator; and
- rotation, reinstall, backup, collision, and lost-key behavior are normative.

This prevents the present leakage and cross-provider/account-system collision. It deliberately gives up cross-deployment equality unless key governance explicitly provides it. Independently keyed deployments must use deployment-owned identifier systems or an explicit deployment/key-epoch namespace; 0.6.0 must not silently change an old NamingSystem's algorithm semantics. If Grove instead chooses clear linkable identifiers, that can be interoperable, but every digest/pseudonym/non-exposure claim must be deleted. UUIDv5 `fullUrl` is a deterministic format conversion, not concealment. HMAC minimizes disclosure of source IDs; it does not de-identify a Bundle whose patient references, times, clinical content, and attachments remain sensitive.

Do not use an unkeyed digest of a low-entropy native ID as a privacy claim. Do not serialize raw repository scope, provider account, or native IDs while calling the result opaque.

Required owner: privacy/security owner plus IG identity owner. This genuinely requires a product/privacy decision because it determines cross-deployment linkage.

### D3 — Standardize one source record per exchange event

Recommended target:

- one active collection Bundle represents one source record version and one conversion event;
- it may contain one or many clinical/source-preservation outputs;
- it contains exactly one conversion Provenance;
- `Bundle.identifier` is the sole event business identifier; R4 `Provenance` has no business `identifier` element;
- the event pair is partitioned by a durable producer-instance/deployment scope plus a monotonic positive sequence (or equivalently strong token), not by provider code;
- the Provenance Bundle entry receives a typed event-scoped node key only through a new/redefined Grove entry-key extension, which is used to derive and verify its `fullUrl` and is not described as a Provenance business identifier; the current extension's “complete business identifier” definition cannot simply be reused;
- entries with a selected native business identifier use that complete pair as their entry key; entries without one use typed event-scoped node keys;
- exact retry reuses event identity, activity/recording/assembly times, and payload; changed content/source version receives a new event; and
- removal is a separate retraction event under D1.

This matches the Android outbox and TypeScript/Swift builders, makes partial failure and replay tractable, and eliminates the IG's current “one event covers many records” ambiguity. If batching is needed for transport efficiency, batch already-complete event Bundles outside the FHIR semantic unit rather than redefining event identity. Because R4 collection Bundle invariants prohibit `entry.request`/`entry.response`, it cannot carry standard FHIR DELETE operations. Separately specify atomic application, idempotent upsert, conflict, and retraction behavior at the sink—or use a separate transaction design; entry order does not perform repository operations.

Required owner: IG identity/lifecycle owner. This can be decided technically.

### D4 — Use an explicit output-mode algebra

Every adapter/source row must declare one of:

- `semanticOnly` — reviewed FHIR projection is sufficient;
- `sourceOnly` — no safe semantic projection exists; emit a versioned source-preservation DocumentReference;
- `hybridRequired` — emit both semantic projection and exact/versioned source artifact with explicit relationship; or
- `choice` — only when two representations are genuinely equivalent alternatives, with exact admitted choices.

Likewise, output count must be an executable closed rule such as `exactlyOne`, `zeroOrOne`, `onePerSample`, `onePerStage`, `onePerPresentField`, or a typed graph-specific rule. Delete contradictory strings such as `0..*; one per record`.

This prevents Swift/MHC `.raw` paths from silently omitting mandatory summaries and prevents “supported” from meaning only that some output was produced.

Required owner: adapter/FHIR mapping owners. Source-specific clinical review is needed for each hybrid/semantic decision.

### D5 — Separate source preservation from semantic projection

Exact source bytes belong in a versioned `DocumentReference` contract with exact media type/format, size, R4 `Attachment.hash` semantics, payload admission, source identity, and provenance. A semantic Observation contains only reviewed clinical meaning. Do not preserve arbitrary metadata through a vaguely typed residual extension and call it verbatim.

For HealthKit clinical records:

- retain exact bytes and declared FHIR release as primary source evidence;
- use release-specific format codes for R4 and DSTU2, or reject DSTU2;
- do not decode, mutate, and reserialize issuer-authored FHIR as source preservation;
- link all payloads/attachments in one validated graph; and
- use FHIR R4's `Attachment.hash` as base64 of SHA-1 over the pre-base64 payload bytes only for its specified change-detection field; put stronger integrity evidence in a separately defined element/manifest.

For HealthKit metadata, choose either reviewed typed allowlisting or a versioned opaque canonical source artifact with explicit datatype tags. Delete the current “verbatim” claim until round-trip behavior is specified.

R4 `Attachment.size` counts pre-base64 bytes, is optional in base R4, and is an `unsignedInt` that cannot exceed 2,147,483,647. Current Grove recording/clinical profiles require exact size, so they must reject larger recordings with a stable rule ID or define a segmented payload/manifest contract before advertising arbitrary recording size.

Required owner: HealthKit/SensorKit adapter owners, privacy owner for retained source content.

### D6 — Correct clinical meaning before regenerating

At minimum:

- split point-in-time Health Connect `RestingHeartRateRecord` from any daily/window aggregate; map `record.time` to `effectiveDateTime` and do not invent `daily-mean` ([official Android API](https://developer.android.com/reference/kotlin/androidx/health/connect/client/records/RestingHeartRateRecord));
- map Health Connect mindfulness type and VO2 max measurement method, with explicit policy for title/notes ([MindfulnessSessionRecord](https://developer.android.com/reference/kotlin/androidx/health/connect/client/records/MindfulnessSessionRecord), [Vo2MaxRecord](https://developer.android.com/reference/kotlin/androidx/health/connect/client/records/Vo2MaxRecord));
- decide whether the HealthKit hypertension notification is an admissible source-specific screening/notification event, never a diagnosis;
- stop assigning `activity` to every non-vital provider Observation;
- use UCUM only for Quantity unit `system/code`, never LOINC or an application concept system; and
- require subject and complete business identity on every app-authored Observation.

Required owner: FHIR/clinical terminology reviewer. These decisions cannot be inferred safely from class names.

### D7 — Model Device and application snapshots honestly

A FHIR Device represents an instance. Manufacturer/model/hardware version does not distinguish two physical units. Require an explicitly governed stable per-unit token to claim an instance; otherwise omit the Device or represent only a model/source description without asserting instance equality.

Split:

- application Device identity and application release/build;
- host Device with OS/hardware, linked through `Device.parent`; and
- event-time firmware/software/OS facts, represented without mutating one shared Device across historical imports.

One Device may legitimately fill several Provenance roles. Graph builders must deduplicate the resource and reference it with multiple role relationships instead of rejecting repeated identity.

Required owner: IG modeling and privacy owners.

### D8 — Keep the Questionnaire contract, replace Swift's evaluation shortcuts

The IG/TypeScript exact instrument-response pairing is a strong foundation. The cross-language contract should require:

- exact canonical plus semantic version resolution;
- occurrence/path-aware repeated-item matching, not global `linkId` lookup;
- injected expression evaluator and explicit evaluation evidence where expressions are normative;
- exact `system + code` comparison when a Coding system is specified;
- FHIR temporal comparison by precision and offset, not lexical strings;
- lexical decimal-scale validation before normalization; and
- explicit calendar/time zone/locale in evaluation context.

Required owner: Questionnaire/FHIRPath owner. This can be decided technically, with validation against SDC R4 behavior.

## Target normative architecture

### Layer 1 — Release manifest

One file owns release version, FHIR release, guide package IDs/canonicals, direct dependencies, catalog-schema generation, package graph generation, publication state, source commit, and release artifact names. No current-version literal is handwritten elsewhere.

### Layer 2 — Closed machine catalogs

Every normative catalog has JSON Schema 2020-12, `additionalProperties: false`, a catalog-schema version, typed discriminated variants, exact URI formats, and cross-file reference checks. Normalize adapters under one source-type/output model while retaining adapter-specific typed fields.

Each supported source field receives a disposition:

- mapped to exact FHIR path/extension/source artifact;
- intentionally omitted with reviewed privacy/semantic rationale;
- rejected with stable rule ID; or
- unavailable in the pinned platform baseline.

CI fails when a new platform/source field or source type lacks a disposition.

### Layer 3 — Generated normative projections

Generate from Layers 1–2:

- FSH constraints and profile slices where expressible;
- NamingSystem narrative that exactly describes the algorithm;
- examples and status matrices;
- identity encoders/parsers and output-role enums;
- Swift/Kotlin/TypeScript models/constants;
- Python reference validation tables;
- package dependency graph and installation prose; and
- generated provenance metadata: generator version, release version, schema version, and normalized-input digest.

### Layer 4 — Shared conformance corpus

Publish normative JSON/byte fixtures with stable rule IDs:

- positive and single-mutation negative graphs;
- identity Unicode/collision/role vectors;
- lifecycle/retraction events;
- output-count/representation-mode matrices;
- decimal, date/time, SampledData, CSV, and binary payload boundaries;
- FHIR JSON repeated primitive and extension-only choice cases;
- Questionnaire pair/expression cases; and
- source-field disposition coverage.

The official Validator, Python reference validator, Swift, Kotlin, and TypeScript must consume the same fixtures rather than reimplementing expected behavior independently.

Byte equality is normative for identity preimages/outputs and registered opaque, CSV, or binary payloads. Compare FHIR graphs semantically through a lossless JSON-token representation that preserves decimal lexemes unless Grove deliberately publishes a canonical FHIR JSON serializer; ordinary parsed-object or whole-Bundle byte equality is not a conformance proof.

### Layer 5 — Named conformance levels

1. **FHIR R4:** base resource syntax, datatypes, bindings, core invariants.
2. **Grove profile:** StructureDefinition/cardinality/slicing/FHIRPath and claimed package closure.
3. **Grove producer:** source semantics, deterministic identity/payload, graph closure, event/lifecycle completeness, and source-field disposition.

Every normative requirement names its layer and validator. A Zod/HAPI/Swift model parse is never described as full FHIR conformance; official validation is never described as proof of source semantics.

## Repository disposition

| Repository/PR | Preserve | Replace before 0.6.0 |
| --- | --- | --- |
| Grove FHIR IG | clinical/adapter layering, R4 discipline, terminology pins, generated measurement profiles, negative corpus, profile-claim modes, UUIDv5 entry URLs | universal tombstones, parallel identity authorities, incorrect resting-HR mapping, unschematized catalogs, stale versions/dependency graph, mutable preview publication |
| Grove Swift #67 | Swift 6 value/Sendable direction, catalog-driven conversion, typed source records, common conversion context, ordered batch results | zero-substituting Decimal path, fragmented/unproven CSV canonicalization, permissive binary decoder, caller-supplied format/media mismatch, clinical record gap, raw-mode bypass, omitted workout children, shared Device/version conflation, mutable duplicate projections, questionnaire shortcuts |
| MHC Android #34 | durable atomic outbox, exact payload replay, complete support inventory, defensive HAPI copies, typed sequence/scope values | status-only tombstones, resting-HR fabrication, dropped source fields, false privacy docs, UTF-16 pair rejection, value-only sink keys, monolithic converter |
| grove-ts #47 | immutable Result API, branded boundaries, generated contracts, package/browser/validator lanes, Questionnaire preflight, skipped-invariant manifest | identity leakage/collisions, event contradiction, type/runtime parser mismatch, weak Grove Bundle parser, primitive JSON generator defects, catch-all category, role-identity rejection |
| MHC iOS #204 | exact Grove pin for review, full Bundle use on some HealthKit/structured paths, generated formats/CSV use, explicit payload admission | stale nonbuilding calls, logged-and-skipped failures, standalone mutated resources, proprietary clinical wrapper, nondeterministic PPG, app-local identities/FHIR helpers, unsafe staging deletion, invalid custom Observations |

The detailed per-repository reports are the implementation backlogs. This table is only the dependency-level disposition.

## Implementation sequence and PR slicing

### Phase 0 — Decision records

Record D1–D8, with explicit owner/sign-off. No SDK contract PR should merge against unresolved identity, retraction, or event semantics.

### Phase 1 — IG authority

1. Add release manifest and catalog schemas.
2. Normalize source/output/cardinality/representation models.
3. Rebuild identity and lifecycle machine contracts.
4. Correct clinical mappings and source-field dispositions.
5. Generate FSH/NamingSystems/examples/docs from those contracts.
6. Create shared corpus and clean 0.6.0 packages.

Suggested IG PRs: release/catalog infrastructure; identity/event; lifecycle/retraction; clinical mapping/source preservation; Device/application; conformance corpus; publication.

### Phase 2 — Core SDKs in parallel

- **Swift:** immutable `ExchangeGraph`; generated identity/mode/format types; one canonical decimal/CSV/binary layer; corrected clinical record; Questionnaire evaluator contract.
- **Kotlin:** retain journal/outbox; generated family converters and field dispositions; complete Identifier keys; corrected semantics/Unicode; new retraction event.
- **TypeScript:** generated contract update; strict profile-aware graph parser; R4 primitive generator corrections; provider identity/category/role fixes; independent official-validator lane.

Each SDK PR should be small enough to review by concern. Generated artifacts get a compact manifest/digest rather than relying on line review.

### Phase 3 — Application integrations

- Make MHC iOS upload exactly one validated Grove graph per source event and adopt a durable acknowledged outbox before deleting staging.
- Remove app-local Grove-owned FHIR conversion and identity helpers.
- Publish a separate MHC IG for genuinely app-owned profiles/extensions or omit them from Grove-profiled resources.
- Integrate Kotlin's corrected core from a standalone Grove KT module/package rather than leaving the FHIR contract permanently embedded in the app.

### Phase 4 — Release candidate and publication

Build all seven IG packages and all SDKs from exact tagged sources in clean environments. Run offline deterministic build and separately recorded online terminology validation. Publish only when canonical routes, version directories, package lists, checksums, QA, semantic diff, and non-clobber behavior are real.

## Cross-language acceptance gates

- One manifest/version/digest is reported by IG, Swift, Kotlin, and TypeScript.
- Every normative catalog validates against a closed schema and has no dangling reference.
- Every source type and public source field has an executable status/disposition.
- Identity golden and mutation vectors pass byte-for-byte across Swift, Kotlin, TypeScript, and Python, including valid non-BMP Unicode and invalid isolated surrogate/code-point cases.
- Provider/Health Connect identifiers cannot collide across provider, source type, account system, account, role, or deployment scope under the selected design.
- Every active and retraction graph validates at all three conformance levels.
- Every Bundle has one durable event identifier; each entry key equals the selected resource business identifier where one exists, otherwise a specified typed event-scoped node key; every `fullUrl` is the exact lowercase UUIDv5 derivation.
- Every internal reference resolves exactly once; complete external identifier references are admitted only where the profile says so.
- Every output row satisfies exact count and representation mode.
- Workout sessions preserve every admitted event/activity/statistic with stable child identities, parent links, profile claims, and complete Provenance targets.
- Point, interval, aggregate, and notification meanings cannot be interchanged by adapters.
- Same-model physical units do not merge when per-unit evidence exists; absent evidence follows the selected omit/event-scope policy; event-time firmware/software and source-author application versions remain immutable under out-of-order import and role deduplication.
- Waveform frame count, dimensions, period, and inclusive end agree exactly.
- CSV and binary sidecars produce identical bytes/hashes across languages; unordered inputs are canonically sorted and malformed/noncanonical encodings fail.
- Recordings above the R4 `Attachment.size` maximum follow the selected reject-or-segment contract.
- FHIR JSON primitive null alignment, primitive-only extensions, choice cardinality, empty values, and decimal-losslessness scope are tested.
- Questionnaire repeated occurrences, expressions, Coding systems, temporal precision/offsets, and decimal scale agree across implementations.
- Application upload checkpoints advance only after durable acknowledgement; failures/retractions survive cancellation and restart.
- Official Validator runs independently of unit/browser lanes and validates every positive fixture with exact 0.6.0 packages.
- Negative fixtures fail for one intended stable rule ID without unrelated cascades.
- Clean regeneration creates no diff; no current-version or algorithm prose is handwritten/stale.
- No release artifact or version directory can be overwritten.

## Explicit sign-offs required

| Decision | Required sign-off |
| --- | --- |
| Opaque versus clear source identity; HMAC key scope/rotation/linkage | Privacy/security and backend identity owners |
| Retraction versus deletion retention behavior | FHIR profiling, backend/storage, privacy/legal owners |
| Hypertension notification clinical admissibility | Clinical terminology/FHIR reviewer |
| HealthKit metadata retention and source-payload minimization | HealthKit adapter and privacy owners |
| Physical Device instance evidence and version snapshot | Device modeling and privacy owners |
| Canonical host and immutable release governance | Project/release owner |
| Terminology server/edition evidence | Terminology owner |

Everything else in the audits can proceed as an engineering correction after these decisions are frozen.

## What should not be carried into 0.6.0

- Compatibility shims for old resource-only converter APIs.
- Raw string identity constructors at public boundaries.
- App-specific mutation of Grove-owned profiled resources.
- “Supported” rows without field dispositions and output obligations.
- Universal `entered-in-error + dataAbsentReason` prose.
- Identity claims that call clear values digests or UUIDv5 concealment.
- Generic “activity” category fallback.
- Generic metadata extensions advertised as verbatim without a typed round-trip contract.
- Mutable duplicate resource projections outside their authoritative Bundle.
- Detached upload tasks that delete durable staging before acknowledgement.
- Package/profile conformance claims based only on a language runtime schema.
- A mutable CI preview relabeled as an immutable FHIR release.

## Review limits

This was a source, generated-artifact, PR-head, CI, and authoritative-specification audit. It did not modify or post to any repository. Device/simulator execution was not used as proof where the environment could not run it; those cases are identified in the Swift reports. The IG worktree changed during review, so the IG report records the exact commit plus observed dirty state and treats stale generated outputs as a release-state finding rather than silently normalizing them.

The audit is intentionally limited to FHIR-related elements. It does not assess unrelated UI, networking, Firebase, general application architecture, or language style outside the FHIR conversion, validation, storage, and exchange boundary.
