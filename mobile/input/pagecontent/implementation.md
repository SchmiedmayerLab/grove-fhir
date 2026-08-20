<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Implement Grove Mobile by building a valid clinical Observation first, then adding only
the source context your application can state accurately.

### Producer sequence

1. Apply the Mobile envelope and choose the matching clinical or research profile.
2. Assign a stable Observation identifier as a complete `(system, value)` pair.
3. Set the Patient, effective time, status, and result. Add category and recording
   method when they are known.
4. Link the recording Device or DeviceMetric only when its acquisition role is known.
5. Link an application with `observation-gatewayDevice` only when it mediated or routed
   the measurement.
6. Link applicable studies with `workflow-researchStudy`.
7. Create conversion Provenance when the application transformed a source record.
8. Validate the resource against FHIR R4 and the Grove package.

Source-platform fields do not pass through a generic metadata container. A platform
adapter owns its identifier namespaces, source-type terminology, and a small allowlist
of typed metadata that lacks a standard FHIR representation. Add a field to that
allowlist only after checking for a base FHIR element, published extension, and
established terminology.

### Add the package

FHIR package tooling identifies this guide as:

```text
org.grovealliance.fhir.mobile#0.1.0
```

The package archive and checksum are published at:

```text
https://grovealliance.org/fhir/mobile/package.tgz
https://grovealliance.org/fhir/mobile/package.tgz.sha256
```

This pre-1.0 continuous build is not published in a FHIR package registry. Download the
archive, verify its checksum, and unpack it into the standard FHIR package cache before
running SUSHI. The continuous build keeps the same pre-1.0 package version while its
checksum changes. Replace the exact cache directory when updating it; do not extract a
new archive over an older copy because removed artifacts would remain:

```sh
mkdir -p grove-mobile-package
curl --fail --location \
  https://grovealliance.org/fhir/mobile/package.tgz \
  --output grove-mobile-package/package.tgz
curl --fail --location \
  https://grovealliance.org/fhir/mobile/package.tgz.sha256 \
  --output grove-mobile-package/package.tgz.sha256
(cd grove-mobile-package && shasum -a 256 --check package.tgz.sha256)
cache_backup="$(mktemp -d)"
test ! -e "$HOME/.fhir/packages/org.grovealliance.fhir.mobile#0.1.0" || \
  mv "$HOME/.fhir/packages/org.grovealliance.fhir.mobile#0.1.0" \
     "$cache_backup/"
mkdir -p "$HOME/.fhir/packages/org.grovealliance.fhir.mobile#0.1.0"
tar -xzf grove-mobile-package/package.tgz \
  -C "$HOME/.fhir/packages/org.grovealliance.fhir.mobile#0.1.0"
```

After caching it, a FHIR Shorthand project can declare the exact dependency:

```yaml
dependencies:
  org.grovealliance.fhir.mobile: 0.1.0
```

### Validate a resource

Download the official FHIR Validator and the Grove package, then run:

```sh
java -jar validator_cli.jar observation.json \
  -version 4.0.1 \
  -ig grove-mobile-package/package.tgz \
  -profile https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-observation \
  -profile http://hl7.org/fhir/StructureDefinition/heartrate
```

Validation checks base FHIR rules, required fields, supported datatypes, terminology
bindings, complete identifier pairs, and the result/member-or-data-absent invariant.
It cannot prove that a source value was mapped to the correct clinical code or that a
device truly recorded a value; implementations test those semantic mappings separately.

At minimum, test one valid fixture for every supported measurement mapping and one
invalid fixture for each contract rule. Include identity collisions, missing results,
point and interval timing, exact step-count intervals, source time zones, absent devices,
gateway applications, study links, and conversion provenance.

The [heart-rate JSON](Observation-GroveMobileHeartRateExample.json) is a compact starting
fixture. The [step-count JSON](Observation-GroveMobileStepCountExample.json) demonstrates
an interval aggregate. The [HealthKit adapter guide](https://grovealliance.org/fhir/healthkit/)
shows how a source package derives from this contract without changing its shared
semantics.

### Dependencies and terminology notices

The generated tables identify this guide's package dependencies and the notices for
terminology used by its artifacts and examples.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
