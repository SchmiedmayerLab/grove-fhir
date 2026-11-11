<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

SensorKit conversion begins with an exact row in the published adapter contract.
That row determines whether the stream admits structured output, a Recording Document, both representations, or no output.

### What each status admits here

The normative status-vocabulary definitions live on the [guide family page](https://grovealliance.org/fhir/mobile/guides.html#status-vocabulary) and mean the same thing in every guide.
What follows is only what admission produces for a SensorKit row.

A `supported` row produces the listed source-neutral Sensor profile plus its SensorKit adapter as the primary structured measurement, and may additionally require a Recording Document to preserve source details the structured projection cannot carry.
A `mapped-standard` row produces only the source-neutral Sensor Recording Document plus its SensorKit adapter, carrying the exact caller-encoded payload; no scalar or waveform meaning is invented.
A `platform-exclusive` row produces the SensorKit-only structured profile its catalog entry names.
The remaining statuses authorize no output under this adapter.

Only rotation rate may use generic SampledData in the Grove FHIR contracts, and only when its complete three-axis values prove one exact uniform period.
Accelerometer batch identity, high-frequency heart-rate confidence, and ECG guidance/per-voltage flags are not representable by bare SampledData without loss, so those streams retain registered Recording Documents alongside or instead of a structured projection. Their actual wire formats include CSV and native JSON and are declared independently in `content.format`.
Streams admitted as `mapped-standard` because they are irregular, incomplete, mixed-unit, or opaque remain Recording Documents rather than being resampled or relabeled.

On-wrist state, the scalar device-usage summary, and visit summary use explicit SensorKit-only profiles.
A visit is not a clinical Encounter.
A SensorKit wrist temperature session is not automatically body temperature, and a composite pedometer record is not automatically one shared step-count result.
The [device-usage walkthrough](walkthrough.html) shows the required two-resource contract: a structured summary linked to its complete native Recording Document in the same exchange Bundle.

See [`catalog/sensorkit-adapter.json`](https://grovealliance.org/fhir/catalog/sensorkit-adapter.json) for the exact 22 source tokens, platform inventory scope, OS availability, profile claims, represented fields, fail-closed conditions, and status.
The [authoritative status matrix](status-matrix.html) lists every one of those rows.

### Recording devices

Every SensorKit record yields a [Grove Recording Device](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-recording-device.html) for the `SRDevice` that recorded it, which a Recording Document names through `DocumentReference.author`.
For each peripheral that `SRFetchResult.sourceDevice`, available from iOS 27, names, the record also yields a recording Device for that peripheral from its `SRSourceDevice`.
A structured Observation references, through `Observation.device`, the peripheral's Device when exactly one peripheral supplied every sample of the record, as the device that generated its data.
Otherwise it references the `SRDevice`'s Device, which recorded the samples but isn't thereby stated to have generated them; the peripherals that may have are the source entity's `performer` agents below.
When the record names any peripheral, its conversion Provenance's source entity names each peripheral's Device as an agent of participant type `performer` (`Provenance.entity.agent`), and the `SRDevice`'s as an agent of participant type `composer`, the device that recorded the peripherals' samples.
The record unit therefore reaches every Device of the record, whichever outputs it has, the way HealthKit names a source application as `author`.
Each Device carries every fact SensorKit exposes, and consumers filter what they do not need:

| SensorKit field | Grove Recording Device element |
|---|---|
| `SRDevice.name` | `deviceName` of type `user-friendly-name`; the name a person gave the device, such as "My iPhone" |
| `SRDevice.model` | `deviceName` of type `model-name` |
| `SRDevice.systemName` | `version` of type `os-name` |
| `SRDevice.systemVersion` | `version` of type `os-version` |
| `SRDevice.productType` | `modelNumber` |
| `SRSourceDevice.localIdentifier` | `identifier` of type `device-local-identifier`, clear, under a deployment-owned system |
| `SRSourceDevice.manufacturer` | `manufacturer` |
| `SRSourceDevice.model` | `modelNumber` |
| `SRSourceDevice.hardwareVersion` | `version` of type MDC `531974` |
| `SRSourceDevice.firmwareVersion` | `version` of type MDC `531976` |

Each Device always carries one content `device-snapshot` identifier, minted over its complete rendered content, and carries a `recording-device` identifier only when the caller supplies a governed stable per-unit token.
`SRDevice.productType` and the other descriptive fields never establish physical-unit identity, and Devices with equal snapshot content are never inferred to be one unit.
`SRDevice.name` can name a person's device as a HealthKit source name can, and `SRSourceDevice.localIdentifier` is local to one host and links a participant's records from one peripheral; a deployment that shares or exports data applies its own policy to both.
`recordingDeviceIdentity.fieldMappings` in [`catalog/sensorkit-adapter.json`](https://grovealliance.org/fhir/catalog/sensorkit-adapter.json) states the same mapping.
