# Producer conformance kit

Grove FHIR validates its own R4 packages, examples, and negative corpora.
A producer repository validates the resources emitted by its real public API.
The dependency is one-way: this repository never checks out, patches, or executes producer code.

A producer manifest binds emitted files to the Grove FHIR package identities and profiles they claim.
During development, build or download all required packages from one exact Grove FHIR source revision and keep the manifest package versions synchronized.
Release evidence binds package checksums to that revision; implementations should pin the exact source revision or published release from which their packages were built.

The fastest first green run needs no downloads at all: the structural layer runs against the example producer in seconds.

```sh
python3 Scripts/validate-producer.py \
  --manifest Conformance/example-producer/manifest.json \
  --structural-only
```

`npm run producer-kit:check` is the same command.
Structural success is not FHIR conformance; it reports only that the graph, identity, and profile-claim rules hold.

The full lane needs the pinned Validator and the exact packages, and both come from this repository.
`Scripts/download-fhir-tools.sh .build/fhir-tools` seeds `.build/fhir-home` with the checksum-pinned Validator the release manifest names, and `Scripts/build-guides.sh mobile questionnaire` writes each `<guide>/output/package.tgz`.

```sh
python3 Scripts/validate-producer.py \
  --manifest Conformance/example-producer/manifest.json \
  --validator .build/fhir-tools/validator_cli.jar \
  --package mobile=mobile/output/package.tgz \
  --package questionnaire=questionnaire/output/package.tgz \
  --allow-example-urls
```

Use the exact Validator version `toolchain.fhirValidator` pins in `catalog/release-manifest.json`; a different build can pass or fail where the release evidence does not.

Real producer output fails official validation when it uses reserved example.org URLs.
Demonstration fixtures may opt in explicitly with `--allow-example-urls`, which is why the command above carries it and why CI does too; a real producer omits it and the default remains fail closed.

The command verifies the manifest and package metadata, ensures each emitted resource declares its required profiles, and invokes the official HL7 FHIR Validator offline.
The producer remains responsible for generating the files before this command runs.

`Conformance/example-producer` is an executable example of the format.
The JSON Schema is useful for editor integration; `validate-producer.py` applies the same fail-closed rules without requiring a third-party Python package.

`Conformance/corpora/mobile-exchange/official-validator-manifest.json` is the release lane manifest.
It sends both normative positive bases—the active conversion event and the retraction assertion—through the exact Mobile package and official Validator.

## Every committed fixture

`Conformance/fixture-validator-manifest.json` is the all-fixtures lane.
A guide's own worked examples are validated by the IG Publisher during its build and audited by `Scripts/check-guide-qa.py`; the fixtures under `Conformance/` and `questionnaire/fixtures/` are the ones no guide build ever sees.

```sh
python3 Scripts/validate-fixtures.py \
  --validator .build/fhir-tools/validator_cli.jar \
  --package mobile=mobile/output/package.tgz \
  --package questionnaire=questionnaire/output/package.tgz
```

Every JSON file beneath the declared roots is either validated here or excluded with a stated reason, so a fixture cannot be added without being classified.
`python3 Scripts/validate-fixtures.py --coverage-only` checks that classification alone and needs neither Java nor a built package.

## Positive and negative corpus

`Conformance/corpora/mobile-exchange` is the normative producer corpus for the Mobile exchange graph.
Its positive bases cover both one immutable conversion event and one dedicated source-record retraction event.
The retraction base also carries the optional native record identifier on its target, so a producer can see the exact shape of the disclosure the addition path's governed-source-identifier policy also governs.
The active Bundle is byte-for-byte equal to the example producer Bundle.
Every negative case applies exactly one RFC 6902 JSON Patch operation and names the one rule it is intended to violate.

`Conformance/corpora/mobile-semantics/corpus.json` is the implementation-neutral clinical projection corpus.
It contains exactly one vector for every shared Mobile measurement and binds the exact profile, code, unit, effective shape, result shape, edge rules, and admitted adapter context to `catalog/measurement-catalog.json`.
A producer manifest binds one generated Observation to every shared Mobile meaning present in its submitted resources through `semanticVectors`.
The producer validator resolves the declared JSON Pointer and compares the exact normalized clinical projection to the versioned vector.
Equal offset-bearing FHIR instants are normalized without losing fractional precision before comparison, so a producer retains a real source offset when available and uses UTC when its source API supplies only an instant; it never invents an offset to match a fixture.
Swift, Kotlin, and TypeScript repositories therefore generate these fixtures in their own CI; Grove FHIR still never executes their implementations.

A response-sourced producer binds vectors through the same mechanism.
An Observation projected from a QuestionnaireResponse carries no adapter context, so it binds the bare source-neutral clinical projection the `comparisonRule` already accepts; its admitted additions are the `questionnaire.default` source-context rule, which the measurement catalog projects onto every measurement whose questionnaire coverage is `supported`.

`producerDiagnostics` in `catalog/exchange-protocol.json` is the shared rule-code registry, and the two sides of the contract do not raise the same subset.
Each entry says which side does: an `emittedBy` of `conformance-kit` means this repository's validator raises it, and `client` means the rule is stated here but enforced in the producer SDKs, whose own source fixtures can see what an output-only manifest cannot.
A code is never registered without an owner, so an unimplemented rule cannot pass for an enforced one.

The structural conformance kit rejects graph, closed-reference, deterministic-identity, exact summary-cardinality, and adapter source-context failures without needing an implementation guide build.
FHIR element cardinality and terminology validation remain the official HL7 FHIR Validator's responsibility with the exact packages selected by the producer manifest.
Completeness of a source-dependent one-per-sample/stage/delta/present-field projection cannot be proved from an output-only manifest; the producer's source-fixture tests own that comparison.
A producer test suite must run all three layers; structural-only success is not FHIR conformance.

Closed-reference validation permits only addressable Bundle entries.
Active and retraction events reject every contained resource and `#id` reference, so all SDKs share one event-node, identity, and reference-closure model.

The active graph is also closed by resource class and direct profile claim.
Observation, DocumentReference, Specimen, VisionPrescription, MedicationAdministration, and MedicationStatement are outputs; Patient, Device, ResearchStudy, ResearchSubject, PlanDefinition, and Grove QuestionnaireResponse are supporting entries; exactly one Provenance is the lifecycle assertion.
Supporting entries must connect to an output or that Provenance.
`DeviceMetric` and every other unlisted R4 type fail closed under the Grove FHIR contracts.

Every adapter output uses one of the permitted direct Grove profile-claim sets in `catalog/profile-claims.json`:

- A shared Mobile or Sensor Observation claims exactly the applicable shared semantic profile and its adapter profile.
  Inherited generic or core profiles are not repeated.
- A HealthKit shared Observation claims exactly one shared semantic profile and the generic HealthKit Observation profile.
  Body-mass index uses the authoritative R4 BMI profile in that pair.
  A HealthKit-specific Observation child instead claims exactly that child; a HealthKit ECG Observation claims exactly the Sensor ECG and HealthKit ECG profiles.
- A Health Connect specimen-specific glucose Observation or a SensorKit-only Observation claims exactly its adapter-specific child profile.
- A SensorKit ECG Observation claims exactly the source-neutral Sensor ECG profile and the SensorKit ECG profile, and includes its required linked native Recording Document in the same graph.
- A source-neutral Sensor Recording Document claims exactly its Sensor profile.
  A raw HealthKit, SensorKit, or Provider DocumentReference claims exactly that source-neutral profile and its adapter Recording Document profile.
  A HealthKit clinical-record envelope claims only its exact child profile, which inherits the Sensor contract; HealthKit VisionPrescription, MedicationAdministration, and MedicationStatement outputs likewise claim only their exact adapter child.
- Adapter conversion Provenance claims exactly its adapter conversion profile.
  Its targets close over every active output profile for that adapter, including child-only and non-Observation HealthKit outputs.

`Specimen`, `VisionPrescription`, `MedicationAdministration`, and `MedicationStatement` are adapter-only active output types.
The first must claim exactly the Health Connect Specimen profile; the other three must claim their exact HealthKit child.
A base Mobile conversion Provenance never makes an unprofiled instance of these types admissible.

A manifest's package list declares the packages available to validate the complete producer fixture; it does not assert that every Observation was emitted by every listed adapter.
A source-neutral Observation with no adapter marker therefore claims only its shared semantic profile.
Once an adapter source marker is present, the exact adapter claim mode above is mandatory, and any claimed adapter profile requires its exact package in the manifest.

The structural conformance kit enforces these modes for standalone resources and Bundle entries.
A producer manifest's `requiredProfiles` must equal the resource's complete direct Grove profile set, so a producer-authored manifest cannot hide an extra claim.
