# MyHeartCounts iOS PR #204 — FHIR audit for Grove 0.6.0

- Audit date: 2026-08-26
- Pull request: [SchmiedmayerLab/MyHeartCounts-iOS#204](https://github.com/SchmiedmayerLab/MyHeartCounts-iOS/pull/204)
- Head branch: `lukas/grove-fhir-migration`
- PR snapshot: [`2fbc1fa921628e01838406d6237b37acb9cec04a`](https://github.com/SchmiedmayerLab/MyHeartCounts-iOS/tree/2fbc1fa921628e01838406d6237b37acb9cec04a)
- Comparison base: `origin/lukas/grove` at `c2599d4a33fadb4e23685abbde51a5d0fc9b516f`
- Nested workspace checkout: `/Users/paulschmiedmayer/Developer/grove-fhir/stack/MyHeartCounts-iOS` (clean at the reviewed HEAD)
- Grove dependency reviewed at: PR #67 `eca40191935c5612ec2660792f01d0195d4cb992`
- IG/catalog cross-check: `/Users/paulschmiedmayer/Developer/grove-fhir` working tree

All implementation paths below are relative to the linked reviewed commit.

## Verdict

Do not merge this migration yet. The app does adopt the new Grove conversion graph on several important paths, but the exact PR does not compile/test cleanly and some remaining paths discard that graph, silently acknowledge failed conversions, mutate issuer-authored clinical FHIR, or generate semantically incorrect Observations. These are not compatibility concerns; they are data integrity, identity, provenance, and FHIR-conformance defects.

For 0.6.0, delete the app-local parallel FHIR conversion layer where Grove owns the contract. Treat one validated Bundle/graph as the upload unit. Failures and lifecycle state must be durable and retryable, and payload/source identities must use one generated, cross-language, deployment-scoped, domain-separated algorithm.

Severity used below:

- **P0** — 0.6.0 merge/release blocker, including red build/conformance gates or a dependency-contract mismatch.
- **P1** — high FHIR, data-integrity, privacy, or interoperability defect.
- **P2** — material API/design/maintainability issue to address in 0.6.0.
- **P3** — release hygiene.

Labels distinguish **Defect**, **Recommendation**, and **Current-IG drift / decision required**.

## Selected highest-risk findings

| Severity | Type | Finding |
|---|---|---|
| P0 | Defect | Unit/UI targets retain removed Grove API calls and an obsolete output shape; reported app unit/UI builds are red. |
| P0 | Defect | The pinned Grove PR itself has failing conformance/lint checks and is not synchronized with the current IG catalog. |
| P1 | Defect | Batch HealthKit conversion failures are only logged; the exporter can persist an empty/successful artifact and advance past failed source records. |
| P1 | Defect | Raw SensorKit upload extracts and mutates one `DocumentReference`, discarding the Bundle, Devices, Provenance, and graph identity. |
| P1 | Defect | Clinical records are decoded, mutated, re-encoded in a proprietary wrapper, and uploaded separately from unlinked attachments. |
| P1 | Defect | PPG binary bytes are nondeterministic because a `Set` is serialized in iteration order. |
| P1 | Defect | SensorKit source IDs use a collision-prone XOR mixer or truncated SHA-1 with unstable/device-description input rather than the Grove identity contract. |
| P1 | Defect | App-authored Observations omit `subject`, misuse `Identifier.id`, and put LOINC/application concept codes into `Quantity.system/code` instead of UCUM. |
| P1 | Defect | Health staging deletes drained records before its detached upload is acknowledged, allowing irreversible FHIR payload loss. |
| P1 | Defect / contract drift | Raw PPG/accelerometer/wrist paths omit mandatory summary Observations in the current IG. |

## Detailed findings

### MHC-01 — The migration leaves source-incompatible tests/call sites (**P0, Defect**)

Evidence:

- `HealthKitSamplesFHIRUploader` now requires a nonnil `standard` at `MyHeartCounts/Health Import/HealthKitSamplesFHIRUploader.swift:37-44`, but the test constructs it with `standard: nil`: `MyHeartCountsTests/HealthSampleProcessingTests.swift:50`.
- The uploader now encodes `[Bundle]`: `HealthKitSamplesFHIRUploader.swift:45-55`, but the test decodes `[Observation]`: `HealthSampleProcessingTests.swift:53`.
- The test calls removed `resource(withMapping:issuedDate:extensions:)`: `HealthSampleProcessingTests.swift:93`.
- The staging test calls removed `turnIntoFHIRResource(issuedDate:using:)`: `HealthSampleProcessingTests.swift:278-284`; the new API requires `conversionInstant`, `subject`, and `using`: `MyHeartCounts/Health Import/HealthObservation.swift:67-72`.
- No corresponding FHIR test migration is present in the PR. The current PR status supplied to the audit reports app unit and UI build failures, plus lint/periphery failures.

Impact: no green executable evidence supports the migration, and old assertions would not catch the new Bundle semantics even if mechanically made to compile.

Breaking recommendation: rewrite these as graph-contract tests, not compatibility shims. Inject a test standard/subject/clock, decode Bundles, verify entries/profiles/identifiers/references/provenance and official validation, and remove obsolete resource-only helpers.

Acceptance: all app, unit, UI, lint, and periphery jobs pass at the exact PR SHA; no deprecated Grove conversion symbol remains (`rg` gate).

### MHC-02 — Partial HealthKit failures are acknowledged as success (**P1, Defect**)

Evidence:

- Batch failures are only logged and then omitted: `MyHeartCounts/Health Import/HealthKitSamplesFHIRUploader.swift:45-50`.
- The method still writes and returns an artifact even if every input failed: `:50-55`.
- The stated comment at `:45` makes this a policy choice, but there is no durable failure manifest, quarantine, retry state, or caller-visible typed result.

Impact: unsupported/malformed clinical source data can be permanently skipped while the bulk-export checkpoint considers the batch handled. An empty artifact falsely represents successful processing.

Breaking recommendation: return a typed `FHIRBatchUploadOutcome` containing successful graphs and durable addressed failures. Quarantine/retry failures and advance a source checkpoint only after each item is either durably uploaded or explicitly acknowledged under a versioned policy. Return `nil` for a truly empty output and never equate “logged” with “handled.”

Acceptance tests: one success/one failure, all failures, retry after restart, unsupported-by-policy acknowledgement, upload failure, and preservation of source order/UUID/type/error cause.

### MHC-03 — Raw SensorKit upload discards the conversion graph (**P1, Defect**)

Evidence:

- `SensorKitGroveRecording.document` creates a complete `SensorKitConversion`, extracts `recordingDocument`, mutates its period, and returns only that copy: `MyHeartCounts/SensorKit/SensorKitGroveRecording.swift:103-135`.
- The upload path then adds app extensions and persists the standalone `DocumentReference`: `MyHeartCounts/SensorKit/SensorKitDataFetcher+Uploading+Base.swift:46-66`.
- The Bundle, converter Device, recording Device, Provenance, graph identity, and converter-established reference relationships are discarded.

Impact: the uploaded artifact is not a Grove Mobile exchange Bundle and no longer proves who converted/recorded it. Mutating the extracted value does not update the original Bundle.

Breaking recommendation: change the helper to return the complete immutable `SensorKitConversion`/exchange graph. Supply effective period and permitted extensions as converter inputs, or mutate through a validating graph builder, then persist the Bundle only. Grove should remove mutable duplicate projections from its 0.6 API.

Acceptance tests: raw upload contains the required Bundle/profile, both Devices, Provenance, exact recording document, closed internal references, unique fullUrls/identifiers, sidecar hash/size, and the requested period; no standalone DocumentReference upload remains.

### MHC-04 — Clinical records are neither byte-preserved nor Grove-wrapped (**P1, Defect**)

Evidence:

- Clinical FHIR is decoded into a model, app/source-revision extensions are injected, and it is re-encoded: `MyHeartCounts/Health Import/HealthObservation.swift:75-92` and `MyHeartCounts/Utils/FHIR/FHIRResource.swift:141-161`.
- `FHIRResource.encode` emits an app-specific `{ "version": ..., "resource": ... }` wrapper rather than a FHIR resource: `FHIRResource.swift:77-109`.
- Attachments are uploaded under `<record UUID>_<index>` with no returned URL, hash/size update, or manifest/DocumentReference relationship: `HealthKitSamplesFHIRUploader.swift:68-78`.
- The comment claiming records are “passed through” at `HealthObservation.swift:63-66` is false in both byte and semantic terms.
- The current IG requires a profiled clinical `DocumentReference` envelope, explicit FHIR release/format, and exact primary source-payload hash/size. It does not yet normatively define how separately extracted HealthKit attachments are linked; that is an additional 0.6.0 contract gap rather than a current profile violation.

Impact: issuer-authored clinical data changes, clients receive non-FHIR JSON, and attachments cannot be discovered or integrity-checked from the resource graph.

Breaking recommendation: use Grove's corrected clinical-record builder. Retain the exact HealthKit `Data` and release as the primary payload, never mutate issuer bytes, and satisfy the current release/format/hash/size envelope. Separately define a normative 0.6 relationship/manifest for extracted attachments; then upload all sidecars through a service returning durable locations and construct one validated graph with content type, size, the R4 `Attachment.hash` SHA-1 change-detection value, title, and URL. If stronger storage-integrity metadata is required, define it separately rather than changing `Attachment.hash` semantics. Define a separate DSTU2 contract or reject it.

Acceptance tests: byte equality before/after upload, correct digest/size, R4 and DSTU2 policy, linked attachment resolution, failed attachment upload rollback/retry, graph/profile validation, and no proprietary wrapper in FHIR collections.

### MHC-05 — App-created “native” SensorKit payloads do not match a registered native contract (**P1, Defect**)

Evidence:

- Device usage constructs a normalized app-owned `NativeReport` JSON schema: `MyHeartCounts/SensorKit/Sample Types/StructuredRecords.swift:63-117`, then calls it byte-exact/native: `:119-164`.
- It is labeled `.nativeRecording` on upload: `MyHeartCounts/SensorKit/SensorKitDataFetcher+Uploading+Structured.swift:54-71`.
- ECG's “native” sidecar includes only `offsetSeconds` and converted `microvolts`: `MyHeartCounts/SensorKit/SensorKitDataFetcher+Uploading+ECG.swift:55-87`; it omits source session/batch identifiers and states such as invalid-signal/crown-touch where those are part of the registered source representation.

Impact: consumers are told bytes have a registered/native schema when they are actually lossy app projections with no published schema/version.

Breaking recommendation: either encode the exact source representation required by the IG, or register a named, versioned, fully specified MHC-derived format with its own media type and schema. Do not use `native-recording` as a generic escape hatch.

Acceptance tests: schema validation and cross-language golden bytes for each admitted sidecar; mutation of every contract field changes bytes/identity; no undeclared source field is silently dropped.

### MHC-06 — PPG byte output is nondeterministic (**P1, Defect**)

Evidence:

- `PPGSample.OpticalSample` encodes `activePhotodiodeIndexes` as a `Set<Int>`: `MyHeartCountsShared/Sources/MyHeartCountsShared/PPGSample+BinaryCodable.swift:55-82`, specifically `:73`.
- Generic `Set` encoding writes its iteration order directly: `MyHeartCountsShared/Sources/MyHeartCountsShared/BinaryCodable/Primitives.swift:144-148`.
- Swift `Set` iteration order is not a stable serialization contract. Raw-record identity is derived from payload bytes at `SensorKitGroveRecording.swift:73-82`.

Impact: the same source PPG sample may yield different bytes, digests, source IDs, file names, and graph identities across launches.

Breaking recommendation: never provide a generic canonical `Set: BinaryEncodable`. For this field, sort the integer values numerically and specify uniqueness/order in the format registry. More generally, canonical encoders should require an explicit ordering function.

Acceptance tests: encode identical sets inserted in every order, across separate processes and all three language producers, and assert identical bytes/digests/IDs.

### MHC-07 — Sensor source identity algorithms are unsafe and inconsistent (**P1, Defect**)

Evidence:

- `SensorKitSampleIDHasher` is a custom rotating XOR over a 128-bit state: `MyHeartCounts/SensorKit/SensorKitSampleIDHasher.swift:12-87`. XOR is linear/cancellation-prone, and calls have no source-type/domain delimiter.
- It is used for visit/on-wrist/device-usage identities: `MyHeartCounts/SensorKit/Sample Types/StructuredRecords.swift:15-26`, `:41-50`, and `:123-151`, and ECG at `SensorKitDataFetcher+Uploading+ECG.swift:61-77`.
- Raw recording IDs instead truncate an insecure SHA-1 digest and include `device.description`: `SensorKitGroveRecording.swift:73-82`.

Impact: distinct source records can collide or identities can change after an OS description-format change. A collision can overwrite a sidecar/graph or falsely treat changed clinical source data as unchanged.

Breaking recommendation: delete both algorithms and use the selected generated 0.6 identity function. If disclosure minimization is required, use deployment-scoped HMAC-SHA-256 over versioned, domain-separated, length-framed UTF-8 fields with an explicit key epoch and deployment-owned identifier system. Keep unkeyed SHA-256 for content integrity only; preserve R4's required SHA-1 semantics in `Attachment.hash`. Derive UUIDv5/fullUrl only as the separate registered formatting step.

Unicode note: the current Swift string loop processes each grapheme's UTF-8 bytes and therefore accepts supplementary Unicode scalars. Keep UTF-8 scalar-string golden vectors; do not reject valid surrogate pairs as some UTF-16 implementations do.

Acceptance tests: cross-language golden vectors; empty/delimiter/non-BMP inputs; type/domain separation; payload changes; mutation of every represented/source field; stable result across devices/processes; deliberate collision tests against the old XOR cancellation patterns.

### MHC-08 — Recording-device identity does not use the IG composition (**P1, Defect**)

Evidence:

- The context invents an MHC-specific device identifier `productType|name`: `MyHeartCounts/SensorKit/SensorKitGroveRecording.swift:169-197`, especially `:181-189`.
- The current Grove contract defines recording-device identity from subject, adapter, manufacturer, model, hardware version, and the published system/composition.
- A user-editable/nonunique name changes identity; two devices with the same product type/name collide.

Breaking recommendation: do not adopt the current IG composition literally: it can merge two physical units with identical manufacturer/model/version facts. First redesign 0.6 around an explicitly governed per-unit pseudonym when the source exposes stable instance evidence. If no such evidence exists, omit the persistent instance Device or use an explicitly event-scoped representation. Never put a user-editable display name into identity, and consume only the redesigned generated contract.

Acceptance tests: published identity vectors; renaming a device does not change identity; two same-model physical units do not silently merge when instance evidence exists; missing instance evidence follows the selected omit/event-scope rule; delimiter and Unicode values remain unambiguous.

### MHC-09 — Conversion time/context is sampled nondeterministically (**P2, Recommendation**)

Evidence: every SensorKit graph reads `.current`, `.now`, and a second `.now` independently: `MyHeartCounts/SensorKit/SensorKitGroveRecording.swift:190-192`.

Impact: retrying identical data changes issued/recorded values, and the two instants can differ within one conversion.

Breaking recommendation: capture one explicit timezone and one conversion instant at the batch boundary, inject a clock, and pass that immutable context to every record. Decide separately whether `recordedAt` is source time or conversion time.

Acceptance tests: fixed context produces semantically equivalent graphs plus exact registered identity and payload bytes across retries, process time zones, and concurrent execution. Whole-Bundle byte equality is required only if Grove separately defines a canonical FHIR JSON serializer.

### MHC-10 — App-authored Observations omit the patient subject (**P1, Defect**)

Evidence:

- `turnIntoFHIRResource` accepts `subject`, but the self-modeled branch does not pass/apply it: `MyHeartCounts/Health Import/HealthObservation.swift:67-72` and `:100-105`.
- `QuantitySample.resource` never assigns `Observation.subject`: `MyHeartCounts/Heart Health Dashboard/QuantitySample+FHIR.swift:29-89`.
- `TimedWalkingTestResult.fhirObservation` also never assigns it: `MyHeartCounts/Task Handling/Active Tasks/Timed Walk Test/TimedWalkingTestResult+FHIR.swift:28-86`.

Impact: clinical observations are not attributable to the patient and will fail profiles requiring a subject.

Breaking recommendation: make subject a required constructor argument in every strict Observation builder and validate it is a typed Patient reference in the exchange graph.

Acceptance tests: every custom Observation has exactly the expected subject; missing/wrong reference fails before upload; reference closure succeeds in its Bundle.

### MHC-11 — Resource and business identifiers are conflated (**P1, Defect**)

Evidence:

- Both custom builders copy the app UUID into `Observation.id` and construct `Identifier(id: observation.id)`: `QuantitySample+FHIR.swift:38-40`; `TimedWalkingTestResult+FHIR.swift:37-39`.
- `Identifier.id` is the element's internal `id`, not `Identifier.value`; the business identifier therefore has neither `system` nor `value`.

Impact: the intended source identity is absent and repository/resource identity is incorrectly asserted as a FHIR logical id.

Breaking recommendation: use a complete generated `BusinessIdentifier(system:value:)` for the source record and let the exchange/repository policy own Resource.id. Lifecycle events must target prior outputs using those complete identity pairs in `Reference.identifier`, not copied clinical tombstones or bare values.

Acceptance tests: exact system/value, no accidental `Identifier.id`, stable identity across retries, correct Resource.id policy, and duplicate/collision rejection.

### MHC-12 — Quantity coding is clinically wrong (**P1, Defect**)

Evidence:

- LDL correctly uses LOINC for `Observation.code`, but repeats LOINC `18262-6` and `http://loinc.org` in `valueQuantity.code/system` while the displayed unit is `mg/dL`: `MyHeartCounts/Heart Health Dashboard/QuantitySample+FHIR.swift:52-68`.
- Score quantities put the MHC concept code/system into `Quantity` and display `count`: `:69-81`.
- The generic component helper repeats a concept coding system/code into every Quantity: `MyHeartCounts/Utils/FHIR/CodingProtocol.swift:85-112`; the timed-walk components use it at `TimedWalkingTestResult+FHIR.swift:45-80`.

Impact: the Quantity claims that a clinical concept code is a unit code. UCUM-aware clients cannot safely convert or compare values.

Breaking recommendation: separate `Observation.code`/component concept coding from Quantity unit coding. Use `http://unitsofmeasure.org` and the exact UCUM code (`mg/dL`, `m`, `min`, `1`/a defined score annotation as appropriate); keep human unit separately. Define each app score's clinical meaning and value domain in an app IG before export.

Acceptance tests: assert concept and unit systems separately for every custom sample/component, UCUM validation, official FHIR validation, and round-trip quantity conversion.

### MHC-13 — Deletion records cannot identify the new exchange artifact (**P1, Defect / design gap**)

Evidence:

- Deletions retain only sample type and raw HealthKit UUID: `MyHeartCounts/Modules/HealthUploadStaging.swift:228-244`.
- The uploaded deletion CSV contains only `sampleType`, `sampleId`, and timestamp: `MyHeartCounts/Modules/HealthUploadStagingUploader.swift:105-128`.
- New conversion output is a Bundle/graph with versioned complete identifiers and potentially multiple output roles, not a resource addressed solely by an uppercase UUID.

Impact: a backend cannot unambiguously retract all resources/sidecars/revisions derived from the deleted source or reconcile changes in identifier algorithms.

Breaking recommendation: emit the dedicated versioned Grove lifecycle Provenance Bundle defined by the 0.6 IG. Give the Bundle a new durable event identity; distinguish activity, recording, and assembly times; and identify the producer. A HealthKit removal triggers the event; use `http://terminology.hl7.org/CodeSystem/v3-DataOperation#DELETE` only if the event asserts completed removal of the prior Grove outputs, otherwise use the reviewed Grove application operation. Target each logical output through a typed, complete, indexed `Reference.identifier`; exact revisions need a revision-specific identifier or version-specific literal reference, while output role needs a discriminator/extension. Include source and adapter-contract evidence needed for resolution. Do not copy prior clinical resources, treat source removal as proof of a resource-specific error, or treat a collection Bundle as a delete command.

Acceptance tests: convert then delete every supported source kind; backend resolves exactly the whole graph and no unrelated graph; repeat deletion is idempotent; algorithm-version migration is defined.

### MHC-14 — Staging deletes data before upload completion (**P1, Defect**)

Evidence:

- The staging uploader starts an unstructured `Task` for sample upload, then immediately deletes the drain batch: `MyHeartCounts/Modules/HealthUploadStagingUploader.swift:87-103`.
- It repeats the pattern for deletion manifests: `:105-128`.
- The live Firebase upload also returns after launching an unstructured task: `MyHeartCounts/MyHeartCountsStandard+HealthKit.swift:189-196`.

Impact: a failed/cancelled upload can occur after the only durable local FHIR copy/tombstone has been deleted. Errors are detached from the caller and retry logic.

Breaking recommendation: await a durable remote/managed-queue acknowledgement inside structured concurrency, persist upload state/idempotency key, and delete staging only after acknowledgement. Treat cancellation as failure and retain the batch.

Acceptance tests: injected network failure before/during/after upload, task cancellation, process restart, duplicate acknowledgement, and deletion-manifest failure; no source batch is lost and retries are idempotent.

### MHC-15 — App-specific extension semantics are unpublished (**P2, Recommendation / ownership decision**)

Evidence:

- App URLs/builders are defined at `MyHeartCounts/MyHeartCountsStandard+HealthKit.swift:290-329` and `MyHeartCounts/Utils/FHIR/DomainResource+HKSourceRevision.swift:159-164`.
- Wrist temperature adds `https://myheartcounts.stanford.edu/.../algorithmVersion`: `MyHeartCounts/SensorKit/Sample Types/WristTemp+CSV.swift:19-48`.
- Grove already publishes the canonical wrist-temperature algorithm extension (`SensorKitContract.wristTemperatureAlgorithmVersionExtension`) and its structured summary profile requires it.
- No corresponding MHC StructureDefinitions/package were found in the Grove IG. The relevant Grove root extension slicing is open, so these extensions are not automatically invalid merely because they are unknown. They remain unresolved/unverifiable canonicals, can produce Validator warnings depending on package loading, and have no published context, cardinality, value-type, or semantic governance.

Breaking recommendation: use generated Grove canonicals for Grove semantics. For genuinely MHC-specific semantics, publish a separately versioned MHC IG with dependency on Grove and derived profiles where tighter conformance is intended, then declare those profiles in `meta.profile`; otherwise keep the metadata outside the profiled clinical resource. Do not describe every unknown extension as a profile violation without a closed slice or an actual Validator error.

Acceptance tests: every emitted extension URL resolves in the loaded package closure, has the correct context/cardinality/value type, and every claimed profile validates.

### MHC-16 — Raw signal paths omit required structured summaries (**P1, Current-IG drift / decision required**)

Evidence:

- Raw PPG, accelerometer, and wrist-temperature paths call the standalone document flow in MHC rather than the typed Grove summary converters.
- The current IG describes mandatory paired summaries: wrist temperature `sensorkit/input/fsh/profiles.fsh:382-405`, accelerometer `:412-434`, and PPG `:442-464`.
- The catalog assigns summary output discriminators, including `accelerometer-recording-summary`, `ppg-recording-summary`, and `wrist-temperature-recording-summary`: `catalog/sensorkit-adapter.json:170`, `:734`, and `:938-956`.

Impact: current MHC output lacks the profiled clinical/coverage artifact and the `derivedFrom`/Provenance relationship required to interpret the sidecar.

Breaking recommendation: construct the typed Grove record and persist the entire paired graph. If raw-only is intended as a valid alternative, change the IG/catalog to state that explicitly and generate an admitted representation mode; do not let app code infer it.

Acceptance tests: per catalog row, assert exact resources, output roles, profiles, sidecar relationship, and official validation for every admitted mode.

### MHC-17 — PPG effective range is incomplete (**P2, Defect**)

Evidence: the upload range is `first.startDate ..< last.startDate`: `MyHeartCounts/SensorKit/Sample Types/PPG+File.swift:30-48`. A one-sample batch has zero duration; the last sample duration is excluded; acknowledged out-of-order samples can lie outside the asserted bounds.

Breaking recommendation: derive coverage from the contract-defined sample interval (minimum start and maximum end/sample duration) and enforce ordering/timing invariants in the typed record. Do not approximate bounds only to name a document.

Acceptance tests: one sample, out-of-order input, nonzero final duration, irregular spacing, and exact agreement between summary period and sidecar sample coverage.

### MHC-18 — FHIR helper duplication creates a second contract surface (**P2, Recommendation**)

Evidence: the PR adds/carries app-local canonical URL, extension builder, resource mutation, date, and collection helpers under `MyHeartCounts/Utils/FHIR/Extensions/`, while Grove 0.6 is simultaneously replacing those APIs with generated/typed contracts. Some builders are type-erased and can fail only at runtime (`SensorKitDataFetcher+Uploading+Base.swift:57-60`).

Breaking recommendation: consolidate shared primitives in `GroveFHIRContract`, generate typed extension builders from StructureDefinitions, and keep only MHC-owned profiles/extensions in a dedicated module/package. Prefer compiler-enforced resource/value/context types over type-erased mutation closures.

### MHC-19 — The dependency pin is good for review but not a release contract (**P2, Recommendation**)

Evidence:

- `Package.resolved` pins the exact reviewed Grove SHA: `MyHeartCounts.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved:99`.
- The project requirement also uses that revision: `MyHeartCounts.xcodeproj/project.pbxproj:1300`.

This is a positive review practice, not a defect. Before 0.6.0, depend on a signed/tagged semantic `0.6.0` release whose generated catalog/IG digest is exposed at runtime and asserted by MHC integration tests.

### MHC-20 — Release hygiene is currently red (**P3, Defect**)

`git diff --check origin/lukas/grove...HEAD` reports trailing whitespace throughout the newly copied FHIR extension helpers, including `FHIRExtensionBuilder+URL.swift:29`, `FHIRExtensionBuilder.swift:17`, `Observation+Dates.swift:26`, and `Resource+Mutation.swift:17`. The reported lint/periphery failures should be fixed, not waived. Removing the duplicated helpers per MHC-18 will eliminate much of this surface.

## What is working well

- The app pins the exact Grove commit, making the integration review reproducible.
- Nonclinical HealthKit conversion uses `HealthKitConverter` with a common subject and a single conversion instant, and stores full Bundles rather than only Observations.
- Structured SensorKit paths generally use typed Grove records and persist `conversion.bundle`; device-usage JSON explicitly sorts dictionary-derived collections to seek deterministic output.
- The app uses generated recording columns/media types and Grove's CSV writer instead of preserving a parallel CSV schema.
- Raw sidecar construction supplies bytes so Grove can calculate size/hash, and authorization/disclosure decisions are explicit.
- Batch conversion preserves successful source order.
- Clinical attachment extraction is separated from the FHIR resource, which is directionally correct; the missing durable linkage/envelope is the issue.

## Validation performed

Read-only/static checks were run against the exact PR head unless stated otherwise:

| Check | Result |
|---|---|
| `git rev-parse HEAD` | Exact requested `2fbc1fa921628e01838406d6237b37acb9cec04a` |
| Source compatibility audit | **Fail:** exact stale call sites listed in MHC-01 |
| `git diff --check origin/lukas/grove...HEAD` | **Fail:** trailing whitespace in new FHIR helper files |
| PR status supplied to this audit | **Fail:** app unit/UI builds; lint/periphery |
| Xcode package/test resolution attempt | **Environment-blocked** by sandboxed cache/package-resolution access; not counted as an additional test result |
| Cross-check against current IG/catalog | **Fail for release:** raw-summary/extension/clinical contracts above are not implemented; Grove generated inputs also currently drift |

## Required 0.6.0 acceptance gate

1. Green all app/unit/UI/lint/periphery jobs at the exact MHC and Grove release SHAs.
2. Upload only complete validated exchange Bundles for Grove-owned conversions; remove standalone extracted-resource paths.
3. Make conversion/upload/deletion failures durable, typed, observable, retryable, and idempotent before advancing checkpoints or deleting staging.
4. Complete the clinical-record byte-preserving envelope and attachment-linking workflow.
5. Replace all source-ID algorithms with the selected generated deployment-scoped, domain-separated HMAC contract and cross-language golden vectors, including supplementary Unicode scalars; use unkeyed SHA-256 only for content integrity.
6. Canonicalize every unordered payload collection; add multi-process/cross-language byte vectors for PPG and every sidecar format.
7. Fix all app-authored Observation subject, business-identifier, concept, unit, effective-time, and provenance semantics; validate them with the official validator and the exact 0.6 package closure.
8. Resolve whether each SensorKit row is raw-only, structured-only, paired-required, or either, then make that a generated closed type and test the full row matrix.
9. Publish an MHC IG for remaining app-owned extensions/profiles or remove them from Grove-profiled resources.
10. Specify and implement dedicated versioned deletion/nullification events—without copied clinical tombstones—then test convert-delete and retry/restart workflows end to end.
