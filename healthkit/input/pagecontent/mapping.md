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
This matters even for a single output: source-record identity answers which source revision was consumed, while source-output identity names the exact FHIR output emitted in every version of the record.
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
Each symptom is its own record, with its own source record and conversion Provenance, and it may travel in the same Bundle as the ECG.
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

A workout retraction, like every HealthKit retraction, names the source record as its only target and suppresses the session and every segment of every version of the record.
An `HKDeletedObject` carries none of the deleted workout's events or activities, and the source-record target needs none of the segment identities a conversion emitted.

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
The correlation's own metadata can be preserved through its typed source-metadata extension. An object's other metadata cannot be moved into that extension without losing its owner; report unrepresented object keys as `mobile-omission.unmodeled-metadata`, naming each key once however many objects carry it. A parent value with the same key does not represent the object's value.

### Device, application, and provenance

Map every non-nil `HKObject.device` to a [Grove Recording Device](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-recording-device.html). When `HKObject.device` is absent, create a recording Device if the sample supplies a nonblank string for a device metadata field listed below. Apply these mappings to both Observation and document outputs: `Observation.device` references the recording Device, and `DocumentReference.author` includes it. Carry the available device facts without inferring a stable physical-unit identity from descriptive metadata.
The Device always carries the content `device-snapshot` identity, minted over its complete rendered content after every field is set.
It also carries the typed `recording-device` identity only when a governed stable per-unit token exists: `HKDevice.localIdentifier` when it is nonempty and the deployment has verified that it is stable and names exactly one unit for the acquisition scope, or another caller-governed token.
That token is local to the host that recorded the sample and writable by any application, so its HMAC is scoped by the writing source's `HKSource.bundleIdentifier`, and the same token stated by two writers names two units.
The scope separates writers only: a writer that states the same token for distinct units of one subject, on one host or on several, merges them into one identity, and only the deployment's verification that the token names exactly one unit guards against that.
Without a token the Device is still emitted and referenced; manufacturer, model, version, subject, a snapshot, or their digest never establish a physical instance, and equal snapshots are never inferred to be one unit.

| HealthKit field | Grove Recording Device element |
|---|---|
| `HKDevice.name` | `deviceName` of type `user-friendly-name`; the name may be one a person gave the device |
| `HKDevice.manufacturer` | `manufacturer` |
| `HKDevice.model` | `modelNumber`; it is not a version |
| `HKDevice.hardwareVersion` | `version` of type MDC `531974` |
| `HKDevice.firmwareVersion` | `version` of type MDC `531976` |
| `HKDevice.softwareVersion` | `version` of type MDC `531975` |
| `HKDevice.localIdentifier` | `identifier` of type `device-local-identifier`, clear, under a deployment-owned system |
| `HKDevice.UDIDeviceIdentifier` | `udiCarrier.deviceIdentifier` |
| `HKMetadataKeyDeviceSerialNumber` | `serialNumber` |
| `HKMetadataKeyDeviceName` | `deviceName` of type `user-friendly-name`, when `HKDevice.name` is absent |
| `HKMetadataKeyDeviceManufacturerName` | `manufacturer`, when `HKDevice.manufacturer` is absent |
| `HKMetadataKeyUDIDeviceIdentifier` | `udiCarrier.deviceIdentifier`, when `HKDevice.UDIDeviceIdentifier` is absent |
| `HKMetadataKeyUDIProductionIdentifier` | the [Grove UDI Production Identifier](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-udi-production-identifier.html) extension on `udiCarrier`, because FHIR R4 has no element for the raw production identifier |

An `HKDevice` property wins over a device metadata key, a metadata key fills only an absent field, and the serial number comes only from its metadata key.
Map each field only when its value is present. Do not duplicate a faithfully mapped value in the typed metadata extension. If a metadata value conflicts with the preferred `HKDevice` property, preserve that different value in the typed extension. Device metadata describes recording hardware; it does not identify the gateway application.
The `Device.version.type` codings use the ISO 11073 MDC revision codes; these standard type codes do not assert conformance to a PHD profile.
The clear local identifier links a participant's samples from one device within one host; a deployment that shares or exports data applies its own policy to it, to the serial number, and to a device name.
`recordingDeviceIdentity.fieldMappings` in [`catalog/healthkit-adapter.json`](https://grovealliance.org/fhir/catalog/healthkit-adapter.json) states the same mapping.

Represent the converting app as a [HealthKit Application Device](StructureDefinition-healthkit-application-device.html), which specializes the shared Grove Application Device.
Its required, typed Apple bundle identifier uses the [Apple Bundle Identifier](NamingSystem-apple-bundle-id.html) namespace and identifies only the application product.
Put the human-facing release and build into separate typed Device version entries.
Represent host hardware and its operating-system name, version, and build as a distinct immutable [Grove Host Device](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-host-device.html) referenced by `Device.parent`; never put the host OS on the application Device.
The application's mandatory content `device-snapshot` HMAC identifies this immutable content, not an installation, account, or person; the host Device it references through `Device.parent` is part of that content.
The app is the assembler agent in [conversion Provenance](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-mobile-conversion-provenance.html). Converting a stored HealthKit object does not by itself make the app an Observation gateway; add `observation-gatewayDevice` only if the app actually mediated or routed the measurement.

The Provenance source entity repeats the typed source-record Identifier actually consumed by the transformation. `HKSourceRevision.source` identifies the application or device that authored that object; do not treat its version as the Grove converter's version.
Comparing it with the converting application's build under the same-application rule below does not treat it as the converter's version.

When the source is a caller-classified application, represent it as a HealthKit Application Device.
Use the [Apple Bundle Identifier](NamingSystem-apple-bundle-id.html) namespace for `HKSource.bundleIdentifier`.
HealthKit takes `HKSourceRevision.version` from the source's `CFBundleVersion`: when HealthKit supplies it, copy it unchanged into the typed application-build slice (`grove-application-version-type#build`), never into the application-version slice.
When HealthKit reports a supported Bluetooth Low Energy source, represent the author as a Grove Recording Device with its content `device-snapshot` identity, under the deployment's source-actor identity policy.
When the caller also supplies a governed stable per-unit token, HMAC-protect it in the deployment-scoped `recording-device` identity defined by the Mobile exchange protocol.
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

When the [writer rules](#device-application-and-provenance) state no author agent for the source entity of a HealthKit conversion Provenance, because the caller did not classify the source or classified it as something those rules cannot state, such as a device that is not a supported Bluetooth Low Energy source, that source entity carries one [HealthKit Source Revision](StructureDefinition-healthkit-source-revision.html) extension, so omitting the writer does not lose where the object came from.
The extension never appears beside an author agent: a graph states a source as its writer or through its source revision, never both.
Only the source entity of a conversion Provenance carries it, and only for a record with an `HKSourceRevision`; a tracked medication has none, because `HKUserAnnotatedMedication` is not an `HKObject`.

The extension has five members, each one `valueString` that appears at most once, in this order:

| Member | `HKSourceRevision` fact | Value | By default |
|---|---|---|---|
| `sourceName` | `source.name` | the exact string | emitted |
| `sourceBundleIdentifier` | `source.bundleIdentifier` | the exact string | emitted |
| `version` | `version` | the exact string, the source's build, which HealthKit takes from its `CFBundleVersion` | emitted |
| `productType` | `productType` | the exact string, the product type of the device that ran HealthKit when the object was created | emitted |
| `operatingSystemVersion` | `operatingSystemVersion` | its `majorVersion`, `minorVersion`, and `patchVersion`, each as canonical decimal integer text without a leading zero and with a `-` only before a negative value, joined by `.`; all three always appear, so `26.5.0` is never written `26.5` | emitted |

A member whose string fact HealthKit does not supply, or supplies empty, is left out.
`HKSourceRevision.operatingSystemVersion` is not optional, so its member is present, `0.0.0` included, unless a disclosure policy withholds it.

Every member is emitted by default: the producer carries every source fact, and consumers filter what they do not need.
`HKSource.name` can be the name a person gave a device, and a device's `HKSource.bundleIdentifier` can embed an identifier that HealthKit assigns to that one device; a producer cannot tell either from an application's without classifying the source, so a deployment that shares or exports data applies its own policy to them.
A deployment's disclosure policy may withhold any of them, or the whole extension; as for every omission a disclosure policy chooses, that is not reported, and an extension with no member left is not emitted.

The extension describes the consumed object, not an actor: it adds no agent, participant type, or Device, and it states neither that the source is an application nor that it is a device.
The rule that a source is never classified from its identifier's string shape, source name, or `productType` holds for its members as it holds for `HKSourceRevision`.
`sourceBundleIdentifier` is text, never an Identifier.
The extension mints no identity, and no business identity is derived from it: adding or withholding it, or any of its members, changes no `source-record`, `source-output`, or `writer-record` Identifier.
It is part of the conversion Provenance, so a record delivered again with the extension or any of its members added or withheld is changed content: it changes the record version and is a new version of the source record, as the [Mobile exchange graph](https://grovealliance.org/fhir/mobile/observations.html#exchange-graph) requires.
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

#### Typed source metadata

The HealthKit package defines the typed source-metadata extension at `https://grovealliance.org/fhir/core/StructureDefinition/metadata` for source values alongside their clinical mappings. Metadata does not override any clinical mapping or relax a required-value check.

Emit at most one container on the primary output, including a recording or clinical DocumentReference wrapper. Never alter embedded clinical source bytes. Each child has URL `entry` and two defined children, in order: `key` with the exact runtime key in `valueString`, and `value` with its typed value. Do not normalize Unicode; distinct source keys remain distinct. Emit each key once, ordered by UTF-16 code units.

Each `value` child carries exactly one `valueString`, `valueDecimal`, `valueBoolean`, `valueDateTime`, `valueCoding`, or `valueQuantity`. Numeric values are finite; dates have a full date-time and offset; coded values name their system and code; quantities state a finite value and compatible UCUM unit. A quantity's original unit is not exposed by HealthKit. Preserve supported custom keys by default within requested metadata scope; report unsupported values instead of converting them to descriptive strings. A deployment's explicit exclusions remain observable separately from conversion failures.

Normalize known quantity keys to the units below. Convert only after `HKQuantity.is(compatibleWith:)` succeeds. A percentage uses the HealthKit fraction multiplied by 100 for UCUM `%`; a quantity incompatible with its declared key's unit is an omission, never guessed from another dimension.

| SDK metadata key (common `HKMetadataKey` prefix omitted) | UCUM code |
|---|---|
| `WeatherTemperature` | `Cel` |
| `WeatherHumidity`, `AlpineSlopeGrade` | `%` |
| `HeartRateRecoveryActivityDuration`, `FitnessMachineDuration`, `AudioExposureDuration` | `s` |
| `HeartRateRecoveryMaxObservedRecoveryHeartRate`, `HeartRateEventThreshold` | `/min` |
| `AverageSpeed`, `MaximumSpeed` | `m/s` |
| `ElevationAscended`, `ElevationDescended`, `IndoorBikeDistance`, `CrossTrainerDistance` | `m` |
| `AverageMETs` | `kcal/(kg.h)` |
| `AudioExposureLevel`, `HeadphoneGain` | `dB[SPL]` |
| `BarometricPressure` | `mm[Hg]` |
| `VO2MaxValue`, `LowCardioFitnessEventThreshold` | `mL/kg/min` |
| `MaximumLightIntensity` | `lx` |
| `SessionEstimate` on a supported quantity sample | the sample's selected measurement unit |

For a quantity under another key, use the first compatible unit in this ordered list: `1`, `/min`, `s`, `m`, `m/s`, `g`, `L`, `L/min`, `kcal`, `W`, `Cel`, `mm[Hg]`, `mg/dL`, `mL/kg/min`, `kcal/(kg.h)`, `[iU]`, `S`, `dB[SPL]`, `dB`, `lx`. Use the corresponding HealthKit constructors, not UCUM strings as HealthKit unit spellings. No compatible unit, a nonfinite result or a result outside the producer's FHIR decimal domain is reported as unsupported. A custom dimensionless percentage uses `1` and retains its fractional value.

Known SDK enumeration keys use their Apple documentation system and raw integer code; the metadata value is independent of any clinical coded mapping. Never truncate a fractional number to select an enumeration case. Preserve CFBoolean as Boolean and other numeric zero/one values as decimals; determine the type from the source object, not its numeric value. Arrays, dictionaries, binary values and unknown value classes are not silently stringified or recursively admitted. Additional classes require verified HealthKit store behavior and a specified FHIR representation.

The extension adds no source/output identifier. Changing metadata changes the record version, and retries of the same version preserve its content. The native `HKObject.uuid` is not automatically copied into metadata; governed native identifier disclosure remains independent. A producer must retain metadata on the source output and avoid repeating a record's metadata on unrelated child outputs. Metadata from contained correlation objects or workout parts remains associated with that part; it is never silently substituted for the parent metadata.

### Withheld metadata

Use the clinical, device and other structured mappings in this guide first. The typed source-metadata extension carries values that have no faithful representation through those mappings; do not duplicate an already represented value. Conflicting source values and values whose original form cannot be recovered from a mapped keyed identity remain eligible for the extension. Preserving metadata does not create an additional clinical interpretation.

| Runtime key | SDK constant | Source types | Element |
|---|---|---|---|
| `HKTimeZone` | `HKMetadataKeyTimeZone` | every type with an Observation output | the `timezone` extension on each `effective[x]` date-time, as the [time rules](#values-units-and-time) define |
| `HKWasUserEntered` | `HKMetadataKeyWasUserEntered` | every type with an Observation output | the `grove-recording-method` extension, `manual-entry` when the key states `true`, as the [capture-mode rule](#capture-mode-and-performer) defines |
| `HKMetadataKeySyncIdentifier` | `HKMetadataKeySyncIdentifier` | every type with an Observation output | the `writer-record` Identifier, as the [revision rules](#logical-identity-and-revisions) define |
| `HKMetadataKeySyncVersion` | `HKMetadataKeySyncVersion` | every type with an Observation output | the Grove Writer Record Version extension beside the `writer-record` Identifier |
| `HKDeviceSerialNumber` | `HKMetadataKeyDeviceSerialNumber` | every type with an Observation or document output | `serialNumber` of the recording Device, as the device rules define |
| `HKDeviceName` | `HKMetadataKeyDeviceName` | every type with an Observation or document output | `deviceName` of type `user-friendly-name` of the recording Device, when `HKDevice.name` is absent |
| `HKDeviceManufacturerName` | `HKMetadataKeyDeviceManufacturerName` | every type with an Observation or document output | `manufacturer` of the recording Device, when `HKDevice.manufacturer` is absent |
| `HKUDIDeviceIdentifier` | `HKMetadataKeyUDIDeviceIdentifier` | every type with an Observation or document output | `udiCarrier.deviceIdentifier` of the recording Device, when `HKDevice.UDIDeviceIdentifier` is absent |
| `HKUDIProductionIdentifier` | `HKMetadataKeyUDIProductionIdentifier` | every type with an Observation or document output | the Grove UDI Production Identifier extension on `udiCarrier` of the recording Device |
| `HKMetadataKeyHeartRateMotionContext` | `HKMetadataKeyHeartRateMotionContext` | `HKQuantityTypeIdentifierHeartRate` | `Observation.component:heartRateMotionContext`, as [above](#supported-healthkit-metadata) |
| `HKHeartRateEventThreshold` | `HKMetadataKeyHeartRateEventThreshold` | `HKCategoryTypeIdentifierHighHeartRateEvent`, `HKCategoryTypeIdentifierLowHeartRateEvent` | `Observation.component:threshold` of the notification, in UCUM `/min` |
| `HKLowCardioFitnessEventThreshold` | `HKMetadataKeyLowCardioFitnessEventThreshold` | `HKCategoryTypeIdentifierLowCardioFitnessEvent` | `Observation.component:threshold` of the notification, in UCUM `mL/kg/min` |
| `HKMetadataKeyAppleECGAlgorithmVersion` | `HKMetadataKeyAppleECGAlgorithmVersion` | `HKDataTypeIdentifierElectrocardiogram` | `Observation.method` of the ECG Observation |
| `HKInsulinDeliveryReason` | `HKMetadataKeyInsulinDeliveryReason` | `HKQuantityTypeIdentifierInsulinDelivery` | the delivery-reason component that the Insulin Delivery measurement requires |
| `HKMenstrualCycleStart` | `HKMetadataKeyMenstrualCycleStart` | `HKCategoryTypeIdentifierMenstrualFlow` | `Observation.component:cycleStart` |
| `HKSexualActivityProtectionUsed` | `HKMetadataKeySexualActivityProtectionUsed` | `HKCategoryTypeIdentifierSexualActivity` | `Observation.valueCodeableConcept`, `protected` or `unprotected` |

Withhold every metadata key that an accepted record carries and that neither an output of its graph (including its typed source-metadata extension) nor the recording Device it references represents, and report those keys as `mobile-omission.unmodeled-metadata`, naming each key once by its runtime key.
For source-sample metadata, this applies when the typed extension cannot preserve the value, including unsupported classes or a quantity with no supported compatible unit. An intentional exclusion is reported separately. Contained metadata follows the owner-preserving rules below.
A runtime key is the string that a metadata dictionary holds as the key, as the table's first column gives it, not the name of the SDK constant that holds it, which can differ: `HKMetadataKeyTimeZone` holds `HKTimeZone`.
A key that no SDK constant declares is named the same way.
`HKMetadataKeyWasUserEntered` stating `false` creates no manual-entry clinical assertion, but the typed extension preserves that Boolean when supplied on the source sample. An unsupported value remains an omission.
A [HealthKit Recording Document](StructureDefinition-healthkit-recording-document.html) can preserve metadata through the typed extension without inventing an Observation mapping or a writer-record identity.
The device mappings apply even when the sample states no `HKDevice`. A recognized nonblank string creates the corresponding recording Device fact; other values remain eligible for the typed extension when supported.

The typed extension carries the source sample metadata. It does not flatten an object of a blood-pressure correlation or an `HKWorkoutEvent` or `HKWorkoutActivity` into its parent. A contained value counts as represented only where the existing clinical mapping explicitly incorporates it; otherwise it remains an observable omission. This extension does not represent metadata belonging to contained parts.
The [correlation-object rules](#blood-pressure-correlation-objects) decide instead what a blood-pressure object's `HKMetadataKeyTimeZone` and `HKMetadataKeyWasUserEntered` contribute.

Reporting never relaxes a rejection: a half or invalid sync pair that the record itself carries rejects the record even when no output could carry the pair.
Report intentional disclosure exclusions separately from unsupported-value omissions; conversion success does not assert complete source coverage.

### Study context

Study linkage follows the Mobile guide's [study model](https://grovealliance.org/fhir/mobile/study.html): a versioned PlanDefinition is referenced by ResearchStudy, ResearchSubject connects the Patient to the study, and `workflow-researchStudy` links the Observation.
The [study Bundle](Bundle-HealthKitStudyBundleExample.html) demonstrates the graph.

### Dependencies and terminology notices

The tables below list this guide's package dependencies and the notices for terminology used by its artifacts and examples.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
