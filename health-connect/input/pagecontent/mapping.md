<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Select the mapping from the concrete Health Connect Record class. The resulting
Observation follows [Health Connect Observation](StructureDefinition-health-connect-observation.html),
the Mobile envelope, and the profile that defines the clinical result. Preserve source
facts without treating Android class or enum names as clinical terminology.

### Common Record fields

| Health Connect field | FHIR destination | Rule |
|---|---|---|
| `metadata.id` plus repository scope | `Observation.identifier:recordId` | Derive the repository-scoped identifier defined below. Repeat the same complete pair on every output from that Record; never expose the raw platform id. |
| Derived stable output key | `Observation.identifier:outputId` | Required identity of one emitted Observation. Keep it stable across retries and equivalent conversions. |
| `metadata.lastModifiedTime` | `Observation.issued` | Required. It states when this source Record version became available; it is not the clinical effective time. |
| `metadata.recordingMethod` | Mobile `grove-recording-method` extension | Map manual, active, and automatic only when Health Connect states that value. Omit `unknown`. |
| `metadata.device` | `Observation.device` referencing Grove Recording Device | Include only fields supplied by Health Connect. Manufacturer and model are optional; a type alone does not identify a device instance. |
| `metadata.dataOrigin.packageName` | source Device and `Provenance.entity.agent` | Use the Android Package Name identifier namespace. It identifies the application that inserted the Record, not necessarily the physical recorder or converter. |

The Health Connect ID, DataOrigin, and last-modified time are populated by Health Connect
after insertion. A converter must not invent them for an object that has not been read
from the repository. `metadata.lastModifiedTime` is a source timestamp, not a monotonic
revision or synchronization sequence.

`clientRecordId` and `clientRecordVersion` support writes into Health Connect. They are not
the platform-assigned Record identity, a FHIR logical id, or a FHIR version id. A deployment
may retain a client record identifier as another `Observation.identifier` only when it owns
and documents a stable URI namespace for that value. This adapter does not create such a
namespace and does not serialize `clientRecordVersion`.

### Source and output identifiers

Assign each synchronized Health Connect repository a stable, opaque `repository-scope`.
Generate it from at least 128 bits of cryptographically secure randomness; the canonical
lowercase text of a UUID version 4 is the required representation in this version of the
algorithm. Retain it durably with the conversion journal. Do not clone, restore, or reuse
the scope for a different Health Connect repository, and do not put it in a FHIR resource
or wire payload. It is not a secret or an authorization token.

The Health Connect Record Identifier value is `v1:<digest>`, where `<digest>` is the
lowercase hexadecimal SHA-256 digest of this UTF-8 byte sequence:

`record NUL <n-scope>:<repository-scope> NUL <n-type>:<record-type> NUL <n-id>:<metadata.id>`

`NUL` means the single zero byte `0x00`; every `<n-…>` is the UTF-8 byte length of the
exact value that follows it. This scoped digest prevents independent repositories that
happen to issue the same raw `metadata.id` from producing the same FHIR identifier. Use
the stable Record-class tokens `heart-rate`, `weight`, and `steps`; a new supported Record
class receives a new reviewed token. Loss or replacement of the repository scope is an
identity migration: the producer must retire the prior receiver projection before it
publishes identifiers under the replacement scope. It must not silently layer a second
identity set over the same repository.

Derive each Health Connect Output Identifier from the complete source identifier. Encode
that identifier as:

`<n-system>:<system> NUL <n-value>:<record-value>`

Then use `v1:<digest>`, where `<digest>` is the lowercase hexadecimal SHA-256 digest of one
of these UTF-8 byte sequences:

- A Record that maps to one Observation hashes
  `single NUL <n-identifier>:<encoded-source-identifier>`.
- A `HeartRateRecord.Sample` hashes
  `sample NUL <n-identifier>:<encoded-source-identifier> NUL <instant> NUL <beats-per-minute> NUL <occurrence>`.
  Format `<instant>` in UTC with `Z` and exactly nine fractional digits. Serialize beats
  per minute and occurrence as base-10 integers without a sign or leading zeros.
  `<occurrence>` is the zero-based position among samples with the same instant and
  beats-per-minute value.

Sort heart-rate samples by instant, then beats per minute, before assigning occurrence
numbers. Exact duplicates remain distinguishable while insertion of a different sample
does not renumber existing outputs. A source update that changes a sample's time or value
produces a new output identifier; synchronization removes outputs that are no longer in
the converted set. Changes to representation that leave the same logical output in place
retain its output identifier; the converter-contract version belongs in the synchronization
journal, not in the identifier value. A breaking identity-algorithm change requires a full
reconciliation. When only the representation changes, retain the business identifiers and
send a normal complete replacement. When the identity algorithm changes, first deliver and
acknowledge the complete tombstone projection under the old source and output identifiers;
only then publish the new identity set. The two source keys have independent event sequences,
so overlapping them would create duplicate active data. The digest prevents source and
clinical values from appearing directly in identifier indexes and logs. It is not an
access-control or confidentiality boundary: the FHIR resource still carries the clinical
result, and authorized systems may possess the preimage inputs. Do not put either business
identifier in `Resource.id`.

Use these fixed vectors to test the byte encoding. The fixture repository scope is
`1f5c58aa-6ec6-4e79-a682-829a9debd3f5`; it is test input and is never emitted.

| Record type and raw id | Record identifier | Output identifier |
|---|---|---|
| `steps`, `source-record` | `v1:f3ad444267f81a426a6d6b1fde24b59553c5623164226a639f755aca851f414e` | `v1:f8e413af42c5e7a9d04152b38cbf60ec43b24d2831965c0be269a5b7ead16736` |
| `steps`, `héal记录` | `v1:6e258b000caca29d65d79445792030e6aadc81216f8c9c3b73dce2d20299b6a4` | `v1:c1d40e4865981bcda26185ed54bb640b7c449210901153dc327de3131e9104fb` |

The second row proves that every length is a UTF-8 byte length, not a character count.
The two published heart-rate examples exercise the sample form and share one Record
identifier while retaining distinct output identifiers.

### Values and time

| Record class | Required clinical profile and code | FHIR value and effective time |
|---|---|---|
| `HeartRateRecord` | FHIR R4 Heart Rate; LOINC `8867-4` | Emit one Observation per `Sample`: `valueQuantity` in UCUM `/min` and `effectiveDateTime = Sample.time`. The source Record interval is a container for its samples, not a heart-rate result to average. |
| `WeightRecord` | FHIR R4 Body Weight; LOINC `29463-7` | `valueQuantity` in UCUM `kg`; `effectiveDateTime = time`. Do not round the source mass. |
| `StepsRecord` | Grove Mobile Step Count; Grove `step-count-total` | `valueQuantity` in UCUM `{steps}`; `effectivePeriod` uses the exact start and end. The count is an interval total, not a rate or cumulative lifetime counter. |

Each emitted Health Connect Observation has a quantity value. The three supported Record
classes do not supply a missing-result state, so the adapter does not manufacture
`dataAbsentReason`; a `HeartRateRecord` without usable samples produces no active
Observations. Synchronization still records that source event and, when an earlier version
had outputs, sends explicit `entered-in-error` tombstones for every removed Observation.

Preserve source instants and fractional seconds. Serialize `WeightRecord.zoneOffset` on its
effective date-time and the two `StepsRecord` offsets on the corresponding Period endpoints.
A `HeartRateRecord` supplies offsets for its Record start and end, not for each inner Sample;
serialize each `Sample.time` as its UTC Instant unless a sample-specific offset is established
separately. The standard FHIR `timezone` extension requires an IANA zone name, while Health
Connect supplies a numeric `ZoneOffset`. Omit the extension unless a separate authoritative
source supplies the IANA name; never infer one from an offset.

Java and Health Connect can represent offsets and instants that FHIR R4 `dateTime` cannot.
Before serialization, require a whole-minute offset between `-14:00` and `+14:00`, inclusive,
and require every emitted instant to fall in FHIR's four-digit-year range. A value outside
those bounds is a durable conversion rejection; do not round an offset, clamp an instant, or
emit syntactically invalid FHIR.

The supported Health Connect value ranges remain input validation requirements. FHIR
validation does not replace Health Connect's constructor constraints, such as the
heart-rate beats-per-minute range or the positive `StepsRecord.count` range.

### Recording method

| Health Connect metadata | Grove recording method |
|---|---|
| `RECORDING_METHOD_MANUAL_ENTRY` | `manual-entry` |
| `RECORDING_METHOD_ACTIVELY_RECORDED` | `actively-recorded` |
| `RECORDING_METHOD_AUTOMATICALLY_RECORDED` | `automatically-recorded` |
| `RECORDING_METHOD_UNKNOWN` | omit the extension |

Capture mode is not a clinical measurement technique, so it does not populate
`Observation.method`. It also does not identify a responsible person. Populate
`Observation.performer` only when separate source evidence establishes that role.

For active or automatic records, Health Connect requires Device metadata. Represent the
physical recorder as Grove Recording Device, but do not mint a hardware identifier from
manufacturer, model, or device type. `Device.type.text` may preserve a known Health Connect
device-type label without defining a local coding system. Feature-gated extended device
types that Health Connect reports as unknown remain unknown in FHIR.

### Applications and provenance

Represent the converter as a Grove Application Device. Its Android package name identifies
the product; populate the typed application-version slice with one exact converter version
string known to the converter. The app is the top-level `assembler` in
[Health Connect Conversion Provenance](StructureDefinition-health-connect-conversion-provenance.html).

Represent `DataOrigin.packageName` as a Device identifier and link that Device through
`Provenance.entity.agent` with participant type `enterer`. DataOrigin identifies the
application that inserted the source Record into Health Connect. It does not prove that the
application measured the value, that it is the converter, or that it is a gateway. Health
Connect does not expose the source application's version through DataOrigin, so omit that
Device version unless it is established independently. It also does not supply a display
name. Do not invent one or require the source Device to conform to Grove Application Device.
When an exact name is independently available, the same Device may additionally conform to
that Mobile profile.

The Provenance source entity carries the exact Health Connect Record identifier consumed by
the transformation. One Provenance may target all Observations emitted from that Record;
it must not group outputs from different source Record identifiers.

### Study context and terminology notices

Study linkage follows the Mobile guide's
[study model](https://schmiedmayerlab.github.io/grove-fhir/fhir/mobile/study.html): a
versioned PlanDefinition is referenced by ResearchStudy, ResearchSubject links the Patient,
and `workflow-researchStudy` links each Observation. Health Connect synchronization tokens,
permissions, and Android package names are operational facts and do not belong in those
study resources.

The generated tables identify this guide's package dependencies and the notices for
standard terminology used by the examples.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}

Primary Android semantics used by this mapping are documented in the official
[Health Connect data format](https://developer.android.com/health-and-fitness/health-connect/data-format),
[Metadata API](https://developer.android.com/reference/androidx/health/connect/client/records/metadata/Metadata),
[HeartRateRecord API](https://developer.android.com/reference/androidx/health/connect/client/records/HeartRateRecord),
[WeightRecord API](https://developer.android.com/reference/androidx/health/connect/client/records/WeightRecord),
and [StepsRecord API](https://developer.android.com/reference/androidx/health/connect/client/records/StepsRecord).
