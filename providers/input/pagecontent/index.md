<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

The Grove Connected Provider Adapter maps data that an application has already obtained from Google Health API, Oura, or Withings into FHIR R4.
It does not define OAuth, permissions, subscriptions, webhooks, polling, fetching, transport, storage, or a receiving service.

Readers who are new to FHIR can begin with the Mobile guide's [FHIR basics page](https://grovealliance.org/fhir/mobile/fhir-basics.html).
That page introduces the resources used by these guides, identifiers and references, and the structure of a profile page.

Every normalized Observation declares exactly two direct profiles:

1. the exact semantic measurement profile: a shared Grove Mobile profile when the meaning is genuinely shared, or a provider-owned profile when it is not; and
2. the exact provider envelope for the source (Google Health, Oura, or Withings), which specializes [Provider Observation](StructureDefinition-providers-observation.html).

The semantic profile owns clinical meaning, result shape, unit, and time semantics.
The adapter profile owns provider lineage and deterministic business identity.
Provider Observation is an abstract common parent; concrete Observations and examples live in the Google Health, Oura, or Withings package that owns the exact provider envelope.
Inherited Mobile and core standard profiles are not repeated in `meta.profile`; the semantic and adapter claims are both explicit and are never inferred from each other.
Provider-native irregular recordings marked `mapped-standard` declare exactly the source-neutral Grove Sensor Recording Document and Provider Recording Document profiles.
The adapter document preserves provider lineage and exact source/output identity without pretending that irregular points are uniform.
Structured and raw transformations use the same Provider conversion Provenance graph shape.

### Responsibility boundaries

One adapter guide serves every connected provider because the providers share one profile shape: one Provider Observation profile, one identity scheme, and one raw-payload admission rule, with only the source vocabulary differing per provider.
This guide owns that shared shape, the provider and source-type terminology, the identifier namespaces, and the complete source inventory.
Represent an additional connected provider in this shared catalog when it uses the common Provider Observation, identity, and raw-payload contracts.

A measurement only one connected provider reports is not source-neutral, so its semantic profile is published by that provider's own guide: [Withings](https://grovealliance.org/fhir/withings), [Oura](https://grovealliance.org/fhir/oura), or [Google Health](https://grovealliance.org/fhir/google-health). The emitted resource still carries that profile together with its provider envelope.
Each of those guides narrows Provider Observation to one vendor and carries only what no other source reports.
A vendor score is not comparable across vendors even when two vendors give it the same name, so publishing it here under a shared code would assert a comparability that does not exist.

Use a separate adapter when a source requires distinct evidence rules, identity, or FHIR resource structures, as HealthKit, SensorKit, and Health Connect do.
The adapter boundary follows the source API contract rather than the vendor: one company may expose several APIs, each governed by the adapter contract for that source.

[`catalog/providers-adapter.json`](https://grovealliance.org/fhir/catalog/providers-adapter.json) is the authoritative Grove FHIR contract inventory.
Every source type and consumed source element from the exhaustive provider source catalogs has exactly one status.
Each published status is normative for producer behavior.

The [Withings walkthrough](walkthrough.html) traces one grouped blood-pressure measure group from provider JSON to the emitted FHIR graph.

Continue with [Mapping](mapping.html) and [Implementation](implementation.html).
Open [Artifacts](artifacts.html) for the package surface.
