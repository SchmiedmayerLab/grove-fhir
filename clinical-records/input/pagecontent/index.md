<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

The Grove FHIR Clinical Records Implementation Guide is the source-neutral layer for provider-issued clinical records and the files that accompany them.
It does not define how an operating-system framework, patient portal, or provider API delivers a record.
An adapter or importer transforms an already obtained record into these R4 resource shapes, so a receiver can find a record, its files, and its FHIR release without knowing which platform sent them.

Readers who are new to FHIR can begin with the Mobile guide's [FHIR basics page](https://grovealliance.org/fhir/mobile/fhir-basics.html).

The package depends only on Grove Mobile, which publishes the [payload format registry](https://grovealliance.org/fhir/mobile/formats.html) and the rules for carrying bytes inline or by immutable URL.
Clinical importers use Mobile and Clinical Records; sensor producers use Mobile and Sensor.

- [Grove Clinical Record Document](StructureDefinition-grove-clinical-record-document.html) byte-preserves one provider-issued FHIR resource, in the FHIR release its producer declares, or one CDA R2 document.
- [Grove Clinical Record Attachment](StructureDefinition-grove-clinical-record-attachment.html) carries one file that accompanies a record, such as a clinical note's PDF, and appends to the record's document in the same exchange Bundle.

[Clinical records and attachments](records.html) states how the two link, and [formats](formats.html) defines the two clinical payload formats.
Platform adapters, such as the HealthKit adapter, derive their own profiles from these two and keep platform identifiers, release detection, and attachment ordering in the adapter.
