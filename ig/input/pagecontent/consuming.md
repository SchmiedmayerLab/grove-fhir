<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

This page is for anyone **receiving** data a Grove app produces — research data
platforms, analysts, downstream services. Everything Grove writes is plain FHIR R4; the
profiles in this guide are the contract for what you will find where.

### Validate what you receive

The guide ships as a standard FHIR NPM package. To validate a resource (or a whole
export) against the contract:

```
java -jar validator_cli.jar your-data.json -version 4.0.1 \
  -ig package.tgz -ig platforms-package.tgz
```

**Both packages are needed, and neither is on a registry yet.** This guide depends on
`org.grovealliance.fhir.platforms` for the HealthKit and SensorKit codings, and package
dependencies resolve from registries the validator can reach — so pointing at this
guide's `package.tgz` alone leaves the platform code systems unresolvable. Download
[this site's `package.tgz`](package.tgz) and the
[platform guide's](https://grovealliance.org/fhir/platforms/package.tgz), and pass both.
When the packages reach a registry, `-ig org.grovealliance.fhir.core` will resolve the
dependency by itself and one flag will do.

Observations declare their profile in `meta.profile`
(`https://grovealliance.org/fhir/core/StructureDefinition/grove-mobile-sensor-observation`),
so profile-aware validators and stores pick the contract up automatically.

### What you will receive

| You get | Where to look |
|---|---|
| The measurement | `code` (LOINC/SNOMED + platform coding), `value[x]`, `category` |
| When, precisely | `effective[x]` (fractional seconds preserved; named zone in the `timezone` extension) |
| Which hardware measured it | `device` → contained [Grove Sensor Device](StructureDefinition-grove-sensor-device.html) |
| Which app saved it | `observation-gatewayDevice` extension → contained [Grove Gateway Device](StructureDefinition-grove-gateway-device.html) |
| Sensed vs user-entered | [Recording Method](StructureDefinition-grove-recording-method.html) extension |
| The platform record id | `identifier` with a [Grove system](identifiers.html) — your deduplication key |
| Everything else the platform attached | [Platform Metadata](StructureDefinition-grove-platform-metadata.html) entries (see [Metadata Policy](metadata.html)) |

Questionnaire answers arrive as standard `QuestionnaireResponse` resources; annotated-image
answers are attachment answers (PNG) on the item whose control is `annotate-image`
(see the [example response](QuestionnaireResponse-GroveQuestionnaireResponseExample.html)).

Worked examples of the observation shapes: a
[chest-strap heart rate](Observation-GroveHeartRateObservationExample.html), a
[phone-recorded step count](Observation-GroveStepCountObservationExample.html), a
[sleep stage](Observation-GroveSleepObservationExample.html), and a
[wear-state observation](Observation-GroveWearStateObservationExample.html) from a
passive sensor stream. The matching
[Health Connect step count](Observation-GroveHealthConnectStepCountExample.html) shows the
Android record-id, sensor-device, gateway-app, and platform-code slices on the same wire format.
The BLE identifier slice is specified and Must Support, but no example instantiates it yet.

The offset on `effective[x]` is the recording device's when the platform recorded one,
and the converting machine's when it did not — so an offset alone does not tell you
where the participant was. The `timezone` extension is the discriminator: present means
the zone is the sample's own, absent means the offset is incidental and only the instant
is meaningful. Batch conversions run on a desktop are the case to watch.

### Before you store it

Everything on this page is identifiable personal health data, and the sensor streams are
identifiable regardless of what `subject` says. Read
[Security and Privacy](security.html) before an extract leaves your system: it states the
confidentiality labels resources carry, what de-identifying these streams actually
requires, and why a content-derived identifier has to be keyed.

### Deduplication

Treat `(identifier.system, identifier.value)` as the platform record identity; the
mechanics — conditional create, server responses, passthrough records — live on the
[Identifiers](identifiers.html) page. Mobile platforms can re-deliver samples, so
receiving a duplicate identifier is normal, not an error.

### Reading historical data

Research databases contain resources written by earlier Grove/Spezi versions. Their
encodings remain valid forever; the [Supersession](supersession.html) page maps every
historical spelling (`bdh.stanford.edu`, `spezi.stanford.edu` extensions, epoch-decimal
time extensions, extension-based sample ids) to its current equivalent. A consumer that
wants one code path can normalize old resources using that concordance; a consumer that
only reads current-profile data can filter on `meta.profile`.
