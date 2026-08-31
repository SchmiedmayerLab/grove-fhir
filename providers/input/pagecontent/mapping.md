<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Provider conversion begins with an exact source element in the published adapter contract.
Its status determines whether the element admits a shared Observation, a provider-specific Observation, a Recording Document, or no output.

### What each status admits here

The normative status-vocabulary definitions live on the [guide family page](https://grovealliance.org/fhir/mobile/guides.html#status-vocabulary) and mean the same thing in every guide.
What follows is only what admission produces for a provider element.

`supported` rows may produce the exact listed shared or provider-owned semantic Observation.
A `platform-exclusive` row produces the provider-owned semantic profile its catalog entry names, which states the vendor and exact nature of the value so nothing reads as a comparable shared measurement.
Every such Observation directly claims that semantic profile together with the reporting provider's exact adapter envelope; neither profile substitutes for the other. `mapped-standard` rows may produce only the listed two-profile Recording Document contract.
The other statuses do not authorize a FHIR output under this adapter profile.

Important fail-closed boundaries include:

- Google Health `blood-glucose` does not supply the specimen evidence needed to select one of the four Health Connect-only specimen-specific glucose profiles.
- daily and sleep-session averages are not relabeled as point-in-time vital signs.
- sleep-stage duration summaries are not relabeled as stage intervals when the source does not provide their boundaries.
- proprietary vendor scores are carried only under provider-scoped profiles that name the vendor.
  Withings vascular age and Oura cardiovascular age are separate measurements, because they are undisclosed algorithms over different inputs and are not comparable.
- a Withings atrial-fibrillation screening result is carried as a notification and never as a rhythm finding, on the same basis as the HealthKit irregular-heart-rhythm notification.
- Withings body-segment fat and muscle masses stay refused: the consumed shape does not recover which segment a value belongs to.
- Withings systolic and diastolic values become one blood-pressure panel only when both occur in the same provider measure group.

See [`catalog/providers-adapter.json`](https://grovealliance.org/fhir/catalog/providers-adapter.json) for every exact source token, element, unit conversion, grouping rule, semantic profile, and definitive status.
The [authoritative status matrix](status-matrix.html) lists every provider field and the atomic Withings grouped mapping in that contract.
The [Withings walkthrough](walkthrough.html) shows the grouped blood-pressure mapping end to end, from measure-group JSON to the emitted exchange Bundle.
