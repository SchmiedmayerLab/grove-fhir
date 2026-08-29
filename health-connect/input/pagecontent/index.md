<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

The Grove Health Connect Adapter maps AndroidX Health Connect 1.1 Records that an application has already read into FHIR R4.
It does not request permissions, fetch Records, or define a receiving service.

Readers who are new to FHIR can begin with the Mobile guide's [FHIR basics page](https://grovealliance.org/fhir/mobile/fhir-basics.html).
That page introduces the resources used by these guides, identifiers and references, and the structure of a profile page.

Each emitted Observation follows one of two direct profile-claim modes:

1. A shared measurement declares the exact source-neutral Grove Mobile measurement profile and [Health Connect Observation](StructureDefinition-health-connect-observation.html).
2. A specimen-specific glucose result declares only its exact Health Connect child profile, which inherits the applicable shared and adapter constraints.

The selected profiles define clinical meaning, result shape, unit, time semantics, source and output identities, and the small allowlist of Health-Connect-specific context.
Inherited Mobile, adapter, and core standard profiles are not repeated in `meta.profile`.
The adapter catalog fixes the claim mode for every admitted output.

### Selected record conversions

| Record family | Shared output |
|---|---|
| `ActiveCaloriesBurnedRecord` | active energy |
| `BasalBodyTemperatureRecord` | basal body temperature |
| `BloodGlucoseRecord` | specimen-specific whole-blood, capillary-blood, serum/plasma, or interstitial glucose |
| `BloodPressureRecord` | blood-pressure panel |
| `BodyTemperatureRecord` | body temperature |
| `DistanceRecord` | distance traveled |
| `HeartRateRecord` | one heart-rate Observation per sample |
| `HeightRecord` | body height |
| `OxygenSaturationRecord` | oxygen saturation |
| `RespiratoryRateRecord` | respiratory rate |
| `SleepSessionRecord` | one duration summary plus zero or more stage Observations |
| `StepsRecord` | step-count interval total |
| `WeightRecord` | body weight |

[`catalog/health-connect-adapter.json`](https://grovealliance.org/fhir/catalog/health-connect-adapter.json) is the normative exhaustive inventory.
It lists all 41 `RecordType.all` members with one definitive status, their output cardinality, and exact context mappings.
The table above is a quick-start subset; the [status matrix](status-matrix.html) and adapter catalog are the exhaustive admission contract, and record types omitted here may still be supported there.

### Identity and source context

The mandatory source-record identifier is repository-scoped and does not disclose `Record.metadata.id`.
Every output, including a one-to-one conversion, carries a distinct typed source-output identifier; a synthesized glucose Specimen uses the specimen output role.
When exact upstream traceability is deliberately enabled, the raw metadata id may additionally appear once under a deployment-governed non-Grove Identifier system on the catalog-designated primary output; it never substitutes for either Grove HMAC identifier.
The HMAC algorithm, event/node identities, fullUrl derivation, lifecycle rules, and language-independent conformance test vectors are normative in [`catalog/exchange-protocol.json`](https://grovealliance.org/fhir/catalog/exchange-protocol.json), while the exact Health Connect component bindings are in the adapter catalog.
None of these values becomes `Resource.id`.

Supported source context is represented explicitly:

- standard SNOMED CT specimen types select the glucose profile;
- standard body-position and body-site elements retain admitted blood-pressure and temperature context;
- a typed extension retains non-unknown meal context;
- the producer explicitly selects `RETAIN` to preserve one non-blank title and note on a sleep, mindfulness, or exercise summary, or `OMIT` to deliberately omit them; and
- each sleep-stage result carries the shared Grove coding first and the exact Health Connect stage coding second.

Unknown context is omitted when it does not change the clinical meaning.
A source value that is required to select an exact clinical profile, such as glucose specimen, fails closed when it is unknown or unsupported.

Continue with [Mapping](mapping.html), [Synchronization](synchronization.html), and [Implementation](implementation.html).
Open [Artifacts](artifacts.html) for the complete package surface.
