<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

A shared HealthKit Observation directly claims the generic HealthKit adapter profile and the one Mobile or standard profile that defines the result.
A HealthKit-specific child Observation directly claims only that exact child; inherited profiles are not repeated.
The ECG hybrid directly claims the Sensor ECG and HealthKit ECG profiles.
Native recording, clinical-record, vision-prescription, medication-dose, and tracked-medication outputs use the exact direct claim modes published in `catalog/profile-claims.json`.
Install Mobile, Sensor, and HealthKit and validate every direct profile together.

### Download the packages

The packages are not published in a FHIR package registry, and the canonical namespace is deliberately not a package host.
Each published guide exposes its archive and checksum from its [Artifacts page](artifacts.html); download this guide's `package.tgz` and `package.tgz.sha256` there, plus the Mobile and Sensor guide pairs from their Artifacts pages, then verify all three checksums:

```sh
(cd grove-packages/mobile && shasum -a 256 --check package.tgz.sha256)
(cd grove-packages/sensor && shasum -a 256 --check package.tgz.sha256)
(cd grove-packages/healthkit && shasum -a 256 --check package.tgz.sha256)
```

To use the profiles from FHIR Shorthand, unpack all three archives into the standard FHIR package cache and declare the `org.grovealliance.fhir.healthkit` package at the exact version in `catalog/release-manifest.json`.
The HealthKit package already declares its exact Mobile and Sensor dependencies.
Move aside each exact cache directory before extracting an update; never overlay a new archive on an older copy.
Use the same manifest version for the package-cache directory and the FHIR Shorthand dependency.

### Validate an Observation

Pass all three local package archives to the official FHIR Validator.
Add the exact direct HealthKit and result profiles.
For a heart-rate Observation:

```sh
java -jar validator_cli.jar observation.json \
  -version 4.0.1 \
  -ig grove-packages/mobile/package.tgz \
  -ig grove-packages/sensor/package.tgz \
  -ig grove-packages/healthkit/package.tgz \
  -profile https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-observation \
  -profile https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-heart-rate
```

Validation checks the resource shape, identifier format, terminology bindings, profile intersection, and inherited Mobile/Sensor rules.
The structural producer gate additionally binds the exact source-type coding to its one per-resource direct claim and requires one HealthKit conversion Provenance to target every output for the source record.
Neither layer can prove that a HealthKit sample type was mapped to the correct clinical profile, that an attributed Device performed the claimed role, or that disclosing a source identifier is authorized.
Verify those adapter semantics and disclosure decisions against representative source records.

Start with the [heart-rate JSON](Observation-HealthKitHeartRateObservationExample.json), then compare it with the field-by-field [mapping rules](mapping.html).

### Retracting a source record

When HealthKit reports a deleted source object, emit the dedicated Grove Mobile Retraction Bundle.
Its sole source-record-retracted Provenance identifies the exact prior output graph through typed logical References carrying complete business Identifier pairs and closed target roles.
Do not copy the former resources, relabel them `entered-in-error`, or encode a FHIR DELETE transaction.
The assertion records source removal; receiver resolution and lifecycle application remain sink policy.
