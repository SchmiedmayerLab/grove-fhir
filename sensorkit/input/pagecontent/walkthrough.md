<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

This page walks a first-time implementer through converting one `SRDeviceUsageReport` batch into the mandated dual-output graph. The complete resource examples are the [structured summary](Observation-SensorKitDeviceUsageExample.html), [native recording](DocumentReference-SensorKitDeviceUsageDocumentExample.html), and [conversion Provenance](Provenance-SensorKitDeviceUsageProvenanceExample.html); an exchange producer places those resources and their referenced context in one Mobile Exchange Bundle.

### Why one record becomes two outputs

A device-usage report carries a scalar summary plus nested per-category application, notification, and web usage that no reviewed Observation shape represents losslessly.
The structured [Device Usage Observation](StructureDefinition-sensorkit-device-usage-observation.html) retains only total unlock duration, screen wakes, and unlocks.
Everything else stays in the caller-encoded native payload, carried unmodified by a [SensorKit Recording Document](StructureDefinition-sensorkit-recording-document.html).
The catalog row for `SRSensor.deviceUsageReport` therefore requires both resources in one [Grove Mobile Exchange Bundle](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-mobile-exchange-bundle.html); a summary without its native document is nonconformant.
Real producers already have this shape: the My Heart Counts app uploads each device-usage batch as one JSON file of encoded samples plus one summary Observation referencing that file, which this adapter formalizes.

### What links the two outputs

Both outputs carry the same opaque source-record v2 HMAC identifier,
`v2:test-key:1:ct2xsuoLAjG1lDQTq8kvZ-59YXjBr84LPF8Adi-x6eE`. SensorKit publishes no
durable sample identifier, so the producer assigns and persists an opaque acquisition-record key
before conversion; exact retries reuse it and measured content never becomes identity.
Each output additionally carries its own source-output HMAC: the Observation uses
`v2:test-key:1:ey9U9SGqloQ8RIGcBQLPw1NDNuUovyfwlUcmbKDODcE` and the Recording Document uses
`v2:test-key:1:NsQH4D0yoTsbEg9zuUMwbqAKqFbJq808gDQqXlWZJm0`. The exact catalog roles and
discriminators are length-framed into the HMAC preimage, so Unicode and delimiters are unambiguous
and no native acquisition key is disclosed.
`Observation.derivedFrom` holds exactly one reference to the document, and `DocumentReference.context.related` points back to exactly the Observation. In an exchange Bundle those internal references use the target entries' UUID `fullUrl` values; the standalone examples use their logical example references.
One [conversion Provenance](StructureDefinition-sensorkit-conversion-provenance.html) targets both outputs and names the record identifier as its sole source entity; omitting the raw target is nonconformant.
Every Bundle entry `fullUrl` is the UUIDv5 of its selected complete entry key under the Mobile
exchange namespace. Exact retries therefore preserve graph identity, while changed content uses a
new event sequence.

### The structured summary

Trimmed to the load-bearing elements:

```json
{
  "resourceType": "Observation",
  "meta": {"profile": ["https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-device-usage-observation"]},
  "identifier": [
    {"type": {"coding": [{"system": "https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role", "code": "source-record"}]}, "system": "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1", "value": "v2:test-key:1:ct2xsuoLAjG1lDQTq8kvZ-59YXjBr84LPF8Adi-x6eE"},
    {"type": {"coding": [{"system": "https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role", "code": "source-output"}]}, "system": "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1", "value": "v2:test-key:1:ey9U9SGqloQ8RIGcBQLPw1NDNuUovyfwlUcmbKDODcE"}
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

### The native recording document

```json
{
  "resourceType": "DocumentReference",
  "meta": {"profile": [
    "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-recording-document",
    "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document"]},
  "identifier": [
    {"type": {"coding": [{"system": "https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role", "code": "source-record"}]}, "system": "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1", "value": "v2:test-key:1:ct2xsuoLAjG1lDQTq8kvZ-59YXjBr84LPF8Adi-x6eE"},
    {"type": {"coding": [{"system": "https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role", "code": "source-output"}]}, "system": "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1", "value": "v2:test-key:1:NsQH4D0yoTsbEg9zuUMwbqAKqFbJq808gDQqXlWZJm0"},
    {"type": {"coding": [{"system": "https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role", "code": "source-artifact"}]}, "system": "https://study.example.org/fhir/NamingSystem/grove-source-artifact-v2/test-key/1", "value": "v2:test-key:1:GrBgxM7stWNYtCREHYwGKKLjcPbW3NWeV_rRZQNqN1o"}
  ],
  "extension": [{"url": "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-source-type", "valueCode": "device-usage"}],
  "status": "current",
  "type": {"coding": [{"system": "https://grovealliance.org/fhir/sensorkit/CodeSystem/sensorkit-source-type", "code": "device-usage", "display": "Device usage report"}]},
  "subject": {"reference": "Patient/SensorKitPatientExample"},
  "date": "2026-08-20T15:15:01Z",
  "author": [{"reference": "Device/SensorKitDeviceExample"}],
  "content": [{"format": {"system": "https://grovealliance.org/fhir/sensor/CodeSystem/grove-recording-format", "code": "native-recording", "version": "0.6.0"}, "attachment": {
    "contentType": "application/vnd.grovealliance.native+json",
    "title": "SensorKit device usage report",
    "data": "eyJ2ZXJzaW9uIjoiMSJ9",
    "size": 15,
    "hash": "sHigu4BMVa0IJ0LR3NDJ5y8l4sc="
  }}],
  "context": {"related": [{"reference": "Observation/SensorKitDeviceUsageExample"}]}
}
```

The payload format identity is `content.format` from the [recording format registry](https://grovealliance.org/fhir/sensor/formats.html) — here `native-recording` — and the `contentType` comes from the [Grove Native Recording MIME Types](https://grovealliance.org/fhir/sensor/ValueSet-grove-native-recording-mime-type.html) value set; the caller-encoded bytes are `application/vnd.grovealliance.native+json`.
The attachment holds exactly one of embedded `data` or a retrievable `url`, and always the required `title`, `size`, and R4 SHA-1 `hash`, which is change detection only, never authorization.
The producer emits the document only after the caller asserts `caller-authorized-opaque-payload` or `verified-sanitized-input`; the mapper itself never fetches, inspects, or re-encodes the bytes.

### How a receiver pairs them

1. Resolve `Observation.derivedFrom` to the entry whose `fullUrl` matches; the target must be a Recording Document in the same Bundle.
2. Check both outputs carry the identical typed source-record `(system, value)` pair and distinct typed source-output pairs.
3. Check `DocumentReference.context.related` holds exactly the Observation's `fullUrl`.
4. Find the one conversion Provenance whose source entity is that record identifier and confirm its targets cover both outputs.
5. Recompute the output identifiers and entry `fullUrl` values from the exchange protocol to detect drift; HMAC verification requires the governed key.

A receiver that only consumes structured summaries can still store the paired document, because retention of the native payload is what keeps the conversion lossless.
