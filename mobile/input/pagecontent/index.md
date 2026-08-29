<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Grove Mobile defines a reusable FHIR R4 exchange contract for measurements collected by mobile applications and connected devices.
Clinical meaning stays in standard FHIR fields and established domain profiles.
Grove profiles make record identity, capture mode, device roles, conversion provenance, and research-study context consistent across source platforms.

The Grove FHIR Implementation Guides form a family of ten guide packages. The [guide family page](guides.html) maps their responsibilities, catalogs, and shared status vocabulary.

Readers who are new to FHIR can begin with [FHIR basics](fhir-basics.html).
That page introduces the core resources used by these guides, distinguishes resource IDs from business identifiers, and explains how to read a profile page.

### Choose a starting point

| Goal | Read | Working example |
|---|---|---|
| Understand FHIR well enough to read this guide | [New to FHIR](fhir-basics.html) | [Heart-rate JSON](Observation-GroveMobileHeartRateExample.json) |
| Encode or consume a measurement | [Observations](observations.html) | [Heart rate](Observation-GroveMobileHeartRateExample.html) |
| Exchange a complete resource graph | [Observations](observations.html#exchange-graph) | [Collection Bundle](Bundle-GroveMobileExchangeBundleExample.html) |
| Distinguish the sensor from the app | [Devices and provenance](devices.html) | [Conversion provenance](Provenance-GroveMobileConversionProvenanceExample.html) |
| Connect data to a study revision | [Study context](study.html) | [Study protocol](PlanDefinition-GroveMobileStudyPlanExample.html) |
| Add the package and validate JSON | [Implement and validate](implementation.html) | [Heart-rate JSON](Observation-GroveMobileHeartRateExample.json) |

### The exchange model

The collection Bundle is the exchange unit.
Its Observation entries are the clinical records; other entries describe the context needed to interpret and audit them.

```text
Patient <--------- Observation ---------> recording Device
                       |
                       +-----------------> application Device
                       |                   (only when a gateway)
                       +-----------------> ResearchStudy
                       |
Provenance ------------+-----------------> source record identifier
     |
     +-----------------------------------> application Device
                                            (assembler)
```

- [Grove Mobile Observation](StructureDefinition-grove-mobile-observation.html) defines the source-neutral exchange envelope.
  A resource also declares an authoritative clinical profile such as FHIR R4 Heart Rate or Body Weight.
- [Grove Mobile Step Count](StructureDefinition-grove-mobile-step-count.html) supplies a precise interval-count definition where FHIR R4 has no mature core profile.
- [Grove Recording Device](StructureDefinition-grove-recording-device.html) represents the physical recorder when it is known.
- [Grove Application Device](StructureDefinition-grove-application-device.html) represents the software that saved or converted the record.
- [Grove Mobile Conversion Provenance](StructureDefinition-grove-mobile-conversion-provenance.html) records which application assembled the FHIR resource from its source.

Source-platform identifiers and metadata belong to adapter packages.
An adapter derives its Observation profile from the Mobile envelope, defines its own identifier systems, and permits only source fields with a documented mapping.
This keeps the shared contract independent of any mobile operating system or vendor API.

### Reading profile pages

The **Differential Table** on a profile page shows the rules added by this guide.
The **Snapshot Table** includes all inherited FHIR R4 rules.
Examples provide XML, JSON, and Turtle representations; the JSON representation is generally the most direct reference for application development.

Start with the [heart-rate JSON](Observation-GroveMobileHeartRateExample.json), then compare it with the [Mobile envelope](StructureDefinition-grove-mobile-observation.html) and the [FHIR R4 Heart Rate profile](https://hl7.org/fhir/R4/heartrate.html).

Every profile carries an example.
Worked examples show measurements in the context emitted by a producer, including the associated device, study, and platform metadata.
The remaining examples demonstrate the minimum content required by their profiles.
They are conformance references rather than templates for richly populated records.
