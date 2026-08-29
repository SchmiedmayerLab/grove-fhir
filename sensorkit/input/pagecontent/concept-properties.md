<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Unlike the HealthKit and Health Connect source-type codes, which are the platform symbols themselves, a SensorKit source-type code is a Grove token.
The associated Apple `SRSensor` identifier is exposed as a concept property so consumers can map each Grove token to the platform value.

### `identifier`
{: #identifier }

The `SRSensor` value the token names, which is what a producer reads back.
It is a reverse-DNS string rather than the constant's name: `ambient-pressure` is `com.apple.SensorKit.ambientPressure`.

### `documentation`
{: #documentation }

This property contains the canonical Apple documentation URL for the corresponding `SRSensor` constant.

### Membership and versioning

The CodeSystem includes every public `SRSensor` constant in the SDK baseline identified in its description and therefore declares `content = complete` for that baseline.
Moving to a later SDK baseline is a version change, not an in-place edit.

The `status` column of the [status matrix](status-matrix.html) defines whether the Grove FHIR contracts admit output for a sensor. Admission status is not part of the terminology.

Each property is defined as a concept in [sensorkit-concept-property](CodeSystem-sensorkit-concept-property.html), which is what `CodeSystem.property.uri` names.
