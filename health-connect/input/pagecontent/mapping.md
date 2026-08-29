<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Conversion dispatches on the exact AndroidX Health Connect 1.1 Record class.
The [Health Connect adapter catalog](https://grovealliance.org/fhir/catalog/health-connect-adapter.json) is normative for record admission, output cardinality, and context mappings.
The normative status-vocabulary definitions live on the [guide family page](https://grovealliance.org/fhir/mobile/guides.html#status-vocabulary).
The [authoritative status matrix](status-matrix.html) lists all 41 record classes.

### Common `Record` mapping

| Health Connect fact | FHIR representation |
|---|---|
| `metadata.id`, repository scope, exact Record class | required source-record identifier |
| deterministic logical output key | required output identifier |
| `metadata.lastModifiedTime` | `Observation.issued` |
| `metadata.clientRecordId` | client record identifier, when the writer assigns one |
| `metadata.clientRecordVersion` | client record version extension |
| `metadata.recordingMethod` | Grove recording-method extension; unknown is omitted |
| `metadata.device` | recording Device when supplied; no invented hardware identifier |
| `metadata.dataOrigin.packageName` | identifier-only logical Device Reference in `Provenance.entity.agent.who`; no Bundle Device entry or Grove Device profile |

The converter must operate on a Record read from Health Connect.
It does not invent platform-assigned ids, last-modified times, DataOrigin, or Device metadata.
Neither `clientRecordId` nor `clientRecordVersion` replaces `metadata.id`, becomes `Resource.id`, or becomes `meta.versionId`; they are carried beside it as the writer's own identity for the measurement.

### Logical identity and revisions

`metadata.id` names the exact stored Record.
It is not a deduplication key on its own: a writer that re-imports a measurement reuses its `clientRecordId` and raises its `clientRecordVersion`, and the stored Record then carries a new `metadata.id`.
Deduplicating on `metadata.id` alone therefore counts a revised measurement twice.

When the Record carries a non-blank `clientRecordId`, map it to a typed `writer-record` `Observation.identifier`.
Derive it from the complete writer-application Identifier pair and logical writer record id as the exchange protocol requires.
Map `clientRecordVersion`, including the AndroidX `Long` default `0`, to the [Grove Writer Record Version](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-writer-record-version.html) extension.
Reject a negative version or a present blank id.
A Record without a `clientRecordId` carries neither; do not synthesize one, because a writer that assigns no client record identity has not promised that any two of its Records are the same measurement.

The HealthKit adapter maps `HKMetadataKeySyncIdentifier` and `HKMetadataKeySyncVersion` into the same typed role and extension only when it can supply the same complete writer-application pair.
Cross-platform equality is asserted only when all three writer-record preimage components are identical.

### Deterministic Grove identifiers

[`catalog/exchange-protocol.json`](https://grovealliance.org/fhir/catalog/exchange-protocol.json) is the complete normative identity and lifecycle algorithm.
The Health Connect adapter catalog binds `Metadata.id`, the exact Record class, and a complete deployment-owned repository-scope pair to its source-record components, and publishes closed multi-output discriminator grammars.

Values are HMAC-SHA-256 over typed, non-empty Unicode-scalar strings using unsigned 32-bit length-framed UTF-8 fields.
Delimiters and Unicode are therefore unambiguous, and independent deployments are not silently linkable.
Implementations must reproduce every published vector and must retain old key epochs while an identifier can be replayed or retracted.
When native round-trip genuinely requires `Metadata.id`, a deployment may additionally disclose it on the one-to-one primary Observation under an explicit absolute repository namespace.
That optional Identifier never replaces Grove identity, is not repeated on graph children or supporting Specimens, and is not copied into `Resource.id`, entry keys, arbitrary components, untyped metadata, attachment names, or logs.

Business identifiers do not populate `Resource.id`.
A producer graph uses the Mobile entry-identity algorithm to derive deterministic `urn:uuid` fullUrls from complete entry business identifiers.

### Shared result mappings

| Record | Shared measurement | Result and time |
|---|---|---|
| `ActiveCaloriesBurnedRecord` | active energy | `Quantity` kcal over exact `Period` |
| `BasalBodyTemperatureRecord` | basal body temperature | `Quantity` Cel at `dateTime` |
| `BloodGlucoseRecord` | specimen-specific glucose | `Quantity` mg/dL at `dateTime`, plus required Specimen |
| `BloodPressureRecord` | blood pressure | systolic and diastolic components in mm[Hg] at `dateTime` |
| `BodyTemperatureRecord` | body temperature | `Quantity` Cel at `dateTime` |
| `DistanceRecord` | distance traveled | `Quantity` m over exact `Period` |
| `HeartRateRecord` | heart rate | one `Quantity` /min Observation per sample time |
| `HeightRecord` | body height | `Quantity` cm at `dateTime` |
| `OxygenSaturationRecord` | oxygen saturation | `Quantity` % at `dateTime` |
| `RespiratoryRateRecord` | respiratory rate | `Quantity` /min at `dateTime` |
| `SleepSessionRecord` | sleep duration and stage | duration summary in h plus zero or more coded stage Periods |
| `StepsRecord` | step count | `Quantity` `{steps}` over exact `Period` |
| `WeightRecord` | body weight | `Quantity` kg at `dateTime` |

Codes, units, effective datatypes, profile canonicals, and standard parent profiles come from [`catalog/measurement-catalog.json`](https://grovealliance.org/fhir/catalog/measurement-catalog.json). Converters normalize only as specified there and must not stamp a profile whose meaning is not established by the source.

### Glucose specimen and meal context

The specimen-source enum selects one Health Connect adapter-specific glucose profile and a synthesized [Health Connect Specimen](StructureDefinition-health-connect-specimen.html).
The Specimen declares that adapter profile directly and carries exactly one admitted SNOMED CT type:

| Source enum | Shared profile meaning | SNOMED CT specimen |
|---|---|---|
| `SPECIMEN_SOURCE_WHOLE_BLOOD` | whole-blood glucose | `258580003` |
| `SPECIMEN_SOURCE_CAPILLARY_BLOOD` | capillary-blood glucose | `122554006` |
| `SPECIMEN_SOURCE_PLASMA` | serum/plasma glucose | `119361006` |
| `SPECIMEN_SOURCE_SERUM` | serum/plasma glucose | `119364003` |
| `SPECIMEN_SOURCE_INTERSTITIAL_FLUID` | interstitial glucose | `258479004` |

Tears and unknown are intentionally unsupported because no shared profile under the Grove FHIR contracts can be stamped without changing or guessing specimen semantics.
Non-unknown relation-to-meal and meal-type values use the typed meal-context extension and exact adapter CodeSystems.

### Blood pressure and temperature context

Map admitted body position with the standard `observation-bodyPosition` extension and admitted measurement location with `Observation.bodySite`.
The adapter catalog contains the exact enum-to-SNOMED CT rows for blood pressure, body temperature, and basal body temperature.
Unknown values are omitted; implementations do not create independent mappings.

Skin temperature has its own narrower location domain: finger, toe, and wrist only.
A present body-position or body-site concept contains exactly one admitted SNOMED CT coding; equivalent translations may accompany it in other systems, but a foreign-only or text-only concept is not an admitted source projection.

### Exact source-coded values

Menstruation flow, ovulation-test result, sexual-activity protection use, cervical-mucus appearance and sensation, exercise type, and exercise segment type carry two codings: the source-neutral Grove result first and the exact AndroidX 1.1 token second.
The complete source domains, their shared projections, and their output locations are normative in the adapter catalog and published complete CodeSystems. Out-of-domain integers fail conversion.
Cervical `SENSATION_UNKNOWN` alone maps to omission; the other UNKNOWN constants are retained when the catalog says they are semantically distinct source assertions.

An exercise session emits exactly one workout summary plus one workout-segment member for every source segment and lap.
A lap uses the exact structural token `EXERCISE_LAP`.
The producer explicitly selects `RETAIN` to preserve a non-blank title and one source note on the summary, or `OMIT` to deliberately omit both; children carry neither.

### Sleep

Emit one sleep-duration summary for the source session and one sleep-stage Observation per admitted stage.
The producer explicitly selects `RETAIN` to preserve a non-blank source title through the typed string extension and one source note through `Annotation.text`, or `OMIT` to deliberately omit both.
Each stage carries exactly two result codings in this order: the source-neutral Grove sleep class, then the exact Health Connect stage token from `https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-sleep-stage`.
Known source states are never collapsed into `unknown`; sleeping, out-of-bed, and awake-in-bed retain their exact second coding.

### Mindfulness

Emit one point-to-point mindfulness-session Observation for each `MindfulnessSessionRecord`.
Preserve the exact closed AndroidX session type in `Observation.method`.
The producer explicitly selects `RETAIN` to preserve a non-blank title through the shared session-title extension and one non-blank note through `Annotation.text`, or `OMIT` to deliberately omit both.
These fields are admitted only on an output whose record-type extension is `MindfulnessSessionRecord`; they are not inferred for other records.

### Provenance and applications

The converting application is a Grove Application Device and the assembler in conversion Provenance. `DataOrigin.packageName` identifies the application that inserted the Record into Health Connect and is represented as the enterer's identifier-only logical Device Reference.
It is not a Bundle Device node, does not claim a Grove Device profile, and does not invent an installation or event snapshot.
The Reference fixes `type` to `Device`, prohibits a literal `reference`, and carries the complete Android package-name Identifier.
It does not prove which hardware measured the value or which person performed it.
Capture mode does not populate `Observation.method` or justify a performer.

Conversion Provenance directly declares only the Health Connect conversion profile.
Its inherited Mobile profile is not repeated.
Exactly one Provenance per source Record targets every Observation produced from that Record and carries the same complete source-record Identifier as its sole source entity.

Study links follow the Mobile study model.
They are included only when independently known and are not inferred from Health Connect metadata.

### Dependencies and terminology notices

The tables below list this guide's package dependencies and the notices for terminology used by its artifacts and examples.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
