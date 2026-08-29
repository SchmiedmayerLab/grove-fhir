<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

The Grove Health Connect Adapter maps AndroidX Health Connect 1.1 Records that have already been read by an application into international FHIR R4.
It does not request permissions, fetch Records, or define a receiving service.

New to FHIR?
[Start with the FHIR basics page](https://grovealliance.org/fhir/mobile/fhir-basics.html) in the Mobile guide.
It covers the resources these guides use, identifiers and references, and how to read a profile page.

Every emitted Observation declares exactly two direct profiles:

1. the exact source-neutral Grove Mobile measurement profile; and
2. [Health Connect Observation](StructureDefinition-health-connect-observation.html).

The shared profile defines clinical meaning, result shape, unit, and time semantics.
The adapter profile defines source and output identities plus the small allowlist of Health-Connect-specific context.
Inherited Mobile and core standard profiles are not repeated in `meta.profile`.

### Supported conversion surface

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

[`catalog/health-connect-adapter.json`](https://grovealliance.org/fhir/catalog/health-connect-adapter.json) is the authoritative closed inventory.
It lists all 41 `RecordType.all` members with one definitive status, their output cardinality, and exact context mappings.
A type omitted from the table above is not silently admitted.

### Identity and source context

The mandatory source-record identifier is repository-scoped and does not disclose `Record.metadata.id`.
Every output, including a one-to-one conversion, carries a distinct typed source-output identifier; a synthesized glucose Specimen uses the specimen output role.
When exact upstream traceability is deliberately enabled, the raw metadata id may additionally appear once under a deployment-governed non-Grove Identifier system on the catalog-designated primary output; it never substitutes for either Grove HMAC identifier.
The HMAC algorithm, event/node identities, fullUrl derivation, lifecycle rules, and cross-language vectors are normative in [`catalog/exchange-protocol.json`](https://grovealliance.org/fhir/catalog/exchange-protocol.json), while the exact Health Connect component bindings are in the adapter catalog.
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
