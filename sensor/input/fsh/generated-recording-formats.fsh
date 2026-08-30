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
Description: "The closed registry of payload formats a Grove recording DocumentReference may declare in content.format. Each code identifies a wire format and structural envelope. Native Recording defines only a JSON object-or-array container; the carrying source type supplies its category and meaning."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #heart-rate-samples "Heart Rate Samples" "One header row naming every column in order, then one row per source sample in source order. Columns: timestamp, value, confidence, device."
* #triaxial-acceleration-samples "Triaxial Acceleration Samples" "One header row naming every column in order, then one row per source sample in source order. Columns: timestamp, identifier, x, y, z, device."
* #ambient-light-samples "Ambient Light Samples" "One header row naming every column in order, then one row per source sample in source order. Columns: timestamp, lux, placement, chromaticityX, chromaticityY, device."
* #ambient-pressure-samples "Ambient Pressure Samples" "One header row naming every column in order, then one row per source sample in source order. Columns: timestamp, identifier, pressure, temperature, device."
* #pedometer-samples "Pedometer Samples" "One header row naming every column in order, then one row per source sample in source order. Columns: start, end, steps, distance, floorsUp, floorsDown, currentPace, currentCadence, avgActivePace, device."
* #wrist-temperature-samples "Wrist Temperature Samples" "One header row naming every column in order, then one row per source sample in source order. Columns: timestamp, value, errorEstimate, condition."
* #triaxial-rotation-samples "Triaxial Rotation Samples" "One header row naming every column in order, then one row per source sample in source order. Columns: timestamp, x, y, z, device."
* #odometer-samples "Odometer Samples" "One header row naming every column in order, then one row per source sample in source order. Columns: start, end, gpsDate, speed, speedAccuracy, slope, maxAbsSlope, deltaDistance, deltaDistanceAccuracy, deltaAltitude, verticalAccuracy, originDevice, device."
* #beat-interval-series "Beat Interval Series" "One header row naming every column in order, then one row per source sample in source order. Columns: timestamp, precededByGap."
* #location-track-samples "Location Track Samples" "One header row naming every column in order, then one row per source sample in source order. Columns: timestamp, latitude, longitude, altitude, horizontalAccuracy, verticalAccuracy, speed, speedAccuracy, course, courseAccuracy."
* #fhir-collection-bundle "FHIR R4 Collection Bundle" "One strict UTF-8 JSON resource with `resourceType` = `Bundle`, `Bundle.type` = `collection`, a required offset-bearing `Bundle.timestamp`, and one `Bundle.entry` for each source sample in source order. The Bundle has at least one entry. Every entry has a unique absolute non-fragment `fullUrl` and a resource object with `resourceType`; `request`, `response`, and `search` are absent."
* #fhir-resource "FHIR Resource" "One complete provider-issued FHIR DSTU2 or R4 resource in FHIR JSON representation, byte-preserved exactly as the source platform delivered it."
* #clinical-document "Clinical Document" "One HL7 Clinical Document Architecture Release 2 document, byte-preserved exactly as the source platform delivered it. Grove never rewrites, reserializes, or asserts conformance over another issuer's document; the carrying document records the issuer."
* #native-recording "Native Recording" "The payload is strict UTF-8 JSON with an object or array root. Byte-order marks, duplicate object member names, non-finite numeric values, scalar roots, malformed UTF-8, and malformed JSON are rejected."
* #provider-recording "Provider Recording" "The payload is the exact JSON response-body bytes returned by the provider API; HTTP transport framing is not part of the payload."
* #photoplethysmogram-samples "Photoplethysmogram Samples" "Varint record count, then that many PPG records."

ValueSet: GroveRecordingFormatVS
Id: grove-recording-format
Title: "Grove Recording Format"
Description: "Every payload format admitted for a Grove recording DocumentReference content entry."
* ^experimental = false
* include codes from system GroveRecordingFormatCS
