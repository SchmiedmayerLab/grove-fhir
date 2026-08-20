<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Unlike the HealthKit and Health Connect source-type codes, which are the platform symbols themselves,
a SensorKit source-type code is a Grove token. The Apple symbol it names is carried as a property so
the lineage stays machine-readable.

### `identifier`
{: #identifier }

The `SRSensor` value the token names, which is what a producer reads back. It is a reverse-DNS string
rather than the constant's name: `ambient-pressure` is `com.apple.SensorKit.ambientPressure`.

### `documentation`
{: #documentation }

The canonical Apple documentation page for that constant, recorded from Apple's published symbol index.

### Membership and versioning

The concepts in this code system are exactly the public `SRSensor` constants in the SDK baseline named
in the code system description, verified against `sensorkit/input/data/sensorkit-inventory.json`.
`content` is therefore `complete` for that baseline. Moving to a later SDK baseline is a version change,
not an in-place edit.

Whether the v0.2 adapter admits output for a sensor is the `status` column of the
[status matrix](status-matrix.html), and never appears in terminology.

Each property is defined as a concept in [sensorkit-concept-property](CodeSystem-sensorkit-concept-property.html), which is what `CodeSystem.property.uri` names.
