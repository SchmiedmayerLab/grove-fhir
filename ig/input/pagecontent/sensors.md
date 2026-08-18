<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Phones and watches produce passive sensor streams beyond the health-record stores:
Apple's SensorKit exposes wear state, location-category visits, device-usage summaries,
and raw ECG/PPG/temperature streams to approved research studies. This page defines how
those streams travel as FHIR, replacing the per-app extension trees earlier study apps
used.

### Summary observations

Streams with a natural per-record summary become Observations conforming to
[Grove Mobile Sensor Observation](StructureDefinition-grove-mobile-sensor-observation.html),
coded with the [SensorKit sample type](https://grovealliance.org/fhir/platforms/CodeSystem-sensorkit-sample-type.html) and
carrying their structure in coded components rather than nested extensions:

- [Wear State](StructureDefinition-grove-wear-state-observation.html) — worn or not,
  with wrist and crown placement as components
  ([example](Observation-GroveWearStateObservationExample.html)). Wear state is the
  denominator for every other wearable stream: consumers use it to tell "no data" from
  "not worn".
- [Visits](StructureDefinition-grove-visit-observation.html) — the kind of place
  (home, work, school, gym) and its timing. SensorKit reports arrival and departure as
  time *windows*, which map to `valuePeriod` components; `effectivePeriod` spans the
  widest possible visit. Coordinates are never present — which is not the same as being
  de-identified, since the distance-from-home component is metre-precise against a named
  anchor. See [Security and Privacy](security.html).
- [Device Usage](StructureDefinition-grove-device-usage-observation.html) — unlock
  duration as the value, screen wakes and unlocks as components.

The record identity travels in `Observation.identifier` under
`https://grovealliance.org/fhir/sid/sensorkit-sample-id`, a deterministic digest over the
sample's own content since SensorKit assigns no record ids. Producers key that digest per
deployment — [Security and Privacy](security.html) says why an unkeyed one is a
re-identification hazard.

The recording watch or phone belongs in `Observation.device` as a contained
[Grove Sensor Device](StructureDefinition-grove-sensor-device.html), exactly as for
health-store records; SensorKit's `SRDevice` supplies the same fields `HKDevice` does.
Grove's SensorKit converter does not populate it yet.

### Raw sensor batches

High-resolution streams — PPG and ECG waveforms, accelerometer data, per-app usage
detail — do not fit Observations. They travel as
[Grove Sensor Batch Documents](StructureDefinition-grove-sensor-batch-document.html):
a `DocumentReference` typed by the sensor stream whose attachment carries the payload's
true media type, hash, and size. Large batches may ship the payload as a sidecar file
next to the FHIR payload, referenced by relative URL. A summary Observation derived
from a batch points back through `derivedFrom`.

### How much of this becomes an Observation

Not every sample deserves a resource. [Dense Series](series.html) gives the rule:
regular sampling becomes one `SampledData` Observation, aggregate-only quantities are
bucketed before conversion, and high-volume raw data travels as a batch document.

### ECG

SensorKit ECG uses the same MDC-coded lead vocabulary
(`urn:iso:std:iso:11073:10101`, `MDC_ECG_ELEC_POTL`) as HealthKit electrocardiograms,
so consumers process both with one code path.
