<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

A FHIR canonical URL is an identifier, not a location. Once a URL has been written into
resources that left the device, it can never stop being understood. Grove therefore
treats every canonical it has ever published as permanently valid: readers accept every
historical spelling, newest first; writers write only the current encoding; and
definitions record their history as `identifier` entries with `use: old`.

This version is a **redesign, not a rename**: most concepts moved to FHIR-native
elements or published HL7/SDC extensions rather than receiving new Grove URLs. The
concordance therefore maps old spellings to *encodings*, not merely to URLs. It also
covers spellings minted by Stanford study apps (My Heart Counts) that this guide now
generalizes.

### Concordance

| Historical spelling | Current encoding |
|---|---|
| `https://bdh.stanford.edu/fhir/defs/sourceDevice` | Contained Device via `Observation.device` → [Grove Sensor Device](StructureDefinition-grove-sensor-device.html) |
| `https://bdh.stanford.edu/fhir/defs/sourceRevision` | Contained Device via HL7 `observation-gatewayDevice` → [Grove Gateway Device](StructureDefinition-grove-gateway-device.html) |
| `https://bdh.stanford.edu/fhir/defs/metadata` | [Layered metadata policy](metadata.html); residue in [Platform Metadata](StructureDefinition-grove-platform-metadata.html) |
| `https://bdh.stanford.edu/fhir/defs/absoluteTimeRangeStart` / `…End` | `effective[x]` at full precision (+ HL7 `timezone` extension) — no extension |
| `https://bdh.stanford.edu/fhir/defs/HealthKitSampleID` | `Observation.identifier` with `…/sid/healthkit-sample-id`; passthrough resources use [Source Record Identifier](StructureDefinition-grove-source-record-id.html) |
| `http://bdh.stanford.edu/fhir/StructureDefinition/validationtext`, `http://biodesign.stanford.edu/fhir/StructureDefinition/validationtext` | HL7 `targetConstraint` (`human` carries the message) |
| `http://bdh.stanford.edu/fhir/StructureDefinition/ios-keyboardtype` | SDC `sdc-questionnaire-keyboard` |
| `http://bdh.stanford.edu/fhir/StructureDefinition/ios-textcontenttype` | [autocomplete](StructureDefinition-grove-autocomplete.html) (WHATWG tokens) |
| `http://bdh.stanford.edu/fhir/StructureDefinition/ios-autocapitalizationType` | [autocapitalize](StructureDefinition-grove-autocapitalize.html) (WHATWG values) |
| `http://spezi.stanford.edu/fhir/CodeSystem/questionnaire-item-control` | [Grove Questionnaire Item Control](CodeSystem-grove-questionnaire-item-control.html) |
| `…/questionnaire-item-control/annotate-image/input-image` | SDC `sdc-questionnaire-itemMedia` |
| `…/questionnaire-item-control/annotate-image/region` | [annotate-image region](StructureDefinition-grove-annotate-image-region.html) |
| `https://bdh.stanford.edu/fhir/defs/SensorKit/sourceDevice` | Contained Device via `Observation.device` → [Grove Sensor Device](StructureDefinition-grove-sensor-device.html) |
| `https://bdh.stanford.edu/fhir/defs/SensorKit/DeviceUsage/*` | [Device-Usage Observation](StructureDefinition-grove-device-usage-observation.html) components + [sensor batches](StructureDefinition-grove-sensor-batch-document.html) for per-app detail |
| `https://bdh.stanford.edu/fhir/defs/SensorKit/Visits/*` | [Visit Observation](StructureDefinition-grove-visit-observation.html) components |
| `https://spezi.stanford.edu/fhir/CodeSystem/watch-wrist-location`, `…/watch-crown-orientation` | [Wear-State Observation](StructureDefinition-grove-wear-state-observation.html) coded components ([SensorKit values](CodeSystem-grove-sensorkit-values.html)) |
| `https://mhc.stanford.edu/fhir/defs/sampleUploadTimeZone` | Sample zone: HL7 `timezone` extension on `effective[x]`, written by the converter. The upload's own zone is not re-encoded — arrival time is the server's `meta.lastUpdated` (see [Provenance Model](provenance.html)) |
| `https://myheartcounts.stanford.edu/fhir/defs/studyEnrollment` | HL7 `workflow-researchStudy` extension referencing the `ResearchStudy`; the enrolled revision moves to [Study Definition Revision](StructureDefinition-grove-study-revision.html) |

### Codings: Apple's documentation namespace

Through 0.4.0 the platform codings used Apple's documentation URLs as their system, and
HealthKit enumerations were coded by raw integer. Those are the codings 0.5.0 re-encoded,
so the concordance runs at the code level, not only at the system level.

| Historical coding | Current encoding |
|---|---|
| system `http://developer.apple.com/documentation/healthkit`, code = the sample-type identifier | system `…/platforms/CodeSystem/healthkit-sample-type`, same code |
| system `https://developer.apple.com/documentation/healthkit/<enum type>`, code = the enumeration's raw integer | one system per enumeration under `…/platforms/CodeSystem/`, code = the case name |

The per-enumeration code mapping is the enumeration's own raw-value order: historical `#3`
under `…/healthkit/hkcategoryvaluesleepanalysis` is the fourth case of
`HKCategoryValueSleepAnalysis`. Sleep analysis in full, being the one most often stored:

| 0.4.0 code | 0.5.0 code in `…/CodeSystem/healthkit-category-value-sleep-analysis` |
|---|---|
| `0` | `inBed` |
| `1` | `asleepUnspecified` |
| `2` | `awake` |
| `3` | `asleepCore` |
| `4` | `asleepDeep` |
| `5` | `asleepREM` |

Grove does not rewrite stored resources. A database holding both encodings normalizes the
old one with this table; a consumer that only wants current data filters on
`meta.profile`, which the old resources do not carry.

The HealthKit-shaped draft that briefly existed under
`https://grovealliance.org/fhir/core/StructureDefinition/{sourceDevice,…}` was never
released; those spellings carry no compatibility obligation and are not listed.

Reading rules for the historical spellings (which resources in research databases still
carry) are implemented by the Grove framework's supersession machinery; the old
extensions remain readable indefinitely.
