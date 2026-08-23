<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

The Grove Connected Provider Adapter maps data that an application has already obtained
from Google Health API, Oura, or Withings into international FHIR R4. It does not define
OAuth, permissions, subscriptions, webhooks, polling, fetching, transport, storage, or a
receiving service.

New to FHIR?
[Start with the FHIR basics page](https://grovealliance.org/fhir/mobile/fhir-basics.html) in the Mobile guide.
It covers the resources these guides use, identifiers and references, and how to read a profile page.

Every normalized Observation declares exactly two direct profiles:

1. the exact source-neutral Grove Mobile measurement profile; and
2. [Provider Observation](StructureDefinition-provider-observation.html).

The shared profile owns clinical meaning, result shape, unit, and time semantics. The
adapter profile owns provider lineage and deterministic business identity. Inherited
Mobile and core standard profiles are not repeated in `meta.profile`. Provider-native
irregular recordings marked `mapped-standard` declare exactly the source-neutral Grove
Sensor Recording Document and Provider Recording Document profiles. The adapter
document preserves provider lineage and exact source/output identity without pretending
that irregular points are uniform. Structured and raw transformations use the same
Provider conversion Provenance graph shape.

### When a source becomes its own adapter

One adapter guide serves every connected provider because the providers share one profile shape: one Provider Observation profile, one identity scheme, and one raw-payload admission rule, with only the source vocabulary differing per provider.
A new provider therefore lands as a section of [`catalog/providers-adapter.json`](https://grovealliance.org/fhir/catalog/providers-adapter.json) by default.
A source graduates to its own adapter guide only when its profile shape genuinely diverges — its own evidence rules, identity contract, or resource structure — which is why HealthKit, SensorKit, and Health Connect are separate adapters and Google Health API, Oura, and Withings are not.
The vendor is never the axis: the same company can ship data through several source APIs, and each API follows the contract of the adapter it arrives through.

[`catalog/providers-adapter.json`](https://grovealliance.org/fhir/catalog/providers-adapter.json) is the authoritative v0.3.0 inventory.
Every source type and consumed source element from the closed provider source catalogs has exactly one status.
The catalog is a closed release contract, not a roadmap.

The [Withings walkthrough](walkthrough.html) traces one grouped blood-pressure measure group from provider JSON to the emitted FHIR graph.

Continue with [Mapping](mapping.html) and [Implementation](implementation.html). Open
[Artifacts](artifacts.html) for the package surface.
