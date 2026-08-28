<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Grove FHIR Sensor and Waveform 0.6.0 is the source-neutral layer for uniformly
sampled time series, ECG channels, and native sensor recordings. It does not define
how an operating-system framework or provider fetches data. An adapter transforms
already obtained source objects into these R4 resource shapes.

New to FHIR?
[Start with the FHIR basics page](https://grovealliance.org/fhir/mobile/fhir-basics.html) in the Mobile guide.
It covers the resources these guides use, identifiers and references, and how to read a profile page.

The package is international and uses FHIR R4 `Observation.valueSampledData` for
inline numeric sequences and `DocumentReference.content.attachment` for a native or
externally encoded recording. An admitted attachment must fit the exact FHIR R4
`Attachment.size` unsigned-integer range (0 through 2,147,483,647 pre-base64 bytes);
larger payloads require a future segmented-manifest contract rather than an implicit
receiver-specific exception.

The HL7 Personal Health Device guide's `PhdRtsaObservation` is the authoritative
profile for IEEE 11073 PHD/PHG workflows. Grove aligns with that package's
SampledData representation, but does not impose its mandatory PHD gateway, device,
category, and measurement-status assertions on non-PHD phone or wearable sources.
