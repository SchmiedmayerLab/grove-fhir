<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

The Grove Health Connect Adapter maps Android Health Connect Records to FHIR R4. It
uses established FHIR profiles and terminology for clinical meaning and adds only the
source identities needed to synchronize converted resources.

Every converted result conforms to two independent contracts:

1. [Health Connect Observation](StructureDefinition-health-connect-observation.html)
   identifies the source Record and the individual FHIR output.
2. A clinical or research profile defines what was measured, its unit, and its time
   semantics.

Both profile canonicals appear in `Observation.meta.profile`, and the resource must
validate against both.

### Start with a record type

| Health Connect input | FHIR representation | Complete example |
|---|---|---|
| `HeartRateRecord` | One FHIR R4 Heart Rate Observation per `Sample`; LOINC `8867-4`; UCUM `/min` | [First sample](Observation-HealthConnectHeartRateSampleOneExample.html) and [second sample](Observation-HealthConnectHeartRateSampleTwoExample.html) |
| `WeightRecord` | FHIR R4 Body Weight; LOINC `29463-7`; UCUM `kg` | [Body weight](Observation-HealthConnectBodyWeightExample.html) |
| `StepsRecord` | Grove Mobile Step Count; Grove `step-count-total`; UCUM `{steps}` over the exact source interval | [Step count](Observation-HealthConnectStepCountExample.html) |

The [documentation Bundle](Bundle-HealthConnectStudyBundleExample.html) aggregates every
resource referenced by these examples: participant, protocol, enrollment, recording
device, applications, Observations, and conversion Provenance. Its
[JSON representation](Bundle-HealthConnectStudyBundleExample.json) is useful for profile
validation and reference inspection. It combines several source records and is therefore
not an operational synchronization event; each event follows the single-source envelope
defined in [Synchronization](synchronization.html).

### Read the identifiers correctly

Each Observation carries two identifiers with different jobs:

- [Health Connect Record Identifier](NamingSystem-health-connect-record-id.html) is the
  repository- and Record-class-scoped digest derived from `Record.metadata.id`. It does not
  disclose the raw platform id. All outputs from one source Record repeat this identifier.
- [Health Connect Output Identifier](NamingSystem-health-connect-output-id.html) identifies
  one emitted Observation. Outputs from a multi-sample `HeartRateRecord` have distinct
  output identifiers.

Neither value is a FHIR `Resource.id`. A receiving FHIR server controls `Resource.id` and
`meta.versionId`; synchronization uses the complete business-identifier pairs.

[Health Connect Conversion Provenance](StructureDefinition-health-connect-conversion-provenance.html)
links all outputs from one Record to that source identifier, the converting application,
and the application reported by `DataOrigin.packageName` as the source-system enterer.
Application identifiers use the
[Android Package Name](NamingSystem-android-package-name.html) namespace.

The adapter publishes no Health Connect CodeSystem and no generic metadata extension.
LOINC, UCUM, standard FHIR profiles, the Mobile recording-method extension, and standard
Provenance roles already express the supported facts. A platform field that has no defined
FHIR meaning is not copied into an opaque extension.

Continue with [Mapping](mapping.html) for field-level rules and
[Synchronization](synchronization.html) for updates, deletions, and change-token recovery.
Open [Artifacts](artifacts.html) for the complete conformance surface.
