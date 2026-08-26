# Grove Swift PR #67 — FHIR audit for 0.6.0

- Audit date: 2026-08-26
- Pull request: [SchmiedmayerLab/Grove#67](https://github.com/SchmiedmayerLab/Grove/pull/67)
- Head branch: `feature/grove-fhir-0.2-healthkit`
- PR snapshot: [`eca40191935c5612ec2660792f01d0195d4cb992`](https://github.com/SchmiedmayerLab/Grove/tree/eca40191935c5612ec2660792f01d0195d4cb992)
- Comparison base: `origin/main` at `fb13cf97f5e2f94e2c950f6d75de5c8d92c73c15`
- Nested workspace checkout: `/Users/paulschmiedmayer/Developer/grove-fhir/stack/Grove` (at the reviewed HEAD, with separately identified post-head user changes)
- IG/catalog cross-check: `/Users/paulschmiedmayer/Developer/grove-fhir` working tree

Unless explicitly under “Moving nested-worktree delta after PR HEAD,” implementation paths below are relative to the linked reviewed commit. That later section uses paths in the nested dirty checkout and separates those observations so they are not misattributed to PR HEAD.

## Verdict

Do not merge or publish this implementation as the Swift 0.6.0 contract yet. The redesign has a strong foundation, but several paths can emit a graph or payload that contradicts the IG, silently changes numeric data, loses required provenance, or is nondeterministic. The most consequential gaps are waveform timing, media-type/format pairing, clinical-record envelopes, raw SensorKit admission, wrist-temperature identity, decimal/CSV encoding, and questionnaire-expression validation.

The PR is intentionally breaking and 0.6.0 can break APIs. Use that freedom to make invalid states unrepresentable, expose one immutable exchange graph as the result, and generate every contract-bearing discriminator from the catalogs.

Severity used below:

- **P0** — 0.6.0 release/merge blocker, including red build/generated/conformance gates or an unresolved contract dependency.
- **P1** — high FHIR, data-integrity, privacy, or interoperability defect.
- **P2** — material API/design/maintainability issue to fix for 0.6.0.
- **P3** — release hygiene.

Labels distinguish **Defect** (the reviewed code violates its declared/current contract), **Recommendation** (a breaking design improvement), and **Current-IG drift / decision required** (the PR snapshot and the current IG no longer describe the same target).

## Selected highest-risk findings

| Severity | Type | Finding |
|---|---|---|
| P0 | Defect / current-IG drift | The generated Swift FHIR contract is not synchronized with the current catalog; the current hypertension row also requires a clinical decision and implementation work before regeneration can define release behavior. |
| P0 | Defect | The PR's reported `FHIR Output Conformance` and SwiftLint checks are failing; conformance must be green on the exact release artifacts. |
| P1 | Defect | Waveform constructors accept an `end` that contradicts frame count and sampling period, then serialize it unchanged. |
| P1 | Defect | Recording `format` and `contentType` are independently supplied; an existing test positively exercises a mismatched pair. |
| P1 | Defect | Wrist-temperature output identity uses `wrist-temperature-samples`, while the catalog/example contract uses `native-recording`. |
| P1 | Defect | Sensor numeric conversion silently substitutes zero when `Double` cannot be converted to `Decimal`. |
| P2 | Recommendation | CSV numeric output uses a separate Foundation formatter whose locale and canonicalization behavior are not explicitly pinned to the shared wire contract. |
| P1 | Defect | Clinical records cannot be emitted as the required profiled `DocumentReference` graph while retaining exact source bytes. |
| P1 | Defect / contract ambiguity | `.raw` can bypass required structured summaries and provenance relationships for SensorKit rows described by the IG as paired/hybrid output. |
| P1 | Defect | HealthKit workout is advertised with session and segment outputs, but PR HEAD emits only the session. |
| P1 | Defect / contract defect | Recording-device identity merges same-model units, leaks a clear value called a digest, and attaches mutable versions to a shared Device; same-bundle source/converter merging can replace historical source-version evidence. |
| P1 | Defect | Questionnaire expression requirements cannot be satisfied by the validator, repeated-item scope is flattened, temporal comparisons are lexical, and coded choice matching can cross systems. |
| P2 | Recommendation | Exchange identity has public validation bypasses and graph validation does not prove reference closure or unique contract extensions. |
| P2 | Recommendation | Conversion results duplicate mutable resources outside their bundle, allowing bundle and projection to diverge. |

## Detailed findings

### GSW-01 — Waveform time bounds are not tied to samples (**P1, Defect**)

Evidence:

- The IG says the inclusive end is exactly `start + (frameCount - 1) * samplingPeriod`: `sensor/input/pagecontent/waveforms.md:18-19`.
- `SensorWaveformRecord` validates positive sampling period, nonempty/divisible samples, and ordering, but not the equation: `Sources/GroveSensorKitFHIR/SensorRecords.swift:118-175`.
- The ECG equivalent has the same omission: `Sources/GroveSensorKitFHIR/SensorRecords.swift:236-281`.
- Both values are serialized without reconciliation: `Sources/GroveSensorKitFHIR/SensorConverter+Resources.swift:50-75` and `:79-117`.

Impact: two resources can claim the same samples with different effective periods; duration and frequency-derived clinical interpretation can disagree.

Breaking recommendation: remove caller-supplied `end` from strict constructors and derive it from `start`, frame count, and a losslessly represented period. If interoperability requires accepting externally supplied bounds, provide a separately named validating initializer that rejects any mismatch before constructing the value.

Acceptance tests:

- One frame yields `end == start`.
- Multi-dimensional frames use frame count, not scalar count.
- Off-by-one and fractional-period mismatches throw typed errors.
- Serialized `effectivePeriod.end` and sidecar timing validate for exact decimal periods.

### GSW-02 — Registered format and media type can contradict each other (**P1, Defect**)

Evidence:

- `SensorRecordingDocument` accepts arbitrary syntactically valid `contentType` independently of `format`: `Sources/GroveSensorKitFHIR/SensorRecords.swift:309-379`.
- `SensorKitNativeRecording` repeats the independent inputs: `Sources/GroveSensorKitFHIR/SensorKitRecords.swift:72-113`.
- The converter writes both claims into the graph: `Sources/GroveSensorKitFHIR/SensorConverter+Resources.swift:120-154` and `:189-210`; `Sources/GroveSensorKitFHIR/SensorKitConverter+Resources.swift:109-143`; `Sources/GroveSensorKitFHIR/SensorKitConverter+Support.swift:251-281`.
- A test constructs a PPG recording with `application/octet-stream` despite `.photoplethysmogramSamples`: `Tests/GroveSensorKitFHIRTests/SensorKitRecordingSummaryTests.swift:141-146`. The generated PPG type is `application/vnd.grovealliance.ppg`: `Sources/GroveSensorKitFHIR/SensorKitGenerated.swift:73-89`.
- The generated comment says vendor subtypes are permitted (`SensorKitGenerated.swift:69-72`), while the current profile/value-set contract binds the registered pair.

Impact: a consumer cannot reliably select a decoder; the `DocumentReference.content.attachment.contentType` assertion can be false.

Breaking recommendation: make `contentType` a generated property of a closed `RecordingFormat`, not a public input. If aliases are genuinely part of the contract, encode an explicit generated set of permitted pairs and update the IG/value set accordingly.

Acceptance tests: iterate every catalog format and assert the one exact media type in model, attachment, examples, and generated constants; reject every cross-product mismatch.

### GSW-03 — Wrist-temperature output discriminator is inconsistent (**P1, Defect**)

Evidence:

- `SensorKitConverter` derives the wrist-temperature discriminator as `wrist-temperature-samples`: `Sources/GroveSensorKitFHIR/SensorKitConverter.swift:194-211`, specifically `:208`.
- The current catalog row uses `native-recording`; the current IG example's output identifier is also `native-recording` while its recording-format code is `wrist-temperature-samples`: `sensorkit/input/fsh/examples.fsh:692` and `:700`.

Impact: output identifiers created by Swift do not address the same artifact as the IG and other producers.

Breaking recommendation: generate output discriminators from the catalog and represent output role, recording format, and profile as different types. Do not infer one from another in a handwritten switch.

Acceptance tests: golden vectors for every SensorKit row must assert exact `(source ID, output discriminator, fullUrl, profile, format)` values across Swift/Kotlin/TypeScript.

### GSW-04 — Failed `Double` → `Decimal` conversion becomes zero (**P1, Defect**)

Evidence:

- `quantity` conversion uses `Decimal(string: ...) ?? 0`: `Sources/GroveSensorKitFHIR/SensorConverter+Resources.swift:157-175`, specifically `:172` and `:174`.
- Record constructors admit all finite `Double` values, including finite values with no supported decimal parse path: `Sources/GroveSensorKitFHIR/SensorRecords.swift:147-159`.

Impact: a nonzero measurement can silently become the clinically distinct value zero.

Breaking recommendation: establish a single declared numeric domain and lossless canonical conversion. A value outside that domain must fail with a typed, field-addressed error; never substitute a value.

Acceptance tests: cover `Double.leastNonzeroMagnitude`, largest finite values, negative zero, boundary exponents, and values immediately around the supported domain. Assert either an exact round trip or an explicit error.

### GSW-05 — Numeric canonicalization is fragmented (**P2, Defect / Recommendation**)

Evidence:

- `String+PlainDecimal.swift` states that every producer uses a shared non-exponent formatter: `Sources/GroveFHIRContract/String+PlainDecimal.swift:12-58`.
- HealthKit scalar conversion instead parses `String(value)` into `Decimal`: `Sources/GroveHealthKitFHIR/HealthKitMobileCanonicalization.swift:15-29`, used at `Sources/GroveHealthKitFHIR/HealthKitConverter.swift:658-667`.
- SensorKit has a separate parse-first route: `Sources/GroveSensorKitFHIR/SensorKitConverter+Support.swift:225-239`.

Impact: the same IEEE-754 value can be accepted, rejected, or serialized differently by producer path, undermining cross-language identity vectors.

Breaking recommendation: expose one `GroveFHIRDecimal` value type with an explicit finite/domain initializer and canonical lexical representation. HealthKit, SensorKit, CSV, JSON identity vectors, and FHIR primitives must all consume it.

Acceptance tests: one shared corpus across all producer modules and all three languages, including locale changes and exponent-expansion boundaries.

### GSW-06 — CSV numeric formatting bypasses the shared canonical path (**P2, Recommendation**)

Evidence:

- `RecordingCSVWriter` uses Foundation printf formatting rather than the shared canonical path, and does not explicitly pin formatter behavior as part of the contract, at `Sources/GroveSensorKitFHIR/RecordingCSVWriter.swift:114`, `:125-126`, and `:140`.
- A targeted check of the exact algorithm, including `Double.leastNonzeroMagnitude` and 199,904 random finite bit patterns, did not demonstrate a round-trip loss. The defect is therefore contract duplication and unproven cross-platform/cross-language canonical equivalence, not the previously suspected subnormal-to-zero case.

Impact: source data and content-derived identities depend on formatter behavior that is separate from the declared shared numeric path. Swift-local round trips do not prove byte equality with other SDKs or future Foundation releases.

Breaking recommendation: replace printf formatting with one locale-independent shortest-round-trip algorithm plus a deterministic plain-decimal exponent expander. Use the same implementation as GSW-05.

Acceptance tests:

- Golden bytes under at least `en_US`, `de_DE`, and a non-Latin locale.
- Min/max/subnormal values, negative zero, halfway values, and round-trip property tests.
- Cross-language byte equality for every registered CSV format.

### GSW-07 — CSV parser does not enforce the registered grammar (**P2, Defect**)

Evidence:

- The parser silently discards carriage return even though the contract specifies LF records: `Sources/GroveSensorKitFHIR/RecordingCSVReader.swift:94-179`, especially `:170`.
- The state machine accepts malformed characters after a closing quote instead of requiring comma/LF/end.
- `number` returns `nil` for both absent and malformed fields and delegates to permissive `Double` parsing: `RecordingCSVReader.swift:41-47`; exponent/nonfinite spellings are not reported as distinct grammar errors.

Breaking recommendation: define a strict parser with typed errors containing row, column, byte offset, and reason. Treat absent, empty, malformed, out-of-domain, and nonfinite as distinct states. If CRLF is allowed, say so in the registry and canonicalize only on write.

Acceptance tests: adversarial quote transitions, embedded CR, CRLF policy, exponent/nonfinite tokens, invalid UTF-8, empty required values, and fuzz round trips.

### GSW-08 — Binary varint reader accepts overflow/noncanonical encodings (**P1, Defect**)

Evidence:

- `readUnsignedVarint` loops while `shift < 70`: `Sources/GroveSensorKitFHIR/RecordingBinaryReader.swift:61-77`. A tenth byte with payload bits beyond the single valid UInt64 bit can be shifted/truncated rather than rejected; overlong encodings are also accepted.
- The writer emits canonical UInt64 encodings: `Sources/GroveSensorKitFHIR/RecordingBinaryWriter.swift:30-47`.

Impact: distinct/malformed byte payloads can decode to the same semantic record, defeating canonical identity and creating parser differential risk.

Breaking recommendation: require the tenth byte to be at most `0x01`, reject continuation on the tenth byte, and reject overlong encodings if the registered format is canonical.

Acceptance tests: `0`, `UInt64.max`, every byte-length boundary, invalid tenth bytes, unterminated input, overlong zero, and property/fuzz tests against a reference implementation.

### GSW-09 — Clinical records do not implement the catalog output contract (**P1, Defect**)

Evidence:

- Generated catalog rows declare `healthkit-clinical-record-document`: `Sources/GroveFHIRContract/Generated.swift:3989-4056`.
- The main converter deliberately returns `platformExclusiveDocument`: `Sources/GroveHealthKitFHIR/HealthKitConverter.swift:288-306`.
- `HealthKitClinicalRecord` only decodes R4/DSTU2 into in-memory models and returns a decoded resource plus attachments: `Sources/GroveHealthKitFHIR/HealthKitClinicalRecord.swift:70-128`.
- The current IG requires a profiled `DocumentReference` with format/release and attachment hash/size: `healthkit/input/fsh/profiles.fsh:116-149`.
- The current format registry defines the FHIR-resource payload as R4 and byte-preserved. Decoding then re-encoding cannot prove byte preservation; admitting DSTU2 under the same format assertion is contradictory.

Impact: the catalog advertises a supported artifact the public converter cannot create; attachment integrity and source release are lost.

Breaking recommendation: make the exact `Data` and source FHIR release the primary clinical payload, with decoding as an optional view. Build the required `DocumentReference`, source/recorder devices, Provenance, identifiers, exact hash/size, and format. Define a separate normative 0.6 relationship for any extracted attachments rather than assuming the current profile already supplies one. Either register a separate DSTU2 format/profile path or reject it.

Acceptance tests: byte-for-byte equality with the HealthKit source, correct R4 `Attachment.hash` (base64 SHA-1 over pre-base64 bytes) and size, separately defined SHA-256 integrity evidence if used, R4/DSTU2 policy tests, attachment URL/relationship resolution, graph reference closure, profile validation, and retry-stable output identity.

### GSW-10 — Raw SensorKit mode can bypass the required graph (**P1, Defect / decision required**)

Evidence:

- `validate` permits `.raw` whenever a raw profile is present: `Sources/GroveSensorKitFHIR/SensorKitConverter.swift:407-439`.
- Raw mode chooses only the raw discriminator: `SensorKitConverter.swift:194-211`.
- Current IG/catalog descriptions for device usage, ECG, wrist temperature, PPG, and accelerometer define paired structured/raw artifacts or summary Observations with provenance relationships.

Impact: a nominally supported conversion can omit the structured clinical meaning and relationship the profile family was designed to guarantee.

Breaking recommendation: generate an explicit closed representation mode per row: `rawOnly`, `structuredOnly`, `pairedRequired`, or `either`. For `pairedRequired`, do not expose a raw-only initializer/result. Clarify the IG first if raw is intended as a complete alternative.

Acceptance tests: exhaustively generate every admitted mode for every row, validate expected resource counts/profiles, and assert provenance targets and graph closure.

### GSW-11 — Exchange identity API permits invalid/bypassable inputs (**P2, Recommendation**)

Evidence:

- The public raw overload `fullURL(system:value:)` and `canonicalName` accept strings without `IdentifierSystem`/`BusinessIdentifier` validation: `Sources/GroveFHIRContract/ExchangeIdentity.swift:105-143`.
- `validate(entries:)` uses the first matching extension, accepts duplicates, and does not prove internal references resolve or that the Bundle/profile/type is the expected exchange graph: `ExchangeIdentity.swift:160-185`.

Breaking recommendation:

- Make raw string overloads internal, or make them throwing and route through the validated types.
- Reject empty values, invalid absolute systems, `|` in system components, duplicate identity extensions, duplicate fullUrls, unresolved internal references, wrong resource types, and wrong Bundle/profile.
- Add an `ExchangeGraph` constructor/validator that owns entries and validates the complete graph before serialization.

Unicode note: Swift's native `String` cannot contain an isolated UTF-16 surrogate, and hashing `String.utf8` correctly includes supplementary Unicode scalars. Preserve that scalar-string behavior in cross-language vectors; do not copy Kotlin character-unit rejection logic.

Acceptance tests: non-BMP identifiers (emoji and supplementary CJK), normalization-distinct strings, delimiter cases, empty inputs, duplicate extensions, duplicate entries, dangling references, and all resource-type mismatches.

### GSW-12 — Conversion result projections can diverge from the Bundle (**P2, Recommendation**)

Evidence:

- `HealthKitConversion`, `SensorConversion`, and `SensorKitConversion` expose resources in addition to a Bundle. They are independent mutable FHIR model values.
- A consumer can mutate the projected `DocumentReference`/Observation and serialize it while the Bundle retains the original graph; the audited MyHeartCounts PR does exactly this for raw SensorKit documents.

Breaking recommendation: make the immutable, validated exchange graph the single source of truth. Provide typed read-only accessors/entry identifiers, and a graph builder for coordinated mutation that revalidates identity/reference/profile invariants. Avoid public mutable duplicate resources.

Acceptance tests: prove no supported API can mutate an entry without updating the serialized graph; verify copy/value semantics under concurrent use.

### GSW-13 — Provenance and error APIs understate invariants (**P2, Recommendation**)

Evidence:

- `SensorGraphIdentifiers.provenance` is optional even though conversion always emits Provenance: `Sources/GroveSensorKitFHIR/SensorConverter.swift:114-121` and `:240-299`.
- SensorKit `convert` is untyped `throws`: `Sources/GroveSensorKitFHIR/SensorKitConverter.swift:119-132`.
- Several conversion error cases flatten dependency failures into strings, losing machine-readable cause/context.

Breaking recommendation: make guaranteed identifiers nonoptional, adopt typed throws throughout the Swift 6 public surface, retain structured underlying errors, and include stable field/record addresses. Keep result values `Sendable`; add `ResourcePair: Sendable` if the dependency types support it (`Sources/GroveQuestionnaireFHIR/ResourcePair.swift:113-138`).

### GSW-14 — Questionnaire expression contract is impossible to validate correctly (**P1, Defect**)

Evidence:

- Completed resources containing `enableWhenExpression` are unconditionally blocked: `Sources/GroveQuestionnaireFHIR/PairRules.swift:495-517`.
- `targetConstraint` unconditionally emits `expressionEngineRequired`: `PairRules.swift:965-991`; no evaluator/evidence is accepted by the validator despite an expression engine existing in the package.
- Expression response lookup gathers every matching `linkId` globally: `Sources/GroveQuestionnaireFHIR/FHIRPathExpressionEngine.swift:126-171` and `:211-229`, losing repeated-group occurrence scope.
- Coding comparison first tests an exact `system|code`, then still accepts a suffix code from another system: `FHIRPathExpressionEngine.swift:312-340`, especially `:325`.
- Temporal comparison compares primitive strings lexically: `PairRules.swift:1076-1101`, which is not FHIR date/dateTime ordering across offsets/partial precision.
- `decimalPlaces` uses an `NSDecimalNumber` normalized description rather than source lexical scale: `PairRules.swift:1138-1146`.

Impact: valid completed resources cannot pass one rule, while other constraints can pass against the wrong repeated answer, wrong coding system, or wrong chronological order.

Breaking recommendation:

- Require an expression evaluator and explicit evaluation evidence/context when validation mode requires expressions.
- Address response items by occurrence/path, not only `linkId`.
- If a Coding specifies a system, require exact system+code; allow code-only matching only under a documented unambiguous/systemless rule.
- Use FHIRPath temporal semantics with precision and timezone awareness, and validate lexical decimal scale before model normalization.

Acceptance tests: completed/draft lifecycle with evaluator success/failure, repeated nested groups with identical linkIds, same code in two systems, offset-equivalent/reversed dateTimes, partial dates, and lexical values `1`, `1.0`, `1.00`.

### GSW-15 — FHIRPath date evaluation depends on the host environment (**P2, Defect**)

Evidence:

- `FHIRPathEvaluationContext` carries only an instant: `Sources/FHIRPathParser/Evaluation/FHIRPathEvaluationContext.swift:12-39`.
- Evaluation uses `Calendar.current`/`TimeZone.current`: `Sources/FHIRPathParser/DateExpressionEvaluation.swift:21`; `Sources/FHIRPathParser/Evaluation/FHIRPathEvaluator+Coercion.swift:89`; `Sources/FHIRPathParser/Date+FHIRPathValue.swift:26` and `:53`; `Sources/FHIRPathParser/Evaluation/FHIRPathFunctionCall+Values.swift:296-307`.

Impact: a fixed `now` can yield different answers on devices/servers in different time zones or calendar settings.

Breaking recommendation: put an explicit Gregorian calendar, time zone, and locale in the evaluation context; require callers to choose them at workflow boundaries. Do not consult process-global `current` values during evaluation.

Acceptance tests: run the same fixture under multiple process time zones/calendars and assert identical results when context is identical.

### GSW-16 — Generated contract provenance is too weak and visibly stale (**P2, Defect / Recommendation**)

Evidence:

- `GroveFHIRContractVersion` exposes only the root canonical: `Sources/GroveFHIRContract/Generated.swift:16-19`, not the catalog/IG version or digest.
- `SensorKitGenerated.swift:23` and `SensorKitCatalog.swift:19`, `:47`, `:64` still describe v0.3, while the generated contract records catalog version 0.5.0 (`SensorKitGenerated.swift:123-127`).

Breaking recommendation: every generated artifact should expose generator version, IG package version, catalog schema version, and normalized input SHA-256. Put the same tuple in producer diagnostics/manifest and fail generation/checks on stale prose or unconsumed catalog fields.

Acceptance tests: changing any catalog/required IG input changes the digest and makes `--check` fail; all generated module versions equal the release version.

### GSW-17 — Current hypertension catalog change is incomplete (**P0 for 0.6.0, Current-IG drift / decision required**)

Evidence:

- At the PR snapshot, hypertension notification is intentionally unsupported with no profiles: `Sources/GroveFHIRContract/Generated.swift:3637-3642`.
- The current workspace catalog now marks it supported and assigns a measurement/profile: `catalog/healthkit-adapter.json:677-690`.
- The current handwritten category binding switch has no hypertension binding and falls through to `nil`: `Sources/GroveHealthKitFHIR/HealthKitCatalog+CategoryBindings.swift:1-195` (terminal default near `:189`).
- The PR tests still inventory/exempt it as unsupported: `Tests/GroveHealthKitFHIRTests/HealthKitConverterTests.swift:627-640`.
- Generating against the current workspace now produces `Profile.healthkitHypertensionNotification`; this confirms that the earlier missing-generated-profile state is no longer a current IG defect, while the PR remains unsynchronized and lacks converter semantics for the newly supported row.

This is not necessarily a defect against the older PR target; it is a definite 0.6.0 integration blocker against the current IG.

Breaking recommendation: first resolve the catalog's contradiction between `status: supported` and its anti-emission requirement. If clinically admitted, finish the binding and exact category-value/status/effective-time semantics and regenerate all languages; otherwise revert the row to unsupported/source-preservation-only. Never publish an advertised supported row without a converter and validator fixture.

### GSW-18 — Default wall-clock construction weakens reproducibility (**P2, Recommendation**)

Evidence: `ResourceBuilder` defaults authored timestamps to `.now`: `Sources/GroveQuestionnaireFHIR/ResourceBuilder.swift:41-60` and `:78-109`.

Breaking recommendation: require an injected clock or explicit authored instant in strict/export APIs. Convenience `.now` APIs can exist only as clearly named UI helpers. Identical source input plus explicit context should produce semantically equivalent FHIR graphs and exact registered identity/payload bytes; whole-Bundle byte equality requires a separately defined canonical serializer.

### GSW-19 — Minor release hygiene (**P3, Defect**)

`git diff --check` reports a blank line at EOF in `Sources/GroveSensorKitFHIR/GroveSensorKitFHIR.docc/GroveSensorKitFHIR.md:56`. Fix this together with the reported SwiftLint failures; do not waive generated/conformance lint failures for release.

### GSW-20 — Workout support silently omits the advertised segment graph (**P1, Defect**)

Evidence:

- The generated contract marks `HKWorkoutTypeIdentifier` supported with both `workout` and `workout-segment` measurements/profiles: `Sources/GroveFHIRContract/Generated.swift:5125-5130`.
- PR HEAD's sample converter calls one binding/one `observation` builder and returns one `HealthKitConversion`: `Sources/GroveHealthKitFHIR/HealthKitConverter.swift:122-141`.
- Graph assembly adds exactly that one clinical Observation at `HealthKitConverter.swift:232-237`; `HealthKitConversion` and `HealthKitGraphIdentifiers` likewise model one Observation at `Sources/GroveHealthKitFHIR/HealthKitConversion.swift:16-40`.
- The inventory test verifies only that the first measurement has a binding (`binding?.contract.id == row.measurements.first?.id`) at `Tests/GroveHealthKitFHIRTests/HealthKitConverterTests.swift:657-675`, so it cannot detect the missing second output.

Impact: laps, pause/resume/marker events, multisport activity intervals, and segment statistics are discarded while the generated public contract calls the full row supported.

Breaking recommendation: make each generated row carry an executable output-count/graph rule and have conversion return one immutable graph with a typed clinical-output collection. Define stable child identities from native activity UUIDs where available and a specified parent/event tuple plus occurrence otherwise. Require every segment/event/statistic source field to have a mapping, explicit omission rationale, or rejection.

Acceptance tests: a multisport fixture with duplicate-time events produces the exact parent/child count, stable identities, `hasMember` links, profile claims, per-child identifiers, and Provenance targets; deleting/reordering/inserting one event has the specified correction semantics.

### GSW-21 — Device identity and version snapshots merge distinct facts (**P1, Defect / IG redesign required**)

Evidence:

- The fallback identity uses only subject, adapter, manufacturer, model, and hardware version at `Sources/GroveFHIRContract/RecordingDeviceIdentity.swift:38-68`. Two same-model physical units for one participant therefore collide. It returns a clear `v1:` tuple even though the converter calls it a “published recording-device digest” at `Sources/GroveHealthKitFHIR/HealthKitConverter+Devices.swift:83-105`.
- That complete clear value becomes the Bundle entry identity. It includes the literal subject reference and device facts, so it is neither a per-unit identifier nor concealment.
- Firmware/software are excluded from identity but written onto the shared Device at `HealthKitConverter+Devices.swift:62-68`. The identity's own documentation says those values are excluded from the shared Device and stated per Observation at `RecordingDeviceIdentity.swift:19-22`; no such per-Observation version path exists. Historical imports can therefore leave whichever shared Device version was processed last.
- If source author and converter share a bundle identifier, graph assembly replaces the source-author resource with the current converter Device at `HealthKitConverter.swift:197-209`, losing a historical `HKSourceRevision.version` assembled at `HealthKitConverter+Devices.swift:146-167`.

Breaking recommendation: redesign the IG first. Claim a persistent physical Device only with governed per-unit evidence/pseudonym; otherwise omit it or use an event-scoped Device. Keep acquisition-time firmware/software evidence immutable without mutating a shared historical Device. Treat clear versus HMAC identity as a privacy decision and never call the clear tuple a digest. Deduplicate a Device across Provenance roles only when its representations are semantically compatible; preserve role/time-specific application-version evidence when the same product acted as writer and converter.

Acceptance tests: two same-model units cannot merge when per-unit evidence exists; absent evidence follows the selected omit/event-scope policy; firmware changes do not rewrite older events; a source revision from an older build remains attributable when the current converter has the same bundle ID; disclosure and key-epoch vectors match all SDKs.

## Moving nested-worktree delta after PR HEAD

The nested Grove checkout also had user-owned, uncommitted FHIR work beyond PR HEAD. It is not attributed to commit `eca4019`, but it was reviewed because it is a likely next implementation step. At `2026-08-26T21:01:47Z`, the tracked binary diff had SHA-256 `3ddb7f4e833f2e8bd68ca93df7862a2261e4deb03f32eee28bee1b0a001ab4f0`; the two untracked files `HealthKitConverter+RetainedMetadata.swift` and `HealthKitConverter+WorkoutSegments.swift` had SHA-256 values `1a4378aa82ebba82ed6c2a6251ddb7a9be697bf492bea783781cb94cd49f977e` and `995b41378c563e43327e76d99e5e15bc3a2e3aebb1547298796e2a0ff16ffb37` respectively.

### WD-01 — The retained-metadata implementation proves the current “verbatim” contract is not lossless (**P1 if carried forward**)

The new implementation calls every unmodelled metadata entry verbatim/lossless at `Sources/GroveHealthKitFHIR/HealthKitConverter+RetainedMetadata.swift:45-50`, but converts `HKQuantity`, numeric `NSNumber`, and unknown objects into strings at `:80-94`; distinct source types/lexical values can collapse and `String(describing:)` is not a canonical wire format. A failed Date conversion is silently removed through `compactMap` at `:62-72` and `:86-87`. The global “modelled” key set at `:21-31` suppresses a key without proving that the particular sample path actually emitted it, while the default policy removes four more keys at `:38-43` and `:58-60`.

The privacy surface is also unsafe: every future/custom key except a four-key denylist is exported by default, even though such keys can carry identifiers or sensitive free text. Conversely, authorizing this generic policy can reveal UDI metadata while the dedicated UDI policy remains `.omit`. The only added Swift test covers one String plus one withheld external UUID. The root cross-repository test is optional when `stack/Grove` is absent and combines modelled/linkable declarations, so it does not prove per-path disjointness or losslessness.

This does not resolve IG VF-07; it demonstrates it. Replace the extension with typed, per-key reviewed mappings or a versioned opaque canonical metadata artifact. If policy omits a field, report that disposition explicitly and never call the conversion lossless.

### WD-02 — Workout children are added to the Bundle but not to the complete identity/provenance model (**P1 if carried forward**)

The attempt correctly recognizes that a workout can require child segment Observations, but it is not yet a conformant graph:

- activity/event identities are array-index based at `HealthKitConverter+WorkoutSegments.swift:29-50`, even though activities expose stable UUIDs and inserting an earlier event can renumber later outputs;
- each child claims `GroveMobileWorkoutSegment` but `segmentObservation` sets no required business `Observation.identifier` at `:62-83`;
- `assembleGraph` adds an entry identity and `hasMember` reference without assigning the child's own published business identifier at `HealthKitConverter.swift:249-270`; copying the parent's writer sync identifier would also be wrong because it would identify multiple resources as one writer record;
- conversion Provenance is constructed first and targets only the parent at `HealthKitConverter.swift:240-247` and `HealthKitConverter+Devices.swift:223-264`; and
- the children claim only `GroveMobileWorkoutSegment`, while the current `HealthKitConversionProvenance.target` admits only `HealthKitObservation`, requiring a HealthKit child overlay or target-profile redesign; and
- `HealthKitGraphIdentifiers`, `HealthKitRepositoryIDs`, and `HealthKitConversion` still expose exactly one Observation (`HealthKitConversion.swift:16-40`; `HealthKitConversionContext.swift:17-42`).

The delta also drops unfinished activities and does not disposition the full event/activity/statistics surface. Its dirty tests add no workout-segment graph coverage. Redesign conversion output around a typed list/graph of clinical outputs; set each child identifier to its own business identity; use native activity UUID where available and a specified parent/event tuple plus occurrence otherwise; define child-specific writer/source revision semantics rather than cloning the parent sync identifier; admit/profile every child in Provenance; and support repository IDs without assuming one Observation.

### WD-03 — Application release/build separation improves, but host OS is still put on the application Device

Separating marketing version from build is a sound improvement. Adding the running host OS to the application Device at `Sources/GroveHealthKitFHIR/HealthKitConverter+Devices.swift:35-50` implements the current dirty profile but preserves IG VF-08's modeling contradiction. Put OS product/version and hardware on a host Device linked through `Device.parent`; snapshot application build and host facts independently. Existing fixtures/docs still pass composite values such as `2.0.0 (42)` and add no build/OS assertion, so the new API continues to admit the old ambiguous form. Same-bundle source/converter collapse from GSW-21 would now replace source revision evidence with current build/OS as well.

### WD-04 — The generated release contract remains unsynchronized

The dirty delta does not update `Sources/GroveFHIRContract/Generated.swift` or the handwritten hypertension binding. The current IG generator can now produce the hypertension profile constant, but the nested implementation still treats that row under the old unsupported contract. GSW-17 remains open pending the clinical decision and full regeneration.

## What is working well

- The package opts into Swift tools 6.3 / Swift 6 language mode and uses value types and `Sendable` broadly. Conversion contexts capture a fixed conversion instant rather than reading the clock per resource.
- HealthKit and SensorKit conversion is catalog-driven far more consistently than the old mapping extensions. Profiles, concepts, units, identities, source/recorder devices, Provenance, and internal references are generally assembled coherently.
- Batch results preserve input order and represent per-item failures rather than making the entire batch nondeterministic.
- Raw-payload admission is explicit, attachments include hash/size, and entry/fullUrl uniqueness is considered.
- Identity construction uses UTF-8, so valid supplementary Unicode scalars work naturally in Swift.
- The questionnaire pair validator sorts issues deterministically and documents the separate official-validator boundary.
- `ResponseCache` protects its `@unchecked Sendable` state with a lock; this is the right direction under Swift 6.
- The generator unit suite passed, and the standalone SensorKit generated-contract check passed at the reviewed snapshot.

## Validation performed

Read-only/static checks were run against the exact PR head unless stated otherwise:

| Check | Result |
|---|---|
| `git rev-parse HEAD` | Exact requested `eca40191935c5612ec2660792f01d0195d4cb992` |
| `python3 -m unittest discover Scripts/Tests` | **Pass: 47 tests** |
| `generate-grove-sensor-swift-contract.py --check` | **Pass** |
| `generate-grove-fhir-swift-contract.py --catalog-directory <current-IG>/catalog --check` | **Fail: generated Swift is not synchronized**; current generation now includes the hypertension profile constant, but the reviewed PR still lacks the decided converter behavior |
| `git diff --check` | **Fail:** blank EOF line noted in GSW-19 |
| PR status supplied to this audit | **Fail:** SwiftLint and FHIR Output Conformance |
| SwiftPM/Xcode package test attempt | **Environment-blocked**, before test execution, by sandboxed module-cache/CoreSimulator access; not counted as an implementation failure |
| Post-head nested-worktree tracked `git diff --check` | **Pass** |
| Post-head strict SwiftLint on changed/new files | **Fail:** four new multiline-bracket errors in `HealthKitConverter+WorkoutSegments.swift`; a disclosure-policy ordering error already exists at PR HEAD |

The generated-contract mismatch against the current IG is expected to include legitimate worktree evolution, so it is classified separately from defects at the exact PR snapshot. It must nevertheless be resolved before cutting 0.6.0.

## Required 0.6.0 acceptance gate

1. Freeze one IG/catalog commit and one normalized catalog schema/version; regenerate Swift/Kotlin/TypeScript from it and publish input digests.
2. Make all generated `--check` jobs, SwiftLint, unit suites, and official FHIR conformance green at the exact release commit.
3. Run official validator closure over every emitted resource and complete Bundle, with the exact 0.6.0 package and all dependent packages loaded; reject warnings by explicit allowlist only.
4. Add cross-language identity and payload golden vectors covering Unicode supplementary scalars, all delimiters, every catalog row, numeric boundaries, and all output roles.
5. Make recording format/media type, waveform timing, output role, profile, and representation mode closed generated types so invalid combinations cannot be initialized.
6. Complete the clinical-record graph and byte-preservation contract.
7. Add adversarial/fuzz/property suites for CSV, binary varints, decimals, reference closure, and questionnaire occurrence/temporal/coding semantics.
8. Serialize only a validated immutable exchange graph; no standalone projected resource may silently escape or diverge.
