<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Version 0.6.0 is a producer mapping contract. It does not define a server, receiver,
database, authentication scheme, transport envelope, or payload-size limit. A producer
converts Records it has already read from Health Connect and returns a FHIR R4 collection
Bundle conforming to the Mobile exchange contract.

### Package closure

The canonical URLs identify artifacts; they are not download endpoints. Build these exact
packages from the reviewed repository revision and install them in an isolated FHIR package
cache:

```text
org.grovealliance.fhir.mobile#0.6.0
org.grovealliance.fhir.health-connect#0.6.0
```

The Health Connect package pins the Mobile package at `0.6.0`. Record the repository
revision and archive checksum in producer CI. Do not overlay an archive on an existing
package directory because removed artifacts would remain.

### Required output contract

For each emitted Observation:

1. Select an admitted row in [`catalog/health-connect-adapter.json`](https://grovealliance.org/fhir/catalog/health-connect-adapter.json).
2. For a shared measurement, declare exactly two profiles in `meta.profile`: the exact
   shared measurement profile selected by that row and Health Connect Observation. A
   specimen-specific glucose output instead declares only its exact Health Connect child
   profile. Do not repeat an inherited Mobile or core standard profile.
3. Populate the typed source-record and source-output business identifiers using the Health
   Connect binding in
   [`catalog/health-connect-adapter.json`](https://grovealliance.org/fhir/catalog/health-connect-adapter.json)
   and the sole normative algorithm in
   [`catalog/exchange-protocol.json`](https://grovealliance.org/fhir/catalog/exchange-protocol.json).
4. Apply every required code, unit, effective type, result shape, specimen, and admitted
   context mapping from the machine catalogs.
5. Add conversion Provenance and every internally referenced graph node. Conversion
   Provenance directly declares only Health Connect Conversion Provenance; its inherited
   Mobile conversion profile is not repeated. Its sole source entity Identifier matches
   the output source-record Identifier, and it targets every output for that source Record.
6. Package the complete graph as a Grove Mobile Exchange Bundle. Derive every entry
   `urn:uuid` from its selected entry node key and use those URNs for internal references.
   Every literal `Reference.reference` resolves to an entry UUID URN in that same Bundle;
   external or unresolved literals, contained resources, and `#id` references are not
   admitted. `Resource.id` remains optional and repository-assigned.

The source-neutral measurement profile inherits the generic Mobile and applicable core
standard constraints. The adapter profile adds Health Connect identity and source context.
Both direct profile claims are required for shared measurements; inherited profiles are
not separately declared. Adapter-specific glucose follows the closed child-only mode above.

### Validate producer output

Use the producer-neutral wrapper from this repository. It verifies package identity,
profile claims, deterministic graph identity, closed reference resolution, visible
exactly-one output cardinalities, and then invokes the
official Validator in FHIR R4 offline mode:

```sh
python3 Scripts/validate-producer.py \
  --manifest path/to/grove-fhir-producer.json \
  --validator path/to/validator_cli.jar \
  --package mobile=path/to/org.grovealliance.fhir.mobile-0.6.0.tgz \
  --package health-connect=path/to/org.grovealliance.fhir.health-connect-0.6.0.tgz
```

The producer repository generates its own fixtures from its public mapping API. This IG
repository never checks out, patches, or executes producer implementations.

### Required converter tests

Test every one of the 41 exact AndroidX Health Connect 1.1 Record classes in the adapter
catalog. Supported rows need positive conversion fixtures; every other row needs a
fail-closed status assertion. Positive coverage includes every supported Record family,
all admitted glucose specimens, blood-pressure and temperature context, all eight sleep
stage tokens, every exact cycle/exercise source coding, exercise segments and laps, multiple
and duplicate-time heart-rate samples, exact point and interval
times, and absent optional metadata. Negative coverage includes unsupported specimens,
unknown source context, invalid identity lexemes, wrong shared profile claims, wrong
code/unit/result shape, repeated summary outputs, one source identity claiming two Record
types, external or unresolved Bundle references, and incomplete Provenance. Completeness of
source-dependent `one-per-sample`, `one-per-stage`, `one-per-delta`, and
`one-per-present-field` rules cannot be inferred from output alone; converter tests compare
each emitted graph with its source fixture, while the producer-neutral validator checks the
observable identities, allowed roles, exact summary cardinality, and graph shape.

Health Connect read permissions, scheduling, and change-token recovery belong to the
calling application. The adapter may expose producer-owned durable synchronization state,
as described in [Synchronization](synchronization.html), but it does not fetch Records or
define how a deployment stores or transmits the resulting Bundle.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}

### Retracting a source record

When Health Connect reports a deleted source record, emit the dedicated Grove Mobile Retraction
Bundle. Its sole source-record-retracted Provenance identifies every previously emitted output,
artifact, specimen, and device snapshot through a typed logical Reference carrying the exact
complete business Identifier and target-role extension. Do not copy the former clinical resources,
set them to `entered-in-error`, or encode FHIR DELETE requests. The assertion records source
removal; receiver resolution, idempotent atomic application, retention, and deletion remain sink
policy.
