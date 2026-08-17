<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Mobile sensor data is not a lighter kind of health data. A week of it identifies the
person it came from, whatever the resources say about the subject, and the resources this
guide defines carry the fields that do the identifying. This page states what those
fields expose, what a receiver has to do about it, and how the guide labels resources so
that the obligation travels with the data.

### What is actually in these resources

| Element | What it discloses |
|---|---|
| `component[distanceFromHome]` on a [Visit](StructureDefinition-grove-visit-observation.html) | Metres from the participant's home, alongside a `home`/`work`/`school`/`gym` category and arrival and departure windows. A month of these is a mobility trace: home, workplace, and daily schedule, without a single coordinate. |
| [Device usage](StructureDefinition-grove-device-usage-observation.html) components | Unlock and screen-wake counts per reporting period. Fine-grained periods reconstruct sleep and wake times, work hours, and periods of inactivity. |
| [Wear state](StructureDefinition-grove-wear-state-observation.html) | When the watch is on the wrist, and on which wrist. The denominator for the streams above, and a behavioural signature in its own right. |
| [Sensor batches](StructureDefinition-grove-sensor-batch-document.html) | Raw PPG, ECG, and accelerometer. Gait from accelerometry and cardiac morphology from PPG/ECG are both biometrics; an ECG segment is re-identifiable against a reference recording. |
| `Observation.identifier`, contained `Device` | Record identity and app/OS/hardware fingerprints, both stable across a study. |

"Coordinates are never present" is true and is not de-identification. Treat every resource
in this guide as identifiable personal health data unless a documented process has made it
otherwise.

### Confidentiality and security labels

Resources produced under this guide SHOULD carry `meta.security` with a confidentiality
code from `http://terminology.hl7.org/CodeSystem/v3-Confidentiality` — `R` (restricted) is
the correct default for research sensor data; `V` (very restricted) applies where local
policy says so. Grove's converters do not set it: an on-device converter does not know the
deployment's policy, so the label is applied by whatever assembles the upload, and a
receiver that finds no label SHALL treat the resource as `R` rather than as unlabelled.
Extracts that have been through a de-identification process SHALL carry the method as an
integrity label from
`http://terminology.hl7.org/CodeSystem/v3-ObservationValue` — `PSEUDED` where a key still
links back to the participant, `ANONYED` where no such key is retained, `MASKED` where
values were suppressed rather than transformed. A pseudonymized extract mislabelled as
anonymized is the failure mode these codes exist to prevent, so producers SHALL NOT apply
`ANONYED` while any re-identification key survives anywhere in the deployment.

Purpose-of-use labels (`http://terminology.hl7.org/CodeSystem/v3-ActReason`, e.g.
`HRESCH`) MAY be carried where the receiving system enforces them.

### De-identification is a receiver obligation, and it is not element removal

Removing `subject` does not de-identify these resources; the mobility, usage, and waveform
content is the identifier. A consumer that intends to hold or share a de-identified
extract SHALL define and document the transformation, and at minimum:

- **Coarsen distance-from-home.** Metre precision plus a `home` anchor is a location.
  Bucket it, or drop the component and keep the category.
- **Coarsen timing.** Sub-second `effective[x]` and fifteen-minute usage periods are
  behavioural fingerprints; widen the periods the analysis does not need.
- **Shift dates consistently per participant** rather than truncating them, and see the
  identifier warning below before assuming a shift holds.
- **Decide about waveforms explicitly.** A raw PPG or ECG batch cannot be de-identified by
  metadata removal. Either it stays in the identifiable tier or it does not leave.
- **Strip or coarsen device fingerprints.** Contained `Device` version and model fields
  are near-unique in small cohorts.

Grove's converters perform none of this. They produce identifiable resources by design —
de-identification is a study-design decision, and a framework that guessed it would be
guessing at the disclosure risk.

### The identifier-linkage hazard

SensorKit assigns no record identity, so this guide derives `…/sid/sensorkit-sample-id`
from a digest of the sample's own content ([Identifiers](identifiers.html)). That is what
makes `ifNoneExist` deduplication work, and it has two consequences that a plain content
hash gets wrong:

- **It joins across extracts.** The same sample de-identified independently by two sites
  produces the same identifier at both, so the two extracts can be linked on the
  identifier alone — exactly what independent de-identification is supposed to prevent.
- **It defeats date shifting.** The timestamp is in the digest's preimage, and the rest of
  the preimage is low-entropy (a sensor name, a boolean, a two-valued enum). Given a
  shifted copy that preserves sub-second offsets, an attacker searches the plausible shift
  range and recovers the true timestamp by recomputing the digest.

Producers SHALL therefore key the derivation — HMAC-SHA-256 under a secret held per
deployment (per study, per site) rather than a bare digest. Keying preserves the property
deduplication needs, the identifier being reproducible for the same sample within one
deployment, and destroys the cross-deployment join. The key is a secret: it SHALL NOT
travel with the extract, and rotating it invalidates deduplication, so rotate at study
boundaries. Extracts whose identifiers were derived without a key SHALL be treated as
linkable, and SHALL NOT be represented as anonymized.

HealthKit record identifiers do not have this problem — `HKObject.uuid` is random, and
carries no information about the sample.

### Consent

FHIR consent modelling is out of scope for this guide, which defines no `Consent` profile
and asserts no consent state on the resources themselves. What the guide does assume:

- Collection of every stream here is consented, at study enrolment, in terms a participant
  can act on. "Sensor data" is not such a term; "where you go, when you use your phone,
  and your heartbeat waveform" is.
- The enrolment record lives in the study's own system. Where a deployment carries it in
  FHIR, `Consent` referencing the `ResearchStudy` is the resource for it, and the same
  `ResearchStudy` is referenced from Observations through the HL7 `workflow-researchStudy`
  extension.
- Withdrawal has to reach the data. Record identifiers are per sample, not per person, so
  a deployment SHOULD keep whatever mapping lets it enumerate every resource belonging to
  one participant — subject reference, pseudonym, or both. Withdrawal that cannot be
  executed is not a right.

**SensorKit specifically.** Apple gates these streams behind a research entitlement granted
per study, and the participant authorizes each sensor individually on the device. Recorded
data is held on the device and becomes fetchable only after a delay (24 hours at the time
of writing), during which the participant can delete it; an app never sees data recorded
before authorization. That regime is the participant's control point, and it is upstream
of everything in this guide — a study that ingests SensorKit data has already agreed to
Apple's terms for it, and those terms, not this guide, govern what may be done with the
data afterwards.

### Transport and storage

Uploads SHALL use TLS, and payloads SHALL be encrypted at rest. Sidecar batch files travel
outside the FHIR resources and are as sensitive as the resources that point at them; a
deployment that protects the FHIR endpoint and serves batch payloads from an unauthenticated
bucket has protected nothing. `Attachment.hash` establishes integrity, not
confidentiality — it detects a corrupted or substituted payload, and does not authenticate
one.

Access to this data SHOULD be logged. `AuditEvent` is the FHIR-native way to do it; this
guide profiles neither it nor the server behaviour, and a deployment handling these streams
is expected to have both.
