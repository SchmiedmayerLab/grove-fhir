<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

# Historical canonical spellings

This table records identifiers associated with the legacy HealthKit-shaped prototype.
It is migration evidence, not a promise that every historical spelling is supported by
current or future Grove readers. New resources should not use these URLs.

| Prototype canonical (tail) | Earlier spelling |
|---|---|
| `StructureDefinition/validationText` | `http://bdh.stanford.edu/fhir/StructureDefinition/validationtext` |
| | `http://biodesign.stanford.edu/fhir/StructureDefinition/validationtext` |
| `StructureDefinition/iosKeyboardType` | `http://bdh.stanford.edu/fhir/StructureDefinition/ios-keyboardtype` |
| `StructureDefinition/iosTextContentType` | `http://bdh.stanford.edu/fhir/StructureDefinition/ios-textcontenttype` |
| `StructureDefinition/iosAutocapitalizationType` | `http://bdh.stanford.edu/fhir/StructureDefinition/ios-autocapitalizationType` |
| `StructureDefinition/absoluteTimeRangeStart` | `https://bdh.stanford.edu/fhir/defs/absoluteTimeRangeStart` |
| `StructureDefinition/absoluteTimeRangeEnd` | `https://bdh.stanford.edu/fhir/defs/absoluteTimeRangeEnd` |
| `StructureDefinition/sourceDevice` | `https://bdh.stanford.edu/fhir/defs/sourceDevice` |
| `StructureDefinition/sourceRevision` | `https://bdh.stanford.edu/fhir/defs/sourceRevision` |
| `StructureDefinition/metadata` | `https://bdh.stanford.edu/fhir/defs/metadata` |
| `StructureDefinition/healthKitSampleId` | `https://bdh.stanford.edu/fhir/defs/HealthKitSampleID` |
| `CodeSystem/questionnaire-item-control` | `http://spezi.stanford.edu/fhir/CodeSystem/questionnaire-item-control` |
| `StructureDefinition/annotateImageInputImage` | `http://spezi.stanford.edu/fhir/CodeSystem/questionnaire-item-control/annotate-image/input-image` |
| `StructureDefinition/annotateImageRegion` | `http://spezi.stanford.edu/fhir/CodeSystem/questionnaire-item-control/annotate-image/region` |

The earlier URLs are not served by this guide. A compatibility policy will retain only
spellings supported by evidence from stored resources or downstream consumers.
