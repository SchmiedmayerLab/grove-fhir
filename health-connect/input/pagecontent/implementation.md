<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

A converted resource validates against the Health Connect adapter, the Mobile envelope,
and the profile that defines its clinical result. Install both Grove packages and validate
all declared profile canonicals together.

### Download the packages

Download the exact archives and verify their checksums:

```sh
mkdir -p grove-packages/mobile grove-packages/health-connect
curl --fail --location \
  https://grovealliance.org/fhir/mobile/package.tgz \
  --output grove-packages/mobile/package.tgz
curl --fail --location \
  https://grovealliance.org/fhir/mobile/package.tgz.sha256 \
  --output grove-packages/mobile/package.tgz.sha256
curl --fail --location \
  https://grovealliance.org/fhir/health-connect/package.tgz \
  --output grove-packages/health-connect/package.tgz
curl --fail --location \
  https://grovealliance.org/fhir/health-connect/package.tgz.sha256 \
  --output grove-packages/health-connect/package.tgz.sha256
(cd grove-packages/mobile && shasum -a 256 --check package.tgz.sha256)
(cd grove-packages/health-connect && shasum -a 256 --check package.tgz.sha256)
```

The Health Connect package declares its exact Mobile dependency. These pre-1.0 continuous
builds retain version `0.2.0` while their checksums change, so replace an old cache directory
rather than overlaying a new archive.

```sh
cache_backup="$(mktemp -d)"
test ! -e "$HOME/.fhir/packages/org.grovealliance.fhir.mobile#0.2.0" || \
  mv "$HOME/.fhir/packages/org.grovealliance.fhir.mobile#0.2.0" "$cache_backup/"
test ! -e "$HOME/.fhir/packages/org.grovealliance.fhir.health-connect#0.2.0" || \
  mv "$HOME/.fhir/packages/org.grovealliance.fhir.health-connect#0.2.0" "$cache_backup/"
mkdir -p "$HOME/.fhir/packages/org.grovealliance.fhir.mobile#0.2.0"
mkdir -p "$HOME/.fhir/packages/org.grovealliance.fhir.health-connect#0.2.0"
tar -xzf grove-packages/mobile/package.tgz \
  -C "$HOME/.fhir/packages/org.grovealliance.fhir.mobile#0.2.0"
tar -xzf grove-packages/health-connect/package.tgz \
  -C "$HOME/.fhir/packages/org.grovealliance.fhir.health-connect#0.2.0"
```

```yaml
dependencies:
  org.grovealliance.fhir.health-connect: 0.2.0
```

### Validate an Observation

Pass both local package archives to the official FHIR Validator. For a heart-rate output:

```sh
java -jar validator_cli.jar observation.json \
  -version 4.0.1 \
  -ig grove-packages/mobile/package.tgz \
  -ig grove-packages/health-connect/package.tgz \
  -profile https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-observation \
  -profile http://hl7.org/fhir/StructureDefinition/heartrate
```

Validation checks required source and output identifiers, the required quantity result,
effective time, issued time, terminology bindings, and the profile intersection. It cannot
prove that all samples from a `HeartRateRecord` were emitted, that output identifiers remain
stable between runs, or that a deletion removed the complete prior output set. Test those
behaviors with a persistent synchronization journal.

### Minimum converter tests

A conforming adapter test suite covers:

- heart-rate records with zero, one, multiple, and duplicate-time samples;
- exact step intervals, zone offsets, and count boundaries;
- weight precision and every recording-method branch;
- absent and populated Device metadata without invented identifiers;
- source and converter applications that are the same and that are different;
- idempotent replay, source updates that add and remove outputs, and deletion changes;
- receiver-limit preflight, unsupported first-seen Records, tombstoning a previously
  published unsupported update, and a two-event replacement whose combined form is too
  large;
- crash and replay between the tombstone-only and active halves of a split replacement;
- failure before and after destination acknowledgement; and
- expired-token full reconciliation, including deletion of stale journaled and pending
  outputs; and
- A→B→A filter changes with exclusive projection ownership and reactivation.

Start with the [documentation Bundle JSON](Bundle-HealthConnectStudyBundleExample.json) to
inspect the profiles and references, then compare each result with the
[mapping rules](mapping.html). The aggregate Bundle is not an operational event: exercise
the single-source event lifecycle described in [Synchronization](synchronization.html).
