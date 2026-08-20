<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

### Definitive status meanings

- `supported`: a complete, lossless structured mapping exists to a listed
  source-neutral Sensor profile plus the SensorKit adapter profile.
- `mapped-standard`: the exact caller-encoded payload is represented by the
  source-neutral Sensor Recording Document plus its SensorKit adapter; no scalar or
  waveform meaning is invented.
- `provider-specific`: a reviewed SensorKit-only structured profile represents the
  source semantics because no exact shared or international profile does.
- `deferred`: the stream is inventoried, but v0.2.0 publishes no admitted output
  contract.
- `intentionally-unsupported`: v0.2.0 deliberately rejects an unsafe or misleading
  representation.

Only rotation rate may use generic SampledData in v0.2.0, and only when its complete
three-axis values prove one exact uniform period. Accelerometer batch identity,
high-frequency heart-rate confidence, and ECG guidance/per-voltage flags are not
representable by bare SampledData without loss, so those streams remain native Recording
Documents. Irregular, incomplete, mixed-unit, opaque, or unreviewed streams likewise
remain native rather than being resampled or relabeled.

On-wrist state, the scalar device-usage summary, and visit summary use explicit
SensorKit-only profiles. A visit is not a clinical Encounter. A SensorKit wrist
temperature session is not automatically body temperature, and a composite pedometer
record is not automatically one shared step-count result.

See `catalog/sensorkit-adapter.json` for the exact 24 source tokens, platform inventory
scope, OS availability, profile claims, represented fields, fail-closed conditions, and
status.
The [authoritative status matrix](status-matrix.html) renders every one of those rows.
