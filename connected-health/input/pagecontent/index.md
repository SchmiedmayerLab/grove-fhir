<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

The Grove Connected Provider Adapter maps data that an application has already obtained
from Google Health API, Oura, or Withings into international FHIR R4. It does not define
OAuth, permissions, subscriptions, webhooks, polling, fetching, transport, storage, or a
receiving service.

Every normalized Observation declares exactly two direct profiles:

1. the exact source-neutral Grove Mobile measurement profile; and
2. [Connected Health Observation](StructureDefinition-connected-health-observation.html).

The shared profile owns clinical meaning, result shape, unit, and time semantics. The
adapter profile owns provider lineage and deterministic business identity. Inherited
Mobile and core standard profiles are not repeated in `meta.profile`. Provider-native
irregular recordings marked `mapped-standard` declare exactly the source-neutral Grove
Sensor Recording Document and Connected Health Recording Document profiles. The adapter
document preserves provider lineage and exact source/output identity without pretending
that irregular points are uniform. Structured and raw transformations use the same
Connected Health conversion Provenance graph shape.

`catalog/connected-health-adapter.json` is the authoritative v0.2.0 inventory. Every
source type and consumed source element from the reference provider adapters has exactly
one status. The catalog is a closed release contract, not a roadmap.

Continue with [Mapping](mapping.html) and [Implementation](implementation.html). Open
[Artifacts](artifacts.html) for the package surface.
