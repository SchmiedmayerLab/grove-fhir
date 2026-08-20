<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

GENERATED FILE. Edit the corresponding catalog JSON and run
`python3 Scripts/render-status-matrices.py`.
-->

# Authoritative SensorKit status matrix

This table is the complete v0.2.0 SensorKit inventory: the 20 streams implemented by the current Grove source adapter, two current stable platform additions, and two beta/unavailable additions. Each of the 24 rows has one definitive status. Native Recording Document support is distinct from a structured semantic mapping and never implies that fetching occurs in FHIR.

| SensorKit source | Adapter code | Grove source case | Inventory scope | Minimum iOS | Status | Structured contract | Raw contract | Binding reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `SRSensor.accelerometer` | `accelerometer` | Sensor.accelerometer | grove-implemented | 14.0 | `mapped-standard` | deferred | sensorkit-recording-document | The source batch identifier is part of the exact SensorKit record and is not preserved by bare SampledData. |
| `SRSensor.acousticSettings` | `acoustic-settings` | — | current-stable-addition | 26.0 | `deferred` | — | — | The current Grove SensorKit source adapter does not implement this stable platform addition. |
| `SRSensor.ambientLightSensor` | `ambient-light` | Sensor.ambientLight | grove-implemented | 14.0 | `mapped-standard` | deferred | sensorkit-recording-document | The source contains heterogeneous light fields for which version 0.2.0 does not publish a lossless component profile. |
| `SRSensor.ambientPressure` | `ambient-pressure` | Sensor.ambientPressure | grove-implemented | 15.4 | `mapped-standard` | deferred | sensorkit-recording-document | Pressure and temperature are mixed-unit fields and must not be collapsed into one SampledData value. |
| `SRSensor.deviceUsageReport` | `device-usage` | Sensor.deviceUsage | grove-implemented | 14.0 | `provider-specific` | sensorkit-device-usage-observation | sensorkit-recording-document | — |
| `SRSensor.electrocardiogram` | `ecg` | Sensor.ecg | grove-implemented | 17.4 | `supported` | sensorkit-ecg-observation | sensorkit-recording-document | — |
| `SRSensor.faceMetrics` | `face-metrics` | Sensor.faceMetrics | grove-implemented | 17.0 | `mapped-standard` | deferred | sensorkit-recording-document | Version 0.2.0 publishes no reviewed structured profile for the heterogeneous face metrics. |
| `SRSensor.headphoneMotion` | `headphone-motion` | — | beta-addition | 27.0 | `deferred` | — | — | The platform API is beta and unavailable to the current Grove source adapter. |
| `SRSensor.headphoneSettings` | `headphone-settings` | — | beta-addition | 27.0 | `deferred` | — | — | The platform API is beta and unavailable to the current Grove source adapter. |
| `SRSensor.heartRate` | `heart-rate` | Sensor.heartRate | grove-implemented | 17.0 | `mapped-standard` | deferred | sensorkit-recording-document | Bare SampledData cannot preserve CMHighFrequencyHeartRateDataConfidence for each source point. |
| `SRSensor.keyboardMetrics` | `keyboard-metrics` | Sensor.keyboardMetrics | grove-implemented | 14.0 | `mapped-standard` | deferred | sensorkit-recording-document | Version 0.2.0 publishes no reviewed structured profile for the heterogeneous keyboard metrics. |
| `SRSensor.mediaEvents` | `media-events` | Sensor.mediaEvents | grove-implemented | 16.4 | `mapped-standard` | deferred | sensorkit-recording-document | Media interactions do not have a reviewed source-neutral clinical Observation representation in version 0.2.0. |
| `SRSensor.messagesUsageReport` | `messages-usage` | Sensor.messagesUsage | grove-implemented | 14.0 | `mapped-standard` | deferred | sensorkit-recording-document | Messages usage has no reviewed source-neutral clinical Observation representation in version 0.2.0. |
| `SRSensor.odometer` | `odometer` | Sensor.odometer | grove-implemented | 17.0 | `mapped-standard` | deferred | sensorkit-recording-document | Speed, slope, and motion fields are heterogeneous and are not a shared Mobile distance total. |
| `SRSensor.onWristState` | `on-wrist` | Sensor.onWrist | grove-implemented | 14.0 | `provider-specific` | sensorkit-on-wrist-observation | sensorkit-recording-document | — |
| `SRSensor.pedometerData` | `pedometer` | Sensor.pedometer | grove-implemented | 14.0 | `mapped-standard` | deferred | sensorkit-recording-document | The composite pedometer record contains multiple aggregates and is not automatically one shared step-count result. |
| `SRSensor.phoneUsageReport` | `phone-usage` | Sensor.phoneUsage | grove-implemented | 14.0 | `mapped-standard` | deferred | sensorkit-recording-document | Phone usage has no reviewed source-neutral clinical Observation representation in version 0.2.0. |
| `SRSensor.photoplethysmogram` | `ppg` | Sensor.ppg | grove-implemented | 17.4 | `mapped-standard` | deferred | sensorkit-recording-document | Version 0.2.0 does not freeze the wavelength/channel and calibration semantics needed for a lossless SampledData mapping. |
| `SRSensor.rotationRate` | `rotation-rate` | Sensor.rotationRate | grove-implemented | 14.0 | `supported` | sensorkit-observation | sensorkit-recording-document | — |
| `SRSensor.siriSpeechMetrics` | `siri-speech-metrics` | Sensor.siriSpeechMetrics | grove-implemented | 15.0 | `mapped-standard` | deferred | sensorkit-recording-document | Speech metrics have no reviewed source-neutral clinical Observation representation in version 0.2.0. |
| `SRSensor.sleepSessions` | `sleep-sessions` | — | current-stable-addition | 26.0 | `deferred` | — | — | The current Grove SensorKit source adapter does not implement this stable platform addition. |
| `SRSensor.telephonySpeechMetrics` | `telephony-speech-metrics` | Sensor.telephonySpeechMetrics | grove-implemented | 15.0 | `mapped-standard` | deferred | sensorkit-recording-document | Speech metrics have no reviewed source-neutral clinical Observation representation in version 0.2.0. |
| `SRSensor.visits` | `visits` | Sensor.visits | grove-implemented | 14.0 | `provider-specific` | sensorkit-visit-observation | sensorkit-recording-document | — |
| `SRSensor.wristTemperature` | `wrist-temperature` | Sensor.wristTemperature | grove-implemented | 17.0 | `mapped-standard` | deferred | sensorkit-recording-document | A wrist-temperature session is not automatically the shared body-temperature or basal-body-temperature meaning. |
