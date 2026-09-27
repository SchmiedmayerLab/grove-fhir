<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

This walkthrough demonstrates how one `SRDeviceUsageReport` becomes the required two-resource graph: a structured summary and a linked complete Recording Document.
The complete resource examples show the [structured summary](Observation-SensorKitDeviceUsageExample.html), [native recording](DocumentReference-SensorKitDeviceUsageDocumentExample.html), and [conversion Provenance](Provenance-SensorKitDeviceUsageProvenanceExample.html). An exchange producer places those resources and their referenced context in one Mobile Exchange Bundle.
The walkthrough is explanatory; the adapter catalog, profiles, and exchange protocol remain normative.

### Why the graph contains two resources

A device-usage report includes aggregate totals and nested application, notification, web-usage, and text-input-session detail that no admitted Grove Observation profile represents losslessly.
The [Device Usage Observation](StructureDefinition-sensorkit-device-usage-observation.html) represents total unlock duration, screen wakes, and unlocks.
The complete caller-encoded representation, including every text-input session, is carried unmodified by a [SensorKit Recording Document](StructureDefinition-sensorkit-recording-document.html).
The catalog row for `SRSensor.deviceUsageReport` therefore requires both resources in one [Grove Mobile Exchange Bundle](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-mobile-exchange-bundle.html). A partial payload must not be labeled as the native recording, and a structured summary without its Recording Document is nonconformant.

### Output linkage

Both outputs carry the same opaque source-record v0 HMAC identifier, and each additionally carries its own source-output HMAC.
SensorKit publishes no durable sample identifier, so the producer assigns that record identity from a durable acquisition ledger; [Durable source identity](implementation.html#durable-source-identity) states the complete pre-yield persistence list and the prohibited identity inputs.
The `v0:<key-id>:<epoch>:…` forms in the abbreviated examples below are schematic; the complete published examples contain distinct concrete conformance-key values.
The exact catalog roles and discriminators are length-framed into the HMAC preimage, so Unicode and delimiters are unambiguous and no native acquisition key is disclosed. `Observation.derivedFrom` holds exactly one reference to the document, and `DocumentReference.context.related` points back to exactly the Observation.
In an exchange Bundle those internal references use the target entries' UUID `fullUrl` values; the standalone examples use their logical example references.
One [conversion Provenance](StructureDefinition-sensorkit-conversion-provenance.html) targets both outputs and names the record identifier as its sole source entity; omitting either target is nonconformant.
Every Bundle entry `fullUrl` is the UUIDv5 of its selected complete entry key under the Mobile exchange namespace.
Exact retries therefore preserve graph identity, while a distinct acquired record uses a distinct acquisition coordinate and event sequence regardless of whether its bytes happen to match another record.

### Structured summary

The following excerpt shows the elements that establish profile conformance, identity, result semantics, source linkage, and device attribution:

```json
{
  "resourceType": "Observation",
  "meta": {"profile": ["https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-device-usage-observation"]},
  "identifier": [
    {"type": {"coding": [{"system": "https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role", "code": "source-record"}]}, "system": "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1", "value": "v0:<key-id>:<epoch>:…"},
    {"type": {"coding": [{"system": "https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role", "code": "source-output"}]}, "system": "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1", "value": "v0:<key-id>:<epoch>:…"}
  ],
  "extension": [{"url": "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-source-type", "valueCode": "device-usage"}],
  "status": "final",
  "code": {"coding": [{"system": "https://grovealliance.org/fhir/sensorkit/CodeSystem/sensorkit-concept", "code": "device-usage-summary", "display": "Device usage summary"}]},
  "subject": {"reference": "Patient/SensorKitPatientExample"},
  "effectivePeriod": {"start": "2026-08-20T08:00:00-07:00", "end": "2026-08-20T08:15:00-07:00"},
  "valueQuantity": {"value": 372, "unit": "seconds", "system": "http://unitsofmeasure.org", "code": "s"},
  "derivedFrom": [{"reference": "DocumentReference/SensorKitDeviceUsageDocumentExample"}],
  "component": [
    {"code": {"coding": [{"system": "https://grovealliance.org/fhir/sensorkit/CodeSystem/sensorkit-concept", "code": "screen-wakes", "display": "Screen wakes"}]},
      "valueQuantity": {"value": 6, "unit": "{count}", "system": "http://unitsofmeasure.org", "code": "{count}"}},
    {"code": {"coding": [{"system": "https://grovealliance.org/fhir/sensorkit/CodeSystem/sensorkit-concept", "code": "unlocks", "display": "Unlocks"}]},
      "valueQuantity": {"value": 4, "unit": "{count}", "system": "http://unitsofmeasure.org", "code": "{count}"}}
  ],
  "device": {"reference": "Device/SensorKitDeviceExample"}
}
```

### Native recording document

```json
{
  "resourceType": "DocumentReference",
  "meta": {"profile": [
    "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-recording-document",
    "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document"]},
  "identifier": [
    {"type": {"coding": [{"system": "https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role", "code": "source-record"}]}, "system": "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1", "value": "v0:<key-id>:<epoch>:…"},
    {"type": {"coding": [{"system": "https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role", "code": "source-output"}]}, "system": "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1", "value": "v0:<key-id>:<epoch>:…"},
    {"type": {"coding": [{"system": "https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role", "code": "source-artifact"}]}, "system": "https://study.example.org/fhir/NamingSystem/grove-source-artifact-v0/test-key/1", "value": "v0:<key-id>:<epoch>:…"}
  ],
  "extension": [{"url": "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-source-type", "valueCode": "device-usage"}],
  "status": "current",
  "type": {"coding": [{"system": "https://grovealliance.org/fhir/sensorkit/CodeSystem/sensorkit-source-type", "code": "device-usage", "display": "Device usage report"}]},
  "subject": {"reference": "Patient/SensorKitPatientExample"},
  "date": "2026-08-20T15:15:01Z",
  "author": [{"reference": "Device/SensorKitDeviceExample"}],
  "content": [{"format": {"system": "https://grovealliance.org/fhir/sensor/CodeSystem/grove-recording-format", "code": "native-recording"}, "attachment": {
    "contentType": "application/json",
    "title": "SensorKit device usage report",
    "data": "eyJ0aW1lc3RhbXAiOjE3ODcyMzgwMDAsImR1cmF0aW9uIjo5MDAsInRvdGFsU2NyZWVuV2FrZXMiOjYsInRvdGFsVW5sb2NrcyI6NCwidG90YWxVbmxvY2tEdXJhdGlvbiI6MzcyLCJ2ZXJzaW9uIjoiMSIsImFwcFVzYWdlQnlDYXRlZ29yeSI6eyJwcm9kdWN0aXZpdHkiOlt7ImJ1bmRsZUlkZW50aWZpZXIiOiJjb20uYXBwbGUubW9iaWxlbm90ZXMiLCJyZXBvcnRBcHBsaWNhdGlvbklkZW50aWZpZXIiOiJyZXBvcnQtYXBwLTEiLCJyZWxhdGl2ZVN0YXJ0VGltZSI6MCwidXNhZ2VUaW1lIjo0ODAsInN1cHBsZW1lbnRhbENhdGVnb3JpZXMiOlt7ImlkZW50aWZpZXIiOiJ3cml0aW5nIn1dLCJ0ZXh0SW5wdXRTZXNzaW9ucyI6W3siZHVyYXRpb24iOjQyLCJzZXNzaW9uVHlwZVJhd1ZhbHVlIjowLCJpZGVudGlmaWVyIjoidGV4dC1zZXNzaW9uLTEifV19XX0sIm5vdGlmaWNhdGlvblVzYWdlQnlDYXRlZ29yeSI6eyJwcm9kdWN0aXZpdHkiOlt7ImJ1bmRsZUlkZW50aWZpZXIiOiJjb20uYXBwbGUubW9iaWxlbm90ZXMiLCJldmVudFJhd1ZhbHVlIjowfV19LCJ3ZWJVc2FnZUJ5Q2F0ZWdvcnkiOnsicHJvZHVjdGl2aXR5IjpbeyJ0b3RhbFVzYWdlVGltZSI6MTIwfV19fQ==",
    "size": 604,
    "hash": "G0xkrUr5NvJP9Tj9yjkJfrNRYnE="
  }}],
  "context": {"related": [{"reference": "Observation/SensorKitDeviceUsageExample"}]}
}
```

The payload format identity is `content.format` from the [recording format registry](https://grovealliance.org/fhir/sensor/formats.html) — here `native-recording` — and the `contentType` comes from the [Grove Recording MIME Types](https://grovealliance.org/fhir/sensor/ValueSet-grove-recording-mime-type.html) value set; the caller-encoded bytes are `application/json`. The format code, rather than a custom media type, identifies the Grove wire format.
The example's JSON members are one producer-defined serialization, not a SensorKit stream schema published by this guide. The source-type code supplies the category and meaning; a generic receiver validates only the UTF-8 object-or-array container and otherwise treats the members as opaque.
The attachment holds exactly one of embedded `data` or a retrievable `url`, always the required `size` and R4 SHA-1 `hash`, and optionally presentation-only `title`. The hash provides change detection only, never authorization.
The producer emits the document only after the caller asserts `caller-authorized-opaque-payload` or `verified-sanitized-input`, and validates the declared format grammar; [Recording payload admission](implementation.html#recording-payload-admission) states those preconditions and exactly how far Grove format validation reaches.

### Receiver verification

1. Resolve `Observation.derivedFrom` to the entry whose `fullUrl` matches; the target must be a Recording Document in the same Bundle.
2. Check both outputs carry the identical typed source-record `(system, value)` pair and distinct typed source-output pairs.
3. Check `DocumentReference.context.related` holds exactly the Observation's `fullUrl`.
4. Find the one conversion Provenance whose source entity is that record identifier and confirm its targets cover both outputs.
5. Recompute the output identifiers and entry `fullUrl` values from the exchange protocol to detect drift; HMAC verification requires the governed key.

A receiver that primarily consumes structured summaries still retains the paired Recording Document because it preserves the report fields that the Observation cannot represent.
