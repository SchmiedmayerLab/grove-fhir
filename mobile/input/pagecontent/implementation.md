<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Implement Grove Mobile by building a valid clinical Observation first, then adding only
the source context your application can state accurately.

### Producer sequence

1. Select the exact shared measurement profile from the normative catalog.
2. Assign a stable Observation identifier as a complete `(system, value)` pair.
3. Set the Patient, effective time, status, and result. Add category and recording
   method when they are known.
4. Link the recording Device only when its acquisition role and admitted Device profile are known.
5. Link an application with `observation-gatewayDevice` only when it mediated or routed
   the measurement.
6. Link applicable studies with `workflow-researchStudy`.
7. Create conversion Provenance when the application transformed a source record.
8. Place the complete graph in a Grove Mobile Exchange Bundle, derive deterministic
   entry UUID URNs, and use them for internal references. Every literal reference resolves to
   an entry in that same Bundle; contained resources and `#id` references are prohibited.
   At a governed path, use either that
   literal form or an identifier-only logical Reference—never both. A logical Reference carries
   the exact `Reference.type` and one complete Identifier with an absolute system; a logical
   Patient uses the deployment's pseudonym and does not require a fabricated Patient entry.
9. Admit only the closed output, supporting, and lifecycle resource types; require every
   supporting entry to connect to an output or the lifecycle Provenance; and apply the exact
   direct-profile mode to every output, Device, QuestionnaireResponse, and Provenance.
10. Validate the Bundle against FHIR R4, the Grove package, and the reason-specific corpus.

Source-platform fields do not pass through a generic metadata container. A platform
adapter owns its identifier namespaces, source-type terminology, and a small allowlist
of typed metadata that lacks a standard FHIR representation. Add a field to that
allowlist only after checking for a base FHIR element, published extension, and
established terminology.

### Add the package

FHIR package tooling identifies this guide as:

```text
org.grovealliance.fhir.mobile#0.6.0
```

The Grove canonical is an identifier, not a package-download promise. Version 0.6.0 is
not hosted at the canonical URLs and is not published in a FHIR package registry.
Build the package from the reviewed repository revision, record that revision and the
package checksum in producer CI, and install the resulting archive in an isolated FHIR
package cache. Do not extract a new archive over an older copy because removed artifacts
would remain:

```sh
cache_backup="$(mktemp -d)"
test ! -e "$HOME/.fhir/packages/org.grovealliance.fhir.mobile#0.6.0" || \
  mv "$HOME/.fhir/packages/org.grovealliance.fhir.mobile#0.6.0" \
     "$cache_backup/"
mkdir -p "$HOME/.fhir/packages/org.grovealliance.fhir.mobile#0.6.0"
tar -xzf path/to/org.grovealliance.fhir.mobile-0.6.0.tgz \
  -C "$HOME/.fhir/packages/org.grovealliance.fhir.mobile#0.6.0"
```

After caching it, a FHIR Shorthand project can declare the exact dependency:

```yaml
dependencies:
  org.grovealliance.fhir.mobile: 0.6.0
```

### Validate a resource

Download the official FHIR Validator and the Grove package, then run:

```sh
java -jar validator_cli.jar exchange-bundle.json \
  -version 4.0.1 \
  -ig grove-mobile-package/package.tgz \
  -profile https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-exchange-bundle
```

Validation checks base FHIR rules, required fields, supported datatypes, terminology
bindings, complete identifier pairs, governed reference shapes, reviewed quantity value
domains, and the result/member-or-data-absent invariant.
It cannot prove that a source value was mapped to the correct clinical code or that a
device truly recorded a value; implementations test those semantic mappings separately.

At minimum, test one valid fixture for every supported measurement mapping and one
invalid fixture for each contract rule. Include identity collisions, missing results,
point and interval timing, exact step-count intervals, source time zones, absent devices,
gateway applications, study links, and conversion provenance.

For producer CI, use the repository's producer-neutral `Scripts/validate-producer.py`
wrapper. It verifies package identity, required profile claims, deterministic UUID URNs,
and internal graph resolution before invoking the official Validator. It does not run
or import producer code.

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
