<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

GENERATED FILE. Edit the corresponding catalog JSON and run
`python3 Scripts/render-status-matrices.py`.
-->

# Authoritative SensorKit status matrix

This table is the complete v0.2.0 SensorKit inventory: 20 catalog-baseline platform symbols and 2 stable additions in the stated Apple SDK baseline. Each of the 22 rows has one definitive status. Native Recording Document support is distinct from a structured semantic mapping and never implies that fetching occurs in FHIR.

| SensorKit source | Adapter code | Inventory scope | Minimum iOS | Status | Structured contract | Raw contract | Binding reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `SRSensor.accelerometer` | `accelerometer` | catalog-baseline | 14.0 | `platform-exclusive` | sensorkit-accelerometer-observation | sensorkit-recording-document | — |
| `SRSensor.acousticSettings` | `acoustic-settings` | stable-addition | 26.0 | `deferred` | — | — | Version 0.3.0 publishes no reviewed output contract for this stable platform symbol. |
| `SRSensor.ambientLightSensor` | `ambient-light` | catalog-baseline | 14.0 | `mapped-standard` | deferred | sensorkit-recording-document | The source contains heterogeneous light fields for which version 0.3.0 does not publish a lossless component profile. |
| `SRSensor.ambientPressure` | `ambient-pressure` | catalog-baseline | 15.4 | `mapped-standard` | deferred | sensorkit-recording-document | Pressure and temperature are mixed-unit fields and must not be collapsed into one SampledData value. |
| `SRSensor.deviceUsageReport` | `device-usage` | catalog-baseline | 14.0 | `platform-exclusive` | sensorkit-device-usage-observation | sensorkit-recording-document | — |
| `SRSensor.electrocardiogram` | `ecg` | catalog-baseline | 17.4 | `supported` | sensorkit-ecg-observation | sensorkit-recording-document | — |
| `SRSensor.faceMetrics` | `face-metrics` | catalog-baseline | 17.0 | `mapped-standard` | deferred | sensorkit-recording-document | Version 0.3.0 publishes no reviewed structured profile for the heterogeneous face metrics. |
| `SRSensor.heartRate` | `heart-rate` | catalog-baseline | 17.0 | `mapped-standard` | deferred | sensorkit-recording-document | Bare SampledData cannot preserve CMHighFrequencyHeartRateDataConfidence for each source point. |
| `SRSensor.keyboardMetrics` | `keyboard-metrics` | catalog-baseline | 14.0 | `platform-exclusive` | sensorkit-keyboard-metrics-observation | sensorkit-recording-document | — |
| `SRSensor.mediaEvents` | `media-events` | catalog-baseline | 16.4 | `mapped-standard` | deferred | sensorkit-recording-document | Media interactions do not have a reviewed source-neutral clinical Observation representation in version 0.3.0. |
| `SRSensor.messagesUsageReport` | `messages-usage` | catalog-baseline | 14.0 | `platform-exclusive` | sensorkit-messages-usage-observation | sensorkit-recording-document | — |
| `SRSensor.odometer` | `odometer` | catalog-baseline | 17.0 | `mapped-standard` | deferred | sensorkit-recording-document | Speed, slope, and motion fields are heterogeneous and are not a shared Mobile distance total. |
| `SRSensor.onWristState` | `on-wrist` | catalog-baseline | 14.0 | `platform-exclusive` | sensorkit-on-wrist-observation | sensorkit-recording-document | — |
| `SRSensor.pedometerData` | `pedometer` | catalog-baseline | 14.0 | `mapped-standard` | deferred | sensorkit-recording-document | The composite pedometer record contains multiple aggregates and is not automatically one shared step-count result. |
| `SRSensor.phoneUsageReport` | `phone-usage` | catalog-baseline | 14.0 | `platform-exclusive` | sensorkit-phone-usage-observation | sensorkit-recording-document | — |
| `SRSensor.photoplethysmogram` | `ppg` | catalog-baseline | 17.4 | `platform-exclusive` | sensorkit-ppg-observation | sensorkit-recording-document | — |
| `SRSensor.rotationRate` | `rotation-rate` | catalog-baseline | 14.0 | `supported` | sensorkit-observation | sensorkit-recording-document | — |
| `SRSensor.siriSpeechMetrics` | `siri-speech-metrics` | catalog-baseline | 15.0 | `mapped-standard` | deferred | sensorkit-recording-document | Speech metrics have no reviewed source-neutral clinical Observation representation in version 0.3.0. |
| `SRSensor.sleepSessions` | `sleep-sessions` | stable-addition | 26.0 | `platform-exclusive` | sensorkit-sleep-session-observation | — | — |
| `SRSensor.telephonySpeechMetrics` | `telephony-speech-metrics` | catalog-baseline | 15.0 | `mapped-standard` | deferred | sensorkit-recording-document | Speech metrics have no reviewed source-neutral clinical Observation representation in version 0.3.0. |
| `SRSensor.visits` | `visits` | catalog-baseline | 14.0 | `platform-exclusive` | sensorkit-visit-observation | sensorkit-recording-document | — |
| `SRSensor.wristTemperature` | `wrist-temperature` | catalog-baseline | 17.0 | `mapped-standard` | deferred | sensorkit-recording-document | A wrist-temperature session is not automatically the shared body-temperature or basal-body-temperature meaning. |
