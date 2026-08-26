<!--

This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

-->

# Findings for the Next Breaking Change

A review of the seven guides, the four adapter catalogs, and the three implementations that consume them, written after the 0.5.0 release.
Every item states what was checked and how, so a reader can disagree with the conclusion rather than only with the summary.

The guides currently publish 242 profiles, 22 extensions, and 337 examples across mobile, sensor, sensorkit, healthkit, health-connect, providers, and questionnaire.

## Conversion completeness

The lossless rule is that a conversion never drops what the source provided.
Three findings break it, and one of them is currently reported as complete.

### Workout conversion is partial but declared `supported`

`HKWorkoutTypeIdentifier` is `supported` in the HealthKit status matrix, and the converter carries the session totals: active duration, distance, active energy, step count, flights climbed, swimming strokes, and average heart rate.

It does not carry `HKWorkout.workoutEvents` — the laps, pauses, resumes, and segments that describe the shape of the session — and it does not carry `workoutActivities`, the per-activity breakdown of a multi-sport workout.
A triathlon converts to one undifferentiated Observation.

This is worse than a gap, because the status matrix asserts otherwise.
Either the events and activities are modelled, or the row states what it omits.

`distanceType(for:)` is a good counterexample within the same file: it selects the distance type the activity actually records, precisely so that cycling, swimming, wheelchair, and snow-sport distances are not dropped.
The same care has not been applied to events.

### Unrecognised HealthKit metadata is dropped

The converter reads `sample.metadata` only through specific known keys — sync identifier, sync version, time zone, was-user-entered, sexual-activity protection, ECG algorithm version, menstrual cycle start.
No code path iterates the dictionary, and the IG defines no extension for retaining what is not modelled.

`HKSample.metadata` is an open dictionary.
Any key a third-party writer sets, and any key Apple adds in a future SDK, is silently discarded.

The adapter is careful in the adjacent case: `@unknown default` appears 3 times in the HealthKit converter and 5 times in SensorKit, and **every one of them throws** rather than substituting a default.
Unknown *enumeration cases* fail closed; unknown *metadata keys* vanish. The asymmetry looks unintended.

A `healthkit-retained-metadata` extension carrying unmodelled key/value pairs would close it.

### Application build number is concatenated into a version string

`HealthKitApplication.main` composes `version` as `"4.2.1 (123)"` from `CFBundleShortVersionString` and `CFBundleVersion`.
The build number is therefore present but not separately addressable: a consumer must parse a parenthesis convention to recover it, and no profile documents that convention.

This is the subject of the `Device.version` proposal below.

## Proposal: coded `Device.version` entries

Grove already emits the producing application as a `Device` on the `GroveApplicationDevice` profile, carrying the bundle identifier, the display name, and a `version` coded with MDC `531975` (`MDC_ID_PROD_SPEC_SW`).
`Device.version` is a list of `DeviceVersion`, each with its own `type` CodeableConcept, so more than one revision can be carried without inventing an extension.

Add a `GroveApplicationVersionType` code system with three codes, and emit one `Device.version` entry per code:

| Code | Meaning | Source |
|---|---|---|
| `marketing-version` | The human-facing release, e.g. `4.2.1` | `CFBundleShortVersionString` |
| `build` | The build that produced the resource, e.g. `123` | `CFBundleVersion` |
| `os-version` | The operating system the conversion ran on | `ProcessInfo.operatingSystemVersion` |

Keep MDC `531975` on the marketing version so existing consumers are unaffected, and stop concatenating build into it.

This is the right shape for three reasons.
It removes a parsing convention that was never specified.
It gives every Grove producer the same three fields rather than each app minting its own extension.
And it is additive to a profile that already exists, so it costs one code system and no new extension.

Grove must also expose the application-`Device` builder publicly.
It is currently internal to `GroveSensorKitFHIR`, which is why an app that authors its own resources cannot reuse it — see the duplication finding below.

## Duplication in the implementations

My Heart Counts defines three FHIR extensions.
All three restate something the guides already model, but only on the paths the guides cover.

| Extension | Status |
|---|---|
| `…/StructureDefinition/study-enrollment` | Duplicate. The standard `workflow-researchStudy` element carries the study reference. Only `studyRevision` is not covered. |
| `…/core/sampleUploadTimeZone` | Not a duplicate, but questionable. It records the zone at upload; the IG uses HL7's `timezone` extension for the zone the observation happened in, which is the analytically meaningful one. |
| `…/core/mhcAppRevision` | Duplicate of the application `Device`, in a worse form. Carries version, build, bundle identifier, and OS version; the `Device` carries version and identifier today, and would carry all four under the proposal above. |

The removal is blocked on the proposal, not on the app.
Four paths — clinical-record passthrough, manually entered quantity samples, timed-walk results, and questionnaire responses — are authored by the app rather than converted by Grove, and the extensions are their only provenance.
Deleting them before Grove exposes a public application-`Device` builder would lose data rather than deduplicate it.

Order: publish the code system, expose the builder, wire the app-authored paths to it, then delete all three.

## Identity derivation is duplicated and inconsistent

`SensorKitSourceRecordID.derived(fromPayload:sourceToken:deviceDescriptor:)` exists precisely so producers agree.
Its own documentation says so: *"Two producers that derive it this way agree; two that each invented a scheme do not."*

My Heart Counts invented two anyway — an `Insecure.SHA1` digest for raw streams, and a bespoke XOR-based 128-bit hasher for structured samples.
Neither agrees with Grove's SHA-256 derivation, so the same recording uploaded by two producers yields two records.

Grove covers the payload case but has no field-based derivation for structured samples that carry no payload bytes, which is why the app wrote one.
Adding `derived(fromFields:)` to Grove would let both schemes be deleted.

Two defects found in the app's own scheme while reviewing it, now fixed, are the argument for centralising it:
the device-usage identity hashed only the *counts* of its three usage breakdowns, so two reports differing inside them collided — and the id also names the sidecar file, so the second upload overwrote the first;
and the same report encoded to different bytes on different runs, because the breakdowns were walked in dictionary order.

## Deferred and refused source types

These are documented decisions rather than defects, listed so the next release can revisit them deliberately.

HealthKit defers 10 and refuses 4 of 218 types.
The deferrals with the clearest analytic value are `HKWorkoutRouteTypeIdentifier`, `HKDataTypeIdentifierHeartbeatSeries`, `HKDataTypeIdentifierAudiogram`, and `HKCorrelationTypeIdentifierFood`.
`HKCharacteristicTypeIdentifierDateOfBirth` and `…BiologicalSex` are deferred but are ordinary `Patient` elements rather than Observations, so they need a decision about whether Grove writes demographics at all.
`HKDocumentTypeIdentifierCDA` and `HKVisionPrescriptionTypeIdentifier` are whole documents, closer to the clinical-record passthrough than to a measurement.

SensorKit defers 1 of 22: `SRSensor.acousticSettings`.

Health Connect defers 1 of 41: `PlannedExerciseSessionRecord`, correctly — a planned session states future intent, not an observed measurement, and belongs to a workflow resource rather than a measurement contract.

## Leftovers removed in this pass

Stale `0.3.0` package pins survived two releases in the installation documentation of four guides.
The version-prose guard did not catch them because its expression matched only `v0.3.0` and `version 0.3.0`, never `org.grovealliance.fhir.mobile#0.3.0` — which is exactly how a pin is written in an installation instruction.
The expression now covers the package-pin form, and found them immediately.

One match was a false positive worth recording: `healthkit/input/pagecontent/terminology-provenance.md` names `0.3.0` as the release the terminology was extracted against, alongside the SDK baseline and extraction date.
That is a historical record, and bumping it would falsify the provenance it exists to keep.
It is exempted by name rather than by pattern, so the exemption cannot silently widen.

## Smaller observations

The `sensor` guide carries 4 profiles and no extensions, and is the only guide whose format registry is fully generated.
It is the model the other adapter guides should move toward: `sensorkit` still hand-maintains 4 extensions, and `healthkit` 9.

`health-connect` and `providers` express their catalogs under different top-level keys than `healthkit` and `sensorkit` (`recordTypes` and `providers` versus `rows` and `entries`).
Nothing is wrong with the data, but a reader or script has to learn four shapes to answer one question.
A shared `sourceTypes` key would let the status audit above run as one query rather than four.
