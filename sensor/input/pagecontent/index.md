<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

The Grove FHIR Sensor and Waveform Implementation Guide is the source-neutral layer for uniformly sampled time series, ECG channels, and registered sensor recording payloads.
It does not define how an operating-system framework or provider fetches data.
An adapter transforms already obtained source objects into these R4 resource shapes.

Readers who are new to FHIR can begin with the Mobile guide's [FHIR basics page](https://grovealliance.org/fhir/mobile/fhir-basics.html).
That page introduces the resources used by these guides, identifiers and references, and the structure of a profile page.

The package is source-neutral and uses FHIR R4 `Observation.valueSampledData` for inline numeric sequences and `DocumentReference.content.attachment` for a recording in one registered format.
An admitted attachment must fit the FHIR R4 `Attachment.size` range (0 through 2,147,483,647 bytes before base64 encoding).
Larger payloads are outside this guide's current contract and require a separately specified segmentation protocol.

The HL7 Personal Health Device guide's `PhdRtsaObservation` is the authoritative profile for IEEE 11073 PHD/PHG workflows.
Grove aligns with that package's SampledData representation, but does not impose its mandatory PHD gateway, device, category, and measurement-status assertions on non-PHD phone or wearable sources.
