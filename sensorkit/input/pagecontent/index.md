<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

This package is the FHIR R4 adapter boundary for data **already obtained** from Apple SensorKit.
It adds exact source identity and preserves SensorKit-only semantics while reusing the source-neutral Mobile and Sensor packages for measurements, uniform time series, ECG recordings, and registered Recording Documents.

Readers who are new to FHIR can begin with the Mobile guide's [FHIR basics page](https://grovealliance.org/fhir/mobile/fhir-basics.html).
That page introduces the resources used by these guides, identifiers and references, and the structure of a profile page.

The authoritative Grove FHIR contract inventory contains all 22 streams in the stated Apple `SRSensor` baseline: 20 catalog-baseline symbols and two stable additions.
Every row has one definitive status in [`catalog/sensorkit-adapter.json`](https://grovealliance.org/fhir/catalog/sensorkit-adapter.json). The [device-usage walkthrough](walkthrough.html) demonstrates the required two-resource graph that pairs a structured summary with its complete Recording Document.

This package does not request SensorKit authorization, start collection, query samples, encode native payloads, transmit resources, or define receiver/storage policy.
Those operations belong to the calling application.
Canonical URLs identify artifacts; they do not imply a hosted FHIR endpoint.
Identifiers and hashes establish representation identity and change detection only; they do not grant access, record consent, or make a sensitive native attachment safe to disclose.
