<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

This page walks a first-time implementer through converting one `SRDeviceUsageReport` batch into the mandated dual-output graph, rendered completely in the [SensorKit Device-usage Exchange Bundle](Bundle-SensorKitDeviceUsageExchangeBundleExample.html).

### Why one record becomes two outputs

A device-usage report carries a scalar summary plus nested per-category application, notification, and web usage that no reviewed Observation shape represents losslessly.
The structured [Device Usage Observation](StructureDefinition-sensorkit-device-usage-observation.html) retains only total unlock duration, screen wakes, and unlocks.
Everything else stays in the caller-encoded native payload, carried unmodified by a [SensorKit Recording Document](StructureDefinition-sensorkit-recording-document.html).
The catalog row for `SRSensor.deviceUsageReport` therefore requires both resources in one [Grove Mobile Exchange Bundle](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-mobile-exchange-bundle.html); a summary without its native document is nonconformant.
Real producers already have this shape: the My Heart Counts app uploads each device-usage batch as one JSON file of encoded samples plus one summary Observation referencing that file, which this adapter formalizes.

### What links the two outputs

Both outputs carry the same SensorKit record identifier, `b4df30d0-2a34-492e-a68e-b1eab1cb471d`, assigned by the producer because SensorKit publishes no durable sample identifier.
Each output additionally carries its own deterministic output identifier: UUIDv5 under namespace `c0b8814a-8178-5e92-996a-c4cf36cd640b` over the RFC 8785 serialization of `[recordSystem, recordValue, outputDiscriminator]`, with discriminator `device-usage-summary` for the Observation and `native-recording` for the document.
`Observation.derivedFrom` holds exactly one internal UUID reference to the document, and `DocumentReference.context.related` points back to exactly the Observation.
One [conversion Provenance](StructureDefinition-sensorkit-conversion-provenance.html) targets both outputs and names the record identifier as its sole source entity; omitting the raw target is nonconformant.
Every Bundle entry `fullUrl` is the UUIDv5 of its complete entry business identifier under the Mobile exchange namespace, so the graph serializes identically on every producer.

### The structured summary

Trimmed to the load-bearing elements:

```json
{
  "resourceType": "Observation",
  "meta": {"profile": ["https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-device-usage-observation"]},
  "identifier": [
    {"system": "https://grovealliance.org/fhir/sensorkit/NamingSystem/sensorkit-record-id", "value": "b4df30d0-2a34-492e-a68e-b1eab1cb471d"},
    {"system": "https://grovealliance.org/fhir/sensorkit/NamingSystem/sensorkit-output-id", "value": "6e7453a7-0045-5f96-a847-5a956a817dd4"}
  ],
  "extension": [{"url": "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-source-type", "valueCode": "device-usage"}],
  "status": "final",
  "code": {"coding": [{"system": "https://grovealliance.org/fhir/sensorkit/CodeSystem/sensorkit-concept", "code": "device-usage-summary", "display": "Device usage summary"}]},
  "subject": {"reference": "urn:uuid:d66ce444-2f05-5661-ac7c-86f080cf3be4"},
  "effectivePeriod": {"start": "2026-08-20T08:00:00-07:00", "end": "2026-08-20T08:15:00-07:00"},
  "valueQuantity": {"value": 372, "unit": "seconds", "system": "http://unitsofmeasure.org", "code": "s"},
  "derivedFrom": [{"reference": "urn:uuid:6f4e4010-4e0b-5f04-adf2-78b20c1a196b"}],
  "component": [
    {"code": {"coding": [{"system": "https://grovealliance.org/fhir/sensorkit/CodeSystem/sensorkit-concept", "code": "screen-wakes", "display": "Screen wakes"}]},
      "valueQuantity": {"value": 6, "unit": "{count}", "system": "http://unitsofmeasure.org", "code": "{count}"}},
    {"code": {"coding": [{"system": "https://grovealliance.org/fhir/sensorkit/CodeSystem/sensorkit-concept", "code": "unlocks", "display": "Unlocks"}]},
      "valueQuantity": {"value": 4, "unit": "{count}", "system": "http://unitsofmeasure.org", "code": "{count}"}}
  ],
  "device": {"reference": "urn:uuid:7b38448e-4b35-5813-979a-65f2b724c703"}
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
    {"system": "https://grovealliance.org/fhir/sensorkit/NamingSystem/sensorkit-record-id", "value": "b4df30d0-2a34-492e-a68e-b1eab1cb471d"},
    {"system": "https://grovealliance.org/fhir/sensorkit/NamingSystem/sensorkit-output-id", "value": "d42f2915-17ba-5891-a068-9a6a9d6732b6"}
  ],
  "extension": [{"url": "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-source-type", "valueCode": "device-usage"}],
  "status": "current",
  "type": {"coding": [{"system": "https://grovealliance.org/fhir/sensorkit/CodeSystem/sensorkit-source-type", "code": "device-usage", "display": "Device usage report"}]},
  "subject": {"reference": "urn:uuid:d66ce444-2f05-5661-ac7c-86f080cf3be4"},
  "date": "2026-08-20T15:15:01Z",
  "author": [{"reference": "urn:uuid:7b38448e-4b35-5813-979a-65f2b724c703"}],
  "content": [{"attachment": {
    "contentType": "application/json",
    "title": "SensorKit device usage report",
    "data": "eyJ2ZXJzaW9uIjoiMSJ9",
    "size": 15,
    "hash": "sHigu4BMVa0IJ0LR3NDJ5y8l4sc="
  }}],
  "context": {"related": [{"reference": "urn:uuid:f83aa5e2-ed76-5ddb-a9eb-8d30858b8b55"}]}
}
```

The attachment's payload format identity is its `contentType` from the [Grove Native Recording MIME Types](https://grovealliance.org/fhir/sensor/ValueSet-grove-native-recording-mime-type.html) value set; here the caller-encoded bytes are `application/json`.
The attachment holds exactly one of embedded `data` or a retrievable `url`, and always the required `title`, `size`, and R4 SHA-1 `hash`, which is change detection only, never authorization.
The producer emits the document only after the caller asserts `caller-authorized-opaque-payload` or `verified-sanitized-input`; the mapper itself never fetches, inspects, or re-encodes the bytes.

### How a receiver pairs them

1. Resolve `Observation.derivedFrom` to the entry whose `fullUrl` matches; the target must be a Recording Document in the same Bundle.
2. Check both outputs carry the identical `sensorkit-record-id` `(system, value)` pair and distinct `sensorkit-output-id` values.
3. Check `DocumentReference.context.related` holds exactly the Observation's `fullUrl`.
4. Find the one conversion Provenance whose source entity is that record identifier and confirm its targets cover both outputs.
5. Recompute the output identifiers and entry `fullUrl` values from the identity rules above to detect tampering or drift.

A receiver that only consumes structured summaries can still store the paired document, because retention of the native payload is what keeps the conversion lossless.
