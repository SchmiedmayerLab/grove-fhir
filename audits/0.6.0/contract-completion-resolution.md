<!--

This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

-->

# 0.6.0 contract-completion resolution

This document records the implementation disposition of the 2026-08-26 audit. It is
not a claim that a local preview has become the canonical publication. “Closed” means
the repository now contains an executable contract and a regression gate. Items that
need an accountable clinical, privacy, terminology, storage, or canonical-host owner
remain explicit release approvals even when their proposed technical shape is complete.

## Release decision

The second 0.6.0 change set deliberately breaks the initial 0.6.0 contract. Consumers
must not mix packages or SDKs from before and after this change. The authoritative wire
contract is `catalog/exchange-protocol.json`; the authoritative package and catalog
inventory is `catalog/release-manifest.json`.

The final freshness pass on 2026-08-27 moved the checksum-pinned toolchain to the
same-day [IG Publisher 2.3.3](https://github.com/HL7/fhir-ig-publisher/releases/tag/2.3.3)
and [FHIR Validator 6.10.3](https://github.com/hapifhir/org.hl7.fhir.core/releases/tag/6.10.3).
Their official GitHub asset SHA-256 digests are part of the release manifest and are
enforced by the downloader; a cached binary with any other digest is replaced or the
build fails.

The release shape is now:

- one immutable collection Bundle per exact source-record revision;
- a separate Provenance-only retraction assertion, never a mutilated clinical result or
  a FHIR server delete command;
- keyed, length-framed, deployment-scoped v2 identities with typed roles;
- deterministic event, entry-node, and `fullUrl` identities with public exact vectors;
- exact source-output and source-artifact identity for every multi-output or preserved
  payload path;
- stable per-unit recording-device identity plus immutable event snapshots, or no Device
  instance when the source cannot establish one;
- registered source-preservation formats rather than a bare JSON array or ambiguous raw
  payload; and
- three separately named conformance levels: FHIR R4, Grove profile, and Grove producer.

## Verified-finding disposition

| Finding | Disposition in this change set | Principal executable evidence |
| --- | --- | --- |
| VF-01 retraction cannot conform | **Closed.** Retraction is a dedicated Bundle with one retraction Provenance and logical, typed targets; active clinical resources are forbidden. | exchange protocol, Mobile profiles, active/retraction corpus, producer validator |
| VF-02 Health Connect identity drift | **Closed.** Clear/native identities and parallel authorities are removed; exact v2 source-record/output roles and examples are required. | exchange vectors, Health Connect catalog, profile slices, catalog and producer tests |
| VF-03 SensorKit identity conflict | **Closed.** Source record, structured/raw output, and source artifact are separate typed identities with exact discriminators. | SensorKit catalog, recording-document profiles/examples, producer tests |
| VF-04 resting heart rate semantics | **Closed.** Health Connect and HealthKit are point-in-time; the profile requires specific LOINC 40443-4 plus generic 8867-4 and imposes the R4 Heart Rate profile. The daily aggregate is a distinct Google Health adapter profile. | measurement and adapter catalogs, generated profiles, semantic corpus, Publisher validation |
| VF-05 provider identity collision | **Closed.** Provider code, source type, complete provider-scope pair, and native id are HMAC-framed; the misleading Grove-global account NamingSystem is removed. | protocol vector, provider catalog/examples, provider tests |
| VF-06 hypertension notification | **Technically closed; clinical approval required.** It is an admitted source screening-notification event and never a diagnosis. | HealthKit catalog row/profile/example and peer-notification consistency test |
| VF-07 “verbatim” metadata claim | **Closed.** The generic residual claim is removed. Four reviewed keys have explicit typed dispositions; unadmitted metadata is not described as losslessly preserved. | HealthKit terminology/profile/catalog gates |
| VF-08 application/host OS conflation | **Closed.** Application release/build and immutable host OS/hardware snapshots are separate Device profiles linked by `Device.parent`. | Mobile Device profiles and HealthKit examples |
| VF-09 physical Device identity | **Closed.** A recording Device requires a governed stable per-unit token and a separate event snapshot; descriptive fields never establish identity. | protocol, adapter device declarations, Mobile profile and tests |
| VF-10 weak identity grammar | **Closed.** One canonical v2 HMAC grammar, positive epochs, Unicode scalar handling, and closed roles replace adapter regexes. | JSON Schema, FHIRPath, Python vectors, language-local conformance tests |
| VF-11 clinical-record contract | **Closed.** Release-specific FHIR R4, CDA, and native artifacts have exact media type/format, source-output/artifact identity, size/hash rules, and provenance. | format registry, HealthKit profiles/examples, producer tests |
| VF-12 package graph mismatch | **Closed.** All ten guides and exact direct dependencies are projected into the 0.6.0 graph and release manifest. | release checker and package-graph tests |
| VF-13 version drift | **Closed.** The release checker binds guide configs, catalogs, corpora, package metadata, and FSH attachment versions to one manifest. | `npm run release:check` and content tests |
| VF-14 mutable release automation | **Repository portion closed.** Release evidence requires a clean tree, is non-overwriting, exact-revision, checksummed, all-guide, and preflights existing assets. Canonical-host activation remains external. | release collector, workflow, publication runbook |
| VF-15 false offline reproducibility | **Closed.** Network-closed offline candidate evidence and online terminology evidence are distinct lanes and are described honestly; Publisher archives are checksum-bound but are not claimed to be byte-reproducible. | build script, collector, publication runbook |
| VF-16 SampledData semantics only in Python | **Closed.** Timing, dimensions, bounds, and payload admission live in the Sensor profiles/catalog; the validator tests the same rules. | Sensor FSH/catalog and positive/negative corpus |
| VF-17 noncanonical PPG bytes | **Closed.** The PPG format now has a versioned byte grammar and cross-language strict parsing/serialization expectations. | format registry, Swift/TypeScript local diffs and boundary tests |
| VF-18 contradictory cardinality prose | **Closed.** Every Health Connect output uses one closed output-count rule; duplicate canonical coordinates use retained source-list order or fail closed. | catalog schema/tests and Android duplicate-coordinate regressions |
| VF-19 unenforced semantic promises | **Closed for advertised 0.6.0 claims.** Incorrect profile claims were removed or made executable; producer-only assertions are identified as such. | generated-profile parity, profile-claim catalog, producer corpus |
| VF-20 missing/loose catalog schemas | **Substantially closed.** Every normative catalog is schema-versioned and validated; top-level envelopes plus identity/device security subcontracts fail closed. Catalog-specific tests enforce remaining typed row variants. A future catalog-shape normalization may improve ergonomics but is not a second authority. | JSON Schema checks and unknown-member mutation tests |
| VF-21 stale terminology provenance | **Repository portion closed.** Current package/version, SDK inputs, hashes, selected metadata, and generated review digests are recorded. Licensed/online terminology verification and accountable ratification remain release evidence. | terminology provenance, review digest, online evidence lane |
| VF-22 incomplete Health Connect source context | **Closed.** Every mapped AndroidX 1.1 cycle, exercise, body-site, title, and note field now has one catalog disposition, exact complete terminology, profile invariants, and catalog-driven structural checks. Two falsely complete CodeSystems were repaired. | Health Connect catalog, terminology, profiles, Kotlin comparison, producer mutations |
| VF-23 open exchange graph and output multiplicity | **Closed for output-observable rules.** All literal references resolve inside the Bundle, one opaque Health Connect source names one Record type, exactly-one summaries are enforced, glucose is one Observation plus one referenced typed Specimen, and clear extra identifiers fail. Source-dependent list completeness remains explicitly owned by source-fixture tests. | producer validator, Health Connect graph rules, negative mutations, language-local suites |
| VF-24 ambiguous lifecycle coding multiplicity | **Closed.** Active events carry exactly one ISO `transform` coding and no Grove lifecycle coding; retractions carry exactly one Grove `source-record-retracted` coding and no ISO lifecycle coding. Unrelated translation systems remain open. | Mobile invariants, exchange catalog, producer validator, adversarial corpus, language-local suites |
| VF-25 profile, reference, entity, and retraction-target bypasses | **Closed.** Active Observations claim an approved shared/adapter profile composition; every internal reference resolves and any declared type matches its target; transform/retraction Provenance contains exactly one logical source-record entity; and each retraction role fixes both the target resource type and target identifier role. | exchange catalog/schema, Mobile invariants, producer validator, adversarial corpus, language-local suites |
| VF-26 uncatalogued quantity value domains | **Closed for mathematically unambiguous source representations.** Percent values are inclusive 0–100, discrete event totals are non-negative integers, and HealthKit valence is inclusive -1–1. The catalog, generated FHIR constraints, producer gate, and clients consume one boundary model; zero is admitted. No physiologic plausibility ranges were invented. | measurement catalog/schema/review digests, generated min/max and FHIRPath invariants, boundary regressions, language-local suites |
| VF-27 manifest package presence mistaken for resource provenance | **Closed.** The manifest package list is a fixture-wide validation capability declaration. It no longer forces every shared Observation to claim an arbitrary present adapter; source-neutral output remains shared-only, while an adapter source marker requires the exact adapter profile and a claimed adapter profile requires its exact package. | profile-claim validator, source-marker fail-closed tests, conformance and Mobile guidance, TypeScript multi-package fixture |
| VF-28 Apple bundle identifier collided with opaque snapshot constraint | **Closed.** HealthKit application Devices now use a dedicated derived profile with one typed clear Apple product bundle identifier and a separate required opaque event-snapshot slice. The source catalog fixes the profile, systems, code, cardinality, meaning, and caller-owned source-actor classification. | HealthKit application Device profile, identifier-type CodeSystem, catalog schema/test, examples, Publisher validation, Swift consumer diff |
| VF-29 profiles overconstrained terminology display text | **Closed.** Generated category and aggregation-method constraints now fix semantic system/code pairs without requiring presentation text. Displays remain in examples for readability, but can be localized or updated by the authoritative terminology without invalidating otherwise conformant resources. | catalog renderer, regenerated profiles/examples, Withings regression, Publisher validation |
| VF-30 ambiguous contained-reference resolution | **Closed by removal.** Active and retraction event graphs prohibit contained resources and `#id` references. Every graph node is an addressable Bundle entry governed by one event identity and reference-closure model; the cross-language corpus includes an exact containment-prohibition diagnostic. | exchange protocol/schema, FSH invariants, producer validator, adversarial corpus, language-local graph validators |
| VF-31 incomplete HealthKit output-claim and provenance closure | **Closed.** All 111 HealthKit-specific Observation children have an exact child-only direct-claim mode; shared, BMI, ECG, recording, clinical-document, vision, dose, and tracked-medication modes are separately closed. HealthKit conversion Provenance targets the exact 118-profile active catalog closure, including non-Observation outputs, and a multi-output source row admits one claim per emitted resource rather than combining sibling output profiles. Specimen, vision, dose, and tracked-medication are explicitly adapter-only active types, so base Mobile Provenance cannot admit an unprofiled resource. Adapter source-marker URLs for HealthKit, Health Connect, providers, and SensorKit are all catalog-owned. | exchange protocol, profile-claim and adapter catalogs/schema, producer validator, catalog-parity and graph regressions, language-local consumers |
| VF-32 presentation text treated as structural data | **Closed.** Sensor Recording Document titles are optional Must Support presentation labels, including for inherited HealthKit clinical documents. QuestionnaireResponse item text remains inherited SDC Must Support content but is optional: actors handle it when present, and it may reflect the administered locale. Matching uses the exact versioned Questionnaire, `linkId`, and hierarchy, while Questionnaire prompt text remains required. | Sensor and Questionnaire profiles, paired validator, locale/omission regressions, guide prose |
| VF-33 open active-event payload boundary | **Closed.** Active event entries use an explicit output/support/lifecycle type classification, reject every other R4 resource including DeviceMetric, require exact direct claims for DocumentReference, Device, QuestionnaireResponse, and Provenance, and reject disconnected supporting context. The canonical corpus asserts exact code, reason, location, and severity for each boundary. | exchange protocol/schema, FSH invariants, producer validator, 30-case corpus, Swift/Kotlin/TypeScript validators |
| VF-34 schema formats declared but ignored | **Closed.** Draft 2020-12 URI, date, and date-time assertions are enabled with an exact dependency pin; malformed values have mutation regressions. | JSON Schema runner, package lock, catalog schema tests |
| VF-35 catalog discriminators and fixed claim sets were one-way | **Closed.** HealthKit clinical source identifiers require exactly the R4 clinical profile and admission contract in both directions. Active Device and adapter Provenance claim inventories are exact-one discriminated sets, so duplication cannot hide an omitted mode. | closed catalog schema and duplicate/missing/disguised-mode regressions |
| VF-36 official Validator output/processes could fail open or hang | **Closed.** Only a populated, typed OperationOutcome from the pinned Validator's admitted exit policy is consumed; missing, malformed, stale, symlinked, crash, or bounded-timeout output retries once and then fails closed in both producer and Questionnaire lanes. | official Validator wrappers and mocked infrastructure regressions |
| VF-37 normative retraction base skipped official validation | **Closed.** One schema-validated release-lane manifest sends the exact active and retraction corpus bases through the official Validator and exact Mobile package in PR and release workflows. | official exchange manifest, CI/release commands, manifest regression |

## Design-recommendation disposition

| Recommendation | Disposition |
| --- | --- |
| DR-01 one release authority | Implemented by the release manifest and checker. |
| DR-02 structured identity internally | Implemented by closed kinds/component order and language-specific typed APIs; only the HMAC value crosses the wire. |
| DR-03 entry identity selection | Implemented by the closed priority list, event node keys, and UUIDv5 formatting vectors. |
| DR-04 source preservation vs semantics | Implemented by output modes and source-artifact identities. |
| DR-05 three conformance levels | Implemented in the protocol and producer documentation. |
| DR-06 mutable snapshots | Implemented by stable recording-unit and event-scoped snapshot identities plus application/host separation. |
| DR-07 standard FHIR collections | Implemented; bare FHIR-resource arrays are no longer registered. |
| DR-08 Questionnaire canonical versions | Implemented by exact canonical-plus-version pairing and the shared questionnaire corpus; SDK evaluators must retain the same context rules. |
| DR-09 precise source status | Implemented by the closed status vocabulary, required rationale, and inventory completeness tests. |

## Explicit decisions and approvals

The implementation selects these technical answers to the audit unknowns:

- U-01: hypertension is a notification assertion, not a diagnosis.
- U-02: native source and linkable context identifiers are opaque by default through
  deployment-scoped HMAC identities; no de-identification claim is made.
- U-03: HealthKit metadata is a four-key reviewed mapping, not an open “verbatim” bag.
- U-04: retraction records a source lifecycle assertion. Receiver application semantics
  are configured separately and must resolve every complete Identifier pair atomically.
- U-07: the JSON protocol, schemas, profiles, and corpus are normative; the Python
  producer validator is the repository reference implementation, not a substitute for
  the published FHIR profiles.

The repository cannot self-approve the following. They remain release checklist items,
not hidden technical debt:

1. clinical sign-off on notification, specimen, aggregate, and provider mappings;
2. privacy/security sign-off on key custody, epoch rotation, identifier-system ownership,
   source artifacts, and route/metadata disclosure;
3. backend sign-off on complete-Identifier indexes, retry/conflict behavior, and atomic
   retraction policy;
4. terminology reviewer ratification and the online licensed terminology evidence lane;
5. canonical `grovealliance.org` hosting, package-list ownership, and immutable
   publication governance; and
6. final SDK pins to the committed IG revision plus cross-language corpus/official
   Validator evidence.

Until item 5 is complete, generated sites and packages are release-candidate evidence,
not a claim that canonical publication succeeded.

## Verification expected on the committed candidate

Run all commands against one clean commit and retain their raw output in the release
evidence directory:

```shell
npm ci
./Scripts/build-release.sh --output .build/release-evidence/0.6.0
```

The final cross-repository gate additionally runs each local Swift, Kotlin, and
TypeScript FHIR suite, consumes the exact protocol vectors/corpora, validates generated
resources against the 0.6.0 packages, and records the implementation base and diff.
