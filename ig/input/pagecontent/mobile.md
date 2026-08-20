<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Grove represents a measurement collected through a mobile health platform as a FHIR R4
`Observation`. The [Grove Mobile Sensor Observation profile](StructureDefinition-grove-mobile-sensor-observation.html)
keeps the clinical measurement in standard FHIR fields and preserves the source context
needed to interpret the record later.

The [step-count example](Observation-GroveStepCountObservationExample.html) is the best
place to begin. It is also available as [raw JSON](Observation-GroveStepCountObservationExample.json).

### The resource at a glance

| Question | FHIR representation |
|---|---|
| What was measured? | `Observation.code` |
| What was the result? | `Observation.value[x]` |
| Who does it describe? | `Observation.subject` |
| When was it measured? | `Observation.effective[x]` |
| Which source record is this? | `Observation.identifier` |
| Which hardware recorded it? | `Observation.device` |
| Which app and operating system saved it? | `observation-gatewayDevice` extension |
| How was it captured? | [Recording Method](StructureDefinition-grove-recording-method.html) extension |
| Which source details have no standard FHIR field? | [Platform Metadata](StructureDefinition-grove-platform-metadata.html) extension |

This abbreviated step-count resource shows the central shape:

```json
{
  "resourceType": "Observation",
  "meta": {
    "profile": [
      "https://grovealliance.org/fhir/core/StructureDefinition/grove-mobile-sensor-observation"
    ],
    "source": "https://grovealliance.org/fhir/source/healthkit"
  },
  "identifier": [{
    "system": "https://grovealliance.org/fhir/sid/healthkit-sample-id",
    "value": "F1E2D3C4-4B5A-4C6D-8E9F-1234567890AB"
  }],
  "status": "final",
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "55423-8",
      "display": "Number of steps in unspecified time Pedometer"
    }]
  },
  "subject": { "reference": "Patient/GrovePatientExample" },
  "effectivePeriod": {
    "start": "2026-08-12T09:00:00-07:00",
    "end": "2026-08-12T10:00:00-07:00"
  },
  "valueQuantity": {
    "value": 1042,
    "system": "http://unitsofmeasure.org",
    "code": "{steps}"
  }
}
```

### Clinical coding and source coding

Use a standard clinical code whenever one describes the measurement. The step-count
example uses LOINC `55423-8`; the heart-rate example uses LOINC `8867-4`. A second
coding may preserve the HealthKit sample type. Consumers should use the clinical code
for clinical interpretation and the platform code when they need the exact source type.

HealthKit code systems and value sets are published in the
[Platform Terminology guide](https://schmiedmayerlab.github.io/grove-fhir/platforms/).

### Source identity

Every mobile observation carries at least one source-record identifier. FHIR compares
identifiers as the complete `(system, value)` pair. For a HealthKit sample, the system
is `https://grovealliance.org/fhir/sid/healthkit-sample-id` and the value is the
`HKObject.uuid`.

Receivers use the complete pair when detecting a record that has already been imported.
The value alone is not globally unique and must not be compared without its system.

### Subject and time

`Observation.subject` is required because a platform sample does not identify the FHIR
Patient on its own. The application performing the conversion supplies that reference.

Use `effectiveDateTime` for a point measurement and `effectivePeriod` for an interval.
Preserve fractional seconds and the UTC offset. When the named time zone is known, add
the standard FHIR `timezone` extension to the effective value.

### Sensor and gateway

The recording sensor and the saving application have different roles:

- `Observation.device` references a [Grove Sensor Device](StructureDefinition-grove-sensor-device.html),
  such as a watch, chest strap, scale, or phone.
- The standard `observation-gatewayDevice` extension references a
  [Grove Gateway Device](StructureDefinition-grove-gateway-device.html), which describes
  the app, app version, hardware model, and operating-system version that saved the record.

These devices are included when the source platform provides the corresponding facts.
The step-count and heart-rate examples contain them inside the Observation, so each
resource remains self-contained. A phone may appear in both roles: once as the hardware
that sensed a value and once as the environment in which an app stored it.

### Recording method and metadata

The [Recording Method extension](StructureDefinition-grove-recording-method.html)
distinguishes automatically recorded, actively recorded, and manually entered values.
This is separate from device identity: a value can be manually entered on a device.

Map source information to a standard FHIR field first. Use the
[Platform Metadata extension](StructureDefinition-grove-platform-metadata.html) only
for a typed source key/value pair that has no suitable FHIR representation. Each entry
contains a coded key and an appropriate typed FHIR value. The
[heart-rate example](Observation-GroveHeartRateObservationExample.html) shows a coded
HealthKit motion-context value; its [raw JSON](Observation-GroveHeartRateObservationExample.json)
shows the complete nested extension.

### Implementing a producer or consumer

A producer:

1. Adds the Grove Mobile Sensor Observation canonical URL to `meta.profile`.
2. Writes the standard Observation content: `status`, `code`, `subject`, and the
   applicable time and result elements.
3. Adds the source-record identifier.
4. Adds sensor, gateway, recording method, and residual metadata when those facts are available.
5. Validates the finished resource against the Grove packages.

A consumer resolves meaning from the standard clinical fields first, uses the identifier
pair for record identity, and preserves all recognized Must Support elements. In this
guide, **Must Support** means that a producer populates an element when the source data
is available and a consumer accepts and preserves or interprets it when present. It does
not change the element's stated cardinality.

Continue with [Read and Validate](consuming.html), or inspect the
[sleep-stage example](Observation-GroveSleepObservationExample.html) and
[heart-rate example](Observation-GroveHeartRateObservationExample.html).
