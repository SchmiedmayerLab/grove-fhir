<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

The Grove HealthKit Adapter maps supported HealthKit objects to FHIR R4 without
turning HealthKit API names into clinical terminology. Each converted Observation
conforms to two independent contracts:

1. [HealthKit Observation](StructureDefinition-healthkit-observation.html) carries the
   source-object identity and the small allowlist of HealthKit context retained by this
   adapter.
2. A clinical or research profile defines what the result means and which units are
   valid.

Both profile canonicals appear in `Observation.meta.profile`, and the resource must
validate against both.

### Start with an example

| HealthKit record | Clinical representation | Example |
|---|---|---|
| Heart rate quantity | FHIR R4 Heart Rate; LOINC `8867-4`; UCUM `/min` | [Heart rate](Observation-HealthKitHeartRateObservationExample.html) |
| Step count quantity | Grove Mobile Step Count; Grove `step-count-total`; UCUM `{steps}` over an exact Period | [Step count](Observation-HealthKitStepCountObservationExample.html) |
| Body mass flagged as user-entered | FHIR R4 Body Weight; LOINC `29463-7`; UCUM `kg` | [Body weight](Observation-HealthKitManuallyEnteredBodyWeightExample.html) |

The [study exchange Bundle](Bundle-HealthKitStudyBundleExample.html) puts the participant,
versioned protocol, study enrollment, devices, Observation, and Provenance together.
Its [JSON representation](Bundle-HealthKitStudyBundleExample.json) is a complete fixture
for an importer.

### What the adapter adds

- [HealthKit Observation](StructureDefinition-healthkit-observation.html) requires one
  identifier in the `HKObject.uuid` namespace.
- [HealthKit Object Identifier](NamingSystem-healthkit-object-id.html) defines that
  namespace using the NamingSystem canonical as the identifier-system URI. Values are
  normalized to lowercase hyphenated UUID text.
- [Apple Bundle Identifier](NamingSystem-apple-bundle-id.html) defines the application
  identifier namespace.
- [HealthKit Source Device Identifier](NamingSystem-healthkit-source-device-id.html)
  defines the privacy-sensitive namespace used only when HealthKit reports a supported
  Bluetooth Low Energy source as a device UUID. Application sources use the Apple Bundle
  Identifier namespace.
- The optional `heartRateMotionContext` component preserves one allowlisted HealthKit
  metadata value. An invariant permits it only on LOINC `8867-4` heart-rate records.

The HealthKit sample type selects the mapping profile and is retained as one additional
adapter-lineage coding beside the normative shared or standard clinical coding.

Continue with [Mapping](mapping.html) for field-by-field rules, or open
[Artifacts](artifacts.html) for every profile, naming system, terminology resource, and
example in the package. [Terminology provenance](terminology-provenance.html) records
the SDK baseline, selection method, source-file hashes, ownership, and publication scope
for the HealthKit names retained by version 0.2.0.
