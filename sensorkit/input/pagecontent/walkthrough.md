<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

This walkthrough demonstrates how one `SRDeviceUsageReport` batch becomes the mandated dual-output graph.
The complete resource examples are the [structured summary](Observation-SensorKitDeviceUsageExample.html), [native recording](DocumentReference-SensorKitDeviceUsageDocumentExample.html), and [conversion Provenance](Provenance-SensorKitDeviceUsageProvenanceExample.html); an exchange producer places those resources and their referenced context in one Mobile Exchange Bundle.
The walkthrough is explanatory; the adapter catalog, profiles, and exchange protocol remain normative.

### Dual-output rationale

A device-usage report carries a scalar summary plus nested per-category application, notification, and web usage that no reviewed Observation shape represents losslessly.
The structured [Device Usage Observation](StructureDefinition-sensorkit-device-usage-observation.html) retains only total unlock duration, screen wakes, and unlocks.
Everything else stays in the caller-encoded native payload, carried unmodified by a [SensorKit Recording Document](StructureDefinition-sensorkit-recording-document.html).
The catalog row for `SRSensor.deviceUsageReport` therefore requires both resources in one [Grove Mobile Exchange Bundle](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-mobile-exchange-bundle.html); a summary without its native document is nonconformant.
This contract formalizes a common producer pattern in which one encoded source batch is retained alongside a structured summary that references it.

### Output linkage

Both outputs carry the same opaque source-record v0 HMAC identifier.
SensorKit publishes no durable sample identifier, so the producer atomically assigns and persists an opaque acquisition-record key from a reset generation and monotonic delivery ordinal that continues across callback batches.
Before yielding, it persists the pending start ordinal/count, ordered keys, verification evidence, and cursor boundary.
Exact crash retries reuse those pending coordinates even after callback rebatching; byte-equal records at different ordinals remain distinct, and measured content or payload digests never select identity.
Each output additionally carries its own source-output HMAC.
The `v0:<key-id>:<epoch>:…` forms in the abbreviated examples below are schematic; the complete published examples contain distinct concrete conformance-key values.
The exact catalog roles and discriminators are length-framed into the HMAC preimage, so Unicode and delimiters are unambiguous and no native acquisition key is disclosed. `Observation.derivedFrom` holds exactly one reference to the document, and `DocumentReference.context.related` points back to exactly the Observation.
In an exchange Bundle those internal references use the target entries' UUID `fullUrl` values; the standalone examples use their logical example references.
One [conversion Provenance](StructureDefinition-sensorkit-conversion-provenance.html) targets both outputs and names the record identifier as its sole source entity; omitting the raw target is nonconformant.
Every Bundle entry `fullUrl` is the UUIDv5 of its selected complete entry key under the Mobile exchange namespace.
Exact retries therefore preserve graph identity, while a distinct acquired record uses a distinct acquisition coordinate and event sequence regardless of whether its bytes happen to match another record.

### Structured summary

Trimmed to the load-bearing elements:

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
    "data": "eyJ0aW1lc3RhbXAiOjE3ODcyMzgwMDAsImR1cmF0aW9uIjo5MDAsInRvdGFsU2NyZWVuV2FrZXMiOjYsInRvdGFsVW5sb2NrcyI6NCwidG90YWxVbmxvY2tEdXJhdGlvbiI6MzcyLCJ2ZXJzaW9uIjoiMSIsImFwcFVzYWdlQnlDYXRlZ29yeSI6W10sIm5vdGlmaWNhdGlvblVzYWdlQnlDYXRlZ29yeSI6W10sIndlYlVzYWdlQnlDYXRlZ29yeSI6W119",
    "size": 198,
    "hash": "0lfmvTj5Gabstqo/ss0WoxE9xjY="
  }}],
  "context": {"related": [{"reference": "Observation/SensorKitDeviceUsageExample"}]}
}
```

The payload format identity is `content.format` from the [recording format registry](https://grovealliance.org/fhir/sensor/formats.html) — here `native-recording` — and the `contentType` comes from the [Grove Recording MIME Types](https://grovealliance.org/fhir/sensor/ValueSet-grove-recording-mime-type.html) value set; the caller-encoded bytes are `application/json`. The format code, rather than a custom media type, identifies the Grove wire format.
The example's JSON members are one producer-defined serialization, not a SensorKit stream schema published by this guide. The source-type code supplies the category and meaning; a generic receiver validates only the UTF-8 object-or-array container and otherwise treats the members as opaque.
The attachment holds exactly one of embedded `data` or a retrievable `url`, always the required `size` and R4 SHA-1 `hash`, and optionally presentation-only `title`. The hash provides change detection only, never authorization.
The producer emits the document only after the caller asserts `caller-authorized-opaque-payload` or `verified-sanitized-input`.
It validates the declared format grammar and derives any grammar-defined summary counts from the accepted payload.

For an inline payload, Grove validation checks size and hash integrity together with the generic native-JSON envelope or selected registered CSV grammar.
The CSV checks are structural and lexical; they do not enforce the source-domain ranges described for individual columns.
For a URL payload, validation checks the required Attachment metadata but does not fetch or verify the referenced bytes.

These checks do not parse the PPG binary grammar, recompute summaries, reinterpret, sanitize, rewrite, or reserialize payloads.
They therefore do not establish URL-backed payload integrity, authorization, or obligations outside the selected format grammar.

### Receiver verification

1. Resolve `Observation.derivedFrom` to the entry whose `fullUrl` matches; the target must be a Recording Document in the same Bundle.
2. Check both outputs carry the identical typed source-record `(system, value)` pair and distinct typed source-output pairs.
3. Check `DocumentReference.context.related` holds exactly the Observation's `fullUrl`.
4. Find the one conversion Provenance whose source entity is that record identifier and confirm its targets cover both outputs.
5. Recompute the output identifiers and entry `fullUrl` values from the exchange protocol to detect drift; HMAC verification requires the governed key.

A receiver that only consumes structured summaries can still store the paired document, because retention of the native payload is what keeps the conversion lossless.
