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
* #heart-rate-samples "Heart Rate Samples" "One header row naming every column in order, then one row per source sample in source order. Columns: timestamp, value, confidence, device."
* #triaxial-acceleration-samples "Triaxial Acceleration Samples" "One header row naming every column in order, then one row per source sample in source order. Columns: timestamp, identifier, x, y, z, device."
* #ambient-light-samples "Ambient Light Samples" "One header row naming every column in order, then one row per source sample in source order. Columns: timestamp, lux, placement, chromacityX, chromacityY, device."
* #ambient-pressure-samples "Ambient Pressure Samples" "One header row naming every column in order, then one row per source sample in source order. Columns: timestamp, identifier, pressure, temperature, device."
* #pedometer-samples "Pedometer Samples" "One header row naming every column in order, then one row per source sample in source order. Columns: start, end, steps, distance, floorsUp, floorsDown, currentPace, currentCadence, avgActivePace, device."
* #wrist-temperature-samples "Wrist Temperature Samples" "One header row naming every column in order, then one row per source sample in source order. Columns: timestamp, value, errorEstimate, condition."
* #triaxial-rotation-samples "Triaxial Rotation Samples" "One header row naming every column in order, then one row per source sample in source order. Columns: timestamp, x, y, z, device."
* #odometer-samples "Odometer Samples" "One header row naming every column in order, then one row per source sample in source order. Columns: start, end, gpsDate, speed, speedAccuracy, slope, maxAbsSlope, deltaDistance, deltaDistanceAccuracy, deltaAltitude, verticalAccuracy, originDevice, device."
* #beat-interval-series "Beat Interval Series" "One header row naming every column in order, then one row per source sample in source order. Columns: timestamp, precededByGap."
* #location-track-samples "Location Track Samples" "One header row naming every column in order, then one row per source sample in source order. Columns: timestamp, latitude, longitude, altitude, horizontalAccuracy, verticalAccuracy, speed, speedAccuracy, course, courseAccuracy."
* #fhir-resource-array "FHIR Resource Array" "A single JSON array; each element is one complete FHIR R4 resource in FHIR JSON representation, in source sample order."
* #fhir-resource "FHIR Resource" "One complete provider-issued FHIR R4 resource in FHIR JSON representation, byte-preserved exactly as the source platform delivered it."
* #native-recording "Native Recording" "The producer's exact native JSON serialization of one source batch, byte-preserved."
* #provider-recording "Provider Recording" "The verbatim JSON payload returned by the provider API call that produced the batch, byte-preserved apart from transport framing."
* #photoplethysmogram-samples "Photoplethysmogram Samples" "Varint record count, then that many PPG records."

ValueSet: GroveRecordingFormatVS
Id: grove-recording-format
Title: "Grove Recording Format"
Description: "Every payload format admitted for a Grove recording DocumentReference content entry."
* ^experimental = false
* include codes from system GroveRecordingFormatCS
