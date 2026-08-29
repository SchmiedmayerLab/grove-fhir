<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

A Grove Mobile implementation begins with a valid clinical Observation and adds only the source context that the producing application can state accurately.

### Producer sequence

1. Select the exact shared measurement profile from the normative catalog.
2. Derive exactly one typed `source-record` Identifier and one typed `source-output` Identifier as complete `(system, value)` pairs using the exchange protocol.
3. Set the Patient, effective time, status, and result.
   Add category and recording method when they are known.
4. Link the recording Device only when its acquisition role and admitted Device profile are known.
5. Link an application with `observation-gatewayDevice` only when it mediated or routed the measurement.
6. Link applicable studies with `workflow-researchStudy`.
7. Create conversion Provenance when the application transformed a source record.
8. Place the complete graph in a Grove Mobile Exchange Bundle, derive deterministic entry UUID URNs, and use them for internal references.
   Every literal reference resolves to an entry in that same Bundle; contained resources and `#id` references are prohibited.
   At a governed path, use either that literal form or an identifier-only logical Reference—never both.
   A logical Reference carries the exact `Reference.type` and one complete Identifier with an absolute system; a logical Patient uses the deployment's pseudonym and does not require a fabricated Patient entry.
9. Allow only the resource types listed for active outputs, supporting entries, and lifecycle entries. Connect every supporting entry to an output or the lifecycle Provenance. Require every output, Device, QuestionnaireResponse, and Provenance to declare exactly the profile set defined in `profile-claims.json`.
10. Validate the Bundle against FHIR R4, the Grove package, and the applicable graph and lifecycle rules.

Source-platform fields do not pass through a generic metadata container.
A platform adapter owns its identifier namespaces, source-type terminology, and a small allowlist of typed metadata that lacks a standard FHIR representation.
Add a field to that allowlist only after checking for a base FHIR element, published extension, and established terminology.

### Add the package

FHIR package tooling identifies this guide by the package ID:

```text
org.grovealliance.fhir.mobile
```

The Grove canonical is an identifier, not a package-download promise.
The Grove FHIR contracts are not hosted at the canonical URLs and are not published in a FHIR package registry.
Resolve the exact package version from `catalog/release-manifest.json` and download its archive and checksum from the [Artifacts page](artifacts.html).
Verify the checksum, install the archive in an isolated FHIR package cache, and replace the exact package directory atomically; never extract a new archive over an older copy because removed artifacts would remain.
Use that same manifest version when declaring the dependency in a FHIR Shorthand project.

### Validate a resource

Download the official FHIR Validator and the Grove package, then run:

```sh
java -jar validator_cli.jar exchange-bundle.json \
  -version 4.0.1 \
  -ig grove-mobile-package/package.tgz \
  -profile https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-exchange-bundle
```

Validation checks base FHIR rules, required fields, supported datatypes, terminology bindings, complete identifier pairs, governed reference shapes, catalog-declared quantity value domains, and the rule requiring either a result (`value[x]`, `component`, or `hasMember`) or `dataAbsentReason`.
It cannot prove that a source value was mapped to the correct clinical code or that a device truly recorded a value; implementations test those semantic mappings separately.

At minimum, test one valid example for every supported measurement mapping and one invalid example for each contract rule.
Include identity collisions, missing results, point and interval timing, exact step-count intervals, source time zones, absent devices, gateway applications, study links, and conversion provenance.

For graph-level validation, use a checkout of the Grove FHIR Implementation Guides source corresponding to the package version.
Run `python3 Scripts/validate-producer.py --manifest <manifest.json> --validator <validator_cli.jar> --package <alias>=<package.tgz>` once per package alias declared by the manifest.
The command verifies package identity, required profile claims, deterministic UUID URNs, and internal graph resolution before invoking the official FHIR Validator.

The [heart-rate JSON](Observation-GroveMobileHeartRateExample.json) is a compact starting example.
The [step-count JSON](Observation-GroveMobileStepCountExample.json) demonstrates an interval aggregate.
The [HealthKit adapter guide](https://grovealliance.org/fhir/healthkit/) shows how a source package derives from this contract without changing its shared semantics.

### Dependencies and terminology notices

The tables below list this guide's package dependencies and the notices for terminology used by its artifacts and examples.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
