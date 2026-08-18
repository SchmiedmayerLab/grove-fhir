<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Mobile platforms attach open-ended metadata dictionaries to health records. Dumping
them wholesale into FHIR loses meaning; this guide instead applies a **layered policy**
— each entry lands in the most semantic home that exists, and only the residue reaches
the generic extension.

### Layer 1 — first-class FHIR homes

| Platform metadata | FHIR home | Written today |
|---|---|---|
| Time zone (`HKTimeZone`) | HL7 `timezone` extension on `effective[x]` (IANA zone name) | yes |
| Body/sensor location | `Observation.bodySite`, or the HL7 `observation-bodyPosition` extension | no — sensor-location keys currently fall to Layer 4 |
| Device-adjacent values (battery, sensor characteristics) | `Device.property` on the sensor Device (PHD IG pattern, MDC-coded) | no |
| Relay/gateway facts | Already modeled — see [Provenance Model](provenance.html) | yes |

The "written today" column states what the Grove framework emits. A consumer keys on the
layer a value actually arrives in, so the unwritten rows say where those values will move
when the framework implements them — not where to look for them now.

### Layer 2 — capture modality (first-class in this guide)

Sensed-vs-self-reported has no HL7 code system, yet it is the single most analytically
important metadata bit in research data. It gets a first-class extension:
[Recording Method](StructureDefinition-grove-recording-method.html), aligned with
Android Health Connect's recording methods and IEEE 1752.1's `modality`.
`HKMetadataKeyWasUserEntered = true` maps to `manual-entry`.

### Layer 3 — measurement-adjacent values

Values that qualify the measurement itself become `Observation.component` entries whose
code is the platform metadata-key coding and whose value keeps the platform's own typed
value. Concretely: the threshold that triggered a high-heart-rate event
(`HKHeartRateEventThreshold`) rides as a component on the event Observation, coded as the
metadata key rather than as the measured concept — a threshold is configuration, and
coding it as a heart rate would let a query for heart rates ingest it as a measurement.

Which keys a producer promotes is a per-type decision; a key not promoted lands in
Layer 4 unchanged, so a consumer that reads both layers loses nothing either way.

### Layer 4 — the residue

Whatever survives layers 1–3 is carried by
[Platform Metadata](StructureDefinition-grove-platform-metadata.html): one extension
instance per entry, `key` a Coding whose system names the platform key space
([fragment code systems](identifiers.html) — arbitrary platform keys remain valid
codes), `value[x]` typed by the entry's runtime type
(string | boolean | decimal | dateTime | Coding | Quantity).

Enum-valued platform entries keep their platform coding, in the Grove-owned code system
published for that enumeration by the
[platform vocabularies guide](https://grovealliance.org/fhir/platforms) — one system per
enumeration, the code being the platform's own case name. A heart-rate motion context is
`…/platforms/CodeSystem/healthkit-heart-rate-motion-context#sedentary`, as the
[heart-rate example](Observation-GroveHeartRateObservationExample.html) shows. Through
0.4.0 these codings used Apple's documentation URL as the system and the enumeration's
raw integer as the code; [Supersession](supersession.html) maps that encoding onto this
one.
