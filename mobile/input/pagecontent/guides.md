<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Grove FHIR 0.6.0 is a coordinated family of ten implementation-guide packages that share one exchange model.
This guide, Mobile, is the hub: it defines the source-neutral profiles every adapter emits.
Each adapter guide binds one platform or provider API to those shared profiles and states exactly which source types convert, which do not, and why.

### The family at a glance

| Guide | Defines | Read it when |
|---|---|---|
| [Mobile](index.html) | The shared measurement profiles, exchange Bundle, device roles, provenance, and study context | You consume Grove data or implement any producer |
| [Sensor](https://grovealliance.org/fhir/sensor/) | Source-neutral time series, waveforms, and the recording DocumentReference contract | Your data is a sampled series or a raw recording rather than a scalar |
| [HealthKit](https://grovealliance.org/fhir/healthkit/) | The closed Apple HealthKit adapter | You convert `HKSample` records on iOS, watchOS, or visionOS |
| [Health Connect](https://grovealliance.org/fhir/health-connect/) | The closed Android Health Connect adapter | You convert Health Connect records on Android |
| [SensorKit](https://grovealliance.org/fhir/sensorkit/) | The closed Apple SensorKit adapter and its dual-output recording pattern | You convert `SRSensor` streams from a study-entitled iOS app |
| [Providers](https://grovealliance.org/fhir/providers/) | The closed adapter for Google Health, Oura, and Withings server APIs | You convert measurements fetched from a provider cloud API |
| [Withings](https://grovealliance.org/fhir/withings/) | The Withings specialization of the provider contract | You implement the exact Withings source surface |
| [Oura](https://grovealliance.org/fhir/oura/) | The Oura specialization of the provider contract | You implement the exact Oura source surface |
| [Google Health](https://grovealliance.org/fhir/google-health/) | The Google Health API specialization of the provider contract | You implement the exact Google source surface |
| [Questionnaire](https://grovealliance.org/fhir/questionnaire/) | Instrument definition, response capture, and the validated pair contract | You define instruments or accept questionnaire responses |

### Choose your route

| I have | Read first | Then | Worked example |
|---|---|---|---|
| An `HKQuantitySample` or other HealthKit record | [HealthKit mapping](https://grovealliance.org/fhir/healthkit/mapping.html) | [Observations](observations.html) | [HealthKit walkthrough](https://grovealliance.org/fhir/healthkit/walkthrough.html) |
| A Health Connect record | [Health Connect mapping](https://grovealliance.org/fhir/health-connect/mapping.html) | [Synchronization](https://grovealliance.org/fhir/health-connect/synchronization.html) | [Status matrix](https://grovealliance.org/fhir/health-connect/status-matrix.html) |
| A SensorKit stream | [SensorKit mapping](https://grovealliance.org/fhir/sensorkit/mapping.html) | [Sensor recordings](https://grovealliance.org/fhir/sensor/waveforms.html) | [Dual-output walkthrough](https://grovealliance.org/fhir/sensorkit/walkthrough.html) |
| Data from Google Health, Oura, or Withings | [Providers mapping](https://grovealliance.org/fhir/providers/mapping.html) | [Observations](observations.html) | [Withings walkthrough](https://grovealliance.org/fhir/providers/walkthrough.html) |
| A waveform, ECG, or raw sensor recording | [Sensor time series](https://grovealliance.org/fhir/sensor/waveforms.html) | [Devices and provenance](devices.html) | [Sensor examples](https://grovealliance.org/fhir/sensor/artifacts.html) |
| An instrument or completed responses | [Questionnaire quick start](https://grovealliance.org/fhir/questionnaire/quick-start.html) | [Study context](study.html) | [Quick-start pair](https://grovealliance.org/fhir/questionnaire/quick-start.html) |

### The machine catalogs

The catalogs are the authoritative machine-readable contracts; the narrative pages explain them but never override them.
Producers generate their conversion tables from these files, and the published guides are rendered from them.

| Catalog | Contents |
|---|---|
| [measurement-catalog.json](https://grovealliance.org/fhir/catalog/measurement-catalog.json) | Every shared Mobile measurement, its codes, units, and per-source coverage |
| [healthkit-adapter.json](https://grovealliance.org/fhir/catalog/healthkit-adapter.json) | The closed HealthKit source-type inventory and conversion status of every row |
| [health-connect-adapter.json](https://grovealliance.org/fhir/catalog/health-connect-adapter.json) | The closed Health Connect record inventory and conversion statuses |
| [sensorkit-adapter.json](https://grovealliance.org/fhir/catalog/sensorkit-adapter.json) | The closed SensorKit stream inventory, structured and raw output contracts |
| [providers-adapter.json](https://grovealliance.org/fhir/catalog/providers-adapter.json) | The closed Google Health, Oura, and Withings element inventory |
| [sensor-catalog.json](https://grovealliance.org/fhir/catalog/sensor-catalog.json) | The source-neutral sensor recording and time-series contract |
| [profile-claims.json](https://grovealliance.org/fhir/catalog/profile-claims.json) | The exact profile sets a conformant resource must claim, per output kind |
| [package-graph.json](https://grovealliance.org/fhir/catalog/package-graph.json) | The dependency graph between the ten guide packages |
| [exchange-protocol.json](https://grovealliance.org/fhir/catalog/exchange-protocol.json) | The single normative identity, event, lifecycle, graph-key, payload, and cross-language vector contract |
| [release-manifest.json](https://grovealliance.org/fhir/catalog/release-manifest.json) | The coordinated release version, FHIR release, package identities, exact direct dependencies, catalogs, and publication state |

### Status vocabulary

Every catalog row carries one status from a single shared vocabulary; a status never means something different in another guide.

- `supported`: the adapter defines and validates an exact conversion to every listed shared profile.
- `mapped-standard`: the source is admitted only as the listed source-neutral recording contract; no scalar clinical meaning is asserted.
- `platform-exclusive`: a reviewed platform-scoped structured profile represents the source because no shared profile fits; output is authorized through that profile alone.
- `unmodeled`: the source element is inventoried, but no shared or platform-scoped profile models it and no output is admitted.
- `deferred`: a plausible shared mapping exists, but source evidence or semantics are insufficient for a conformant conversion.
- `intentionally-unsupported`: the contract deliberately refuses the conversion because any available representation would mislead.

The per-guide mapping pages state the same tokens with the guide's specifics; the definitions here are the normative ones.
