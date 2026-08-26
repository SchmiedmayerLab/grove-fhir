//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//
// GENERATED FILE. Edit catalog/format-registry.json and run
// `python3 Scripts/render-format-registry.py`.
//

CodeSystem: GroveRecordingFormatCS
Id: grove-recording-format
Title: "Grove Recording Format"
Description: "The closed registry of payload formats a Grove recording DocumentReference may declare in content.format. Each code is fully specified in the format registry and on the formats page, so a receiver can parse any admitted payload from the guide alone."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #sensorkit-heart-rate "SensorKit Heart Rate" "One header row naming every column in order, then one row per source sample in source order. Columns: timestamp, value, confidence, device. Source: SRSensor.heartRate (CMHighFrequencyHeartRateData)."
* #sensorkit-accelerometer "SensorKit Accelerometer" "One header row naming every column in order, then one row per source sample in source order. Columns: timestamp, identifier, x, y, z, device. Source: SRSensor.accelerometer (CMRecordedAccelerometerData)."
* #sensorkit-ambient-light "SensorKit Ambient Light" "One header row naming every column in order, then one row per source sample in source order. Columns: timestamp, lux, placement, chromacityX, chromacityY, device. Source: SRSensor.ambientLightSensor (SRAmbientLightSample)."
* #sensorkit-ambient-pressure "SensorKit Ambient Pressure" "One header row naming every column in order, then one row per source sample in source order. Columns: timestamp, identifier, pressure, temperature, device. Source: SRSensor.ambientPressure (CMRecordedPressureData)."
* #sensorkit-pedometer "SensorKit Pedometer" "One header row naming every column in order, then one row per source sample in source order. Columns: start, end, steps, distance, floorsUp, floorsDown, currentPace, currentCadence, avgActivePace, device. Source: SRSensor.pedometerData (CMPedometerData)."
* #sensorkit-wrist-temperature "SensorKit Wrist Temperature" "One header row naming every column in order, then one row per source sample in source order. Columns: timestamp, value, errorEstimate, condition. Source: SRSensor.wristTemperature (SRWristTemperatureSession)."
* #sensorkit-rotation-rate "SensorKit Rotation Rate" "One header row naming every column in order, then one row per source sample in source order. Columns: timestamp, x, y, z, device. Source: SRSensor.rotationRate (CMRecordedRotationRateData)."
* #sensorkit-odometer "SensorKit Odometer" "One header row naming every column in order, then one row per source sample in source order. Columns: start, end, gpsDate, speed, speedAccuracy, slope, maxAbsSlope, deltaDistance, deltaDistanceAccuracy, deltaAltitude, verticalAccuracy, originDevice, device. Source: SRSensor.odometer (CMOdometerData)."
* #healthkit-heartbeat-series "HealthKit Heartbeat Series" "One header row naming every column in order, then one row per source sample in source order. Columns: timestamp, precededByGap. Source: HKDataTypeIdentifierHeartbeatSeries (HKHeartbeatSeriesSample)."
* #fhir-resource-array "FHIR Resource Array" "A single JSON array; each element is one complete FHIR R4 resource in FHIR JSON representation, in source sample order."
* #fhir-resource "FHIR Resource" "One complete provider-issued FHIR resource in FHIR JSON representation, byte-preserved exactly as the source platform delivered it."
* #native-recording "Native Recording" "The producer's exact native JSON serialization of one source batch, byte-preserved."
* #provider-recording "Provider Recording" "The verbatim JSON payload returned by the provider API call that produced the batch, byte-preserved apart from transport framing."
* #sensorkit-photoplethysmogram "SensorKit Photoplethysmogram" "Varint record count, then that many PPG records."
* #batch-archive "Batch Archive" "A POSIX ustar tar stream compressed as one whole with Zstandard; every archived file is itself a registry-format payload or a documented sidecar of one."

ValueSet: GroveRecordingFormatVS
Id: grove-recording-format
Title: "Grove Recording Format"
Description: "Every payload format admitted for a Grove recording DocumentReference content entry."
* ^experimental = false
* include codes from system GroveRecordingFormatCS
