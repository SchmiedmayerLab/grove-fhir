<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

# Metadata in the combined prototype

The current HealthKit mapping uses standard FHIR elements for measurements, timing,
and device links. The `GrovePlatformMetadata` extension preserves typed source metadata
for which the Grove Swift conversion has no explicit standard mapping.

| Source information | Current representation |
|---|---|
| Measurement and timing | `Observation.value[x]`, `effective[x]`, and standard units |
| Recording and gateway devices | `Observation.device` and the standard gateway-device extension |
| Capture method | Grove Recording Method extension |
| Remaining typed source metadata, including HealthKit sensor-location keys | Repeating Grove Platform Metadata extensions |

Each residual entry keeps the source key as a `Coding` and its value as the corresponding
FHIR datatype. More specific mappings, such as `Observation.bodySite`, require separate
semantic review before they replace that fallback. The HealthKit mapping is under review
for the Mobile contract. No Grove Swift implementation evidence currently supports the
Health Connect key space.
