<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

This walkthrough follows one HealthKit heart-rate sample from `HKQuantitySample` to the uploaded exchange Bundle.
Every value below comes from the linked example instances, so a first producer run can be diffed against them field by field.

### 1. The sample and the conversion context

The app has already fetched the sample; the converter never queries HealthKit itself.

```swift
// HKQuantitySample fetched by the app:
//   uuid       9A2F4D6E-1C3B-4F8A-B7D0-5E6A8C9B0D1F
//   type       HKQuantityTypeIdentifierHeartRate
//   quantity   76 count/min
//   startDate  2026-08-20 09:12:45.128 -07:00 (equal to endDate: a point result)
//   device     nil

let context = HealthKitFHIRConversionContext(
    subject: Reference(reference: "https://study.example.org/fhir/Patient/participant-hk-001"),
    converter: HealthKitFHIRApplication(
        name: "Grove Study",
        bundleIdentifier: "org.grovealliance.example",
        version: "1.4.0"
    ),
    graphIdentifierSystem: "https://study.example.org/fhir/identifiers/mobile-graph"
)
let converter = HealthKitFHIRConverter()
let conversion = try converter.convert(sample, context: context)
upload(conversion.bundle)
```

Three inputs cannot be derived from the sample: the subject as the receiving system knows the participant, the converting application's identity, and the deployment-owned `graphIdentifierSystem` namespace for the graph nodes that exist only because of this export.

### 2. The catalog row that admits it

Conversion is admitted only when the frozen adapter catalog carries a `supported` row for the exact sample type.
The [status matrix](status-matrix.html) row for `HKQuantityTypeIdentifierHeartRate` is `supported`, maps to measurement `heart-rate`, and requires the [Grove Mobile Heart Rate](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-mobile-heart-rate.html) profile beside [HealthKit Observation](StructureDefinition-healthkit-observation.html).
Any type without a `supported` row fails closed; no best-effort Observation is emitted.

### 3. The Observation

The [exchange heart-rate Observation](Observation-HealthKitExchangeHeartRateObservationExample.html) claims both profile canonicals, keeps LOINC `8867-4` as the normative meaning, and retains the exact sample type as one adapter-lineage coding.

```json
"identifier": [{
  "system": "https://grovealliance.org/fhir/healthkit/NamingSystem/healthkit-object-id",
  "value": "9a2f4d6e-1c3b-4f8a-b7d0-5e6a8c9b0d1f"
}],
"effectiveDateTime": "2026-08-20T09:12:45.128-07:00",
"issued": "2026-08-20T16:12:47.000Z",
"valueQuantity": { "value": 76, "code": "/min", "system": "http://unitsofmeasure.org", "unit": "beats/minute" }
```

`effectiveDateTime` is the sample's own measurement instant, millisecond-rounded with the source offset preserved; `issued` is the conversion instant.
The sample has no `HKDevice`, so no recording Device is emitted and `Observation.device` stays absent rather than guessed.

### 4. The application Device

The [converting application](Device-HealthKitApplicationDeviceExample.html) is a [Grove Application Device](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-application-device.html), not a recording device.

```json
"identifier": [{
  "system": "https://grovealliance.org/fhir/healthkit/NamingSystem/apple-bundle-id",
  "value": "org.grovealliance.example"
}],
"deviceName": [{ "type": "user-friendly-name", "name": "Grove Study" }]
```

Its MDC-typed software-version slice carries the exact converter version `1.4.0`.

### 5. The conversion Provenance

The [conversion Provenance](Provenance-HealthKitExchangeConversionProvenanceExample.html) records the transform: the application is the `assembler` agent, and the HealthKit object identifier is the sole source entity.

```json
"agent": [{ "type": { "coding": [{ "code": "assembler" }] },
            "who": { "reference": "urn:uuid:88912f8b-fd4e-51f9-8a72-ab97fde584d9" } }],
"entity": [{ "role": "source",
             "what": { "identifier": {
               "system": "https://grovealliance.org/fhir/healthkit/NamingSystem/healthkit-object-id",
               "value": "9a2f4d6e-1c3b-4f8a-b7d0-5e6a8c9b0d1f" } } }],
"target": [{ "reference": "urn:uuid:697f6d32-7fb0-54d3-ba0e-8d933f6e5457" }]
```

No source author appears because the caller did not classify `HKSourceRevision`; the adapter never guesses whether the source was an app or a device.

### 6. The exchange Bundle

The [exchange Bundle](Bundle-HealthKitExchangeBundleExample.html) is a [Grove Mobile Exchange Bundle](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-mobile-exchange-bundle.html): a `collection` whose three entries each carry one complete entry business identifier and a fullUrl derived from it.
Its [JSON representation](Bundle-HealthKitExchangeBundleExample.json) is the complete upload payload.

### Why each identifier is what it is

| Graph node | Identifier system | Value | Entry fullUrl |
|---|---|---|---|
| Observation | HealthKit object namespace | `9a2f4d6e-1c3b-4f8a-b7d0-5e6a8c9b0d1f` | `urn:uuid:697f6d32-7fb0-54d3-ba0e-8d933f6e5457` |
| Application Device | Apple bundle namespace | `org.grovealliance.example` | `urn:uuid:88912f8b-fd4e-51f9-8a72-ab97fde584d9` |
| Provenance | caller graph namespace | `9a2f4d6e-…\|conversion-provenance` | `urn:uuid:16d49bf9-a6dc-58da-bc29-7146da34831c` |
| Bundle | caller graph namespace | `9a2f4d6e-…\|exchange-bundle` | none; the Bundle is the payload |

The Observation reuses the sample's own `HKObject.uuid` under the [HealthKit Object Identifier](NamingSystem-healthkit-object-id.html) namespace, and the application reuses its Apple bundle identifier: both identities exist independently of this export.
The Provenance and the Bundle exist only because of this export, so their values are minted deterministically in the caller's `graphIdentifierSystem` from the object UUID plus a role suffix.
Each fullUrl is the UUIDv5 of the RFC 8785 canonical `["system","value"]` pair under the frozen namespace `a9a39cf1-c944-5d15-a3c2-c395969ea101`, so converting the same sample twice yields byte-identical identities and re-sends deduplicate on the server.
`Resource.id` plays no part in source identity; a logical id appears only when a FHIR repository assigns one.

### Validate the output

Validate the extracted Observation with both packages and both profile canonicals, exactly as described in [Implement and validate](implementation.html):

```sh
java -jar validator_cli.jar observation.json \
  -version 4.0.1 \
  -ig grove-packages/mobile/package.tgz \
  -ig grove-packages/healthkit/package.tgz \
  -profile https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-observation \
  -profile https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-heart-rate
```

Validation proves the shape, identifiers, and terminology; it cannot prove the catalog admitted the type or that identifier disclosure was authorized, so test those against representative source fixtures.
