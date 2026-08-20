<!--
SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
SPDX-License-Identifier: MIT
-->

# Conformance evidence

This directory defines the reproducible evidence contract for the current Grove FHIR
implementation guides. It separates reviewable expectations from build-specific byte
hashes:

- `evidence.json` declares guides, semantic artifacts, fixture corpora, implementation
  provenance, classifications, and the repository path matrix.
- `toolchain.json` pins the exact direct tools and every downloaded JAR or FHIR package
  by SHA-256.
- `evidence.schema.json` is the JSON Schema 2020-12 contract for both declarative files
  and the generated evidence lock.
- `evidence-lock.json` exists only in generated evidence. It records the current source
  revision and hashes the complete input, proposal, gitlink, resolved-package, FHIR
  package, dependency, corpus, and output closure.

The declarative manifest intentionally contains no hash of a guide package produced by
the same revision. Package byte hashes belong in the generated lock, avoiding a
self-referential checked-in update.

## Build order

The CI build performs these operations exactly once:

1. Build all four guides.
2. Assemble and sanitize the Pages tree, including each `ci-build/package.tgz`.
3. Build semantic snapshots and the evidence lock from those exact sanitized package
   bytes.
4. Verify the lock and deterministic archive.
5. Inject the lock, manifest, schema, toolchain pins, and archive into the already
   assembled Pages tree.

Later jobs download those artifacts. They do not rebuild a guide or substitute a raw
`output/package.tgz`.

The evidence build intentionally has no fallback to checked-in or previously generated
implementation fixtures. First run the exact proposal groups and stage the eight
manifest-declared sets at the same paths used below (the command block does not create
those platform fragments). Then, from a clean checkout, build the guides and generate
the locked domain report with the complete inventory:

```console
npm ci
npm run schema:validate
npm run pages:build
python3 Scripts/validate-study-graph.py
node Scripts/validate-receiver-evidence.cjs --external-evidence my-heart-counts-android-wire=.build/fragments/linux/android-wire --require-external-evidence
python3 Scripts/validate-heart-rate-equivalence.py --external-evidence grove-current-resources=.build/fragments/mac/grove-current-resources --external-evidence my-heart-counts-android-conformance=.build/fragments/linux/android-conformance --require-implementation-fixtures
python3 Scripts/validate-domain-fhir.py \
  --evidence Conformance/evidence.json \
  --toolchain Conformance/toolchain.json \
  --tools-directory .build/fhir-tools \
  --require-external-evidence \
  --external-evidence grove-questionnaire-resources=.build/fragments/mac/grove-questionnaire-resources \
  --external-evidence grove-current-resources=.build/fragments/mac/grove-current-resources \
  --external-evidence my-heart-counts-android-conformance=.build/fragments/linux/android-conformance \
  --external-evidence my-heart-counts-android-wire=.build/fragments/linux/android-wire \
  --external-evidence firebase-lifecycle-result=.build/fragments/linux/firebase-lifecycle-result.json \
  --external-evidence grove-legacy-healthkit-sample=.build/fragments/mac/grove-0.2.1-healthkit-sample.json \
  --external-evidence grove-current-reader-result=.build/fragments/mac/grove-current-reader-result.json \
  --external-evidence mhc-ios-study-enrollment=.build/fragments/mac/my-heart-counts-ios-e7ae-study-enrollment.json \
  --report .build/conformance/domain-fhir-validation.json
python3 Scripts/build-conformance-evidence.py build \
  --external-evidence grove-questionnaire-resources=.build/fragments/mac/grove-questionnaire-resources \
  --external-evidence grove-current-resources=.build/fragments/mac/grove-current-resources \
  --external-evidence my-heart-counts-android-conformance=.build/fragments/linux/android-conformance \
  --external-evidence my-heart-counts-android-wire=.build/fragments/linux/android-wire \
  --external-evidence firebase-lifecycle-result=.build/fragments/linux/firebase-lifecycle-result.json \
  --external-evidence grove-legacy-healthkit-sample=.build/fragments/mac/grove-0.2.1-healthkit-sample.json \
  --external-evidence grove-current-reader-result=.build/fragments/mac/grove-current-reader-result.json \
  --external-evidence mhc-ios-study-enrollment=.build/fragments/mac/my-heart-counts-ios-e7ae-study-enrollment.json \
  --validation-report domain-fhir-validation=.build/conformance/domain-fhir-validation.json
python3 Scripts/check-evidence-lock.py full
python3 Scripts/build-conformance-evidence.py inject-pages
```

The two Grove resource directories are deliberately disjoint even though Mobile
materialization applies the Questionnaire proposal first: the Questionnaire set owns
Questionnaire/QuestionnaireResponse and a canonical attestation over their exact bytes,
while the Mobile/HealthKit set owns its six FHIR resources and a separate canonical
attestation. Raw Validator transcripts are never published because they contain
machine-specific paths and timings; the path-free domain report independently validates
every declared FHIR resource. The current-reader attestation is owned by a distinct
reader implementation at the same Grove source commit.

Accepted-contract FHIR sets are validated against the complete accepted guide-package
closure. Historical-writer and legacy-candidate sets instead run in a separate core-R4
Validator invocation: their retired extension trees remain exact evidence rather than
being reintroduced as active StructureDefinitions. Each such set declares every expected
unknown extension by file, FHIR expression, URL, and value field. The gate requires the
resource shape and the Validator's `Extension_EXT_Unknown_NotHere` errors to match that
declaration one-to-one; a missing, extra, moved, renamed, or differently represented
extension, or any other error, fails validation.

For an intentionally supplied package, `build` accepts one or more
`--package GUIDE=PATH` options. The package must have the declared identity, version,
canonical URL, FHIR version, and dependency map. The generated lock records
`inputMode: "override"`, the guide identity, and the resulting byte and semantic hashes;
it never records the caller's machine-specific absolute path.

To deliberately refresh reviewed package semantics after an accepted guide change,
run `python3 Scripts/build-conformance-evidence.py update-semantic-baseline` against the
exact sanitized Pages packages and inspect the resulting base-to-head semantic diff.
Normal evidence builds fail on a stale baseline and never update it implicitly.

## Evidence classifications

Classification is explicit and is not inferred from age or repository location:

- `accepted-contract` is active conformance evidence for an accepted Grove FHIR
  contract.
- `historical-writer` is a real earlier writer retained for compatibility evidence.
- `legacy-candidate` is a pinned current implementation that may require a bounded
  migration; it is not described as already migrated.
- `inactive-reference` preserves provenance without activating an obsolete shape.
- `dependency-pin` records an exact dependency revision separately from a source
  repository state or nested gitlink.

Accepted, historical, and legacy-candidate entries must name a generator introduced or
executed by their exact integration proposal. Dependency and inactive entries cannot
claim a generator. In particular, the My Heart Counts iOS gitlink, its SwiftPM-selected
StudyDefinitions package, and the later StudyDefinitions repository state remain three
separate provenance facts.

## Determinism and verification

JSON is encoded canonically and parsed without duplicate keys, non-finite values, or
decimal precision loss. Fixture corpora and Conformance inputs are hashed recursively.
FHIR package snapshots retain authored conformance semantics and examples while
normalizing only documented Publisher build noise. The evidence archive uses sorted
regular files, fixed ownership and modes, and the exact source commit epoch for every
tar member and the gzip header. That epoch is recorded in the lock and verified on
replay.

`check-evidence-lock.py full` rejects source drift, stale or added evidence files,
package substitution, semantic snapshot drift, proposal or gitlink changes, incorrect
source revisions, and archive differences. Documentation deployment uses
`check-evidence-lock.py site` to prove that the downloaded Pages artifact carries the
same source revision as the successful main-branch Build and Test run.

This evidence is for the continuously replaced `ci-build` publication. It does not
create immutable releases or introduce release-version behavior.

The public contract is rooted at `/conformance/ci-build/`: `evidence-lock.json`,
`corpus.tgz`, `corpus.tgz.sha256`, and `semantic-diff.json`/`semantic-diff.md` are stable
routes for reviewers and automation.
