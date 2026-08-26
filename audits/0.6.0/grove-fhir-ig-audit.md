# Grove FHIR implementation-guide audit for 0.6.0

- Audit date: 2026-08-26
- Audited revision: `7e6ec8c` (`feature/0.6.0-conversion-completeness`) plus the dirty worktree as it existed during this review
- Scope: FHIR R4 and implementation-guide contracts only; no Swift, Kotlin, or TypeScript style review is included here
- Change policy assumed: 0.6.0 may break every prior API, package, identity, profile, and catalog contract

## Executive decision

**Do not release the current worktree as 0.6.0.** The project has an unusually strong conformance-testing foundation, but several normative artifacts disagree about the same wire contract. The highest-risk disagreements concern:

1. retractions that prose requires but the claimed profiles make impossible to validate;
2. Health Connect, SensorKit, provider, and shared writer identities whose machine catalogs, NamingSystems, FSH constraints, examples, and validator implement different algorithms;
3. a Health Connect `RestingHeartRateRecord` mapping that converts an instantaneous source fact into a daily mean over a Period;
4. a generic HealthKit metadata extension that promises verbatim losslessness but neither models nor tests a lossless type system;
5. publication tooling that still describes and produces a mutable CI preview, not an immutable 0.6.0 release.

These are not backward-compatibility concerns. They can cause two conformant-looking implementations to emit different identifiers or clinical semantics, and they can cause an official FHIR Validator result to disagree with the Grove producer validator. The cleanest 0.6.0 is therefore a deliberate re-foundation around one source of truth for lifecycle, identity, catalog schemas, and release metadata.

### Minimum release blockers

- Resolve verified findings **VF-01 through VF-11 and VF-17** before cutting 0.6.0; the remaining High findings are also required unless an accountable release decision explicitly removes the affected surface.
- Make every normative identity grammar executable from one machine source and use it in generation, examples, repository validation, and all three language SDKs.
- Define separate conformance levels: base FHIR R4, profile conformance, and Grove graph/semantic conformance.
- Rebuild all seven guides from a clean checkout and make the repository, SUSHI, Publisher, official Validator, semantic corpus, and package-diff gates green.
- Activate a real immutable publication path; do not relabel the current `ci-build-only` surface as a release.

## Method and evidence status

This audit distinguishes three evidence classes:

- **Verified defect:** directly reproducible from current files, generated artifacts, tests, or authoritative platform documentation.
- **Design recommendation:** the current contract can be internally consistent, but a breaking redesign would materially improve FHIR correctness or cross-language interoperability.
- **Unknown requiring decision:** the repository does not contain enough evidence to choose safely.

Checks performed without changing implementation files:

- Final pinned dirty-worktree observation: `2026-08-26T21:09:22Z` at full HEAD `7e6ec8cdd5a1c562a586607c803b53e123edaf52`. The tracked non-audit binary patch (`git diff --binary HEAD -- . ':(exclude)audits'`) had SHA-256 `1eec4617b35849c948de6e814536a8f7815ab5ec0722cc184fb1e3866afeee96`; untracked `Tests/test_conversion_completeness.py` had SHA-256 `191f56ba10cb6652f827441c979be7ba1c59d1dd76033a6bbe147efe2461b278`; observed `questionnaire/output/package.tgz` had SHA-256 `e880208d0a0ca7bf88ade35accfd0da497496e5392d84a02856b082b264dcead`; `healthkit/output` was empty. This pins one instant of the moving local evidence without treating it as a releasable commit.
- `npm test` against that pinned dirty state: **pass** for the 260-test suite, with 1 skip because HealthKit Publisher output was absent. Schema checks, content checks, terminology, measurement rendering, format rendering, package/allowlist checks, and all executed tests passed. Other observations during the concurrent build briefly had the Publisher outputs present and no skip; that volatility is itself why all release gates must be rerun on a clean, frozen checkout. An earlier run had two stale built/SUSHI-artifact failures that later regenerated. This moving dirty snapshot still requires a clean Publisher/official-Validator release build.
- The terminology gate reported `loinc-uses=138`, `ucum-uses=161`, `pinned-concepts=66`, `problems=0`.
- Measurement rendering reported 204 emitted measurements and no renderer problems.
- An isolated Mobile SUSHI run completed with zero errors. An isolated HealthKit SUSHI run completed with zero errors but warned that `writerRecordVersion` was declared again on an inherited slice. Both runs also attempted network-based version/latest resolution, relevant to reproducibility below.
- A standalone Health Connect SUSHI invocation without the repository's staged local Mobile package failed to resolve `org.grovealliance.fhir.mobile#0.5.0`; that result is **not** counted as a guide defect because the supported build script stages local packages first.
- A full current Publisher build was not treated as trustworthy while dirty generated packages were demonstrably stale. Existing `output/package.tgz` files describe an earlier 0.5.0 build, not the current source tree.

Severity meanings:

- **Critical:** release blocker; can change clinical meaning, lifecycle validity, or stable identity.
- **High:** likely interoperability failure or a material gap between official/profile and Grove conformance.
- **Medium:** contract drift or reproducibility issue that should be fixed in 0.6.0.
- **Low:** editorial or governance defect with limited wire impact.

## Verified defects

### VF-01 — Critical — The universal retraction contract cannot conform to several claimed profiles

**Evidence**

Health Connect requires an `entered-in-error` stub to keep its profiles/code/identifiers and replace its value with `dataAbsentReason` at `/Users/paulschmiedmayer/Developer/grove-fhir/health-connect/input/pagecontent/implementation.md:92-97`. HealthKit repeats the rule at `/Users/paulschmiedmayer/Developer/grove-fhir/healthkit/input/pagecontent/implementation.md:73-78`, and SensorKit repeats it at `/Users/paulschmiedmayer/Developer/grove-fhir/sensorkit/input/pagecontent/implementation.md:58-63`.

The profiles make those stubs impossible for several shapes:

- Health Connect specimen-specific glucose requires `value[x] 1..1` at `/Users/paulschmiedmayer/Developer/grove-fhir/health-connect/input/fsh/profiles.fsh:97-163`.
- SensorKit On-Wrist requires a root value and two populated components and prohibits `dataAbsentReason` at `/Users/paulschmiedmayer/Developer/grove-fhir/sensorkit/input/fsh/profiles.fsh:78-104`.
- SensorKit Device Usage requires its root value and two component values and prohibits absence reasons at `/Users/paulschmiedmayer/Developer/grove-fhir/sensorkit/input/fsh/profiles.fsh:135-168`.
- Sensor and SensorKit ECG profiles require populated SampledData components and set root/component `dataAbsentReason` to `0..0` at `/Users/paulschmiedmayer/Developer/grove-fhir/sensor/input/fsh/profiles.fsh:55-86` and `/Users/paulschmiedmayer/Developer/grove-fhir/sensorkit/input/fsh/profiles.fsh:106-133`.
- A Recording Document has no `dataAbsentReason` element and still requires `content` plus payload metadata at `/Users/paulschmiedmayer/Developer/grove-fhir/sensor/input/fsh/profiles.fsh:88-112`.

The custom graph validator only decides that a source is a retraction when all target resources have `status = entered-in-error`; it checks absence of conversion Provenance but not the promised no-value/DAR stub shape at `/Users/paulschmiedmayer/Developer/grove-fhir/Scripts/validate-producer.py:1815-1847`.

**Impact**

The guide mandates resources that the official Validator must reject. A producer can also retain the original clinical value, pass the Grove lifecycle check, and still violate the prose contract. DocumentReference outputs cannot use the advertised representation at all.

**Breaking change**

Replace the universal clinical-resource tombstone with a dedicated, profiled lifecycle `Provenance` in a retraction exchange Bundle. A source-platform removal is the trigger, not automatically the Provenance target activity: use v3-DataOperation `DELETE` only when the event asserts that prior Grove output objects were actually removed, and `NULLIFY` only when its narrower “treated as though it never existed” meaning applies; otherwise define a reviewed Grove lifecycle code/application operation. Constrain target Reference type. A complete indexed `Reference.identifier` can select a logical output, but an exact revision needs a revision-specific identifier or version-specific literal reference; encode output role in the identifier discriminator or a profiled extension. Define resource-specific `entered-in-error` projections separately at the sink. Do not clone prior clinical values into the transport event, and do not overload conversion Provenance or treat it as an executable delete command.

**Acceptance criteria**

- One official-Validator-positive source-removal lifecycle Bundle for every output family, plus explicit nullification fixtures only where the selected code and resource-specific semantics actually apply: scalar Observation, panel/component Observation, SampledData, hybrid Observation plus DocumentReference, and DocumentReference-only output.
- Negative fixtures for retained clinical values, missing business identity, mixed converted/retracted outputs, illegal conversion Provenance, and an attempted DAR on DocumentReference.
- The same lifecycle corpus passes/fails identically in Swift, Kotlin, TypeScript, the Python validator, and the official R4 Validator.

### VF-02 — Critical — Health Connect exact identities are not enforced and multiple published examples violate the machine contract

**Evidence**

The normative machine contract gives exact component sequences for record, sample output, sleep-stage output, specimen, and writer identity at `/Users/paulschmiedmayer/Developer/grove-fhir/catalog/health-connect-identity.json:22-56`, with exact lexical rules at `:69-82`. The FSH constraints instead accept any `v1:` value with two or more non-empty components at `/Users/paulschmiedmayer/Developer/grove-fhir/health-connect/input/fsh/profiles.fsh:14-27`. They do not constrain arity, UUID repository scope, embedded Record class, timestamps, occurrence, literal selectors, or specimen token.

The producer validator binds a source-type extension to an admitted measurement, but does not parse and compare the record/output identity at `/Users/paulschmiedmayer/Developer/grove-fhir/Scripts/validate-producer.py:1120-1167`. Its specimen graph check validates the SNOMED meaning but does not bind the specimen identifier to the referenced Observation record identity at `:2091-2129`.

Concrete source defects prove the gap:

- The generator composes example record identity from `measurement["id"]`, not the required Android Record class, at `/Users/paulschmiedmayer/Developer/grove-fhir/Scripts/render-measurement-profiles.py:539-544`. The resulting example uses `basal-metabolic-rate` while its source-type extension says `BasalMetabolicRateRecord` at `/Users/paulschmiedmayer/Developer/grove-fhir/health-connect/input/fsh/generated-measurement-profiles.fsh:197-211`.
- Heart-rate sample two embeds `2026-08-19T17:30:30.000000000Z` in its output identity but has `effectiveDateTime = 17:30:45Z` at `/Users/paulschmiedmayer/Developer/grove-fhir/health-connect/input/fsh/examples.fsh:131-148`.
- The capillary Specimen identity says `StepsRecord|record-010` while the Observation says `BloodGlucoseRecord|record-004` at `/Users/paulschmiedmayer/Developer/grove-fhir/health-connect/input/fsh/examples.fsh:196-224`.
- The whole-blood, serum, and interstitial Specimens use another result's raw ID and/or the capillary token at `/Users/paulschmiedmayer/Developer/grove-fhir/health-connect/input/fsh/examples.fsh:227-293`.
- The profile leaves `outputId` optional even for one-to-many Records at `/Users/paulschmiedmayer/Developer/grove-fhir/health-connect/input/fsh/profiles.fsh:74-85`; the validator does not make it conditionally required.
- The machine JSON does not enumerate the nutrient and workout-segment selectors implemented separately by `/Users/paulschmiedmayer/Developer/grove-fhir/Scripts/health_connect_identity.py:212` and following.

The Health Connect NamingSystems further claim identifiers use a versioned digest and do not expose repository scope or `Metadata.id` at `/Users/paulschmiedmayer/Developer/grove-fhir/health-connect/input/fsh/naming-systems.fsh:9-37`. The machine contract says values are unaltered components at `/Users/paulschmiedmayer/Developer/grove-fhir/catalog/health-connect-identity.json:6-13`, and the published mapping says “Nothing is hashed” at `/Users/paulschmiedmayer/Developer/grove-fhir/health-connect/input/pagecontent/mapping.md:53-66`.

**Impact**

The official Validator and current Grove validator accept identities that cannot be reproduced or safely deduplicated from the normative grammar. Published examples teach incorrect algorithms. The privacy narrative is also false for clear composed values.

**Breaking change**

Replace the parallel FSH/JSON/Python definitions with one typed identity specification. Generate FSH constraints where expressible, generated examples, language fixtures, and validator parsers from that source. Bind the embedded record type to the source-type extension; bind sample/stage selector fields to effective time/source tokens; bind specimen identity and clinical type to its referenced Observation. Choose clear or opaque identity intentionally and make NamingSystem privacy prose exact.

**Acceptance criteria**

- Mutation tests for wrong arity, repository scope, Record class, raw ID, sample timestamp, occurrence, discriminator, specimen token, cross-record reference, and omitted one-to-many `outputId`.
- Every checked-in example is derived from and round-trips through the identity parser.
- Swift, Kotlin, TypeScript, and Python reproduce every positive vector byte-for-byte and reject the same negative vectors.

### VF-03 — Critical — SensorKit output identity has incompatible definitions and the showcased Bundle mixes them

**Evidence**

The profile says `v1:<source UUID>|<discriminator>` at `/Users/paulschmiedmayer/Developer/grove-fhir/sensorkit/input/fsh/profiles.fsh:14-17`. The machine catalog says the same and explicitly says nothing is hashed at `/Users/paulschmiedmayer/Developer/grove-fhir/catalog/sensorkit-adapter.json:73-150`. The walkthrough repeats the clear composition at `/Users/paulschmiedmayer/Developer/grove-fhir/sensorkit/input/pagecontent/walkthrough.md:19-25`.

The published NamingSystem instead says values use a UUIDv5 source-record-plus-discriminator algorithm at `/Users/paulschmiedmayer/Developer/grove-fhir/sensorkit/input/fsh/naming-systems.fsh:25-38`.

The exchange resources carry clear composed identifiers at `/Users/paulschmiedmayer/Developer/grove-fhir/sensorkit/input/fsh/examples.fsh:360-393`, while the Bundle entry-identity extension uses UUID values under that same output NamingSystem beginning at `:423-445`. The Bundle validator recomputes `fullUrl` from whichever extension pair is supplied but does not prove that the extension is the resource's selected native business identifier at `/Users/paulschmiedmayer/Developer/grove-fhir/Scripts/validate-producer.py:1954-1999`.

The catalog also includes a nominally positive discriminator containing U+0001 at `/Users/paulschmiedmayer/Developer/grove-fhir/catalog/sensorkit-adapter.json:131-138`. That value can be represented in JSON escape syntax but cannot be serialized in XML 1.0, so it is not a portable FHIR string across the JSON/XML representations published by an IG.

**Impact**

Two SDKs can follow different normative artifacts and derive different stable IDs. The example graph's entry identity is not the resource identity it claims to identify. The control-character vector makes format-independent round trips impossible.

**Breaking change**

Select one algorithm from an explicit privacy decision and use it everywhere. If source-ID disclosure should be minimized, use the release-wide deployment-scoped HMAC and new/epoch-scoped identifier systems; if clear linkable tuples are authorized, retain a structured clear representation and delete concealment claims. In either case, use the selected complete pair as the Bundle entry key where it is the resource business identity, derive only `fullUrl` through UUIDv5, and restrict identity components to the intersection of valid FHIR JSON strings and XML 1.0 characters.

**Acceptance criteria**

- For each output, the entry-identity pair equals the selected resource business identifier and `fullUrl` is UUIDv5 of that exact pair.
- JSON and XML round-trip tests for all Unicode boundary vectors; C0 controls fail closed.
- Mutating either the resource identity or entry identity makes graph validation fail.

### VF-04 — Critical — Health Connect RestingHeartRate changes an instantaneous source fact into a daily aggregate

**Evidence**

The adapter maps `RestingHeartRateRecord` to `resting-heart-rate` at `/Users/paulschmiedmayer/Developer/grove-fhir/catalog/health-connect-adapter.json:765-775`. That shared measurement is explicitly a derived daily mean over an effective Period with required `method = daily-mean` at `/Users/paulschmiedmayer/Developer/grove-fhir/catalog/measurement-catalog.json:5006-5042` and `/Users/paulschmiedmayer/Developer/grove-fhir/mobile/input/fsh/generated-measurement-profiles.fsh:1386-1397`.

The authoritative AndroidX 1.1 API describes each `RestingHeartRateRecord` as “a single instantaneous measurement” and exposes an `Instant time` plus `beatsPerMinute`, not a source Period or source daily mean: [Android Developers: RestingHeartRateRecord](https://developer.android.com/reference/androidx/health/connect/client/records/RestingHeartRateRecord). The separate aggregation metrics calculate averages over query windows; the record itself is not that aggregate.

**Impact**

This fabricates aggregation method and time semantics. It is a clinical mapping error, not merely a cardinality mismatch.

**Breaking change**

Split the concepts. Map Health Connect's record to a point-in-time resting-heart-rate Observation, preferably using an appropriate standard code/profile after terminology review. Keep the existing daily/window aggregate only for sources that actually provide an aggregation window and method. Do not infer a day or `daily-mean` from the class name.

**Acceptance criteria**

- A Health Connect fixture maps `time` to `effectiveDateTime` exactly and carries no invented aggregation method.
- Daily aggregate fixtures require explicit source window and aggregate evidence.
- Terminology review documents the point concept versus derived aggregate and tests that they cannot be interchanged.

### VF-05 — Critical — Provider source identity can collide and its NamingSystem contradicts its machine catalog

**Evidence**

All connected providers share `https://grovealliance.org/fhir/providers/NamingSystem/provider-source-record-id` at `/Users/paulschmiedmayer/Developer/grove-fhir/providers/input/fsh/naming-systems.fsh:9-23`. The catalog nevertheless says a globally unique vendor key may pass through unchanged because “the system already says which provider” at `/Users/paulschmiedmayer/Developer/grove-fhir/catalog/providers-adapter.json:82-93`. The system is shared and does not say which provider. The Oura example uses the pass-through form at `/Users/paulschmiedmayer/Developer/grove-fhir/providers/input/fsh/examples.fsh:97-115`, while the catalog's own no-account vector uses `v1:oura|sleep|<uuid>` at `/Users/paulschmiedmayer/Developer/grove-fhir/catalog/providers-adapter.json:185-193`.

The NamingSystem says source-native keys are digest input only and are not exposed at `/Users/paulschmiedmayer/Developer/grove-fhir/providers/input/fsh/naming-systems.fsh:20`; the machine catalog says inputs are unaltered and “nothing is hashed” at `/Users/paulschmiedmayer/Developer/grove-fhir/catalog/providers-adapter.json:82-88`. The profile accepts almost any pass-through string or two-plus-component composition at `/Users/paulschmiedmayer/Developer/grove-fhir/providers/input/fsh/profiles.fsh:14-39`.

The catalog requires a provider-account `Identifier.system` but the composed identity grammar uses only the account value, so equal values under two account systems collide. It also gives incompatible event rules: a provider/sequence/role formula and byte-equal exchange/conversion values. R4 `Provenance` has no business `identifier`, so the latter cannot be implemented as written; the guide must distinguish `Bundle.identifier`, a Provenance entry node key, and resource business identity.

**Impact**

Identical native keys from two providers—or identical account values under different account systems—can produce the same complete `(system,value)` pair. Consumers cannot infer which algorithm or privacy property applies, and SDKs cannot implement one coherent conversion-event identity.

**Breaking change**

Always include provider code, exact source key-space token, and the complete account `(system,value)` when account-scoped. Prefer deployment-scoped, domain-separated, length-framed HMAC identities when privacy is required; use deployment-owned or explicit key-epoch identifier systems and reserve unkeyed SHA-256 for content integrity. Remove the ambiguous pass-through branch. Define one Bundle event identity partitioned by durable producer instance and sequence; give resources without native business identifiers typed event-scoped entry keys rather than inventing a nonexistent Provenance identifier. Generate exact parsers and constraints.

**Acceptance criteria**

- Cross-provider collision vectors with the same raw key produce different complete identifiers.
- Equal account values under different account systems, producer instances, source types, and key epochs do not collide.
- Retry, changed-revision, and sequence-reset fixtures prove the Bundle event rule; the Provenance entry has a typed node key, not a business identifier.
- Every provider example matches exactly one grammar and NamingSystem description.
- No artifact calls a clear value a digest.

### VF-06 — Critical clinical decision — Hypertension is marked supported while its own adapter requirement argues that emission fabricates a finding

**Evidence**

The HealthKit adapter marks `HKCategoryTypeIdentifierHypertensionEvent` supported and assigns the generated `healthkit-hypertension-notification` profile at `/Users/paulschmiedmayer/Developer/grove-fhir/catalog/healthkit-adapter.json:677-690`. The same row's normative `requirement` says that emitting it as an Observation would fabricate a blood-pressure-adjacent finding with no quantity.

The generated profile now deliberately models a proprietary screening notification rather than a diagnosis at `/Users/paulschmiedmayer/Developer/grove-fhir/healthkit/input/fsh/generated-measurement-profiles.fsh:1035-1047`. The measurement definition nevertheless says it is “a device notification of blood-pressure readings consistent with hypertension” at `/Users/paulschmiedmayer/Developer/grove-fhir/catalog/measurement-catalog.json:3550-3587`. The final observed `npm test` run passes because the generated FSH, allowlist, and built-package artifacts have been synchronized; mechanical parity cannot decide whether the clinical representation is admissible.

The new completeness test makes every `HKCategoryTypeIdentifier*Event` share the same supported status solely from its name suffix at `/Users/paulschmiedmayer/Developer/grove-fhir/Tests/test_conversion_completeness.py:20-35`. Peer naming is not clinical evidence that hypertension, high/low heart rate, and other proprietary notifications have the same admissible FHIR meaning.

**Impact**

All generated layers can agree while the source row simultaneously says the output is supported and should not be emitted. Consumers may interpret a hypertension-coded Observation more strongly than the intended proprietary notification, particularly when the underlying pressure readings are absent.

**Breaking change**

Obtain an accountable clinical/FHIR terminology decision. If admitted, model and name this strictly as a source-specific screening-notification event, keep it disjoint from diagnosis and blood-pressure measurements, and remove the contradictory anti-emission requirement. If that meaning cannot be defended, mark it unsupported or source-preservation-only. Then regenerate every derived artifact from the decided source.

**Acceptance criteria**

- The adapter requirement, measurement definition, terminology review, profile description, examples, status matrix, and SDK behavior express one non-diagnostic meaning.
- Negative semantic fixtures prevent diagnosis, measured blood pressure, or inferred quantitative result claims.
- A clinical/terminology review record identifies accountable approval for the release.
- `npm test` and a clean rebuild remain green after the semantic decision.

### VF-07 — High — The generic retained-metadata extension is neither lossless nor integrated with the existing HealthKit contract

**Evidence**

`HealthKitRetainedMetadata` promises every unmodelled `HKSample.metadata` entry is carried “verbatim,” under the exact key and “in the shape it carried,” at `/Users/paulschmiedmayer/Developer/grove-fhir/healthkit/input/fsh/extensions.fsh:135-146`. Its value choices are only `string`, `boolean`, `Quantity`, and `dateTime`; it has no numeric source-type discriminator or lexical rule, and it is valid only on Observation. It is not sliced into `HealthKitObservation`, has no cardinality or key-uniqueness/disjointness invariant there, and has no example covering its type choices.

The published mapping says the opposite: “There is no generic metadata extension”; each new key requires a semantic purpose, typed representation, allowlist, and examples at `/Users/paulschmiedmayer/Developer/grove-fhir/healthkit/input/pagecontent/mapping.md:185-209`. Terminology provenance describes a closed residual allowlist of two keys at `/Users/paulschmiedmayer/Developer/grove-fhir/healthkit/input/data/terminology-provenance.json:58-60`.

The new test reads every `HKMetadataKey...` token from the adjacent Swift retained-metadata file—combining its “modelled” and “linkable” sets—and checks only that keys mentioned by any other converter occur somewhere in that union at `/Users/paulschmiedmayer/Developer/grove-fhir/Tests/test_conversion_completeness.py:38-55`. It skips when the ignored `stack/Grove` checkout is absent. It therefore proves neither per-path modelled/retained disjointness nor value-type coverage, lexical fidelity, duplicate-key rejection, presence, serialization stability, or a round trip.

**Impact**

“Verbatim” is a cross-language promise the profile cannot establish. Numeric Foundation values cannot be reconstructed in their original shape from a Quantity without a documented discriminator and canonicalization rule. Non-Observation HealthKit outputs remain outside the extension context. The current source contract and published guide directly contradict each other.

**Breaking change**

Choose one of two defensible models:

1. Continue semantic allowlisting: define typed, reviewed key-specific elements/extensions and fail closed or explicitly report dropped unknowns.
2. Preserve an opaque source metadata payload: publish a versioned canonical serialization with source datatype tags, numeric lexical rules, ordering, duplicate handling, Unicode rules, privacy classification, and exact bytes/hash, then carry it as an immutable recording/source artifact rather than pretending a small FHIR datatype union is verbatim.

If a generic complex extension remains, close its subextension slicing, define exact source types and conversions, apply it to every relevant output context, and prohibit a key already modeled elsewhere with an executable invariant.

**Acceptance criteria**

- Authoritative platform type inventory and one round-trip vector for every supported source type.
- Duplicate keys and typed-key overlap fail.
- Swift/Kotlin/TypeScript preserve semantically identical typed extension values under lossless JSON/XML parsers; require FHIR wire-byte equality only if Grove defines canonical serializers, or carry identical opaque metadata bytes instead.
- Published mapping, terminology provenance, extension, implementation behavior, and privacy guidance agree.

### VF-08 — High — Application OS version is placed on the software Device despite the guide's explicit host separation

**Evidence**

The dirty profile adds `applicationBuild` and `operatingSystemVersion` as `GroveApplicationDevice.version` slices at `/Users/paulschmiedmayer/Developer/grove-fhir/mobile/input/fsh/profiles.fsh:165-179`; the new terminology defines `os-version` at `/Users/paulschmiedmayer/Developer/grove-fhir/mobile/input/fsh/terminology.fsh:176-192`.

The normative device page distinguishes application and host resources at `/Users/paulschmiedmayer/Developer/grove-fhir/mobile/input/pagecontent/devices.md:9-18`, says the host is linked through `Device.parent` at `:79-83`, and explicitly says operating-system and host-hardware versions belong on a separate host Device and must not be added to the application-version slice at `:85-86`. The same page still says separate release/build values use one deterministic serialization, not multiple entries, at `:71-75`.

**Impact**

The wire meaning is ambiguous: an application Device now asserts a host OS version, while the guide tells consumers that host facts live on its parent. It also prevents precise platform/product coding for the host.

**Breaking change**

Add a constrained `GroveHostDevice` profile, put OS name/version and host hardware there, and link it with application `Device.parent`. Keep application marketing version and build as separate, explicitly typed application facts. Decide whether the application Device is a product, build, installation, or execution snapshot and make its identity match that lifecycle.

**Acceptance criteria**

- Application example with separate marketing/build slices and parent host.
- Host example with coded OS product and version.
- Negative official-Validator fixture for OS version on the application slice.
- Identical host/application separation in all SDK builders.

### VF-09 — High — The recording Device identity contract is not represented by the FHIR profile and cannot safely identify a physical instance

**Evidence**

The machine identity uses subject reference, adapter, manufacturer, model, and hardware version and claims this deduplicates a recorder across Observations at `/Users/paulschmiedmayer/Developer/grove-fhir/catalog/exchange-identity.json:25-82`. It excludes firmware/software from both identity and the shared Device and says each Observation states the versions in force at `:28`.

The `GroveRecordingDevice` profile leaves `identifier` optional, provides no required system/slice for this algorithm, and does not require `Device.patient` at `/Users/paulschmiedmayer/Developer/grove-fhir/mobile/input/fsh/profiles.fsh:133-148`. The canonical example supplies manufacturer/model/firmware but no identifier or patient at `/Users/paulschmiedmayer/Developer/grove-fhir/mobile/input/fsh/examples.fsh:70-82`. No NamingSystem is published for the derived recording-device identity.

The device page says each Observation states recording-time firmware/software at `/Users/paulschmiedmayer/Developer/grove-fhir/mobile/input/pagecontent/devices.md:35-56`, but no Observation element or Grove extension carries those facts. HealthKit mapping instead tells producers to put hardware, firmware, and software versions on the Device at `/Users/paulschmiedmayer/Developer/grove-fhir/healthkit/input/pagecontent/mapping.md:120-131`, and its example does so at `/Users/paulschmiedmayer/Developer/grove-fhir/healthkit/input/fsh/examples.fsh:55-67`.

Even if implemented exactly, a model-level tuple cannot distinguish two same-model, same-hardware-version devices used by one participant. In FHIR R4, `Device` represents an instance; the tuple establishes equivalence of descriptions, not physical identity. The use of repository-relative `Patient/…` references in identity vectors also makes cross-repository stability depend on a repository logical ID that the same contract says is optional and not source identity at `/Users/paulschmiedmayer/Developer/grove-fhir/catalog/exchange-identity.json:15-18,39-71`.

**Impact**

Implementers cannot emit a Device that proves conformance to the claimed identity. The algorithm can merge distinct physical devices and can change across repositories.

**Breaking change**

Require an evidenced stable per-unit token to deduplicate a physical Device. When it is unavailable, omit the Device, retain a record-scoped source description, or explicitly model a device model/type rather than asserting physical instance identity. If a privacy-preserving derived identity remains, publish its NamingSystem, require its identifier slice and subject link, and derive from a stable subject business identifier rather than a relative Resource.id. Choose a version-at-measurement model: immutable per-version Device identities or a typed Observation/source extension, but not mutable shared Device state.

**Acceptance criteria**

- Same participant with two identical models does not collide.
- Resource renaming/migration does not change derived business identity.
- Official Validator requires the selected identity slice and patient/subject relationship.
- Cross-language vectors cover absent device, insufficient evidence, same model/two instances, and firmware update/backfill.

### VF-10 — High — Shared writer identity and adapter identity regexes are materially weaker than their normative grammars

**Evidence**

The shared writer description forbids `|` in either component, but its regex permits additional bars after the first at `/Users/paulschmiedmayer/Developer/grove-fhir/mobile/input/fsh/profiles.fsh:220-223`. The defect is duplicated in HealthKit, Health Connect, and Providers at:

- `/Users/paulschmiedmayer/Developer/grove-fhir/healthkit/input/fsh/profiles.fsh:9-12`;
- `/Users/paulschmiedmayer/Developer/grove-fhir/health-connect/input/fsh/profiles.fsh:9-12`; and
- `/Users/paulschmiedmayer/Developer/grove-fhir/providers/input/fsh/profiles.fsh:9-12`.

At minimum the described grammar is `^v1:[A-Za-z0-9._-]+[|][^|]+$`. The base Mobile profile declares only the version extension; adapters separately add the writer identifier and their pair invariants, so the common contract is not actually common at `/Users/paulschmiedmayer/Developer/grove-fhir/mobile/input/fsh/profiles.fsh:48-83`.

The provider route also claims to use this shared writer identity but composes `providerCode|sourceNativeId` at `/Users/paulschmiedmayer/Developer/grove-fhir/catalog/providers-adapter.json:139-145`; its example emits `v1:withings|17348211` at `/Users/paulschmiedmayer/Developer/grove-fhir/providers/input/fsh/examples.fsh:117-126`. The NamingSystem requires the first component to be the writing application's reverse-DNS identifier at `/Users/paulschmiedmayer/Developer/grove-fhir/mobile/input/fsh/naming-systems.fsh:7-20`.

Health Connect record/output/specimen FSH uses a generic two-plus-component regex at `/Users/paulschmiedmayer/Developer/grove-fhir/health-connect/input/fsh/profiles.fsh:14-27`, despite exact arities in its identity JSON. SensorKit uses the same broad shape at `/Users/paulschmiedmayer/Developer/grove-fhir/sensorkit/input/fsh/profiles.fsh:14-17`. Provider accepts either any no-bar string or any two-plus-component value at `/Users/paulschmiedmayer/Developer/grove-fhir/providers/input/fsh/profiles.fsh:14-17`.

**Impact**

Official profile validation admits values that the machine contracts and language helpers reject. Provider cannot make the cross-route writer equality claim without evidence of an actual reverse-DNS writer application identifier.

**Breaking change**

Move the writer identifier slice and version-pair invariant into Mobile, inherit it once, and delete duplicated invariant definitions. Remove provider writer identity unless the provider source actually supplies the writer namespace required by the shared contract. Use exact adapter-specific structured parsers; FHIRPath regexes should be a defense-in-depth projection of the same machine grammar.

**Acceptance criteria**

- Official Validator rejects extra/missing/empty components and extra bars.
- Provider example either carries a valid writer application ID or no writer identity.
- There is one invariant definition, one NamingSystem, one machine grammar, and one shared vector corpus.

### VF-11 — High — Clinical-record payload release, media format, identity, and provenance do not form a coherent contract

**Evidence**

The format registry says `fhir-resource` means exactly one FHIR **R4** resource and that another FHIR release is not admitted at `/Users/paulschmiedmayer/Developer/grove-fhir/catalog/format-registry.json:412-422`. The HealthKit clinical-release CodeSystem admits both DSTU2 and R4 at `/Users/paulschmiedmayer/Developer/grove-fhir/healthkit/input/fsh/terminology.fsh:218-233`. The clinical DocumentReference fixes every attachment to `application/fhir+json` and the R4-only `fhir-resource` format while allowing either release extension at `/Users/paulschmiedmayer/Developer/grove-fhir/healthkit/input/fsh/profiles.fsh:116-149`.

The profile requires only an unsliced identifier, not exactly one HealthKit object ID with the UUID invariant. `HealthKitConversionProvenance.target` permits only `HealthKitObservation`, not this DocumentReference, at `/Users/paulschmiedmayer/Developer/grove-fhir/healthkit/input/fsh/profiles.fsh:101-139`. The clinical example says Grove asserts identity and provenance but contains no Provenance at `/Users/paulschmiedmayer/Developer/grove-fhir/healthkit/input/fsh/examples.fsh:428-446`. HealthKit's target-profile claim list similarly covers Observation/ECG only at `/Users/paulschmiedmayer/Developer/grove-fhir/catalog/profile-claims.json:72-82`.

**Impact**

A DSTU2 payload can validate with a code whose normative registry says R4 only. The pass-through document lacks the same exact identity and conversion/source graph guarantees advertised for HealthKit outputs.

**Breaking change**

Publish release-specific format codes (for example `fhir-r4-resource` and `fhir-dstu2-resource`) or an equally explicit, machine-validated media-type/version model. Add an invariant binding payload release to format. Slice and constrain the HealthKit object identifier on the DocumentReference. Add a dedicated clinical-document provenance profile/claim, or explicitly and consistently state that this is source preservation rather than a Grove conversion event. Define large-payload behavior: base R4 makes `Attachment.size` optional, counts pre-base64 payload bytes, and types it as `unsignedInt` with maximum 2,147,483,647; Grove's exact-size profiles therefore must reject larger recordings with a stable rule or use an explicit segmentation/manifest contract ([official R4 datatypes](https://hl7.org/fhir/R4/datatypes.html)). `Attachment.hash` is base64 of SHA-1 over those pre-base64 bytes.

**Acceptance criteria**

- Positive DSTU2 and R4 pass-through examples and negative cross-pair fixtures.
- Exact object identity required by official Validator.
- Complete Bundle example with the chosen source/provenance relationship.
- Byte-preservation test verifies data, size, and hash for each release.
- Boundary fixtures at the maximum attachment size and immediately above it exercise the selected reject-or-segment rule.

### VF-12 — High — The machine package graph is not the dependency graph declared by SUSHI

**Evidence**

The schema says the graph states what each package depends on and requires exact pins at `/Users/paulschmiedmayer/Developer/grove-fhir/catalog/schemas/package-graph.schema.json:3-32`. The graph omits direct dependencies declared in the guide configurations:

- Sensor graph at `/Users/paulschmiedmayer/Developer/grove-fhir/catalog/package-graph.json:121-128` omits `hl7.fhir.uv.extensions.r4#5.3.0`, declared at `/Users/paulschmiedmayer/Developer/grove-fhir/sensor/sushi-config.yaml:36-41`.
- SensorKit graph at `/Users/paulschmiedmayer/Developer/grove-fhir/catalog/package-graph.json:137-144` omits the extension package declared at `/Users/paulschmiedmayer/Developer/grove-fhir/sensorkit/sushi-config.yaml:35-43`.
- HealthKit graph at `/Users/paulschmiedmayer/Developer/grove-fhir/catalog/package-graph.json:163-170` omits the extension package declared at `/Users/paulschmiedmayer/Developer/grove-fhir/healthkit/sushi-config.yaml:37-45`.
- Providers graph at `/Users/paulschmiedmayer/Developer/grove-fhir/catalog/package-graph.json:313-319` omits both `hl7.terminology.r4#7.3.0` and `hl7.fhir.uv.extensions.r4#5.3.0`, declared at `/Users/paulschmiedmayer/Developer/grove-fhir/providers/sushi-config.yaml:35-43`.

The package-graph test checks shape, sort order, and canonical form but does not compare dependencies with `sushi-config.yaml` or built `package/package.json` at `/Users/paulschmiedmayer/Developer/grove-fhir/Tests/test_package_graph.py:20-45`.

**Impact**

Downstream Swift/Kotlin/TypeScript consumers reading the graph do not receive the build graph SUSHI uses. It is unclear whether `dependencies` means direct declared dependencies or a resolved closure.

**Breaking change**

Generate the graph from a release manifest/SUSHI configuration and built package metadata. Define separate `directDependencies` and `resolvedDependencies` if both are useful; otherwise document exclusions such as core explicitly.

**Acceptance criteria**

- CI exact-compares graph, all `sushi-config.yaml` files, and every built `package.json`.
- No manually duplicated package version pins.
- Dependency closure installation succeeds in an empty offline cache populated only from the release bundle.

### VF-13 — High — Version drift remains in normative prose and tooling despite a passing content check

**Evidence**

Current package/guide version is 0.5.0, but:

- `/Users/paulschmiedmayer/Developer/grove-fhir/README.md:19,35-36` calls the current contract/graph 0.3.0.
- `/Users/paulschmiedmayer/Developer/grove-fhir/Conformance/README.md:7-18,49-53` gives 0.3.0 packages and validator contract.
- `/Users/paulschmiedmayer/Developer/grove-fhir/PUBLICATION.md:13-15` calls 0.3.0 the coordinated implementation contract.
- `/Users/paulschmiedmayer/Developer/grove-fhir/health-connect/input/pagecontent/implementation.md:20-27` lists 0.5.0 packages and then says Health Connect pins Mobile 0.3.0.
- `/Users/paulschmiedmayer/Developer/grove-fhir/health-connect/input/pagecontent/mapping.md:108-110` refers to a shared 0.3.0 profile.
- `/Users/paulschmiedmayer/Developer/grove-fhir/Scripts/build-guides.sh:75-91` copies current local packages under `*-0.3.0.tgz` filenames.
- `/Users/paulschmiedmayer/Developer/grove-fhir/Scripts/validate-producer.py:1581` describes “v0.3” SampledData semantics.

`Scripts/check-content.py` obtains all tracked files at `/Users/paulschmiedmayer/Developer/grove-fhir/Scripts/check-content.py:84-89`, but scans version prose only in guide FSH/pagecontent globs at `:154-173`. It therefore passes while root documentation, Conformance, and scripts remain stale; its expression also misses some bare-version prose.

**Impact**

Implementers can install or claim the wrong package generation. Passing CI creates false confidence that release pins are synchronized.

**Breaking change**

Create one release manifest containing IG version, FHIR version, package IDs, canonicals, direct dependencies, catalog schema generations, and publication label. Generate configs, package graph, installation snippets, and release asset names from it. Scan every normative tracked text file, with a narrow allowlist for explicitly historical provenance.

**Acceptance criteria**

- No current-version literal outside the manifest or generated output.
- A repository-wide stale-version mutation test catches README, script filename, JSON prose, FSH, and pagecontent cases.
- All seven packages and all consumer-manifest examples move to 0.6.0 in one atomic change.

### VF-14 — High — Publication and release automation do not implement the repository's own immutable-release requirements

**Evidence**

`/Users/paulschmiedmayer/Developer/grove-fhir/publication/config.json:1-7` is `ci-build-only`. All guide configs are 0.5.0 with `releaseLabel: ci-build`; examples include Mobile at `/Users/paulschmiedmayer/Developer/grove-fhir/mobile/sushi-config.yaml:9-20` and HealthKit at `/Users/paulschmiedmayer/Developer/grove-fhir/healthkit/sushi-config.yaml:9-19`. No guide contains `publication-request.json`.

The repository documents the prerequisites for an immutable release—including canonical-host resolution, publication requests, publication-mode build, publication branch, QA, checksums, and non-overwrite behavior—at `/Users/paulschmiedmayer/Developer/grove-fhir/PUBLICATION.md:98-123`. It also states the canonical host is not served yet at `:42-44`.

The deployment workflow instead runs `npm run pages:build` and `npm test`, copies only `.tgz` packages, and uploads them at `/Users/paulschmiedmayer/Developer/grove-fhir/.github/workflows/deployment.yml:121-175`. It does not call `Scripts/build-release.sh`, promote version directories, or attach the documented QA/checksum set. For an existing release it uses `gh release upload --clobber` at `:170-175`, allowing a released asset to be replaced.

**Impact**

Calling this path “0.6.0 release” would not produce an immutable canonical IG release and could replace bits under an existing release tag.

**Breaking change**

Implement one release workflow that starts from a clean, tagged commit; performs publication-mode builds once; verifies live canonical hosting; promotes immutable version directories; attaches packages, semantic diffs, QA, checksums, and build provenance; and refuses any overwrite. Keep preview deployment separate.

**Acceptance criteria**

- Canonical `https://grovealliance.org/fhir/...` routes resolve HTML plus canonical JSON/XML/Turtle and package lists.
- Tag, package version, IG version, package-list entry, checksum manifest, and commit SHA agree.
- Re-running a release fails closed instead of clobbering an asset or version directory.
- Release dry-run starts with an empty cache and clean worktree and produces byte-identical package artifacts on repeat.

### VF-15 — High — “Offline reproducibility” contradicts the actual build path

**Evidence**

`/Users/paulschmiedmayer/Developer/grove-fhir/PUBLICATION.md:49-57` says Publisher and Validator runs execute without network access. `/Users/paulschmiedmayer/Developer/grove-fhir/Scripts/build-guides.sh:57-68` defaults to `https://tx.fhir.org`; only `GROVE_TX_OFFLINE` adds `-tx n/a -no-network`. The deployment workflow does not set that offline switch at `/Users/paulschmiedmayer/Developer/grove-fhir/.github/workflows/deployment.yml:121-132`.

Isolated SUSHI checks attempted registry/latest resolution and warned about automatically provided `hl7.fhir.uv.tools.r4#latest`. This is observable tool behavior even though exact declared dependencies were otherwise loaded from the cache.

**Impact**

Build outcome can depend on network availability and mutable terminology service behavior while publication prose promises otherwise. Conversely, a truly offline build cannot perform the same external terminology validation as an online terminology server.

**Breaking change**

Define two explicit lanes: a deterministic offline structural/package lane and an online, pinned-policy terminology-validation lane. Record the terminology server, request policy, and result evidence used for release. Never silently fall back between them, and do not claim the online lane is offline.

**Acceptance criteria**

- Network-disabled offline build succeeds from a declared cache and produces deterministic packages.
- Online terminology lane fails closed on unavailable service and stores a reviewable result ledger.
- No dependency is resolved through `latest` in a release build.

### VF-16 — High — Important SampledData semantics live only in a repository-specific validator

**Evidence**

The sensor guide requires at least two complete frames, token count divisible by dimensions, and exact `effectivePeriod.end = start + (F - 1) × period` at `/Users/paulschmiedmayer/Developer/grove-fhir/sensor/input/pagecontent/waveforms.md:9-22`. The FSH profile checks only decimal token syntax, positive period, and positive dimensions at `/Users/paulschmiedmayer/Developer/grove-fhir/sensor/input/fsh/profiles.fsh:9-53`. The custom Python validator enforces the omitted frame and timing rules at `/Users/paulschmiedmayer/Developer/grove-fhir/Scripts/validate-producer.py:1576-1628`.

The Mobile implementation page does explain that official validation cannot prove all source semantics and points producer CI to the wrapper at `/Users/paulschmiedmayer/Developer/grove-fhir/mobile/input/pagecontent/implementation.md:65-89`, but package-only consumers can still reasonably believe that satisfying the published StructureDefinition is satisfying the waveform contract.

**Impact**

Swift/Kotlin/TypeScript consumers that use only the official Validator accept malformed frames and timing. The conformance boundary is not machine-readable in the package.

**Breaking change**

Encode portable constraints in FHIRPath where the R4 engine supports them, and designate the remaining graph/numeric rules as a named, versioned “Grove producer conformance” layer. Package its corpus and expected rule IDs as normative artifacts rather than Python behavior alone.

**Acceptance criteria**

- Official Validator rejects every constraint that is expressible portably.
- The normative semantic corpus covers the rest with exact expected rule IDs.
- All four validators/SDK suites consume the same corpus, including fractional precision and timezone cases.

### VF-17 — High — The PPG binary format is not canonically serializable across languages

**Evidence**

The format registry defines a set as elements whose order is not significant at `/Users/paulschmiedmayer/Developer/grove-fhir/catalog/format-registry.json:446-458`, then encodes `activePhotodiodeIndexes` as that set at `:494-504`. No canonical element order is specified. The binary64 rule at `:452-455` does not define whether NaN, infinities, or negative zero are allowed/canonicalized. Strings have no normalization policy.

The repository's own breaking-change memo records a real nondeterminism caused by iterating dictionary-like data in implementation order at `/Users/paulschmiedmayer/Developer/grove-fhir/Documentation/next-breaking-change.md:96-109`.

**Impact**

The same logical PPG record can produce different payload bytes, hashes, DocumentReference identities, and retry behavior in Swift, Kotlin, and TypeScript.

**Breaking change**

Specify sets as sorted ascending unique values before encoding. Define or reject all non-finite float cases and negative zero. Define exact UTF-8/Unicode policy. Better, publish a formal schema and a reference encoder/decoder contract with golden byte fixtures.

**Acceptance criteria**

- Golden bytes and hashes for empty, singleton, reordered, duplicate, boundary integer, negative-zero, non-finite, and non-ASCII cases.
- Every language produces exactly the golden payload and rejects the same non-canonical encodings.

### VF-18 — Medium — Health Connect output cardinalities are often internally contradictory

**Evidence**

Many one-record/one-output rows say `cardinality: 0..*` and simultaneously `onePer: record`, for example Basal Metabolic Rate at `/Users/paulschmiedmayer/Developer/grove-fhir/catalog/health-connect-adapter.json:153-161`, Body Fat Percentage at `:215-223`, and Resting Heart Rate at `:765-775`. The generated status matrix exposes this as “0..*; one per record” at `/Users/paulschmiedmayer/Developer/grove-fhir/health-connect/input/pagecontent/status-matrix.md:48`.

**Impact**

Consumers cannot know whether zero, one, or multiple outputs are valid. It complicates conditional output-ID requirements and retraction completeness.

**Breaking change**

Use an explicit closed output algebra: `exactlyOne`, `zeroOrOne`, `onePerSample`, `onePerStage`, `onePerPresentField`, and so on. Generate both human cardinality and validation behavior from it.

**Acceptance criteria**

- Every supported Record has an executable output-count rule.
- Mutation fixtures cover missing, duplicate, and extra outputs.

### VF-19 — Medium — Several generated/profile constraints promise semantics they do not enforce

**Evidence**

The unspecified-specimen glucose profile says specimen “REQUIRES ... ABSENT,” but has no `* specimen 0..0` rule at `/Users/paulschmiedmayer/Developer/grove-fhir/mobile/input/fsh/generated-measurement-profiles.fsh:262-275`. A resource may therefore carry a Specimen while claiming the unspecified-specimen profile.

HealthKit and Health Connect redeclare the inherited `writerRecordVersion` slice at `/Users/paulschmiedmayer/Developer/grove-fhir/healthkit/input/fsh/profiles.fsh:39-55` and `/Users/paulschmiedmayer/Developer/grove-fhir/health-connect/input/fsh/profiles.fsh:65-95`, even though Mobile already declares it at `/Users/paulschmiedmayer/Developer/grove-fhir/mobile/input/fsh/profiles.fsh:48-54`. An isolated HealthKit SUSHI build warned that the named slice already exists.

**Impact**

The glucose profile is not semantically disjoint as advertised; duplicated slices add warning noise and risk differential/snapshot surprises.

**Breaking change**

Add `specimen 0..0` to the generated unspecified profile. Constrain inherited slices by name instead of re-adding them, and fail CI on unexpected SUSHI warnings.

**Acceptance criteria**

- Official Validator rejects any specimen on the unspecified profile.
- SUSHI runs with zero unexpected warnings for every guide.

### VF-20 — Medium — Normative machine catalogs lack schemas and use four incompatible adapter shapes

**Evidence**

Only measurement catalog and package graph have JSON Schemas under `/Users/paulschmiedmayer/Developer/grove-fhir/catalog/schemas/`. `format-registry.json`, `exchange-identity.json`, `health-connect-identity.json`, `profile-claims.json`, and the adapter catalogs have no `$schema` and are checked by bespoke partial tests. Adapter collections use different top-level keys (`rows`, `recordTypes`, `entries`, `providers`), as also observed at `/Users/paulschmiedmayer/Developer/grove-fhir/Documentation/next-breaking-change.md:134-141`.

The current identity/example defects demonstrate that partial tests do not establish cross-file referential integrity.

**Impact**

Swift/Kotlin/TypeScript consumers must each hand-code a different parser and rediscover conditional invariants. Schema evolution is tied informally to IG version.

**Breaking change**

Publish JSON Schema 2020-12 for every normative catalog, with `additionalProperties: false`, discriminated unions, canonical URI formats, exact conditional fields, and a separate catalog-schema version. Normalize adapter data under a shared `sourceTypes` model while retaining adapter-specific payloads in typed variants. Generate language models and cross-file checks.

**Acceptance criteria**

- Every catalog declares and validates against a schema.
- Unknown fields, unknown status, incomplete identity variant, and dangling profile/measurement/canonical references fail.
- Generated Swift/Kotlin/TypeScript decoders accept/reject the same schema fixtures.

### VF-21 — Low — Terminology metadata contains stale or insufficient provenance even though code/unit gates are strong

**Evidence**

`/Users/paulschmiedmayer/Developer/grove-fhir/catalog/terminology/loinc-concepts.json:5` says all 17 rows were checked, while the current pin contains 66 concepts and the terminology gate reports 66 pinned concepts. Many terminology review entries still use `ratification: pending-pull-request-review` and `reviewRef: pending-integration-commit`; one example is `/Users/paulschmiedmayer/Developer/grove-fhir/mobile/input/data/terminology-reviews.json:4299-4319`.

The new hypertension review is owner-approved and records a digest at `/Users/paulschmiedmayer/Developer/grove-fhir/mobile/input/data/terminology-reviews.json:1896-1904`, but it does not yet include the same structured reviewer roles/review reference used by mature entries.

**Impact**

The terminology set is mechanically well controlled, but an auditor cannot reproduce exactly which authoritative lookup result and accountable clinical/terminology review ratified every release concept.

**Breaking change**

Require immutable commit/PR references, structured accountable reviewer roles, version-aware terminology evidence, and no pending ratification state in a release. Correct generated counts from data.

**Acceptance criteria**

- Every used concept has release-version evidence and a non-pending review record where clinical judgment was required.
- Counts and prose are generated from the pin files.

## Design recommendations for a breaking 0.6.0

The following are recommendations rather than proven current validation failures.

### DR-01 — Make the release manifest the sole authority

One checked-in release manifest should own:

- IG/package/catalog version;
- FHIR release;
- package ID and canonical per guide;
- direct package dependencies;
- publication label/status/path;
- catalog schema generations; and
- the exact commit/tag provenance.

Generate `sushi-config.yaml` version/dependency fragments, package graph, release asset names, installation prose, validation manifest examples, and package-list entries. This removes most current drift classes.

### DR-02 — Use structured identity fields internally, serialize only at the wire boundary

Each adapter identity should be a discriminated structured type such as `HealthConnectRecordIdentity` or `SensorKitSampleOutputIdentity`, not a free-form string passed among builders. Define fixed arity, allowed characters, component semantics, and version once. Encode/decode the `Identifier.value` at the edge. Use versioned length-framed UTF-8 input for arbitrary platform fields; do not reject valid source data merely because it contains an internal separator. Delimiter composition is acceptable only for Grove-controlled domains that normatively exclude the delimiter and have exact parsers.

### DR-03 — Define entry-identifier selection for every resource type

The UUIDv5 Bundle algorithm is sound only after the selected `(system,value)` pair is deterministic. Publish a priority/role rule for every admitted entry resource type, including Patient, Device, Observation, Specimen, DocumentReference, and Provenance (which lacks a native business identifier in R4). Require the entry identity to equal the selected resource business identity where one exists; otherwise require a typed event-scoped node key. Split or redefine the current entry extension before doing so because it calls every value a complete business identifier. Keep `Bundle.identifier` as the separate event identity. Add collision and multiple-identifier fixtures.

### DR-04 — Separate source preservation from semantic projection

The strongest Grove pattern is the SensorKit hybrid: a semantic Observation plus an immutable source recording when the projection is not lossless. Generalize that pattern rather than adding loosely typed residual extensions. A source-preservation artifact should state schema, exact bytes, source identity, privacy/admission assertion, and hash; the semantic resource should state only reviewed FHIR meaning.

### DR-05 — Clarify three conformance levels

Publish a machine-readable conformance declaration:

1. **FHIR R4 conformance:** base schema and terminology.
2. **Grove profile conformance:** StructureDefinitions, bindings, and FHIRPath.
3. **Grove producer conformance:** cross-resource graph, source mapping, deterministic identity, exact registered identity/payload bytes, semantic vectors, and lifecycle completeness.

Every normative sentence should name its level and validator. Do not say “the profile requires” when only Python code enforces it.

### DR-06 — Treat mutable device/application snapshots explicitly

Decide whether a Device is an enduring instance, a versioned configuration, or an event-time snapshot. For immutable exchange, a practical model is an enduring physical/app product identity plus a separate observation/provenance snapshot of firmware/software/OS/build in effect. Do not mutate a shared Device while importing historical records out of order.

### DR-07 — Prefer standard FHIR collections for FHIR resources

`fhir-resource-array` at `/Users/paulschmiedmayer/Developer/grove-fhir/catalog/format-registry.json:401-410` invents a bare JSON array of FHIR resources. Unless byte compatibility with an upstream source requires that exact shape, prefer a standard FHIR `Bundle` with an explicit type and profile. It brings base validation, resource identity, and reference semantics for free.

### DR-08 — Tighten QuestionnaireResponse canonical version semantics

`gqr-canonical-1` proves only `url|nonempty` at `/Users/paulschmiedmayer/Developer/grove-fhir/questionnaire/input/fsh/profiles.fsh:99-102`. If Grove requires an exact instrument version, constrain the version lexical form and use pair-level validation to prove it equals the referenced/resolved Questionnaire version. This is not a demonstrated current failure, but 0.6.0 is the right time to eliminate an underspecified canonical contract.

### DR-09 — Make unsupported/deferred status semantically precise

Use a closed status vocabulary that distinguishes:

- source not inventoried;
- inventoried but no FHIR meaning designed;
- deliberately refused because representation would be misleading;
- structurally representable but blocked on terminology/evidence;
- supported semantic projection;
- supported only as opaque source preservation; and
- supported hybrid requiring both.

This avoids calling a partial projection simply `supported` and gives SDK generators an executable output obligation.

## Unknowns requiring explicit decisions

### U-01 — Clinical admissibility of hypertension notification

The repository has an owner-approved terminology projection, but the adapter requirement still argues against emission. A FHIR/clinical terminology reviewer should decide whether this is an admissible source-specific screening event, how it differs from a diagnosis and blood-pressure measurement, and whether `Observation` is the right resource. If admitted, all narrative must state that it is a device notification and never a diagnosis.

### U-02 — Source identifier privacy policy

Health Connect and Providers alternately promise opaque digest identities and publish clear source values. Decide whether disclosure minimization is a requirement. If yes, specify a keyed deployment-scoped derivation, collision/security properties, key epoch/rotation, and linkage consequences. If no, remove every non-exposure claim and document that FHIR business identifiers may be indexed and linkable.

### U-03 — Exact HealthKit metadata type universe

The repository does not contain an authoritative inventory of every value type accepted or returned by `HKSample.metadata`, nor the desired behavior for custom writer keys. That inventory and privacy analysis must precede any “verbatim” promise.

### U-04 — Retraction target and sink semantics

Confirm the recommended dedicated lifecycle Provenance event, then decide whether it asserts completed removal of prior Grove outputs (`v3-DataOperation#DELETE`), the narrower `#NULLIFY` meaning, or a Grove application operation; whether it targets a logical output, exact revision, or whole source-derived graph; and how each repository resolves and applies it atomically/idempotently. A collection Bundle/Provenance is not itself a delete command. Keep repository projections separate from the transport assertion.

### U-05 — Canonical-host ownership and release governance

The docs explicitly say `grovealliance.org` is not served. A real release needs an owner, TLS/DNS deployment, permanence policy, package-list history, correction policy, and approval path. Until then, label outputs CI previews rather than immutable releases.

### U-06 — External terminology reproducibility

The pin files are strong, but SNOMED/LOINC validation through a public server can vary by edition/configuration. Decide which licensed terminology environment and edition evidence is authoritative for release acceptance.

### U-07 — Producer-validator normative status

The current docs sometimes present Python checks as the contract and sometimes present the package as the contract. Decide whether `Scripts/validate-producer.py` is a normative reference implementation, one implementation of a language-neutral corpus, or merely repository CI. The recommended answer is the second.

## Positive aspects to preserve

- **FHIR release discipline:** guide configurations consistently target R4 `4.0.1`; package IDs and canonical roots are generally coherent.
- **Layering of clinical and adapter meaning:** shared Mobile/Sensor profiles versus adapter lineage profiles is a good architecture. It avoids cloning clinical profiles for every source.
- **Use of authoritative profiles:** `structuredefinition-imposeProfile` is used to retain standard vital-sign expectations rather than approximating them in Grove-only profiles.
- **Identity versus Resource.id:** the project correctly treats `Resource.id` as repository-local and business `Identifier` as the synchronization surface.
- **Provenance roles:** conversion Provenance uses standard lifecycle `transform` and assembler participation, with source entities and target graphs rather than vague app metadata.
- **Source inventory honesty:** adapter catalogs enumerate supported, deferred, and unsupported source concepts and often explain why a mapping is unsafe.
- **Terminology and units:** exact LOINC/UCUM/SNOMED pins, code/display checks, dimension checks, and terminology gates are substantially stronger than typical early-stage IGs.
- **Generated profile catalog:** generating measurement profiles/examples from a machine catalog is the right direction and already prevents many unit/effective-time drifts.
- **Negative corpora:** deterministic patches, exact expected rule IDs, graph checks, decimal precision preservation, and package semantic diff tests are excellent foundations.
- **Fail-closed custom validation:** the producer validator has strong checks for internal UUID references, profile-claim modes, SampledData timing, ECG completeness, raw attachment hashes, and specimen meanings.
- **Artifact allowlisting:** the gate caught a half-regenerated intermediate worktree during the audit and passed after the artifacts were synchronized. That is useful evidence that the drift protection works.
- **Publication safety primitives:** `publish-version.py` already has non-overwrite and staged-publication protections; the release workflow should build around these rather than replace them.

## Recommended 0.6.0 execution sequence

1. **Freeze semantic decisions.** Resolve retractions, source-identifier privacy, recording Device identity, application/host snapshot model, hypertension admissibility, RestingHeartRate point versus aggregate, and generic metadata retention.
2. **Define schemas.** Create a release manifest and schemas for all catalogs, including one normalized adapter/source-type union and structured identity variants.
3. **Rebuild identity.** Generate parsers, FSH projections, examples, NamingSystem narrative, validator checks, and language fixtures from the structured grammar.
4. **Rebuild lifecycle.** Make status-conditional profile shapes and family-specific retraction graphs validate in official R4 tooling.
5. **Repair clinical/profile defects.** Split resting-heart-rate meanings, bind clinical payload release/format, fix unspecified specimen, application/host roles, and clinical-document provenance.
6. **Define conformance levels.** Publish shared positive/negative corpora and exact rule IDs; make each SDK consume them.
7. **Regenerate everything.** FSH, source CodeSystems, examples, status matrices, allowlists, package graph, validation maps, and release prose from the new sources.
8. **Run a clean release candidate.** SUSHI with no unexpected warnings, Publisher QA, official Validator over every positive/negative fixture, terminology lane, package semantic diff, and all SDK corpus lanes.
9. **Activate immutable publication.** Canonical host, publication requests, versioned directories, package lists, checksums, QA, tag/commit provenance, and non-clobber release assets.
10. **Require independent review.** FHIR profiling, clinical terminology, privacy/identity, and Swift/Kotlin/TypeScript interoperability sign-off should be recorded separately.

## Final 0.6.0 acceptance checklist

- [ ] Clean checkout; no untracked/generated drift.
- [ ] All seven `sushi-config.yaml` files, catalog/release manifest, package graph, built `package.json`, package lists, and tag say 0.6.0.
- [ ] `npm test` passes with no relevant package-output skip.
- [ ] SUSHI reports zero errors and zero unexpected warnings for every guide.
- [ ] Publisher QA has zero unsuppressed errors/warnings and every suppression is exact, justified, and exercised once.
- [ ] Every positive example validates with the official R4 Validator and exact release packages.
- [ ] Every negative fixture fails for the intended exact rule and no unrelated cascade.
- [ ] Identity golden/mutation corpora pass identically in Swift, Kotlin, TypeScript, and Python.
- [ ] Lifecycle/retraction examples cover every Observation and DocumentReference family.
- [ ] Clinical semantic corpus distinguishes point, interval, aggregate, and notification meanings without inference.
- [ ] Format payload golden bytes/hashes are deterministic across languages.
- [ ] Every normative catalog validates against a closed schema and has no dangling reference.
- [ ] Terminology pins and accountable review records are non-pending and version-reproducible.
- [ ] Canonical host resolves all owned canonical representations and immutable package history.
- [ ] Release assets cannot be overwritten and include checksums, QA, semantic diff, and source commit provenance.
