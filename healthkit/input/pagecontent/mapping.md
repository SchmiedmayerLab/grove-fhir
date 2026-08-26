<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Conversion begins by selecting a mapping from the HealthKit sample type. The resulting
Observation follows [HealthKit Observation](StructureDefinition-healthkit-observation.html)
and the applicable clinical or research profile. Preserve the facts HealthKit states;
do not infer hardware, capture mode, clinical meaning, or study membership from an API
type alone.

The normative status-vocabulary definitions live on the [guide family page](https://grovealliance.org/fhir/mobile/guides.html#status-vocabulary).
The [authoritative status matrix](status-matrix.html) renders all 218 source-type identifiers from
the release's machine catalog, including every admitted and fail-closed row.
The [walkthrough](walkthrough.html) applies the rules below to one concrete heart-rate sample, from `HKQuantitySample` to the uploaded exchange Bundle.

### Object identity

Map `HKObject.uuid` to `Observation.identifier` with the
[HealthKit Object Identifier](NamingSystem-healthkit-object-id.html) system. The complete
`(system, value)` pair identifies the exact HealthKit row the Observation was read from.
Do not use the UUID as `Observation.id`; a FHIR repository controls that logical id.
Serialize the value as lowercase UUID text in `8-4-4-4-12` hyphenated form. This pair
identifies the source HealthKit object; it does not claim that independently created
clinical records are globally the same event.

The object UUID is not a deduplication key on its own.
HealthKit replaces a sample when a writer saves one carrying the same `HKMetadataKeySyncIdentifier` and a higher `HKMetadataKeySyncVersion`, and the replacement is a new object with a new UUID.
Deduplicating on the UUID alone therefore counts a revised measurement twice, which affects exactly the revisable data: sleep, energy, heart rate, and anything a server-synced third-party application re-imports.

### Availability time

`Observation.issued` is not emitted. It states when this version of the record became available,
and HealthKit keeps no per-object modification time to answer that. Writing the conversion instant
instead would make an unchanged sample convert to a different Observation on every run, which
defeats the deduplication the exchange identity provides. The conversion instant is recorded once,
on the conversion `Provenance`.

### Logical identity and revisions

When the sample carries `HKMetadataKeySyncIdentifier`, map it to a second `Observation.identifier`
in the shared
[Grove Writer Record Identifier](https://grovealliance.org/fhir/mobile/NamingSystem-grove-writer-record-id.html)
namespace, scoping it to its writer as that namespace requires, and map `HKMetadataKeySyncVersion`
to the
[Grove Writer Record Version](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-writer-record-version.html)
extension.
The Health Connect adapter maps `clientRecordId` and `clientRecordVersion` into that same namespace
and extension, so an application writing the same measurement on both platforms produces the same
value in both.

The two identifiers answer different questions, and a receiver needs both:

- the object identifier names the row that was read, so a re-read of the same row is recognised;
- the sync identifier names the measurement, so a revision of it is recognised as the same
  measurement and the higher sync version supersedes the lower.

A sample without a sync identifier carries neither, and its object identifier remains the only
identity it has. Do not synthesize one: a writer that does not assign a sync identity has not
promised that any two of its samples are the same measurement.

The sample-type identifier dispatches converter code and is preserved as exactly one
additional coding from the adapter's `healthkit-source-type` CodeSystem. The shared or
authoritative standard coding remains the normative clinical meaning; the HealthKit
coding preserves adapter lineage and is not a substitute clinical code.

### Electrocardiograms

A structured HealthKit ECG directly claims the source-neutral Sensor ECG profile and
the HealthKit ECG adapter profile. The caller supplies the already-obtained
`HKElectrocardiogram`, every voltage measurement and exact offset, and every associated
symptom `HKCategorySample`; the adapter performs no query and never resamples. Voltage
offsets must form one exact uniform sequence, the reported count must match, and an
optional sampling frequency must agree exactly with the SampledData period.

Each correlated symptom preserves its UUID, exact Period, type, severity, and complete
`HKSourceRevision` source name, bundle identifier, optional version/product type, and
operating-system version components. These fields are linkable. The producer therefore
requires explicit caller authorization for their disclosure; without it, the lossless
structured ECG claim is not admitted and conversion fails closed. This authorization
is producer input, not a FHIR consent or authorization assertion. Distinct symptom
samples may have the same type; their HealthKit UUIDs, not their types, are unique.

### Values, units, and time

| HealthKit sample type | Required profile and code | FHIR value |
|---|---|---|
| `HKQuantityTypeIdentifierHeartRate` | Grove Mobile Heart Rate (imposes FHIR R4 Heart Rate); LOINC `8867-4` | `valueQuantity`, UCUM `/min` |
| `HKQuantityTypeIdentifierStepCount` | Grove Mobile Step Count; Grove `step-count-total` | `valueQuantity`, UCUM `{steps}`, exact `effectivePeriod` |
| `HKQuantityTypeIdentifierBodyMass` | Grove Mobile Body Weight (imposes FHIR R4 Body Weight); LOINC `29463-7` | `valueQuantity`, UCUM `kg` |

Use `effectiveDateTime` for a point result. Use `effectivePeriod` when HealthKit supplies
a start and end that define an interval. Preserve fractional seconds and the numeric
offset. Map an available IANA time-zone name to the standard FHIR `timezone` extension
on the corresponding date-time value.

Step count preserves the source interval total with Grove `step-count-total` and UCUM
`{steps}`. The effective Period must have both endpoints and a positive duration. The
value is the total count attributed to that Period; do not turn a point sample into a
step count and do not normalize the source count to `/h` or another rate.

### Capture mode and performer

When `HKMetadataKeyWasUserEntered` is explicitly `true`, set the Mobile
`grove-recording-method` extension to `manual-entry`. This flag does not identify the
person who entered the value, so it does not justify a Patient performer. Populate
`Observation.performer` only when separate source evidence identifies a responsible
party. The
[body-weight example](Observation-HealthKitManuallyEnteredBodyWeightExample.html)
shows this mapping.

Do not infer `actively-recorded` or `automatically-recorded` when the flag is absent or
false; omission means the converter does not know the capture mode. Do not add the
Patient as performer solely from capture mode. `Observation.method` remains available
for a clinical measurement technique and is not used for HealthKit capture mode.

### Device, application, and provenance

Map `HKDevice` to a [Grove Recording Device](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-recording-device.html)
only when it identifies the hardware that acquired the value. Omit the recorder when
HealthKit does not establish it. Do not assign a serial number or globally linkable
hardware identifier unless the exchange requires it and the study authorizes it.

Map `HKDevice.hardwareVersion`, `firmwareVersion`, and `softwareVersion` only when each
value is present. Their `Device.version.type` codings use the ISO 11073 MDC revision
codes `531974`, `531976`, and `531975`, respectively. `HKDevice.model` maps to
`Device.modelNumber`; it is not a version. These standard type codes do not assert
conformance to a PHD profile.

Represent the converting app as a
[Grove Application Device](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-application-device.html).
Its Apple bundle identifier uses the [Apple Bundle Identifier](NamingSystem-apple-bundle-id.html)
namespace. The bundle identifier identifies the application product. The converter's
exact software-version string populates its typed application-version slice. If an
implementation has separate release and build values, it must define one deterministic
serialization for this field. Neither the bundle identifier nor that version identifies
an installation, host, account, or person. Do not generate a per-install identifier by
default; add one only under an explicit namespace and use case with the required privacy
authorization. The app is the assembler agent in
[conversion Provenance](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-mobile-conversion-provenance.html).
Converting a stored HealthKit object does not by itself make the app an Observation
gateway; add `observation-gatewayDevice` only if the app actually mediated or routed the
measurement.

The Provenance source entity is the HealthKit object identifier actually consumed by
the transformation. `HKSourceRevision.source` identifies the application or device that
authored that object; do not treat its version as the Grove converter's version.

When the source is an application, represent it as a Grove Application Device. Use the
[Apple Bundle Identifier](NamingSystem-apple-bundle-id.html) namespace for
`HKSource.bundleIdentifier`, and copy `HKSourceRevision.version` into the typed
application-version slice when HealthKit supplies it. When HealthKit reports a supported
Bluetooth Low Energy source as a device UUID, represent the author as a Device and use
the [HealthKit Source Device Identifier](NamingSystem-healthkit-source-device-id.html)
namespace. Such a UUID can link records wherever the exact value recurs; include that
Device and identifier only when the use case and privacy policy authorize the
linkability. HealthKit does not specify that the UUID is a serial number, a globally
stable hardware identity, or stable outside the contexts in which the exact value
recurs. If the
adapter cannot establish whether the source is an application or a device, omit the
source-author agent rather than guessing its identity. `HKSourceRevision` does not expose
an application-or-device discriminator: do not classify the source from the identifier's
string shape, source name, or `productType`. A producer therefore needs explicit source
actor classification from its caller or adapter context before it emits this author
Device. The classification is the only caller-supplied part: the author name, identifier,
and version are copied from that same sample's `HKSourceRevision` and must not be replaced
with independently supplied identity data.
The [Bluetooth heart-rate example](Observation-HealthKitBluetoothHeartRateObservationExample.html)
and its [source Provenance](Provenance-HealthKitBluetoothSourceProvenanceExample.html)
shows this explicit, privacy-gated branch without treating the source identifier as a
serial number.

Link an included source application or device through `Provenance.entity.agent` with
participant type `author`. This author role is distinct from the converter's top-level
`assembler` role and does not make either Device a gateway. When the same application
performed both roles, both agents may reference the same Grove Application Device while
retaining their separate roles.

Study resources are linked through the study model; they are not source entities unless
the conversion literally consumed them as inputs.

### Allowlisted metadata

Map source facts to standard FHIR fields and published extensions before retaining
adapter-specific metadata. Version 0.5.0 permits one residual key:
`HKMetadataKeyHeartRateMotionContext`. It is represented by the named
`Observation.component:heartRateMotionContext` slice and bound to
[HealthKit Heart Rate Motion Context](CodeSystem-healthkit-heart-rate-motion-context.html).
The component is valid only on a LOINC `8867-4` heart-rate Observation.

Map the source `NSNumber` without renumbering or inferring a context:

| `HKHeartRateMotionContext` raw `NSNumber` value | Adapter code | Display |
|---:|---|---|
| `0` | `not-set` | Not Set |
| `1` | `sedentary` | Sedentary |
| `2` | `active` | Active |

The lower-case values in the second column are codes in the adapter's FHIR CodeSystem;
the integer in the first column is the value supplied by HealthKit.
For any other integer, reject the unsupported value or omit the component according to
the importer's policy. Never default an unknown value to `not-set`.

There is no generic metadata extension. Adding another key requires a defined semantic
purpose, a typed FHIR representation, an explicit allowlist update, and validation
examples.

### Study context

Study linkage follows the Mobile guide's
[study model](https://grovealliance.org/fhir/mobile/study.html): a
versioned PlanDefinition is referenced by ResearchStudy, ResearchSubject connects the
Patient to the study, and `workflow-researchStudy` links the Observation. The
[study Bundle](Bundle-HealthKitStudyBundleExample.html) demonstrates the graph.

### Dependencies and terminology notices

The generated tables identify this guide's package dependencies and the notices for
terminology used by its artifacts and examples.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
