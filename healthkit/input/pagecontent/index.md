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

New to FHIR?
[Start with the FHIR basics page](https://grovealliance.org/fhir/mobile/fhir-basics.html) in the Mobile guide.
It covers the resources these guides use, identifiers and references, and how to read a profile page.

Both profile canonicals appear in `Observation.meta.profile`, and the resource must
validate against both.

### Start with an example

| HealthKit record | Clinical representation | Example |
|---|---|---|
| Heart rate quantity | FHIR R4 Heart Rate; LOINC `8867-4`; UCUM `/min` | [Heart rate](Observation-HealthKitHeartRateObservationExample.html) |
| Step count quantity | Grove Mobile Step Count; Grove `step-count-total`; UCUM `{steps}` over an exact Period | [Step count](Observation-HealthKitStepCountObservationExample.html) |
| Body mass flagged as user-entered | FHIR R4 Body Weight; LOINC `29463-7`; UCUM `kg` | [Body weight](Observation-HealthKitManuallyEnteredBodyWeightExample.html) |

The [study documentation Bundle](Bundle-HealthKitStudyBundleExample.html) puts the participant,
versioned protocol, study enrollment, devices, Observation, and Provenance together.
Its [JSON representation](Bundle-HealthKitStudyBundleExample.json) is a complete fixture
for human inspection; it is not an operational exchange unit. The
[walkthrough](walkthrough.html) follows one heart-rate sample from `HKQuantitySample` to
the profiled one-source-record exchange event.

### What the adapter adds

- [HealthKit Observation](StructureDefinition-healthkit-observation.html) requires typed
  deployment-scoped v2 source-record and source-output HMAC identifiers. A deployment may also
  disclose `HKObject.uuid` on the one-to-one primary output under an explicit, governed absolute
  HealthKit-store namespace when native round-trip is required; it never replaces Grove identity.
- [HealthKit Application Device](StructureDefinition-healthkit-application-device.html)
  carries exactly one typed [Apple Bundle Identifier](NamingSystem-apple-bundle-id.html)
  in addition to the shared opaque event snapshot. The bundle namespace identifies an
  application product; it does not identify an installation, host, account, or person.
- A physical source Device is emitted only with a governed stable per-unit token and the
  shared `recording-device` plus `device-snapshot` identities. Any deliberate disclosure of a
  HealthKit source UUID uses its own governed Identifier namespace and deployment purpose;
  descriptive source metadata alone is not physical-device identity.
- The optional `heartRateMotionContext` component preserves one allowlisted HealthKit
  metadata value. An invariant permits it only on LOINC `8867-4` heart-rate records.

The HealthKit sample type selects the mapping profile and is retained in the dedicated
source-type lineage extension. It is not asserted as an equivalent coding beside the normative
shared or standard clinical concept.

Continue with [Mapping](mapping.html) for field-by-field rules, or open
[Artifacts](artifacts.html) for every profile, naming system, terminology resource, and
example in the package. [Terminology provenance](terminology-provenance.html) records
the SDK baseline, selection method, source-file hashes, ownership, and publication scope
for the HealthKit names retained by version 0.6.0.
