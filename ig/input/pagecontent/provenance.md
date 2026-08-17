<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Mobile health data has two distinct provenance questions, and FHIR has a native home
for each:

**Who measured it?** The recording hardware — a chest strap, watch, scale, or the phone
itself — is a Device resource referenced from `Observation.device`, profiled as
[Grove Sensor Device](StructureDefinition-grove-sensor-device.html). Version fields use
the IEEE 11073 MDC production-specification codes (hardware 531974, software 531975,
firmware 531976), the same vocabulary as HL7's Personal Health Device IG.

**Who saved it?** The app that wrote the record into the platform store — with its
bundle/application identifier, version, host hardware product type, and OS version — is
a second Device, profiled as
[Grove Gateway Device](StructureDefinition-grove-gateway-device.html) and linked from
the Observation via the HL7 `observation-gatewayDevice` extension. This mirrors the
PHD IG's gateway (PHG) role and R5's `Device.gateway`.

### Contained, and why that is the choice

Mobile platforms provide no stable device identity — HealthKit's `localIdentifier` is
ephemeral, UDIs and serials are almost never present — so sensor and gateway Devices are
**contained** in their Observation.

A deterministic `Device.identifier`, hashed over manufacturer, model, and versions, would
make Devices standalone and searchable. It would also stay stable for as long as the
participant keeps the watch and come out identical in every dataset that participant's
data reaches — precisely the durable join key Grove's per-sample identifier hashing
exists to withhold, and enough on its own to link two datasets that share nothing else.
Grove therefore does not mint one. The trade is deliberate; what it costs in search, the
next section buys back another way.

### The queryable facts, denormalised

A contained resource cannot be reached by a FHIR search, so "which of these came from my
watch" has to be answerable from the Observation itself. The two facts consumers filter
on are carried in FHIR's own resource metadata:

| Fact | Carrier | Searchable by |
|---|---|---|
| Acquisition channel | `meta.source` | `_source` |
| Device form factor | `meta.tag` | `_tag` |
| Form factor (semantic home) | `Device.type` on the contained Device | — |
| Relaying app and OS | `observation-gatewayDevice` extension | — |

`meta.source` is a URI naming the acquisition path, one per channel:

- `https://grovealliance.org/fhir/source/healthkit`
- `https://grovealliance.org/fhir/source/health-connect`
- `https://grovealliance.org/fhir/source/sensorkit`
- `https://grovealliance.org/fhir/source/fitbit-web-api`

Channel granularity only. It never identifies an app instance — that would multiply the
values, duplicate what the gateway Device already says, and turn a coarse filter into
another identifier.

`meta.tag` carries the recording device's form factor from the
[Grove Mobile Device Type](CodeSystem-grove-device-type.html) code system (`phone`,
`watch`, `ring`, `scale`, `chest-strap`, and the rest). It is a copy for searching;
`Device.type` on the contained Device remains the semantically correct home, and writers
populate both.

### One phone, two Devices

When the phone is itself the sensor (phone-recorded step counts), an Observation
legitimately carries two Devices describing one physical phone: hardware facts in
`Observation.device`, app + OS facts in the gateway. They are not duplicates — their
version slicing differs — and SHALL NOT be collapsed.

### Maturity notes

`observation-gatewayDevice` is FMM 3 and mandated 1..1 by the published PHD IG STU2 —
solid ground. The newer `device-gateway` extension (the R4 backport of R5's
`Device.gateway`, FMM 1, adopted by no IG yet) is deliberately **not** used by this
guide; it is noted only as the likely R6-era successor for Device-to-Device linkage.

### Uploads

Provenance travels on the Observation itself, so this guide defines no upload resource.
When a batch arrived is recorded by the server in `meta.lastUpdated`; when each sample
was measured, and in which named zone, travels on that sample's own `effective[x]` with
the HL7 `timezone` extension, exactly as it always has.

### Platform mapping

| Concept | HealthKit | Health Connect |
|---|---|---|
| Sensor device fields | `HKDevice` | `Metadata.device` |
| Gateway app name | `HKSourceRevision.source.name` | (app attribution) |
| Gateway app id | `HKSourceRevision.source.bundleIdentifier` → `identifier[appleBundleId]` | `Metadata.dataOrigin.packageName` → `identifier[androidApplicationId]` |
| Gateway app version | `HKSourceRevision.version` | — |
| Gateway host hardware | `HKSourceRevision.productType` → `modelNumber` | — |
| Gateway OS version | `HKSourceRevision.operatingSystemVersion` → `version[operatingSystem]` | — |
| Device form factor | `HKDevice.model` (inferred) → `Device.type` + `meta.tag` | `Metadata.device.type` → `Device.type` + `meta.tag` |
| Acquisition channel | `…/fhir/source/healthkit` → `meta.source` | `…/fhir/source/health-connect` → `meta.source` |

HealthKit has no form-factor field, so Grove infers one from `HKDevice.model`, which
recognizes only the literal strings `iPhone`, `Watch` and `Apple Watch`. The inference is
deliberately incomplete: a hardware-versioned model string (`Watch7,12`) or a BLE
peripheral's own model name yields no `Device.type` at all, and a consumer SHALL NOT read
its absence as "not a phone or a watch". Health Connect reports the form factor directly,
so its mapping is exact.
