<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

This walkthrough traces one already-obtained Withings measure group into the emitted FHIR graph.

### The source measure group

The Withings Measure API returns blood pressure as two measures inside one measure group:

```json
{
  "status": 0,
  "body": {
    "updatetime": 1787245201,
    "timezone": "America/Los_Angeles",
    "measuregrps": [
      {
        "grpid": 4759723856,
        "attrib": 0,
        "date": 1787237100,
        "created": 1787237112,
        "modified": 1787237112,
        "category": 1,
        "deviceid": "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b",
        "measures": [
          { "value": 118, "type": 10, "unit": 0 },
          { "value": 76, "type": 9, "unit": 0 }
        ]
      }
    ]
  }
}
```

### One group, one panel

Type 9 (diastolic) and type 10 (systolic) are single components of one clinical result, so neither is a standalone `supported` output.
The catalog's grouped mapping `getmeas:9+10` emits exactly one [Grove Mobile Blood Pressure](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-mobile-blood-pressure.html) panel only when one type 9 value and one type 10 value occur in the same measure group.
A group holding only one of the two emits nothing; the adapter never fabricates the missing component or downgrades the pair to two loose Observations.

Each provider value is `value * 10^unit`, so systolic `118 * 10^0` and diastolic `76 * 10^0` become the panel's two UCUM `mm[Hg]` components.
The group `date` becomes `effectiveDateTime` in the payload's `timezone`, here `2026-08-20T07:45:00-07:00`; `issued` is the conversion time.

### Opaque identity from the grpid

The `grpid` is the stable native key shared by both measures, so it is the `sourceNativeId` of one source record covering the whole group.
Withings does not document `grpid` as unique across accounts, so the complete deployment-scoped
account Identifier pair participates in identity. The grouped token `getmeas:9+10` is used, never
`getmeas:9` or `getmeas:10` alone. With the public conformance key, the exact source-record value is:

```
v2:test-key:1:xcGtq_GbAQhydEiOKVmFc1iLIbtqP1Xa6WG8sT17Ws8
```

That digest is HMAC-SHA-256 over the typed, length-framed provider components; neither the account
pseudonym nor `grpid` is disclosed. The Observation also carries the distinct source-output value
`v2:test-key:1:2rfHQTve-qJZhh5CT50hxoPKPvnj3u3gFEkAv50ns6o`, derived with output role
`blood-pressure-panel` and discriminator `single`. Production deployments use a managed key and
their own immutable identifier systems; the public test key is prohibited.
The source-type extension carries `withings/getmeas:9+10`, keeping the exact catalog dispatch token recoverable directly from the resource.

### What the adapter refuses

- `deviceid`, `attrib`, `category`, `created`, and `modified` are not consumed source elements; they are dropped, not smuggled into FHIR metadata.
- an unpaired type 9 or type 10 emits no normalized Observation at all.
- a type 11 heart rate in the same group would be its own `getmeas:11` source record and heart-rate output, never a third panel component.
- `unmodeled` group members such as type 6 (fat ratio) or type 155 (vascular age) never yield a normalized Observation in v0.6.0.

### The emitted graph

The conversion emits one [Observation](Observation-WithingsBloodPressureExample.html) claiming exactly the shared blood-pressure profile plus [Provider Observation](StructureDefinition-providers-observation.html), and one [conversion Provenance](Provenance-WithingsBloodPressureProvenanceExample.html) whose sole source entity is the source-record identifier pair.
The [Withings Exchange Bundle](https://grovealliance.org/fhir/withings/Bundle-WithingsExchangeBundleExample.html) carries the complete graph as a [Grove Mobile Exchange Bundle](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-mobile-exchange-bundle.html): every entry carries its selected typed node key, `fullUrl` is the protocol's length-framed UUID version 5 projection of that complete Identifier pair, and all internal references use those UUID URNs.
See the [authoritative status matrix](status-matrix.html) and [`catalog/providers-adapter.json`](https://grovealliance.org/fhir/catalog/providers-adapter.json) for the definitive grouped-mapping contract.
