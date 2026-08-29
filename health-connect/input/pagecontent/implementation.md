<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

The Grove FHIR contracts define producer mappings.
They do not define a server, receiver, database, authentication scheme, transport envelope, or payload-size limit.
A producer converts Records it has already read from Health Connect and returns a FHIR R4 collection Bundle conforming to the Mobile exchange contract.

### Install the package closure

The canonical URLs identify artifacts; they are not download endpoints.
The Health Connect package and its Mobile dependency use these package IDs:

```text
org.grovealliance.fhir.mobile
org.grovealliance.fhir.health-connect
```

Resolve both exact versions from `catalog/release-manifest.json`; the Health Connect package pins the matching Mobile package version.
Download each archive and checksum from the corresponding Artifacts page, verify the checksum, and install the archive in an isolated FHIR package cache.
Replace an existing package directory rather than overlaying it, because an overlay can retain artifacts removed by the newer package.

### Required output contract

For each emitted Observation:

1. Select an admitted row in [`catalog/health-connect-adapter.json`](https://grovealliance.org/fhir/catalog/health-connect-adapter.json).
2. For a shared measurement, declare exactly two profiles in `meta.profile`: the exact shared measurement profile selected by that row and Health Connect Observation.
   A specimen-specific glucose output instead declares only its exact Health Connect child profile.
   Do not repeat an inherited Mobile or core standard profile.
3. Populate the typed source-record and source-output business identifiers using the Health Connect binding in [`catalog/health-connect-adapter.json`](https://grovealliance.org/fhir/catalog/health-connect-adapter.json) and the sole normative algorithm in [`catalog/exchange-protocol.json`](https://grovealliance.org/fhir/catalog/exchange-protocol.json).
4. Apply every required code, unit, effective type, result shape, specimen, and admitted context mapping from the machine catalogs.
5. Add conversion Provenance and every internally referenced graph node.
   Conversion Provenance directly declares only Health Connect Conversion Provenance; its inherited Mobile conversion profile is not repeated.
   Its sole source entity Identifier matches the output source-record Identifier, and it targets every output for that source Record.
6. Package the complete graph as a Grove Mobile Exchange Bundle.
   Derive every entry `urn:uuid` from its selected entry node key and use those URNs for internal references.
   Every literal `Reference.reference` resolves to an entry UUID URN in that same Bundle; external or unresolved literals, contained resources, and `#id` references are not admitted. `Resource.id` remains optional and repository-assigned.

The source-neutral measurement profile inherits the generic Mobile and applicable core standard constraints.
The adapter profile adds Health Connect identity and source context.
Both direct profile claims are required for shared measurements; inherited profiles are not separately declared.
Adapter-specific glucose follows the closed child-only mode above.

### Validate producer output

Use the Grove producer validation command for graph-level checks.
It verifies package identity, profile claims, deterministic graph identity, closed reference resolution, and observable single-output cardinalities before invoking the official FHIR Validator in R4 offline mode:

```sh
python3 Scripts/validate-producer.py \
  --manifest path/to/grove-fhir-producer.json \
  --validator path/to/validator_cli.jar \
  --package mobile=path/to/mobile-package.tgz \
  --package health-connect=path/to/health-connect-package.tgz
```

### Verify converter behavior

Verify every one of the 41 exact AndroidX Health Connect 1.1 Record classes in the adapter contract.
Admitted rows need a positive conversion example; every other row needs a fail-closed assertion.
Positive coverage includes every supported Record family, all admitted glucose specimens, blood-pressure and temperature context, all eight sleep stage tokens, every exact cycle/exercise source coding, exercise segments and laps, multiple and duplicate-time heart-rate samples, exact point and interval times, and absent optional metadata.
Negative coverage includes unsupported specimens, unknown source context, invalid identity lexemes, wrong shared profile claims, wrong code/unit/result shape, repeated summary outputs, one source identity claiming two Record types, external or unresolved Bundle references, and incomplete Provenance.
Some cardinality rules depend on the source record and cannot be inferred from FHIR output alone.
For `one-per-sample`, `one-per-stage`, `one-per-delta`, and `one-per-present-field`, compare the emitted graph with the source record.
Grove producer validation checks only the observable identities, allowed roles, summary cardinality, and graph shape.

Health Connect read permissions, scheduling, and change-token recovery belong to the calling application.
The adapter may expose producer-owned durable synchronization state, as described in [Synchronization](synchronization.html), but it does not fetch Records or define how a deployment stores or transmits the resulting Bundle.

### Retracting a source record

When Health Connect reports a deleted source record, emit the dedicated Grove Mobile Retraction Bundle.
Its sole source-record-retracted Provenance identifies every previously emitted output, artifact, specimen, and device snapshot through a typed logical Reference carrying the exact complete business Identifier and target-role extension.
Do not copy the former clinical resources, set them to `entered-in-error`, or encode FHIR DELETE requests.
The assertion records source removal; receiver resolution, idempotent atomic application, retention, and deletion remain sink policy.

### Dependencies and terminology notices

The tables below list this guide's package dependencies and the notices for terminology used by its artifacts and examples.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
