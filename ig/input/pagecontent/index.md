<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

This implementation guide defines how mobile health data — observations captured on
phones, watches, and connected sensors, and questionnaires answered on mobile devices —
is encoded in FHIR R4, independent of any one platform. It is written and maintained by
the [Grove](https://grovealliance.org) framework and designed so the same encoding works
for Apple HealthKit, Android Health Connect, and directly-connected BLE devices.

### How to read this guide

- **Receiving Grove data?** Start with [Consuming Grove Data](consuming.html), then the
  worked examples: a [heart rate](Observation-GroveHeartRateObservationExample.html)
  from a chest strap, [phone-counted steps](Observation-GroveStepCountObservationExample.html),
  and a [sleep stage](Observation-GroveSleepObservationExample.html).
- **Authoring questionnaires?** [Questionnaire Hints](questionnaires.html) and the
  [Renderer Support Matrix](questionnaire-support.html) state exactly what the renderer
  honors; the [example questionnaire](Questionnaire-GroveQuestionnaireExample.html) and
  [its response](QuestionnaireResponse-GroveQuestionnaireResponseExample.html) show both
  directions.
- **Working with passive sensor streams?** [Sensor Streams](sensors.html) covers
  SensorKit-style data: wear state, visits, device usage, and raw batches.
- **Storing or sharing any of it?** [Security and Privacy](security.html) states what
  these streams disclose, the labels resources carry, and what de-identifying them takes.
- **Holding historical data?** [Supersession](supersession.html) maps every earlier
  spelling to its current encoding.
- Everything normative is on the [Artifacts](artifacts.html) page; changes between
  releases are in the [Change Log](changes.html).

### Conformance language

SHALL, SHOULD, and MAY carry their RFC 2119 meanings. *Must Support* (`MS`) means:
producers populate the element whenever the platform supplies a value, and consumers
process resources without failing when it is present.

### Design stance: adopt first, mint last

Every concept was checked against published standards before anything was defined here.

| Concept | Encoding |
|---|---|
| Recording device | `Observation.device` → [Grove Sensor Device](StructureDefinition-grove-sensor-device.html) profile (MDC-coded version types, PHD-IG-aligned) |
| Saving app + OS | HL7 `observation-gatewayDevice` extension → [Grove Gateway Device](StructureDefinition-grove-gateway-device.html) profile |
| Record identity / dedup | `Observation.identifier` with [Grove identifier systems](identifiers.html) |
| Timing | `effective[x]` at full platform precision + HL7 `timezone` extension — no epoch extensions |
| Capture modality | [Recording Method](StructureDefinition-grove-recording-method.html) extension (Health-Connect- and IEEE-1752-aligned) |
| Residual platform metadata | Layered policy, [Platform Metadata](StructureDefinition-grove-platform-metadata.html) as the last resort |
| Text-input validation | HL7 `targetConstraint` extension (FHIRPath + human message) |
| Keyboards | SDC `sdc-questionnaire-keyboard` |
| Autofill / capitalization | [autocomplete](StructureDefinition-grove-autocomplete.html) / [autocapitalize](StructureDefinition-grove-autocapitalize.html) extensions carrying WHATWG HTML vocabularies |
| Image-annotation questions | SDC `itemMedia` base image + [region legend](StructureDefinition-grove-annotate-image-region.html) with body-site codes |
| Passive sensor streams | [Sensor Streams](sensors.html): coded components + raw-batch documents |

The conformance load is carried by profiles —
[Grove Mobile Sensor Observation](StructureDefinition-grove-mobile-sensor-observation.html)
is the entry point — while extensions stay small and reusable.

### What this guide does not do

It does not re-standardize what exists: no per-measure codes (LOINC/SNOMED are used
directly), no device model beyond what mobile platforms can actually populate, and no
questionnaire machinery beyond what SDC already provides. Where HL7's Caliper accelerator
or the Physical Activity IG later standardize overlapping concepts, this guide will
adopt and deprecate in their favor.

### History

Earlier versions of these concepts were published under Stanford-hosted URLs and once in
a HealthKit-shaped draft; [Supersession](supersession.html) maps every historical
spelling to its current encoding, and readers of the Grove framework continue to accept
them.

### Dependencies

{% include dependency-table.xhtml %}

{% include globals-table.xhtml %}

### Cross-Version Analysis

{% include cross-version-analysis.xhtml %}

### Intellectual Property Statements

{% include ip-statements.xhtml %}
