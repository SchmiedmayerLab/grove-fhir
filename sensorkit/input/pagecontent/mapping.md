<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

SensorKit conversion begins with an exact row in the published adapter contract.
That row determines whether the stream admits structured output, a Recording Document, both representations, or no output.

### Definitive status meanings

The normative status-vocabulary definitions live on the [guide family page](https://grovealliance.org/fhir/mobile/guides.html#status-vocabulary). The list below states the SensorKit specifics.

- `supported`: the listed source-neutral Sensor profile plus SensorKit adapter represents the primary structured measurement; a row may also require a Recording Document to preserve source details not represented structurally.
- `mapped-standard`: the exact caller-encoded payload is represented by the source-neutral Sensor Recording Document plus its SensorKit adapter; no scalar or waveform meaning is invented.
- `platform-exclusive`: a SensorKit-only structured profile represents the source semantics because no exact shared or established FHIR profile does.
- `unmodeled`: the stream is inventoried, but no shared or SensorKit-scoped profile models it and no output is admitted.
- `deferred`: the stream is inventoried, but the Grove FHIR contracts publish no admitted output contract.
- `intentionally-unsupported`: the Grove FHIR contracts reject an unsafe or misleading representation.

Only rotation rate may use generic SampledData in the Grove FHIR contracts, and only when its complete three-axis values prove one exact uniform period.
Accelerometer batch identity, high-frequency heart-rate confidence, and ECG guidance/per-voltage flags are not representable by bare SampledData without loss, so those streams retain registered Recording Documents alongside or instead of a structured projection. Their actual wire formats include CSV and native JSON and are declared independently in `content.format`.
Streams admitted as `mapped-standard` because they are irregular, incomplete, mixed-unit, or opaque remain Recording Documents rather than being resampled or relabeled.

On-wrist state, the scalar device-usage summary, and visit summary use explicit SensorKit-only profiles.
A visit is not a clinical Encounter.
A SensorKit wrist temperature session is not automatically body temperature, and a composite pedometer record is not automatically one shared step-count result.
The [device-usage walkthrough](walkthrough.html) shows the required two-resource contract: a structured summary linked to its complete native Recording Document in the same exchange Bundle.

See [`catalog/sensorkit-adapter.json`](https://grovealliance.org/fhir/catalog/sensorkit-adapter.json) for the exact 22 source tokens, platform inventory scope, OS availability, profile claims, represented fields, fail-closed conditions, and status.
The [authoritative status matrix](status-matrix.html) lists every one of those rows.
