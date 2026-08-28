<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

### Definitive status meanings

The normative status-vocabulary definitions live on the [guide family page](https://grovealliance.org/fhir/mobile/guides.html#status-vocabulary).
The list below states the SensorKit specifics.

- `supported`: a complete, lossless structured mapping exists to a listed
  source-neutral Sensor profile plus the SensorKit adapter profile.
- `mapped-standard`: the exact caller-encoded payload is represented by the
  source-neutral Sensor Recording Document plus its SensorKit adapter; no scalar or
  waveform meaning is invented.
- `platform-exclusive`: a reviewed SensorKit-only structured profile represents the source semantics because no exact shared or international profile does.
- `unmodeled`: the stream is inventoried, but no shared or SensorKit-scoped profile models it and no output is admitted.
- `deferred`: the stream is inventoried, but v0.6.0 publishes no admitted output
  contract.
- `intentionally-unsupported`: v0.6.0 deliberately rejects an unsafe or misleading
  representation.

Only rotation rate may use generic SampledData in v0.6.0, and only when its complete
three-axis values prove one exact uniform period. Accelerometer batch identity,
high-frequency heart-rate confidence, and ECG guidance/per-voltage flags are not
representable by bare SampledData without loss, so those streams remain native Recording
Documents. Irregular, incomplete, mixed-unit, opaque, or unreviewed streams likewise
remain native rather than being resampled or relabeled.

On-wrist state, the scalar device-usage summary, and visit summary use explicit
SensorKit-only profiles. A visit is not a clinical Encounter. A SensorKit wrist
temperature session is not automatically body temperature, and a composite pedometer
record is not automatically one shared step-count result.
The [device-usage walkthrough](walkthrough.html) shows the mandated dual-output contract of structured summary plus native Recording Document in one exchange Bundle.

See [`catalog/sensorkit-adapter.json`](https://grovealliance.org/fhir/catalog/sensorkit-adapter.json) for the exact 22 source tokens, platform inventory
scope, OS availability, profile claims, represented fields, fail-closed conditions, and
status.
The [authoritative status matrix](status-matrix.html) renders every one of those rows.
