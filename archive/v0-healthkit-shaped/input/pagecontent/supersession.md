<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

A FHIR canonical URL is an identifier, not a location. Once an extension URL has been
written into resources that left the device — questionnaires authored elsewhere,
observations uploaded to research databases — it can never stop being understood, even
when the authority behind it changes.

Grove therefore treats every canonical it has ever published as permanently valid:

- **Readers accept every spelling.** Grove reads an extension under its current
  canonical first, then under each superseded spelling, newest first.
- **Writers write the current canonical.** Optionally, consumers can enable
  *dual-write*, which additionally writes each extension under its superseded
  spellings for compatibility with readers that only know the old URLs.
- **Definitions record their history.** Each StructureDefinition in this guide lists
  its superseded spellings as `identifier` entries with `use: old`.

### Mapping

| Current canonical (tail) | Superseded spelling |
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

The pre-Grove annotate-image spellings filed extensions under `CodeSystem` and carried
path separators a FHIR identifier may not contain; both are corrected in the current
canonicals.

The superseded spellings are **not** served by this guide's host. They resolve only in
the sense that every conformant Grove reader accepts them; new content should always
use the current canonicals.
