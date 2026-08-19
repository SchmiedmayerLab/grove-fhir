<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

The Grove Platform Terminology package defines the FHIR code systems and value sets
used to preserve HealthKit identifiers in Grove FHIR resources. It is separate from the
clinical profiles because a platform identifier describes where data came from; it does
not define the clinical meaning of the measurement.

### Clinical and platform coding

Use a standard clinical terminology whenever one describes the measurement. Add the
HealthKit sample type as another coding when retaining the exact source type is useful.
For example, a step count can carry both LOINC and HealthKit codings:

```json
"code": {
  "coding": [
    {
      "system": "http://loinc.org",
      "code": "55423-8",
      "display": "Number of steps in unspecified time Pedometer"
    },
    {
      "system": "https://grovealliance.org/fhir/platforms/CodeSystem/healthkit-sample-type",
      "code": "HKQuantityTypeIdentifierStepCount",
      "display": "Step Count"
    }
  ]
}
```

Consumers use the clinical coding for clinical interpretation and the platform coding
when they need to identify the original source type. The
[HealthKit Sample Types code system](CodeSystem-healthkit-sample-type.html) defines this
second coding.

### Platform metadata keys

Some HealthKit metadata has a direct FHIR representation. Time zone and recording
method, for example, use dedicated fields or extensions in the core guide. A remaining
typed key/value pair uses the Grove Platform Metadata extension and identifies its key
with the [HealthKit Metadata Keys code system](CodeSystem-healthkit-metadata-key.html).

The key code is the raw HealthKit metadata key. The source value is mapped to the
corresponding FHIR datatype. Coded metadata values use their corresponding code system, such as
[HealthKit Heart Rate Motion Context](CodeSystem-healthkit-heart-rate-motion-context.html).
See the core guide's [Mobile Observations](https://schmiedmayerlab.github.io/grove-fhir/mobile.html#recording-method-and-metadata)
page for the complete mapping.

### Open-ended platform vocabularies

HealthKit adds identifiers over time and permits application-defined metadata keys.
The sample-type and metadata-key code systems therefore use FHIR's `fragment` content
mode: the package documents known values without claiming that an unlisted source
identifier is invalid. Finite HealthKit enumerations use `complete` content mode. Codes
are case-sensitive and retain the source platform's spelling.

Apple's platform documentation remains authoritative for the availability and behavior
of HealthKit APIs. This package defines how their identifiers are carried in FHIR; it
does not redefine the APIs or assign clinical meaning to vendor terms.

### Source terms and licensing

HealthKit identifiers retain the names and raw values defined by Apple. Grove FHIR does
not claim ownership of those identifiers. The repository's MIT license applies to the
original Grove FHIR source and documentation; third-party names and platform APIs remain
subject to their owners' terms.

The [step-count example](https://schmiedmayerlab.github.io/grove-fhir/Observation-GroveStepCountObservationExample.html)
and [heart-rate example](https://schmiedmayerlab.github.io/grove-fhir/Observation-GroveHeartRateObservationExample.html)
show the terminology in complete resources.

<details markdown="1">
<summary><strong>Package dependencies</strong></summary>

{% include dependency-table.xhtml %}

{% include globals-table.xhtml %}

{% include cross-version-analysis.xhtml %}

</details>
