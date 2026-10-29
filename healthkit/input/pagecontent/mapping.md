<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Conversion begins by selecting a mapping from the HealthKit sample type.
The resulting Observation follows [HealthKit Observation](StructureDefinition-healthkit-observation.html) and the applicable clinical or research profile.
Preserve the facts HealthKit states; do not infer hardware, capture mode, clinical meaning, or study membership from an API type alone.

The normative status-vocabulary definitions live on the [guide family page](https://grovealliance.org/fhir/mobile/guides.html#status-vocabulary).
The [authoritative status matrix](status-matrix.html) lists all 218 source-type identifiers in the published adapter contract, including every admitted and fail-closed row.
The [walkthrough](walkthrough.html) applies the rules below to one concrete heart-rate sample, from `HKQuantitySample` to the operational exchange Bundle.

### Source-record and output identity

Derive one typed `source-record` v0 HMAC Identifier from the exact component order in `catalog/exchange-protocol.json`: adapter id, exact HealthKit source type, complete deployment-owned HealthKit-store scope pair, and lowercase canonical UUID text.
The Identifier system is deployment-owned and immutable for the identity kind, key id, and positive epoch.

Derive a distinct typed `source-output` Identifier by adding the closed output role and catalog discriminator.
This matters even for a single output: source-record identity answers which source revision was consumed, while source-output identity names the exact FHIR graph node previously emitted and later retracted.
A FHIR repository controls `Resource.id`; Grove business identifiers never do.

When native round-trip or traceability genuinely requires `HKObject.uuid`, a deployment may opt in to one additional Identifier on the designated one-to-one primary output.
Its absolute system is a governed HealthKit-store namespace and its value is the exact lowercase UUID. `Identifier.type` is optional; if present it must not use a Grove graph-role coding.
This disclosure does not replace or alter either HMAC identity, and the UUID is not repeated on child outputs or support resources.
Never copy it into `Resource.id`, Bundle entry keys, retraction addresses, arbitrary components, or untyped metadata, and do not incidentally propagate it into attachment names, URLs, or logs.

HealthKit replaces a sample when a writer saves the same `HKMetadataKeySyncIdentifier` with a higher `HKMetadataKeySyncVersion`, and that replacement has a new object UUID.
The new source record and output therefore receive new v0 identities.
Logical revision correlation is carried separately as writer identity.

### Availability time

`Observation.issued` is not emitted.
It states when this version of the record became available, and HealthKit keeps no per-object modification time to answer that.
Writing the conversion instant instead would make an unchanged sample convert to a different Observation on every run, which defeats the deduplication the exchange identity provides.
The conversion instant is recorded once, on the conversion `Provenance`.

### Logical identity and revisions

`HKMetadataKeySyncIdentifier` and `HKMetadataKeySyncVersion` are an exact pair.
A producer MUST reject either half-pair, a blank or non-String identifier, or a version that is not an integral non-negative number; it MUST NOT fabricate version `0`.
For a valid pair, derive a typed `writer-record` v0 HMAC Identifier from the complete writing-application Identifier pair and exact sync identifier.
Map `HKMetadataKeySyncVersion` to the [Grove Writer Record Version](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-writer-record-version.html) extension.
The Health Connect adapter uses the same identity kind and extension for `clientRecordId` and `clientRecordVersion`; equality is meaningful only where the deployment deliberately uses the same complete writer-application pair, identity system, key, and epoch.

The two identifiers answer different questions, and a receiver needs both:

- the source-record identifier names the exact row/revision that was read, so an exact retry is recognized;
- the sync identifier names the measurement, so a revision of it is recognized as the same measurement and the higher sync version supersedes the lower.

A sample with neither sync field omits writer identity and writer version.
It still carries mandatory source-record and source-output identities.
Do not synthesize writer identity: a writer that did not assign one has not promised cross-revision correlation.

The sample-type identifier dispatches converter code and is preserved as exactly one `healthkit-source-type` value.
This is adapter lineage, not a second expression of the observed clinical concept: `Observation.code` and `DocumentReference.type` retain only codings that actually mean the result or document type.

### Electrocardiograms

A structured HealthKit ECG directly claims the source-neutral Sensor ECG profile and the HealthKit ECG adapter profile.
The caller supplies the already-obtained `HKElectrocardiogram`, every voltage measurement and exact offset, and every associated symptom `HKCategorySample`; the adapter performs no query and never resamples.
Voltage offsets must form one exact uniform sequence, the reported count must match, and an optional sampling frequency must agree exactly with the SampledData period.

Classification is carried in `Observation.interpretation`, and the optional Apple ECG algorithm version is carried in `Observation.method`.
The reported sampling frequency and voltage count are admission inputs: they must match `SampledData.period` and the exact data frame count, but they are not duplicated as extensions.
When average heart rate is present, emit a separate LOINC 8867-4 `/min` Observation over the exact waveform Period; it has its own `average-heart-rate` source-output identity and `derivedFrom` points to the waveform.

Each correlated symptom is converted through its existing HealthKit symptom Observation profile, retaining its own source-record and source-output identity, exact Period, severity, source Device, and conversion Provenance.
Because one Mobile Exchange Bundle represents one source-record revision, each symptom is exchanged as its own event.
The ECG groups the separately available observations with identifier-only `hasMember` references carrying the symptoms' opaque `source-output` Identifiers.
Distinct equal-type samples remain distinct; `present` requires at least one distinct member, while `none` and `notSet` require none.

### Workouts

An `HKWorkout` converts to exactly one session Observation and one segment Observation for every workout event and every workout activity.
The session directly claims [Workout](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-mobile-workout.html) and HealthKit Observation; its output role is `workout` and its discriminator is `single`, whether or not it has segments.
Each segment directly claims [Workout Segment](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-mobile-workout-segment.html) and HealthKit Observation; its output role is `workout-segment`.
The workout row's `outputs` in [`catalog/healthkit-adapter.json`](https://grovealliance.org/fhir/catalog/healthkit-adapter.json) state both output contracts.
The segments are part of the conversion: a producer that does not emit every segment this section defines does not convert the workout and refuses it with `mobile-input.not-yet-convertible`.

Emit one segment for every `HKWorkoutEvent` in `HKWorkout.workoutEvents`, in array order, then one for every `HKWorkoutActivity` in `HKWorkout.workoutActivities`, in array order, and no other workout child.
A workout with a single activity still emits that activity's segment.
`HKWorkoutActivity.workoutEvents` lists a subset of the workout's events, so it emits nothing of its own.
The session lists every segment under `hasMember`, each once and in that emission order, through a resolving literal Reference.

An event segment's value carries the shared Grove workout-segment-type coding first and the exact [HealthKit Workout Event Type](CodeSystem-healthkit-workout-event-type.html) coding second:

| `HKWorkoutEventType` raw value | HealthKit code | Grove workout-segment-type code |
|---:|---|---|
| `1` | `pause` | `pause` |
| `2` | `resume` | `resume` |
| `3` | `lap` | `lap` |
| `4` | `marker` | `marker` |
| `5` | `motionPaused` | `motion-paused` |
| `6` | `motionResumed` | `motion-resumed` |
| `7` | `segment` | `segment-generic` |
| `8` | `pauseOrResumeRequest` | `pause-or-resume-request` |

The session's value classifies `HKWorkout.workoutActivityType`, and an activity segment's value classifies `HKWorkoutActivity.workoutConfiguration.activityType` the same way; each carries the shared Grove workout-activity coding first and the exact [HealthKit Workout Activity](CodeSystem-healthkit-workout-activity.html) coding second.
The shared code is the one this table gives the exact code, as the workout output's `activityMapping` in [`catalog/healthkit-adapter.json`](https://grovealliance.org/fhir/catalog/healthkit-adapter.json) states for every code: a code the shared vocabulary names maps to it, a code each of whose activities is a kind of one shared activity maps to that activity, and every other code maps to `other`.
A related activity that is not such a kind maps to `other` rather than to its nearest shared activity: water fitness is not swimming, and a wheelchair pace is neither running nor walking.

| Grove workout-activity code | HealthKit Workout Activity codes |
|---|---|
| `running` | `running` |
| `walking` | `walking` |
| `cycling` | `cycling`, `handCycling` |
| `hiking` | `hiking` |
| `swimming` | `swimming` |
| `strength-training` | `coreTraining`, `functionalStrengthTraining`, `traditionalStrengthTraining` |
| `high-intensity-interval-training` | `highIntensityIntervalTraining` |
| `yoga` | `yoga` |
| `pilates` | `pilates` |
| `rowing` | `rowing` |
| `elliptical` | `elliptical` |
| `stair-climbing` | `stairClimbing`, `stairs` |
| `dancing` | `cardioDance`, `dance`, `socialDance` |
| `tennis` | `tennis` |
| `table-tennis` | `tableTennis` |
| `badminton` | `badminton` |
| `squash` | `squash` |
| `basketball` | `basketball` |
| `soccer` | `soccer` |
| `american-football` | `americanFootball` |
| `baseball` | `baseball` |
| `volleyball` | `volleyball` |
| `golf` | `golf` |
| `boxing` | `boxing` |
| `martial-arts` | `kickboxing`, `martialArts`, `taiChi`, `wrestling` |
| `skiing` | `crossCountrySkiing`, `downhillSkiing` |
| `snowboarding` | `snowboarding` |
| `other` | every other code, `other` included |

The Workout Segment value set and Mobile measurement catalog admit both classifications: `resultCodeSystem` and `allowedValues` state the structural codes, and `additionalResultBindings` states the shared activity codes under their own system.

A raw value that this guide does not list does not refuse the workout and is not lost.
An `HKWorkoutEventType` raw value that the event-type table above does not list gives its segment the Grove workout-segment-type code `unknown`, and an `HKWorkoutActivityType` that HealthKit Workout Activity does not list gives the session or the activity segment the Grove workout-activity code `other`.
Such a value carries no HealthKit coding, because both HealthKit CodeSystems are complete, and carries its raw SDK integer in one [HealthKit Unmapped Source Value](StructureDefinition-healthkit-unmapped-source-value.html) extension, in canonical decimal text exactly as the discriminator's `raw value` below writes it, so every raw value the SDK can hold is kept.

A workout is refused when one of its outputs cannot be stated:

- with `mobile-input.required-metadata-missing` when an activity has no `endDate`;
- with `mobile-input.effective-period-invalid` when an event or activity lies outside the workout's own interval.

A segment's `effectivePeriod` runs from the start to the end of the event's `dateInterval`, or from the activity's `startDate` to its `endDate`; an instantaneous event has equal endpoints.
It uses the session's time zone, never one from the event's or activity's own metadata.
Every segment states the same subject, recording Device, gateway Device, study associations, and `grove-recording-method` as its session, and carries no governed source identifier.
The session and every segment carry the same writer-record Identifier and Grove Writer Record Version, or none of them carries either; the [revision rules](#logical-identity-and-revisions) decide whether the session carries them.
Metadata that an `HKWorkoutEvent` or `HKWorkoutActivity` carries is represented or withheld as the [withheld-metadata rules](#withheld-metadata) define.

A segment's discriminator is `<start>|<end>|<kind>|<raw value>|<occurrence>`:

- `start` and `end` are the interval endpoints: the exact binary64 `timeIntervalSinceReferenceDate` of each `NSDate` plus 978307200 seconds, added exactly and never as a binary64 sum such as `Date.timeIntervalSince1970`, then rounded half-even to a whole nanosecond and rendered in UTC as `YYYY-MM-DDThh:mm:ss.fffffffffZ` with exactly nine fractional digits;
- `kind` is `event` or `activity`;
- `raw value` is the `HKWorkoutEventType` or `HKWorkoutActivityType` raw SDK integer in decimal, without leading zeros and with `-` only before a negative value, whether or not this guide lists it, so a segment keeps its identity when a later version names that value;
- `occurrence` is the count, in decimal without leading zeros, of earlier segments in emission order with the identical start, end, kind, and raw value.

The segment output's `instantVectors` fix the endpoint rendering, and the `healthkit-workout-*` identity vectors in [`catalog/exchange-protocol.json`](https://grovealliance.org/fhir/catalog/exchange-protocol.json) fix one session, one event segment, and one activity segment.

The exact targets of a workout retraction name the session as `primary-output` and every segment its conversion emitted as `child-output`.
An `HKDeletedObject` carries none of the deleted workout's events or activities, so a producer that did not retain the segment identities it emitted uses the source-record target.

### Clinical FHIR records

HealthKit can expose both DSTU2 and R4 `HKFHIRResource` payloads.
The Grove exchange Bundle and HealthKit Clinical Record Document envelope remain FHIR R4, while the provider-issued attachment may be either DSTU2 or R4.
Admit a clinical record only when `HKFHIRResource.fhirVersion.fhirRelease` is exactly `dstu2` or `r4`.
Map that source value directly to `Attachment.contentType`: `application/fhir+json; fhirVersion=1.0` for DSTU2 or `application/fhir+json; fhirVersion=4.0` for R4.
The standard `fhirVersion` media-type parameter carries the release; never infer it from the JSON shape.
Reject an unknown or missing release, as well as every future release that the contract does not yet admit, before creating the DocumentReference.

Carry the provider-issued bytes under the release-neutral `fhir-resource` format contract.
Do not parse and reserialize, relabel, upgrade, downgrade, or otherwise rewrite those bytes.
Grove validation checks that an inline attachment is strict UTF-8 JSON containing one `resourceType`-bearing object, but it does not apply R4 rules to a DSTU2 payload or assert conformance to the issuer's FHIR release.
The R4 envelope asserts the exact source release, payload integrity, identity, and provenance—not that Grove has validated or endorsed the provider's clinical content.

### Values, units, and time

| HealthKit sample type | Required profile and code | FHIR value |
|---|---|---|
| `HKQuantityTypeIdentifierHeartRate` | Grove Mobile Heart Rate (imposes FHIR R4 Heart Rate); LOINC `8867-4` | `valueQuantity`, UCUM `/min` |
| `HKQuantityTypeIdentifierStepCount` | Grove Mobile Step Count; Grove `step-count-total` | `valueQuantity`, UCUM `{steps}`, exact `effectivePeriod` |
| `HKQuantityTypeIdentifierBodyMass` | Grove Mobile Body Weight (imposes FHIR R4 Body Weight); LOINC `29463-7` | `valueQuantity`, UCUM `kg` |

Use `effectiveDateTime` for a point result.
Use `effectivePeriod` when HealthKit supplies a start and end that define an interval. Preserve fractional seconds and the numeric offset.
Where the selected profile admits only `dateTime`, an interval sample states its `startDate` as `effectiveDateTime` and withholds its `endDate`.
Map an available IANA time-zone name to the standard FHIR `timezone` extension on the corresponding date-time value.

Step count preserves the source interval total with Grove `step-count-total` and UCUM `{steps}`.
The effective Period must have both endpoints and a positive duration.
The value is the total count attributed to that Period; do not turn a point sample into a step count and do not normalize the source count to `/h` or another rate.

### Percentages

HealthKit reports a percentage type as a binary64 fraction in `HKUnit.percent()`, where 1 means 100 percent, and the adapter emits UCUM `%`.
Here the shortest round-trip decimal of a binary64 is the decimal with the fewest significant digits that converts back to exactly that binary64, of several such decimals the one nearest it, and of two equally near ones the one whose last digit is even.
The adapter scales the fraction to percent in three steps, which the catalog's `percentScaling` names `shortest-round-trip-decimal-shift-rounded-once`:

1. Write the fraction as its shortest round-trip decimal.
2. Move that decimal's point two places to the right, which multiplies it by 100 exactly.
3. Convert the result once to the nearest binary64, a tie going to the one with the even significand (round to nearest, ties to even), as a correctly rounded decimal parser does, and emit that binary64 as its shortest round-trip decimal.

A fraction of 0.282 is therefore emitted as `28.2`.
Never multiply the binary64 fraction by 100 in binary64; for 0.282 that yields `28.199999999999996`.
Never emit the shifted decimal of step 2 without step 3 either: 0.49543508709194095 is emitted as `49.54350870919409`, not `49.543508709194095`.
The emitted value never has more significant digits than the fraction's shortest round-trip decimal.
A fraction of 0.5 + 2⁻¹⁷ is exactly 0.50000762939453125, equally near the round-trip decimals 0.5000076293945312 and 0.5000076293945313, so step 1 writes `0.5000076293945312` and the emitted value is `50.00076293945312`, never `50.00076293945313`.
Each of the catalog's `percentScalingVectors` pairs a fraction with its percent, and a producer's emitted value equals the vector's `percent` as an exact decimal.
The Mobile percent domain of 0 through 100 applies to the emitted value.

### Capture mode and performer

When `HKMetadataKeyWasUserEntered` is explicitly `true`, set the Mobile `grove-recording-method` extension to `manual-entry`.
A sample states the flag only through an `NSNumber` equal to 1, which is `true`, or 0, which is `false`; any other value, such as 2, states nothing, even though Objective-C `boolValue` reads it as `true`.
This flag does not identify the person who entered the value, so it does not justify a Patient performer.
Populate `Observation.performer` only when separate source evidence identifies a responsible party.
The [body-weight example](Observation-HealthKitManuallyEnteredBodyWeightExample.html) shows this mapping.

Do not infer `actively-recorded` or `automatically-recorded` when the flag is absent or false; omission means the converter does not know the capture mode.
Do not add the Patient as performer solely from capture mode. `Observation.method` remains available for a clinical measurement technique and is not used for HealthKit capture mode.

### Blood-pressure correlation objects

An `HKCorrelationTypeIdentifierBloodPressure` correlation converts to one Observation: its identity and effective time come from the `HKCorrelation`, and its systolic and diastolic components from the `HKQuantitySample` objects in `HKCorrelation.objects`.
The objects' `HKMetadataKeyTimeZone` and `HKMetadataKeyWasUserEntered` count for that Observation as this section defines.
`HKCorrelation.objects` is a set, so no outcome below depends on the order in which a producer reads the objects.
This section does not apply to an `HKCorrelationTypeIdentifierFood` correlation, whose objects are nutrient samples converted to Observations of their own.

Use the correlation's `HKMetadataKeyTimeZone` when it carries one, and consult no object's.
Otherwise consult every object's, and an object that does not carry one abstains: when at least one object carries one and every object that carries one carries the same name, compared character for character, use that name as if the correlation carried it.
When no object carries one, or two objects carry different names, even a link and its target such as `US/Pacific` and `America/Los_Angeles`, the record supplies no time-zone name: serialize the effective value in UTC without a `timezone` extension and report `mobile-omission.source-offset`.
Refuse the record with `mobile-input.unsupported-source-value` when an object's consulted value is not a valid IANA time-zone name, even when other objects carry a valid one.

When the correlation states `HKMetadataKeyWasUserEntered`, its value decides as the [capture-mode rule](#capture-mode-and-performer) defines, whatever its objects state.
Otherwise set `manual-entry` when there is at least one object and every object states `true`, and omit it when any object states `false` or nothing.
When the correlation or an object states `true` and the Observation carries no `grove-recording-method` extension, report `mobile-omission.recording-method`.

These rules decide what an object's `HKMetadataKeyTimeZone` and `HKMetadataKeyWasUserEntered` contribute, so neither key on an object is reported as `mobile-omission.unmodeled-metadata`.
An object's other metadata keys are withheld under the same condition as the correlation's own; report the keys withheld from the correlation and its objects as `mobile-omission.unmodeled-metadata`, naming each key once however many of them carry it.

### Device, application, and provenance

Map `HKDevice` to a [Grove Recording Device](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-recording-device.html) only when the caller supplies a governed stable per-unit token for the hardware that acquired the value.
HMAC-protect that token in the typed `recording-device` identity and add the event-scoped `device-snapshot` identity.
Omit the recorder when no stable token exists; manufacturer, model, version, subject, or their digest cannot establish a physical instance.

Map `HKDevice.hardwareVersion`, `firmwareVersion`, and `softwareVersion` only when each value is present.
Their `Device.version.type` codings use the ISO 11073 MDC revision codes `531974`, `531976`, and `531975`, respectively. `HKDevice.model` maps to `Device.modelNumber`; it is not a version.
These standard type codes do not assert conformance to a PHD profile.

Represent the converting app as a [HealthKit Application Device](StructureDefinition-healthkit-application-device.html), which specializes the shared Grove Application Device.
Its required, typed Apple bundle identifier uses the [Apple Bundle Identifier](NamingSystem-apple-bundle-id.html) namespace and identifies only the application product.
Put the human-facing release and build into separate typed Device version entries.
Represent host hardware and its operating-system version as a distinct immutable [Grove Host Device](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-host-device.html) referenced by `Device.parent`; never put the host OS on the application Device.
The application's mandatory event-scoped `device-snapshot` HMAC identifies this immutable event view, not an installation, account, or person.
The app is the assembler agent in [conversion Provenance](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-mobile-conversion-provenance.html). Converting a stored HealthKit object does not by itself make the app an Observation gateway; add `observation-gatewayDevice` only if the app actually mediated or routed the measurement.

The Provenance source entity repeats the typed source-record Identifier actually consumed by the transformation. `HKSourceRevision.source` identifies the application or device that authored that object; do not treat its version as the Grove converter's version.
Comparing it with the converting application's build under the same-application rule below does not treat it as the converter's version.

When the source is a caller-classified application, represent it as a HealthKit Application Device.
Use the [Apple Bundle Identifier](NamingSystem-apple-bundle-id.html) namespace for `HKSource.bundleIdentifier`.
HealthKit takes `HKSourceRevision.version` from the source's `CFBundleVersion`: when HealthKit supplies it, copy it unchanged into the typed application-build slice (`grove-application-version-type#build`), never into the application-version slice.
When HealthKit reports a supported Bluetooth Low Energy source, represent the author as a Grove Recording Device only when the caller supplies a governed stable per-unit token under the deployment's source-actor identity policy.
HMAC-protect it with the deployment-scoped `recording-device` and `device-snapshot` identities defined by the Mobile exchange protocol.
If native source-actor round-trip requires the clear HealthKit source UUID, disclose it only as a separately governed, system-qualified Identifier under that policy.
HealthKit does not specify that its UUID is a serial number, a globally stable hardware identity, or stable outside the contexts in which the exact value recurs.
If the adapter cannot establish whether the source is an application or a device, omit the writer agent rather than guessing its identity. `HKSourceRevision` does not expose an application-or-device discriminator: do not classify the source from the identifier's string shape, source name, or `productType`.
A producer therefore needs explicit source actor classification from its caller or adapter context before it emits this author Device.
The classification is the only caller-supplied part: the author name, identifier, and version are copied from that same sample's `HKSourceRevision` and must not be replaced with independently supplied identity data.
The same-application rule below is the only exception.
The [Bluetooth heart-rate example](Observation-HealthKitBluetoothHeartRateObservationExample.html) and its [source Provenance](Provenance-HealthKitBluetoothSourceProvenanceExample.html) show this explicit governed branch without treating the source identifier as a serial number.

Link an included source application or device through `Provenance.entity.agent` with participant type `author`.
This author role is distinct from the converter's top-level `assembler` role and does not make either Device a gateway.
When the same application performed both roles, both agents may reference the same Grove Application Device while retaining their separate roles.
For a HealthKit source, the same-application rule decides when that is so: a producer may treat an application-classified source as the converting application only when all of the following hold:

- `HKSource.bundleIdentifier` equals the converting application's Apple bundle identifier;
- HealthKit supplies `HKSourceRevision.version`, and it equals, character for character, the build that the converting application's Device states in its application-build slice;
- the producer never reuses a build across releases of that bundle identifier.

HealthKit reports only the source's build, and a platform may let a build number recur in another release; without the last condition, the source's release is unknown.
A producer that applies the rule makes the author agent reference the converting application's Device, which states that application's name, release, and build as reported at conversion; its `Device.parent`, when present, remains the conversion host.
It then emits no other Device for the source and makes no claim about the host on which the source wrote the object.
Every application-classified source that the producer does not treat as the converting application is a distinct application snapshot, including one without `HKSourceRevision.version`, one of another build, and every one compared with a converting application Device that states no build.

Study resources are linked through the study model; they are not source entities unless the conversion literally consumed them as inputs.

### Unclassified source revision

When the [writer rules](#device-application-and-provenance) state no author agent for the source entity of a HealthKit conversion Provenance, because the caller did not classify the source or classified it as something those rules cannot state, such as a Bluetooth source without a governed per-unit token, that source entity carries one [HealthKit Source Revision](StructureDefinition-healthkit-source-revision.html) extension, so omitting the writer does not lose where the object came from.
The extension never appears beside an author agent: a graph states a source as its writer or through its source revision, never both.
Only the source entity of a conversion Provenance carries it, and only for a record with an `HKSourceRevision`; a tracked medication has none, because `HKUserAnnotatedMedication` is not an `HKObject`.

The extension has five members, each one `valueString` that appears at most once, in this order:

| Member | `HKSourceRevision` fact | Value | By default |
|---|---|---|---|
| `sourceName` | `source.name` | the exact string | withheld |
| `sourceBundleIdentifier` | `source.bundleIdentifier` | the exact string | withheld |
| `version` | `version` | the exact string, the source's build, which HealthKit takes from its `CFBundleVersion` | emitted |
| `productType` | `productType` | the exact string, the product type of the device that ran HealthKit when the object was created | emitted |
| `operatingSystemVersion` | `operatingSystemVersion` | its `majorVersion`, `minorVersion`, and `patchVersion`, each as canonical decimal integer text without a leading zero and with a `-` only before a negative value, joined by `.`; all three always appear, so `26.5.0` is never written `26.5` | emitted |

A member whose string fact HealthKit does not supply, or supplies empty, is left out.
`HKSourceRevision.operatingSystemVersion` is not optional, so its member is present, `0.0.0` included, unless a disclosure policy withholds it.

`sourceName` and `sourceBundleIdentifier` are withheld by default: a producer carries them only under an explicit deployment authorization to disclose the names and identifiers of the applications and devices that wrote its records.
`HKSource.name` can be the name a person gave a device, a device's `HKSource.bundleIdentifier` can embed an identifier that HealthKit assigns to that one device, and a producer cannot tell either from an application's without classifying the source.
`version`, `productType`, and `operatingSystemVersion` are emitted by default.
A deployment's disclosure policy may withhold any of them, or the whole extension; as for every omission a disclosure policy chooses, that is not reported, and an extension with no member left is not emitted.

The extension describes the consumed object, not an actor: it adds no agent, participant type, or Device, and it states neither that the source is an application nor that it is a device.
The rule that a source is never classified from its identifier's string shape, source name, or `productType` holds for its members as it holds for `HKSourceRevision`.
`sourceBundleIdentifier` is text, never an Identifier.
The extension mints no identity, and no identity is derived from it: adding or withholding it, or any of its members, changes no Identifier that is not event-scoped, such as a `source-record`, `source-output`, or `writer-record` Identifier.
A record delivered again with the extension or any of its members added or withheld is still changed content: it receives a new event sequence and with it new event-scoped identities, as the [Mobile exchange graph](https://grovealliance.org/fhir/mobile/observations.html#exchange-graph) requires.
Writer identity depends neither on the extension nor on the source's classification: for a sample from every source, whether the caller classified it as an application, as a device, or not at all, the writing-application Identifier pair from which the [revision rules](#logical-identity-and-revisions) derive the `writer-record` Identifier is the [Apple Bundle Identifier](NamingSystem-apple-bundle-id.html) namespace with `HKSource.bundleIdentifier`.
Whether a graph states an author therefore never decides whether its outputs carry the sample's `writer-record` Identifier and version; the [revision rules](#logical-identity-and-revisions) and the [withheld-metadata rules](#withheld-metadata) decide that, and withholding `sourceBundleIdentifier` does not withhold them.

### Supported HealthKit metadata

Map source facts to standard FHIR fields and published extensions before retaining adapter-specific metadata.
Of the five keys in [HealthKit Metadata Keys](CodeSystem-healthkit-metadata-key.html), one is carried as an adapter-coded component: `HKMetadataKeyHeartRateMotionContext`.
It is represented by the named `Observation.component:heartRateMotionContext` slice and bound to [HealthKit Heart Rate Motion Context](CodeSystem-healthkit-heart-rate-motion-context.html).
The component is valid only on a LOINC `8867-4` heart-rate Observation.

Map the source `NSNumber` without renumbering or inferring a context:

| `HKHeartRateMotionContext` raw `NSNumber` value | Adapter code | Display |
|---:|---|---|
| `0` | `not-set` | Not Set |
| `1` | `sedentary` | Sedentary |
| `2` | `active` | Active |

The lower-case values in the second column are codes in the adapter's FHIR CodeSystem; the integer in the first column is the value supplied by HealthKit.
For any other integer, reject the unsupported value or omit the component according to the importer's policy.
Never default an unknown value to `not-set`.

Another is carried as an adapter-coded component: `HKMetadataKeyInsulinDeliveryReason`.
It is represented by the required `Observation.component:insulinDeliveryReason` slice of [Insulin Delivery](StructureDefinition-healthkit-insulin-delivery.html) and bound to [HealthKit Insulin Delivery Reason](ValueSet-healthkit-insulin-delivery-reason.html).
The component's code is `HKInsulinDeliveryReason`, the key that the constant `HKMetadataKeyInsulinDeliveryReason` holds and a sample's metadata carries.

Map the source `NSNumber` without renumbering or inferring a reason:

| `HKInsulinDeliveryReason` raw `NSNumber` value | Adapter code | Display |
|---:|---|---|
| `1` | `basal` | Basal |
| `2` | `bolus` | Bolus |

A sample that does not carry the key, or carries a value the table does not map, is rejected; the component is never omitted and a reason is never inferred.

There is no generic metadata extension.
Adding another key requires a defined semantic purpose, a typed FHIR representation, an explicit allowlist update, and validation examples.

### Withheld metadata

A metadata key that a source record carries is represented only by the element that this table gives it, for the source types the table names, and only when an output of the record's graph carries the key's value in that element.

| Runtime key | SDK constant | Source types | Element |
|---|---|---|---|
| `HKTimeZone` | `HKMetadataKeyTimeZone` | every type with an Observation output | the `timezone` extension on each `effective[x]` date-time, as the [time rules](#values-units-and-time) define |
| `HKWasUserEntered` | `HKMetadataKeyWasUserEntered` | every type with an Observation output | the `grove-recording-method` extension, `manual-entry` when the key states `true`, as the [capture-mode rule](#capture-mode-and-performer) defines |
| `HKMetadataKeySyncIdentifier` | `HKMetadataKeySyncIdentifier` | every type with an Observation output | the `writer-record` Identifier, as the [revision rules](#logical-identity-and-revisions) define |
| `HKMetadataKeySyncVersion` | `HKMetadataKeySyncVersion` | every type with an Observation output | the Grove Writer Record Version extension beside the `writer-record` Identifier |
| `HKMetadataKeyHeartRateMotionContext` | `HKMetadataKeyHeartRateMotionContext` | `HKQuantityTypeIdentifierHeartRate` | `Observation.component:heartRateMotionContext`, as [above](#supported-healthkit-metadata) |
| `HKHeartRateEventThreshold` | `HKMetadataKeyHeartRateEventThreshold` | `HKCategoryTypeIdentifierHighHeartRateEvent`, `HKCategoryTypeIdentifierLowHeartRateEvent` | `Observation.component:threshold` of the notification, in UCUM `/min` |
| `HKLowCardioFitnessEventThreshold` | `HKMetadataKeyLowCardioFitnessEventThreshold` | `HKCategoryTypeIdentifierLowCardioFitnessEvent` | `Observation.component:threshold` of the notification, in UCUM `mL/kg/min` |
| `HKMetadataKeyAppleECGAlgorithmVersion` | `HKMetadataKeyAppleECGAlgorithmVersion` | `HKDataTypeIdentifierElectrocardiogram` | `Observation.method` of the ECG Observation |
| `HKInsulinDeliveryReason` | `HKMetadataKeyInsulinDeliveryReason` | `HKQuantityTypeIdentifierInsulinDelivery` | the delivery-reason component that the Insulin Delivery measurement requires |
| `HKMenstrualCycleStart` | `HKMetadataKeyMenstrualCycleStart` | `HKCategoryTypeIdentifierMenstrualFlow` | `Observation.component:cycleStart` |
| `HKSexualActivityProtectionUsed` | `HKMetadataKeySexualActivityProtectionUsed` | `HKCategoryTypeIdentifierSexualActivity` | `Observation.valueCodeableConcept`, `protected` or `unprotected` |

Withhold every metadata key that an accepted record carries and that no output of its graph represents, and report those keys as `mobile-omission.unmodeled-metadata`, naming each key once by its runtime key.
That includes a key the table does not list, a key it lists only for other source types, and a listed key whose element no output carries.
A runtime key is the string that a metadata dictionary holds as the key, as the table's first column gives it, not the name of the SDK constant that holds it, which can differ: `HKMetadataKeyTimeZone` holds `HKTimeZone`.
A key that no SDK constant declares is named the same way.
`HKMetadataKeyWasUserEntered` stating `false`, whether the record or a part of it carries it, maps to no element, as the capture-mode rule defines, and is never reported; a value that states nothing is reported.
Every element in the table belongs to an Observation, so a [HealthKit Recording Document](StructureDefinition-healthkit-recording-document.html) represents no key, not even a valid sync pair.

A key that a part of the record carries, an object of a blood-pressure correlation or an `HKWorkoutEvent` or `HKWorkoutActivity` of a workout, is represented only when the record itself carries the same key with an equal value that its graph represents; otherwise it is withheld and reported with the record's own keys.
Two values are equal when they are time-zone names or sync identifiers that match character for character, user-entered flags that state the same thing, or sync versions that are the same number.
The [correlation-object rules](#blood-pressure-correlation-objects) decide instead what a blood-pressure object's `HKMetadataKeyTimeZone` and `HKMetadataKeyWasUserEntered` contribute.

Reporting never relaxes a rejection: a half or invalid sync pair that the record itself carries rejects the record even when no output could carry the pair.
As for every omission, a key that a disclosure policy withholds is not reported.

### Study context

Study linkage follows the Mobile guide's [study model](https://grovealliance.org/fhir/mobile/study.html): a versioned PlanDefinition is referenced by ResearchStudy, ResearchSubject connects the Patient to the study, and `workflow-researchStudy` links the Observation.
The [study Bundle](Bundle-HealthKitStudyBundleExample.html) demonstrates the graph.

### Source metadata artifact

This section is a draft proposal for owner review and is not yet admitted.
Until it is admitted, a producer emits no source-metadata artifact, and the [withheld-metadata rules](#withheld-metadata) apply unchanged.
It proposes a carrier for the metadata keys that those rules withhold; its open questions close the section.

Under a source-metadata disclosure authorization, a producer adds one source-metadata artifact to the graph of a record for which the payload below would carry at least one key: a DocumentReference that claims the proposed HealthKit Source Metadata Document profile, a specialization of the [HealthKit Recording Document](StructureDefinition-healthkit-recording-document.html).
It is a source artifact: beside the record's `source-record` Identifier it carries a `source-output` Identifier with output role `source-metadata` and discriminator `single`, and a `source-artifact` Identifier with format code `source-metadata` and part index `0`.
Its `content.format` is the proposed recording format `source-metadata`, its `Attachment.contentType` is `application/json`, and its `Attachment.data` holds the payload below, with `size` and `hash` taken over the payload bytes.
It references no other output and no other output references it: the shared `source-record` Identifier and the conversion Provenance, which targets it as it targets every output, relate it to the record, so adding or omitting it changes nothing that another output takes from the record and no Identifier that is not event-scoped, such as a `source-record`, `source-output`, or `writer-record` Identifier.
It is never the designated primary output and never carries a governed source identifier or a `writer-record` Identifier.

The authorization is the deployment's explicit decision to disclose source metadata, and it is never inferred from the converting application, a key's spelling, or a value.
It names each key it reaches by its runtime key, as the [withheld-metadata rules](#withheld-metadata) define it, or it reaches every ordinary key, or both.
Every key is ordinary except the identifying keys below, which can identify a person, a device, or a writer's record: an authorization reaches an identifying key only when it names that key, and reaching every ordinary key reaches none of them.

| Runtime key | SDK constant |
|---|---|
| `HKMetadataKeySyncIdentifier` | `HKMetadataKeySyncIdentifier` |
| `HKExternalUUID` | `HKMetadataKeyExternalUUID` |
| `HKDeviceSerialNumber` | `HKMetadataKeyDeviceSerialNumber` |
| `HKUDIDeviceIdentifier` | `HKMetadataKeyUDIDeviceIdentifier` |
| `HKUDIProductionIdentifier` | `HKMetadataKeyUDIProductionIdentifier` |
| `HKDeviceName` | `HKMetadataKeyDeviceName` |
| `HKDigitalSignature` | `HKMetadataKeyDigitalSignature` |

Without an authorization, a producer emits no artifact; that is the default.
A producer also emits no artifact for a record whose payload would carry no key, so a missing artifact never says whether a record carried metadata.
The deployment's disclosure policy takes precedence over the authorization: a key that the policy withholds is never carried, whatever the authorization reaches, and, as for every omission a disclosure policy chooses, it is not reported.
A record that the producer refuses has no graph and so no artifact, and a workout route, which is disclosed only under a route-disclosure authorization, has an artifact only when its route is disclosed.

The payload is the RFC 8785 canonical JSON serialization of one object, in UTF-8 without a byte-order mark: no insignificant whitespace, members in the order of their names' UTF-16 code units, and strings escaped as RFC 8785 escapes them.
Its `metadata` member is always present: it holds every key that the record itself carries and that the payload carries, and it is the empty object when the record itself carries no such key.
Its `parts` member, left out when empty, holds one entry of `part` and `metadata` for each part of the record that carries such a key, ordered by the UTF-16 code units of `part` and then by the canonical bytes of `metadata`, so no outcome depends on the order of `HKCorrelation.objects`.
The parts are a blood-pressure correlation's objects, each named by its exact source type identifier, and a workout's events and activities, each named by the discriminator of the segment that the [workout rules](#workouts) emit for it.
A food correlation's objects are records of their own and carry their keys in their own artifacts.
The payload names each key by its runtime key and carries the key whether or not an element of the graph also represents it.
A producer reads the metadata as the `NSDictionary` that HealthKit holds, and each key and each string value as the UTF-16 code units of its `NSString`, never through a type that compares strings by canonical equivalence: two keys whose code units differ are two keys even when Unicode calls them equivalent, so naming a key reaches only the key with the same code units, and a key is identifying only when its code units are those of a runtime key in the table above.
Swift's `String` compares by canonical equivalence, so bridging the dictionary to `[String: Any]`, as `HKObject.metadata` is bridged in Swift, keeps only one of two such keys: on the SDK baseline, a sample whose metadata holds `é` both as U+00E9 and as U+0065 U+0301 keeps both keys in its `NSDictionary` and one once bridged.
Each value is an object with exactly one member, chosen by the value's class:

| Value class | Member | Value |
|---|---|---|
| `NSString` | `string` | the exact string, its UTF-16 code units without Unicode normalization; a string that is not a sequence of Unicode scalar values, such as one holding an unpaired surrogate, is not carried |
| `NSDecimalNumber` | `number` | its exact value, the decimal mantissa times ten to the power of its exponent, as plain decimal text without an exponent, a leading zero before another integer digit, or a trailing fractional zero, and `0` for zero; the class is checked before the `objCType`, which is `d`, and the value is never read through `doubleValue`; `NaN` is not carried |
| `NSNumber` whose `objCType` is `c`, `C`, `s`, `S`, `i`, `I`, `l`, `L`, `q`, `Q`, or `B` | `number` | the exact integer as canonical decimal text, so a Boolean, which reports `c`, is `1` or `0` |
| `NSNumber` whose `objCType` is `f` or `d` | `number` | the binary64 that `doubleValue` returns, which widens a `float` exactly, as its [shortest round-trip decimal](#percentages) in plain positional notation, choosing the one whose last digit is even when two are equally near it, and as `0` for either zero; a nonfinite value is not carried |
| `NSDate` | `instant` | the instant as a [workout segment endpoint](#workouts) renders it, `YYYY-MM-DDThh:mm:ss.fffffffffZ` in UTC and the proleptic Gregorian calendar; a nonfinite date, or one whose year falls outside 0001 through 9999, is not carried |
| `HKQuantity` | `quantity` | an object of `unit`, the UCUM code of the first unit below with which the quantity is compatible, and `value`, the binary64 that `doubleValue(for:)` returns in that unit, written as for a floating `NSNumber`; a quantity compatible with no unit below, or with a nonfinite value, is not carried |
| `NSData` | `data` | the bytes in base64 with the standard alphabet and padding and without line breaks, as RFC 4648 section 4 defines |

A value of any other class, and a key that is not a sequence of Unicode scalar values, is not carried.
A number is written as text rather than as a JSON number, so the payload never depends on how a JSON library writes numbers, and an integer whose magnitude exceeds 2^53 keeps every digit, as does a decimal.
An `NSDecimalNumber` is written from its exact value because its mantissa has a precision of at least 38 decimal digits, more than a binary64 keeps, and because its `doubleValue` is not always correctly rounded: on the SDK baseline it returns `0.12345678901234565` for the decimal `0.123456789012345678`, whose nearest binary64 is `0.12345678901234568`.

`HKQuantity` exposes no unit of its own, so the payload writes each quantity in the first of these HealthKit units with which it is compatible, under its UCUM code, in the order of this table:

| HealthKit unit | UCUM code |
|---|---|
| `count` | `1` |
| `count/min` | `/min` |
| `s` | `s` |
| `m` | `m` |
| `m/s` | `m/s` |
| `g` | `g` |
| `L` | `L` |
| `L/min` | `L/min` |
| `kcal` | `kcal` |
| `W` | `W` |
| `degC` | `Cel` |
| `mmHg` | `mm[Hg]` |
| `mg/dL` | `mg/dL` |
| `mL/(kg*min)` | `mL/kg/min` |
| `kcal/(kg*hr)` | `kcal/kg/h` |
| `IU` | `[iU]` |
| `S` | `S` |
| `dBASPL` | `dB[SPL]` |
| `dBHL` | `dB` |
| `lx` | `lx` |
| `appleEffortScore` | `{score}` |

On the SDK baseline no two of these units are compatible, so the order decides nothing there; it decides only if a later SDK makes two of them compatible.
A percentage is therefore written in `1` as the fraction HealthKit holds, because HealthKit's percent and `count` units are compatible.

Once the artifact is admitted, the record itself and each of its parts are decided path by path: a key that the payload carries on a path is represented there by the graph.
A key that the payload does not carry on a path, because the authorization does not reach it or the payload cannot carry its value, is treated there exactly as the withheld-metadata rules decide without an authorization: it is represented by its element where the table maps it, and is otherwise withheld.
A key that those rules report on any path where the payload does not carry it is reported as `mobile-omission.unmodeled-metadata` once, even when the payload carries it on another path, and a key that the disclosure policy withholds is neither carried nor reported.
An authorization only discloses: it is not a disclosure policy that withholds keys, so it never silences a report.
The artifact never replaces an element: a key that the [withheld-metadata table](#withheld-metadata) maps is still carried in its element, and the artifact never excuses leaving that element out.
Carrying a key changes no other rule: a half or invalid sync pair that the record itself carries still rejects the record, a sync pair in the payload is never writer identity, and the [revision rules](#logical-identity-and-revisions) still decide which outputs carry writer identity.

The payload depends only on the record's metadata, the authorization, the deployment's disclosure policy, and the unit table above, never on the conversion instant, a locale, or the order in which a dictionary or set is iterated.
Converting an unchanged record again under the same authorization and disclosure policy therefore yields the same bytes, as an exact retry requires.
A changed authorization, disclosure policy, or unit table that still yields an artifact changes its content, which the producer delivers as a new event, and the artifact keeps its `source-output` and `source-artifact` Identifiers, so a receiver supersedes it in place.
A change that leaves the record no carried key yields no artifact, so it neither supersedes nor retracts the delivered one; that is the withdrawal question below.
An exact retraction names the artifact with target role `source-artifact` when the producer establishes that it emitted the artifact.
An `HKDeletedObject` carries no metadata beyond the sync pair, so a producer that kept no record of the output set uses the source-record target, which addresses the artifact with the record's other nodes.
Retraction asserts that the source removed the record, so it is not the means to withdraw an artifact once its authorization ends.

A receiver may store, index, and show the payload's keys as facts that the record's writer stated, read an SDK key's meaning from Apple's HealthKit documentation, and drop or segregate the artifact without changing any other output.
A receiver must not treat a value as a clinical result or prefer it over the element of the same graph that represents the key, derive identity, deduplication, revision order, or a retraction address from a value such as a sync identifier or an external UUID, read a missing key or a missing artifact as a statement that the record carried no such metadata, or rewrite the payload and present it as the producer's.
A value can identify a person, a device, or a writer's record, so the artifact carries the deployment's disclosure obligations wherever a receiver keeps it.

#### Rationale

HealthKit metadata is an open dictionary that every writing application fills: besides the keys this guide maps, it holds the identifying keys above, free text, and keys whose meaning only their writer knows, and the SDK header discourages storing the UDI production identifier in HealthKit for user privacy reasons.
Disclosure is therefore the deployment's explicit decision and is off by default, an identifying key is disclosed only by name, and the withheld-metadata report keeps every loss visible, including that of an origin key such as `HKDeviceManufacturerName`.
A separate artifact keeps that content off the clinical resources: a receiver can drop, segregate, or retract it on its own, and the authorization changes nothing that another output takes from the record and no Identifier that is not event-scoped.
In the new event that delivers a changed artifact, another output differs only in what every new event changes, such as a reference to a node with an event-scoped identity.
An extension would need a context on every output type, repeat itself across a multi-output graph, and change a clinical resource whenever the authorization changes, and this guide admits no generic metadata extension.
The payload defines a canonical value for each class rather than promising a verbatim copy, because what a copy preserves cannot be checked across platforms; it names its losses instead: an `NSNumber`'s storage class, an `NSDate`'s detail below a nanosecond, a quantity's original unit, which `HKQuantity` does not expose, the sign of a floating zero, and every value it does not carry.
`HKObject.h` names four value classes, `NSString`, `NSNumber`, `NSDate`, and `HKQuantity`; on the SDK baseline the `HKQuantitySample` initializer also admits `NSData` and `NSDecimalNumber` values and rejects `NSArray` and `NSNull` values.

#### Open questions

- Carrier: is a separate DocumentReference source artifact the carrier the owner wants, rather than an extension on each output?
- Admission: admitting the artifact also registers `source-metadata` in the Sensor recording-format registry; adds the HealthKit Source Metadata Document profile, with a `type` coding and a `date` that states when the reference was created, as FHIR R4 defines `DocumentReference.date`, and that an exact retry reuses, under a parent whose description says byte-preserved; adds its claim to `catalog/profile-claims.json`, whose HealthKit conversion Provenance claim and ECG claim name the Provenance targets, while HealthKit Conversion Provenance already admits it as a target through that parent; excludes it in the HealthKit selector of the governed source identifier in `catalog/exchange-protocol.json`; amends that identifier's `source-only` output-mode rule and `recordingDocumentRule` there, which let a DocumentReference carry it only as the event's sole DocumentReference or sole source-derived output, and the Mobile statement that it may sit on the source Recording Document when no structured output exists, because twelve HealthKit rows emit a recording document as their only output; adds a `source-artifact` identity vector and producer-kit checks; amends the Mobile statement that source-platform fields do not pass through a generic metadata container and the `untypedMetadata` enforcement in `catalog/exchange-protocol.json`; amends this page's statements that there is no generic metadata extension and that another key needs a typed FHIR representation, that a key is represented only by the element the withheld-metadata table gives it, that a HealthKit Recording Document represents no key, and that the exact targets of a workout retraction are its session and its segments; amends the description of HealthKit Metadata Keys, which calls its keys the ones the guide retains after the standard mappings; amends the HealthKit catalog's identity `outputRoleRule`, which takes every output role from a catalog row, and its `sourceArtifact` rule, which gives a format code only to a clinical or native recording; and amends the conditional outputs that the [implementation page](implementation.html) names for a retracted source record.
- Source types: should an authorization also be able to name the source types it reaches? If it may, it names a record's own source type identifier and reaches the record with all of its parts, a blood-pressure correlation's objects and a workout's events and activities among them, while a part's type, such as `HKQuantityTypeIdentifierBloodPressureSystolic` for a blood-pressure object, names no record and reaches nothing.
- `NSNumber` storage class: should the payload state whether a number was stored as a Boolean, an integer, a floating value, or a decimal? An integer whose magnitude exceeds 2^53 keeps every digit when stored as an integer and is rounded when stored as a floating value.
- `NSData` and `NSDecimalNumber`: the `HKQuantitySample` initializer admits both although `HKObject.h` does not list them; whether the store returns them after a save is not known, and until it is, either could instead stay uncarried and reported.
- Withdrawal: how does a deployment withdraw an artifact that it delivered before its authorization ended, or before a change left its record no carried key?
- Units: a quantity compatible with no listed unit is not carried; extending the list changes the payload for such a key, which is then a new event, not a retry.

### Dependencies and terminology notices

The tables below list this guide's package dependencies and the notices for terminology used by its artifacts and examples.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
