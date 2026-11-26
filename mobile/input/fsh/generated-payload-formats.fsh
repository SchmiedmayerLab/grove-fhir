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

CodeSystem: GrovePayloadFormatCS
Id: grove-payload-format
Title: "Grove Payload Format"
Description: "The closed registry of payload formats a Grove payload DocumentReference may declare in content.format: a Sensor recording document, a Clinical Records document or attachment, or an adapter document derived from one of them. Each code identifies a wire format and structural envelope, and the guide that owns it states its full definition. Native Recording JSON defines only a JSON object-or-array container; the carrying source type supplies its category and meaning."
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
* #sensor-sample-collection-bundle "Sensor Sample Collection Bundle" "One strict UTF-8 JSON resource with `resourceType` = `Bundle`, `Bundle.type` = `collection`, a required offset-bearing `Bundle.timestamp`, and one `Bundle.entry` for each source sample in source order. The Bundle has at least one entry. Every entry has a unique absolute non-fragment `fullUrl` and a resource object with `resourceType`; `request`, `response`, and `search` are absent."
* #provider-issued-fhir-json "Provider-Issued FHIR JSON" "One complete provider-issued FHIR resource in FHIR JSON representation, of the FHIR release its producer declares, byte-preserved exactly as the source delivered it."
* #cda-document "CDA Document" "One HL7 Clinical Document Architecture Release 2 (CDA R2) document in its XML representation, media type `application/hl7-cda+xml`, byte-preserved exactly as the source platform delivered it. CDA R2 XML is the one representation this format currently admits. Grove never rewrites, reserializes, or asserts conformance over another issuer's document; the carrying document records the issuer."
* #source-file "Source File" "One file exactly as the source platform stored it, in any format. Grove never opens, rewrites, reserializes, or interprets the file."
* #native-recording-json "Native Recording JSON" "The payload is strict UTF-8 JSON with an object or array root. Byte-order marks, duplicate object member names, non-finite numeric values, scalar roots, malformed UTF-8, and malformed JSON are rejected."
* #provider-response-json "Provider Response JSON" "The payload is the exact JSON response-body bytes returned by the provider API; HTTP transport framing is not part of the payload."
* #photoplethysmogram-samples "Photoplethysmogram Samples" "Version byte 0x01, then a varint record count, then that many PPG records. Decoders reject any other version byte; a payload whose grammar changes takes the next version."

ValueSet: GrovePayloadFormatVS
Id: grove-payload-format
Title: "Grove Payload Format"
Description: "Every registered Grove payload format. A document profile binds the narrower value set of the guide that owns its formats, or fixes the one format it carries."
* ^experimental = false
* include codes from system GrovePayloadFormatCS
