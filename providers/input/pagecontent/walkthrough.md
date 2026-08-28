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
The group `date` becomes `effectiveDateTime` in the payload's `timezone`, here `2026-08-20T07:45:00-07:00`. The adapter omits `Observation.issued`: no v0.6 provider row declares an authoritative result-availability or current-version modification field. Conversion time belongs on `Provenance.recorded`, never in `issued`.

### Opaque identity from the grpid

The `grpid` is the stable native key shared by both measures, so it is the `sourceNativeId` of one source record covering the whole group.
Withings does not document `grpid` as unique across accounts, so the complete deployment-scoped
account Identifier pair participates in identity. The grouped token `getmeas:9+10` is used, never
`getmeas:9` or `getmeas:10` alone. With the public conformance key, the exact source-record value is:

```
v2:test-key:1:xcGtq_GbAQhydEiOKVmFc1iLIbtqP1Xa6WG8sT17Ws8
```

That digest is HMAC-SHA-256 over the typed, length-framed provider components; this example omits
both the account pseudonym and the optional governed exact `grpid` Identifier. A deployment with an
explicit upstream-traceability purpose may place the exact `grpid` once on this catalog-designated
primary Observation under its absolute non-Grove namespace. The Observation also carries the distinct source-output value
`v2:test-key:1:YlJWGJsSEmsyv8i-R9edsO8HpySQzLap4F6yvclNm-w`, derived under the
provider-specific `provider-output` identity kind (whose Identifier role remains `source-output`) with output role
`blood-pressure-panel` and discriminator `single`. Production deployments use a managed key and
their own immutable identifier systems; the public test key is prohibited.
The source-type extension carries `withings/getmeas:9+10`, keeping the exact catalog dispatch token recoverable directly from the resource.

### What the adapter refuses

- `deviceid`, `attrib`, `category`, `created`, and `modified` are not consumed source elements; they are dropped, not smuggled into FHIR metadata.
- an unpaired type 9 or type 10 emits no normalized Observation at all.
- a type 11 heart rate in the same group would be its own `getmeas:11` source record and heart-rate output, never a third panel component.
- an `unmodeled` group member never yields a normalized Observation; type 155 is not unmodeled, but is emitted separately under the Withings-owned vascular-age semantic profile and the Withings provider envelope.

### The emitted graph

The conversion emits one [Observation](https://grovealliance.org/fhir/withings/Observation-WithingsBloodPressureExample.html) claiming exactly the shared blood-pressure semantic profile plus [Withings Observation](https://grovealliance.org/fhir/withings/StructureDefinition-withings-observation.html), and one [conversion Provenance](https://grovealliance.org/fhir/withings/Provenance-WithingsBloodPressureProvenanceExample.html) whose sole source entity is the source-record identifier pair. Concrete provider Observations live in the exact provider package; the shared Provider Observation profile is an abstract lineage envelope and cannot be claimed directly.
The [Withings Exchange Bundle](https://grovealliance.org/fhir/withings/Bundle-WithingsExchangeBundleExample.html) carries the complete graph as a [Grove Mobile Exchange Bundle](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-mobile-exchange-bundle.html): every entry carries its selected typed node key, `fullUrl` is the protocol's length-framed UUID version 5 projection of that complete Identifier pair, and all internal references use those UUID URNs.
See the [authoritative status matrix](status-matrix.html) and [`catalog/providers-adapter.json`](https://grovealliance.org/fhir/catalog/providers-adapter.json) for the definitive grouped-mapping contract.
