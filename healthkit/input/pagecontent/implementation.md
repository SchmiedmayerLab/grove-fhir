<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

A HealthKit Observation conforms to the HealthKit adapter profile, the Mobile envelope,
and the profile that defines the clinical or research result. Install both Grove
packages and validate all applicable profile canonicals together.

### Download the packages

This pre-1.0 continuous build is not published in a FHIR package registry, and the canonical namespace is deliberately not hosted.
Each published guide exposes its archive and checksum from its [Artifacts page](artifacts.html); download this guide's `package.tgz` and `package.tgz.sha256` there, plus the Mobile guide's pair from its own Artifacts page, then verify both checksums:

```sh
(cd grove-packages/mobile && shasum -a 256 --check package.tgz.sha256)
(cd grove-packages/healthkit && shasum -a 256 --check package.tgz.sha256)
```

To use the profiles from FHIR Shorthand, unpack both archives into the standard FHIR
package cache and declare `org.grovealliance.fhir.healthkit#0.5.0`. The HealthKit package
already declares its exact Mobile dependency. These continuous builds retain their
pre-1.0 version while their checksums change. Move aside each exact cache directory
before extracting an update; never overlay a new archive on an older copy.

```sh
cache_backup="$(mktemp -d)"
test ! -e "$HOME/.fhir/packages/org.grovealliance.fhir.mobile#0.5.0" || \
  mv "$HOME/.fhir/packages/org.grovealliance.fhir.mobile#0.5.0" \
     "$cache_backup/"
test ! -e "$HOME/.fhir/packages/org.grovealliance.fhir.healthkit#0.5.0" || \
  mv "$HOME/.fhir/packages/org.grovealliance.fhir.healthkit#0.5.0" \
     "$cache_backup/"
mkdir -p "$HOME/.fhir/packages/org.grovealliance.fhir.mobile#0.5.0"
mkdir -p "$HOME/.fhir/packages/org.grovealliance.fhir.healthkit#0.5.0"
tar -xzf grove-packages/mobile/package.tgz \
  -C "$HOME/.fhir/packages/org.grovealliance.fhir.mobile#0.5.0"
tar -xzf grove-packages/healthkit/package.tgz \
  -C "$HOME/.fhir/packages/org.grovealliance.fhir.healthkit#0.5.0"
```

```yaml
dependencies:
  org.grovealliance.fhir.healthkit: 0.5.0
```

### Validate an Observation

Pass both local package archives to the official FHIR Validator. Add the HealthKit
profile and the profile that defines the result. For a heart-rate Observation:

```sh
java -jar validator_cli.jar observation.json \
  -version 4.0.1 \
  -ig grove-packages/mobile/package.tgz \
  -ig grove-packages/healthkit/package.tgz \
  -profile https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-observation \
  -profile http://hl7.org/fhir/StructureDefinition/heartrate
```

Validation checks the resource shape, identifier format, terminology bindings, profile
intersection, and Mobile rules. It cannot prove that a HealthKit sample type was mapped
to the correct clinical profile, that an attributed Device performed the claimed role,
or that disclosing a source identifier is authorized. Test those adapter semantics and
privacy decisions against representative source fixtures.

Start with the [heart-rate JSON](Observation-HealthKitHeartRateObservationExample.json),
then compare it with the field-by-field [mapping rules](mapping.html).

### Retracting an entered-in-error record

When a previously converted source record is retracted, publish a bundle whose outputs for that source are all `entered-in-error` stubs.
Each stub keeps the profile claims, the normative code, and the complete business identifiers of the output it retracts, sets `status` to `entered-in-error`, and carries `dataAbsentReason` in place of a value.
A bundle whose outputs for a source record are all entered-in-error records a retraction rather than a conversion and carries no conversion Provenance.
The repository conformance validator enforces both directions: a retraction claiming a conversion Provenance and a conversion missing one are each rejected.
