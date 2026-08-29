<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

GENERATED FILE. Edit the corresponding catalog JSON and run
`python3 Scripts/render-status-matrices.py`.
-->

### SensorKit support matrix

This table is the normative SensorKit support inventory: 20 catalog-baseline platform symbols and 2 stable additions in the stated Apple SDK baseline. Each of the 22 sources has one status, and only the listed representations are admitted. Recording Document support preserves a registered payload and does not imply that FHIR retrieves it; `content.format` states whether its payload is CSV, FHIR, binary, native JSON, or another admitted format.

| SensorKit source | Adapter code | Inventory scope | Minimum iOS | Status | Structured profile claim(s) | Raw profile claim(s) | Binding reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `SRSensor.accelerometer` | `accelerometer` | catalog-baseline | 14.0 | `platform-exclusive` | sensorkit-accelerometer-observation | grove-sensor-recording-document; sensorkit-recording-document | — |
| `SRSensor.acousticSettings` | `acoustic-settings` | stable-addition | 26.0 | `deferred` | — | — | The Grove FHIR contracts publish no admitted output contract for this stable platform symbol. |
| `SRSensor.ambientLightSensor` | `ambient-light` | catalog-baseline | 14.0 | `mapped-standard` | — | grove-sensor-recording-document; sensorkit-recording-document | The source contains heterogeneous light fields for which the Grove FHIR contracts do not publish a lossless component profile. |
| `SRSensor.ambientPressure` | `ambient-pressure` | catalog-baseline | 15.4 | `mapped-standard` | — | grove-sensor-recording-document; sensorkit-recording-document | Pressure and temperature are mixed-unit fields and must not be collapsed into one SampledData value. |
| `SRSensor.deviceUsageReport` | `device-usage` | catalog-baseline | 14.0 | `platform-exclusive` | sensorkit-device-usage-observation | grove-sensor-recording-document; sensorkit-recording-document | — |
| `SRSensor.electrocardiogram` | `ecg` | catalog-baseline | 17.4 | `supported` | grove-sensor-ecg-observation; sensorkit-ecg-observation | grove-sensor-recording-document; sensorkit-recording-document | — |
| `SRSensor.faceMetrics` | `face-metrics` | catalog-baseline | 17.0 | `mapped-standard` | — | grove-sensor-recording-document; sensorkit-recording-document | The Grove FHIR contracts publish no structured profile for the heterogeneous face metrics. |
| `SRSensor.heartRate` | `heart-rate` | catalog-baseline | 17.0 | `mapped-standard` | — | grove-sensor-recording-document; sensorkit-recording-document | Bare SampledData cannot preserve CMHighFrequencyHeartRateDataConfidence for each source point. |
| `SRSensor.keyboardMetrics` | `keyboard-metrics` | catalog-baseline | 14.0 | `platform-exclusive` | sensorkit-keyboard-metrics-observation | grove-sensor-recording-document; sensorkit-recording-document | — |
| `SRSensor.mediaEvents` | `media-events` | catalog-baseline | 16.4 | `mapped-standard` | — | grove-sensor-recording-document; sensorkit-recording-document | Media interactions do not have a source-neutral clinical Observation representation under the Grove FHIR contracts. |
| `SRSensor.messagesUsageReport` | `messages-usage` | catalog-baseline | 14.0 | `platform-exclusive` | sensorkit-messages-usage-observation | grove-sensor-recording-document; sensorkit-recording-document | — |
| `SRSensor.odometer` | `odometer` | catalog-baseline | 17.0 | `mapped-standard` | — | grove-sensor-recording-document; sensorkit-recording-document | Speed, slope, and motion fields are heterogeneous and are not a shared Mobile distance total. |
| `SRSensor.onWristState` | `on-wrist` | catalog-baseline | 14.0 | `platform-exclusive` | sensorkit-on-wrist-observation | grove-sensor-recording-document; sensorkit-recording-document | — |
| `SRSensor.pedometerData` | `pedometer` | catalog-baseline | 14.0 | `mapped-standard` | — | grove-sensor-recording-document; sensorkit-recording-document | The composite pedometer record contains multiple aggregates and is not automatically one shared step-count result. |
| `SRSensor.phoneUsageReport` | `phone-usage` | catalog-baseline | 14.0 | `platform-exclusive` | sensorkit-phone-usage-observation | grove-sensor-recording-document; sensorkit-recording-document | — |
| `SRSensor.photoplethysmogram` | `ppg` | catalog-baseline | 17.4 | `platform-exclusive` | sensorkit-ppg-observation | grove-sensor-recording-document; sensorkit-recording-document | — |
| `SRSensor.rotationRate` | `rotation-rate` | catalog-baseline | 14.0 | `supported` | grove-sensor-sampled-data-observation; sensorkit-observation | grove-sensor-recording-document; sensorkit-recording-document | — |
| `SRSensor.siriSpeechMetrics` | `siri-speech-metrics` | catalog-baseline | 15.0 | `mapped-standard` | — | grove-sensor-recording-document; sensorkit-recording-document | Speech metrics have no source-neutral clinical Observation representation under the Grove FHIR contracts. |
| `SRSensor.sleepSessions` | `sleep-sessions` | stable-addition | 26.0 | `platform-exclusive` | sensorkit-sleep-session-observation | — | — |
| `SRSensor.telephonySpeechMetrics` | `telephony-speech-metrics` | catalog-baseline | 15.0 | `mapped-standard` | — | grove-sensor-recording-document; sensorkit-recording-document | Speech metrics have no source-neutral clinical Observation representation under the Grove FHIR contracts. |
| `SRSensor.visits` | `visits` | catalog-baseline | 14.0 | `platform-exclusive` | sensorkit-visit-observation | grove-sensor-recording-document; sensorkit-recording-document | — |
| `SRSensor.wristTemperature` | `wrist-temperature` | catalog-baseline | 17.0 | `platform-exclusive` | sensorkit-wrist-temperature-observation | grove-sensor-recording-document; sensorkit-recording-document | A sleep-interval wrist skin reading is neither body nor basal body temperature, so the Grove FHIR contracts publish a platform-scoped summary rather than binding it to a shared clinical meaning. |
