<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

### 0.5.0 — 2026-08

A breaking release: pre-1.0 guides are the place to get encodings right rather than
carry mistakes forward.

**Platform vocabularies moved out of Apple's documentation namespace.** HealthKit value
enumerations, sample-type identifiers, metadata keys, and SensorKit sensor streams are
now Grove-owned code systems published by the companion
[platform vocabularies guide](https://grovealliance.org/fhir/platforms). Codes are
Swift case names rather than raw integers (`asleepREM`, not `5`), and each enumeration
has its own system. The HealthKit systems are generated from the framework's source, so
they cannot drift from what it writes. [Supersession](supersession.html) maps the old
systems, and the old integer codes, onto the new ones.

**SensorKit stream codes corrected.** Eight of the eleven published codes were wrong —
`onWrist` is `com.apple.SensorKit.onWristState`, ambient light is `…als`, the ECG
stream is `…ECG`. The real values are now pinned by a test.

**State of mind is fully coded.** Kind, valence classification, labels, and
associations became `valueCodeableConcept` components; valence carries UCUM's unity
code as the dimensionless score it is.

**ECG.** The waveform is one `SampledData` per lead rather than ten-second slices
across repeated components, which carried no ordering or timing semantics. The
sampling period is exact, the no-frequency fallback counts intervals rather than
samples, `Observation.code` leads with MDC and adds LOINC 11524-6, and heart rate
gained MDC 147842.

**Platform metadata changed shape.** Entries used to nest the platform key inside the
extension URL — `…/StructureDefinition/metadata/HKWeatherTemperature`. No
StructureDefinition can define that, and every extension URL has to resolve to one.
Each entry is now its own `grove-platform-metadata` extension with a `key` coding and a
typed `value`. The key codes are HealthKit's **raw** values, which differ from the
Swift constant names for most of the keys Grove handles (`HKMetadataKeyTimeZone` is
`HKTimeZone`) and include one doubled word Apple shipped by mistake; a test pins every
code to what the framework returns.

**Autofill hints became platform-neutral.** `iosTextContentType` and
`iosAutocapitalizationType` are now `grove-autocomplete` and `grove-autocapitalize`,
carrying WHATWG `autocomplete` and `autocapitalize` values. They map onto
`UITextContentType` on Apple platforms and onto autofill hints elsewhere — the
questionnaire no longer names one vendor's API.

**Observations declare their profile** in `meta.profile`, and metadata keys with
first-class homes (time zone, user-entered) no longer duplicate into the metadata
envelope.

**A security and privacy page.** What these streams disclose, the `meta.security` labels
resources carry, what de-identifying mobility and waveform data actually takes, and why a
content-derived SensorKit identifier has to be keyed:
[Security and Privacy](security.html).

### 0.4.0 — 2026-08

The platform-neutral redesign, and the questionnaire renderer's conformance overhaul.

**Data model.** Recording device and saving app became contained Devices
([Sensor Device](StructureDefinition-grove-sensor-device.html) via `Observation.device`,
[Gateway Device](StructureDefinition-grove-gateway-device.html) via the HL7
`observation-gatewayDevice` extension), superseding the string-valued
`sourceDevice`/`sourceRevision` extensions. Record identity moved into
`Observation.identifier` under Grove identifier systems. Timing dropped the epoch-decimal
extensions in favor of full-precision `effective[x]` plus the HL7 `timezone` extension.
Count-valued quantities carry UCUM annotation codes; sleep stages carry parallel LOINC
codes; oxygen saturation, glucose, fiber, VO2max, and walking-distance codings were
corrected or completed; activity metrics carry the `activity` category.

**Sensor streams.** SensorKit wear state, visits, device usage, and raw batches got
first-class profiles and vocabulary — see [Sensor Streams](sensors.html).

**Questionnaires.** The renderer implemented the SDC expression stack
(enableWhenExpression, calculatedExpression, initialExpression + launchContext,
variable, targetConstraint), answer pre-population, translation-based localization,
publication-lifecycle gating, drafts with in-progress export, and the presentation
vocabulary in the [support matrix](questionnaire-support.html). Two invalid-output bugs
in the deprecated ResearchKit path were fixed: skipped questions no longer serialize
empty answer objects, and a missing `Questionnaire.url` no longer fabricates a
canonical.

### Earlier

Concepts now in this guide were previously published under `bdh.stanford.edu`,
`biodesign.stanford.edu`, and `spezi.stanford.edu` URLs, and drafted once in a
HealthKit-shaped form. [Supersession](supersession.html) maps every historical spelling.
