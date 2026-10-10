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

When the source is a caller-classified application, represent it as a HealthKit Application Device.
Use the [Apple Bundle Identifier](NamingSystem-apple-bundle-id.html) namespace for `HKSource.bundleIdentifier`, and copy `HKSourceRevision.version` into the typed application-version slice when HealthKit supplies it.
When HealthKit reports a supported Bluetooth Low Energy source, represent the author as a Grove Recording Device only when the caller supplies a governed stable per-unit token under the deployment's source-actor identity policy.
HMAC-protect it with the deployment-scoped `recording-device` and `device-snapshot` identities defined by the Mobile exchange protocol.
If native source-actor round-trip requires the clear HealthKit source UUID, disclose it only as a separately governed, system-qualified Identifier under that policy.
HealthKit does not specify that its UUID is a serial number, a globally stable hardware identity, or stable outside the contexts in which the exact value recurs.
If the adapter cannot establish whether the source is an application or a device, omit the writer agent rather than guessing its identity. `HKSourceRevision` does not expose an application-or-device discriminator: do not classify the source from the identifier's string shape, source name, or `productType`.
A producer therefore needs explicit source actor classification from its caller or adapter context before it emits this author Device.
The classification is the only caller-supplied part: the author name, identifier, and version are copied from that same sample's `HKSourceRevision` and must not be replaced with independently supplied identity data.
The [Bluetooth heart-rate example](Observation-HealthKitBluetoothHeartRateObservationExample.html) and its [source Provenance](Provenance-HealthKitBluetoothSourceProvenanceExample.html) show this explicit governed branch without treating the source identifier as a serial number.

Link an included source application or device through `Provenance.entity.agent` with participant type `author`.
This author role is distinct from the converter's top-level `assembler` role and does not make either Device a gateway.
When the same application performed both roles, both agents may reference the same Grove Application Device while retaining their separate roles.

Study resources are linked through the study model; they are not source entities unless the conversion literally consumed them as inputs.

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

### Dependencies and terminology notices

The tables below list this guide's package dependencies and the notices for terminology used by its artifacts and examples.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
