<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

This walkthrough follows one HealthKit heart-rate sample into a conformant Grove FHIR HealthKit exchange event.
The linked examples illustrate the individual adapter resources; the [Mobile exchange example](https://grovealliance.org/fhir/mobile/Bundle-GroveMobileExchangeBundleExample.html) shows the complete operational Bundle shape.

### 1. Establish conversion context

The application fetches the HealthKit object before conversion.
The producer supplies facts the sample cannot establish: the receiving-system Patient reference, a stable HealthKit-store scope, the converting application and host snapshots, an event-system/producer sequence, and a managed v0 HMAC key identifier and positive epoch.
The key published with the conformance examples is for testing only and must not be used in production.

For the illustrated record, the source coordinates are:

```text
adapter-id:             healthkit
source-type:            HKQuantityTypeIdentifierHeartRate
repository-scope:       <complete deployment-owned Identifier pair>
native-record-id:       lowercase canonical HKObject.uuid
output-role:            heart-rate
output-discriminator:   single
```

Every field is length-framed as exact UTF-8 according to the [Grove exchange protocol](https://grovealliance.org/fhir/catalog/exchange-protocol.json); the protocol does not use delimiter-based parsing.
The opaque Grove identities are always present.
They are deliberately non-reversible: equality supports retry, reconciliation, and retraction, but the digest cannot recover the UUID.
When exact upstream round-trip is required, a deployment may additionally place the clear UUID on this catalog-designated primary Observation as a governed Identifier under its own absolute HealthKit-store namespace.
That optional identifier is not a Grove graph key and is not repeated on child or support resources.
The `single` discriminator has no independent clinical meaning; any meaningful source order, time, multiplicity, or ordinal must also appear in a FHIR element or registered payload rather than only in the preimage.

### 2. Confirm that the source type is supported

The [status matrix](status-matrix.html) row for `HKQuantityTypeIdentifierHeartRate` is `supported`, selects measurement `heart-rate`, and requires both [FHIR R4 Heart Rate](http://hl7.org/fhir/R4/heartrate.html) and [HealthKit Observation](StructureDefinition-healthkit-observation.html).
An absent, deferred, or intentionally unsupported row fails closed; it never falls back to a generic Observation.

### 3. Emit separate source and output identities

The [heart-rate Observation](Observation-HealthKitHeartRateObservationExample.html) carries exactly one source-record identity and one source-output identity.
Their deployment-owned systems bind the kind, key id, and epoch; their values are canonical v0 HMAC results:

The HMAC values in this abbreviated example are schematic; the complete published example contains concrete conformance-key values.

```json
"identifier": [
  {
    "type": { "coding": [{
      "system": "https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role",
      "code": "source-record"
    }]},
    "system": "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1",
    "value": "v0:<key-id>:<epoch>:…"
  },
  {
    "type": { "coding": [{
      "system": "https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role",
      "code": "source-output"
    }]},
    "system": "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1",
    "value": "v0:<key-id>:<epoch>:…"
  }
]
```

`Resource.id` remains optional and repository-assigned. `effectiveDateTime` is the source measurement instant, not conversion time.
The exact source type remains in the adapter-lineage extension beside LOINC `8867-4`; the optional motion-context component is admitted only for this result.

### 4. Represent device roles

The [recording Device](Device-HealthKitRecordingDeviceExample.html) exists only because the caller supplied a governed stable per-unit token.
It carries both a stable `recording-device` identity and an event-scoped `device-snapshot` identity.
Descriptive manufacturer/model/version fields alone would require the Device to be omitted.

The [converting application](Device-HealthKitApplicationDeviceExample.html) and [host](Device-HealthKitHostDeviceExample.html) are distinct immutable snapshots linked through `Device.parent`.
Application release and build are separate typed versions; operating-system version belongs to the host.
An Apple bundle-identifier pair names the application product but is not an installation, host, account, or physical-device identity.

### 5. Record the conversion with Provenance

The [conversion Provenance](Provenance-HealthKitConversionProvenanceExample.html) targets the output, records the source activity time separately from mandatory `recorded`, names the converter as assembler, and carries the same typed source-record Identifier as its source entity.
In an operational event its entry gets an event-scoped `n0:` node key; Provenance does not invent a second event business identifier.

### 6. Assemble one immutable event

The operational Bundle conforms to [Grove Mobile Exchange Bundle](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-mobile-exchange-bundle.html):

- `Bundle.identifier` alone owns `e0:<producer-instance-uuid>:<positive-sequence>`;
- the Bundle contains every output for exactly this source-record revision and exactly one conversion Provenance;
- every entry has one selected complete entry key and a deterministic lowercase UUIDv5 `fullUrl`;
- `Bundle.timestamp`, `Provenance.occurred[x]`, and `Provenance.recorded` keep their separate meanings; and
- collection entries contain no FHIR request/response operations.

An exact retry reuses the event identity, all three times, entry keys, and payload.
Changed source content or revision receives a new event.
A later source deletion produces a separate [retraction Bundle](https://grovealliance.org/fhir/mobile/Bundle-GroveMobileRetractionBundleExample.html) that identifies prior outputs without copying their clinical values or issuing a server DELETE.

The [HealthKit study Bundle](Bundle-HealthKitStudyBundleExample.html) illustrates how the participant, protocol, enrollment, devices, Observation, and Provenance relate.
It is a documentation example, not the operational exchange unit.
