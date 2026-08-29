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

The sample-type identifier dispatches converter code and is preserved as exactly one `healthkit-source-type-extension` value.
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
The relevant Grove FHIR Implementation Guide targets R4 and does not perform cross-version conversion, so a clinical-record row is admitted only when `HKFHIRResource.fhirVersion.fhirRelease` is exactly `r4`.
Reject `dstu2`, an unknown or missing release, and every future release before creating the DocumentReference.
Do not infer the release from JSON shape and do not relabel, upgrade, or downgrade the preserved bytes.

An admitted R4 payload is carried byte-for-byte under the HealthKit Clinical Record Document profile and `fhir-r4-resource` format contract.
The DocumentReference carries exactly one `healthkit-clinical-fhir-release` extension whose `valueCode` is fixed to `r4`; `catalog/healthkit-adapter.json.clinicalRecordAdmission.fhirRepresentation` publishes the exact URL, element, cardinality, and value.
That envelope does not assert that Grove has validated or endorsed the issuer's clinical content; it asserts only the exact source release, payload integrity, identity, and provenance contract.

### Values, units, and time

| HealthKit sample type | Required profile and code | FHIR value |
|---|---|---|
| `HKQuantityTypeIdentifierHeartRate` | Grove Mobile Heart Rate (imposes FHIR R4 Heart Rate); LOINC `8867-4` | `valueQuantity`, UCUM `/min` |
| `HKQuantityTypeIdentifierStepCount` | Grove Mobile Step Count; Grove `step-count-total` | `valueQuantity`, UCUM `{steps}`, exact `effectivePeriod` |
| `HKQuantityTypeIdentifierBodyMass` | Grove Mobile Body Weight (imposes FHIR R4 Body Weight); LOINC `29463-7` | `valueQuantity`, UCUM `kg` |

Use `effectiveDateTime` for a point result.
Use `effectivePeriod` when HealthKit supplies a start and end that define an interval. Preserve fractional seconds and the numeric offset.
Map an available IANA time-zone name to the standard FHIR `timezone` extension on the corresponding date-time value.

Step count preserves the source interval total with Grove `step-count-total` and UCUM `{steps}`.
The effective Period must have both endpoints and a positive duration.
The value is the total count attributed to that Period; do not turn a point sample into a step count and do not normalize the source count to `/h` or another rate.

### Capture mode and performer

When `HKMetadataKeyWasUserEntered` is explicitly `true`, set the Mobile `grove-recording-method` extension to `manual-entry`.
This flag does not identify the person who entered the value, so it does not justify a Patient performer.
Populate `Observation.performer` only when separate source evidence identifies a responsible party.
The [body-weight example](Observation-HealthKitManuallyEnteredBodyWeightExample.html) shows this mapping.

Do not infer `actively-recorded` or `automatically-recorded` when the flag is absent or false; omission means the converter does not know the capture mode.
Do not add the Patient as performer solely from capture mode. `Observation.method` remains available for a clinical measurement technique and is not used for HealthKit capture mode.

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
If the adapter cannot establish whether the source is an application or a device, omit the source-author agent rather than guessing its identity. `HKSourceRevision` does not expose an application-or-device discriminator: do not classify the source from the identifier's string shape, source name, or `productType`.
A producer therefore needs explicit source actor classification from its caller or adapter context before it emits this author Device.
The classification is the only caller-supplied part: the author name, identifier, and version are copied from that same sample's `HKSourceRevision` and must not be replaced with independently supplied identity data.
The [Bluetooth heart-rate example](Observation-HealthKitBluetoothHeartRateObservationExample.html) and its [source Provenance](Provenance-HealthKitBluetoothSourceProvenanceExample.html) show this explicit governed branch without treating the source identifier as a serial number.

Link an included source application or device through `Provenance.entity.agent` with participant type `author`.
This author role is distinct from the converter's top-level `assembler` role and does not make either Device a gateway.
When the same application performed both roles, both agents may reference the same Grove Application Device while retaining their separate roles.

Study resources are linked through the study model; they are not source entities unless the conversion literally consumed them as inputs.

### Supported HealthKit metadata

Map source facts to standard FHIR fields and published extensions before retaining adapter-specific metadata.
The Grove FHIR contracts permit one residual key: `HKMetadataKeyHeartRateMotionContext`.
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

There is no generic metadata extension.
Adding another key requires a defined semantic purpose, a typed FHIR representation, an explicit allowlist update, and validation examples.

### Study context

Study linkage follows the Mobile guide's [study model](https://grovealliance.org/fhir/mobile/study.html): a versioned PlanDefinition is referenced by ResearchStudy, ResearchSubject connects the Patient to the study, and `workflow-researchStudy` links the Observation.
The [study Bundle](Bundle-HealthKitStudyBundleExample.html) demonstrates the graph.

### Dependencies and terminology notices

The tables below list this guide's package dependencies and the notices for terminology used by its artifacts and examples.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
