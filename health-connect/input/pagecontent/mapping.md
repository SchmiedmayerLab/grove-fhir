<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Conversion dispatches on the exact AndroidX Health Connect 1.1 Record class. The normative
inventory, output cardinality, and context mappings are machine-readable in
[`catalog/health-connect-adapter.json`](https://grovealliance.org/fhir/catalog/health-connect-adapter.json); prose never expands or overrides that closed table.
The normative status-vocabulary definitions live on the [guide family page](https://grovealliance.org/fhir/mobile/guides.html#status-vocabulary).
The [authoritative status matrix](status-matrix.html) renders all 41 record classes.

### Common Record mapping

| Health Connect fact | FHIR representation |
|---|---|
| `metadata.id`, repository scope, exact Record class | required source-record identifier |
| deterministic logical output key | required output identifier |
| `metadata.lastModifiedTime` | `Observation.issued` |
| `metadata.recordingMethod` | Grove recording-method extension; unknown is omitted |
| `metadata.device` | recording Device when supplied; no invented hardware identifier |
| `metadata.dataOrigin.packageName` | source application Device and Provenance enterer |

The converter must operate on a Record read from Health Connect. It does not invent
platform-assigned ids, last-modified times, DataOrigin, or Device metadata. Neither
`clientRecordId` nor `clientRecordVersion` replaces `metadata.id`, becomes `Resource.id`,
or becomes `meta.versionId`.

### Identity

[`catalog/health-connect-identity.json`](https://grovealliance.org/fhir/catalog/health-connect-identity.json) is the complete normative identity contract. It
defines the six NamingSystem URLs, JCS string and array canonicalization, SHA-256 preimages,
lexical rules, and test vectors for source Records, single and multi-output Observations,
sleep stages, Specimens, conversion Provenance, and exchange Bundles.

Every digest is `v1:` followed by 64 lowercase hexadecimal digits. The preimage is the
UTF-8 encoding, without BOM, of the specified RFC 8785-compatible array serialization.
Strings contain only Unicode scalar values; invalid surrogates are rejected. Do not replace
the catalog algorithm with locale-sensitive JSON, object serialization, length-prefixed
text, or concatenation. Implementations must pass every published vector.

Business identifiers do not populate `Resource.id`. A producer graph uses the Mobile
entry-identity algorithm to derive deterministic `urn:uuid` fullUrls from complete entry
business identifiers.

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

Codes, units, effective datatypes, profile canonicals, and standard parent profiles come
from [`catalog/measurement-catalog.json`](https://grovealliance.org/fhir/catalog/measurement-catalog.json). Converters normalize only as specified there and
must not stamp a profile whose meaning is not established by the source.

### Glucose specimen and meal context

The specimen-source enum selects one Health Connect adapter-specific glucose profile and a synthesized
[Health Connect Specimen](StructureDefinition-health-connect-specimen.html). The Specimen
declares that adapter profile directly and carries exactly one admitted SNOMED CT type:

| Source enum | Shared profile meaning | SNOMED CT specimen |
|---|---|---|
| `SPECIMEN_SOURCE_WHOLE_BLOOD` | whole-blood glucose | `258580003` |
| `SPECIMEN_SOURCE_CAPILLARY_BLOOD` | capillary-blood glucose | `122554006` |
| `SPECIMEN_SOURCE_PLASMA` | serum/plasma glucose | `119361006` |
| `SPECIMEN_SOURCE_SERUM` | serum/plasma glucose | `119364003` |
| `SPECIMEN_SOURCE_INTERSTITIAL_FLUID` | interstitial glucose | `258479004` |

Tears and unknown are intentionally unsupported because no shared 0.2.0 profile can be
stamped without changing or guessing specimen semantics. Non-unknown relation-to-meal and
meal-type values use the typed meal-context extension and exact adapter CodeSystems.

### Blood pressure and temperature context

Map admitted body position with the standard
`observation-bodyPosition` extension and admitted measurement location with
`Observation.bodySite`. The adapter catalog contains the exact enum-to-SNOMED CT rows for
blood pressure, body temperature, and basal body temperature. Unknown values are omitted;
implementations do not create independent mappings.

### Sleep

Emit one sleep-duration summary for the source session and one sleep-stage Observation per
admitted stage. The summary may retain a non-blank source title through the typed string
extension and source notes through `Annotation.text`. Each stage carries exactly two result
codings in this order: the source-neutral Grove sleep class, then the exact Health Connect
stage token from
`https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-sleep-stage`.
Known source states are never collapsed into `unknown`; sleeping, out-of-bed, and
awake-in-bed retain their exact second coding.

### Provenance and applications

The converting application is a Grove Application Device and the assembler in conversion
Provenance. `DataOrigin.packageName` identifies the application that inserted the Record
into Health Connect and is represented as an enterer. It does not prove which hardware
measured the value or which person performed it. Capture mode does not populate
`Observation.method` or justify a performer.

Conversion Provenance directly declares only the Health Connect conversion profile. Its
inherited Mobile profile is not repeated. Exactly one Provenance per source Record targets
every Observation produced from that Record and carries the same complete source-record
Identifier as its sole source entity.

Study links follow the Mobile study model. They are included only when independently known
and are not inferred from Health Connect metadata.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
