<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Identifier systems minted by this guide live under
`https://grovealliance.org/fhir/sid/`; its code systems live under
`https://grovealliance.org/fhir/core/CodeSystem/`, and the platform vocabularies under
`https://grovealliance.org/fhir/platforms/CodeSystem/`. All are stable, permanent URIs;
none are resolvable endpoints.

### Record identity

| System | Used in | Value |
|---|---|---|
| `…/sid/healthkit-sample-id` | `Observation.identifier` | `HKObject.uuid` (UUID string) |
| `…/sid/health-connect-record-id` | `Observation.identifier` | Health Connect `Metadata.id` |
| `…/sid/sensorkit-sample-id` | `Observation.identifier` | Deterministic digest of a SensorKit sample's own content, keyed per deployment (SensorKit assigns no record ids) — see [Security and Privacy](security.html) |

Deduplication: writers use conditional create
(`Bundle.entry.request.ifNoneExist: identifier=<system>|<value>`) — servers return
`200` on a single existing match (no duplicate written) and `412` on multiple matches,
so uploaders treat `412` as a data-hygiene signal, not a transient failure. Readers treat
(system, value) as the platform record identity. For passthrough resources whose own
`identifier` list carries source-institution identity (clinical records), the record id
travels in the [Source Record Identifier](StructureDefinition-grove-source-record-id.html)
extension instead.

### App identity

| System | Used in | Value |
|---|---|---|
| `…/sid/apple-bundle-id` | `Device.identifier` (gateway) | The app's bundle identifier |
| `…/sid/android-application-id` | `Device.identifier` (gateway) | The app's application id |

If HL7's mobile-app-identifier work (UMHAI) produces a standard system, it slots in as
an additional `Device.identifier` without displacing these.

### Device identity

| System | Used in | Value |
|---|---|---|
| `…/sid/device-local-id` | `Device.identifier` (sensor) | The platform's ephemeral local device identifier |

### Platform metadata key spaces

| System | Kind |
|---|---|
| `…/platforms/CodeSystem/healthkit-metadata-key` | Fragment code system — raw HealthKit metadata keys |
| `…/platforms/CodeSystem/health-connect-metadata-key` | Fragment code system — Health Connect metadata fields |

Both are published by the
[platform vocabularies guide](https://grovealliance.org/fhir/platforms), alongside the
sample-type and value enumerations.
