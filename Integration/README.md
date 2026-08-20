<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

# Integration proposals

This directory pins the public source evidence used to design cross-repository
contract changes. There is one physical submodule checkout per exact source commit,
so several paths can intentionally name the same repository at different revisions.
`sources.json` records each checkout's commit and reviewer-facing purpose. A source
that no proposal references is provenance-only; the inactive SensorKit tip and the
two StudyDefinitions revisions are retained this way. The historical Grove 0.2.1
checkout is active only as the exact producer of frozen compatibility bytes.

The source check requires the manifest source set, `.gitmodules` source set, and
stage-zero gitlink set to match exactly. It verifies every initialized checkout's
detached `HEAD`, clean status, origin URL, exact commit, proposal metadata, and patch
checksum without resolving or fetching any branch, tag, pull-request ref, or target.
The proposal check then creates a new detached repository from the selected physical
source. A selected proposal requires initialized checkouts only for its dependency and
application closure; every declared source is still matched to its stage-zero gitlink,
and the dedicated source check remains the full-set gate. Before materializing, the
proposal validator proves each required checkout has the declared detached `HEAD`, a
clean status, and the declared origin. It runs `git apply --check` before applying every
patch, runs only explicitly declared test commands, and deletes the repository afterward.
The validator does not give a temporary repository a remote, create a branch or commit,
follow a mutable ref, or write into a source checkout. Git lazy fetching is disabled, so
every required object must already be present in the exact physical checkout.

Run the source check after initializing the submodules:

```sh
git submodule update --init --depth 1
python3 Scripts/check-integration-sources.py
python3 Scripts/validate-integration-proposals.py \
  --platform linux \
  --test-group portable
```

## Physical source schema

Schema version 3 gives every exact commit its own source ID and gitlink:

```json
{
  "id": "grove-healthkit",
  "repository": "https://github.com/SchmiedmayerLab/Grove.git",
  "path": "Integration/Sources/GroveHealthKit",
  "commit": "fb78db4c5343c234825b433706f7ee62f111c5cc",
  "purpose": "Exact Grove Mobile and HealthKit proposal base."
}
```

There are no source refs, nested targets, moving-tip resolution, or source-level
predecessors. A source participates in materialization only when a proposal names its
ID; otherwise its `purpose` explains why the exact revision remains review evidence.

## Proposal dependencies

`dependsOn` controls validation order and may refer to a proposal for any source.
It does not compose patches. `appliesAfter` opts into patch composition: each named
proposal must also be in `dependsOn`, and the two physical source IDs must normalize
to the same repository URL. The validator materializes the child proposal's exact
source commit, then checks and applies the declared patch chain there. This makes
composition across two pinned revisions an explicit, tested claim rather than an
assumption; source array order and mutable Git refs carry no semantics.

Tests are optional. When present, each command names an explicit execution `group`,
the platforms on which that complete group may run, a repository-relative `cwd`,
and an `argv` array. The validator requires both `--platform` and `--test-group`;
it refuses to run a group on another platform. An optional, repeatable `--proposal`
selects one proposal and its dependency closure. For example:

```json
{
  "id": "grove-mobile-contract",
  "source": "grove-healthkit",
  "patch": "Integration/Patches/grove-mobile-contract.patch",
  "sha256": "<64 lowercase hexadecimal characters>",
  "dependsOn": [],
  "appliesAfter": [],
  "tests": [
    {
      "group": "portable",
      "platforms": ["linux", "macos"],
      "cwd": ".",
      "argv": ["git", "diff", "--check"]
    }
  ],
  "claims": ["Grove emits resources conforming to the mobile contract."]
}
```

The manifest contains the reviewable Grove Swift Questionnaire and Mobile contracts,
the exact legacy-writer/current-reader compatibility boundary, the current My Heart
Counts iOS study-enrollment writer evidence, the My Heart Counts Android Health Connect
adapter, and the My Heart Counts Firebase receiver proposals with their exact checksums.
The Questionnaire patch is applied before the Mobile patch when the later Grove revision
is tested. The current-reader proposal applies only those two current patches; its
dependency on the exact 0.2.1 writer orders the external evidence but does not apply the
historical patch to the current checkout. Every composed patch is explicit and
apply-checked. Portable checks may run on Linux or macOS. Swift contract,
compatibility-evidence, and emitted-resource checks run only on macOS. Android and
Firebase contract tests run on either platform.

## Compatibility evidence

The historical fixture invokes the real Grove 0.2.1 `HKSample.resource(...)` conversion
at `7fbc89d590ee29d9e73b9d700f91aa1e3d905883`, rather than reconstructing a presumed
Observation with current code. It freezes the retired sample identity, eight-field
source device, nested source revision, and metadata wire trees. HealthKit gives an
unsaved CI sample no publicly constructible `HKSource`, so the production output
truthfully omits the optional source-revision version, product type, and OS-version
leaves. Determinism changes only five volatile production leaves: `Observation.id`,
`identifier[0].id`, `identifier[0].value`, and the existing retired source-revision
`source/name` and `source/bundleIdentifier` values. The replacement source name and
bundle are fixture normalizations, not real `HKSource` identity; the fixture neither
fabricates an `HKSource` nor hand-builds the extension graph.

The composed current Grove checkout at
`fb78db4c5343c234825b433706f7ee62f111c5cc` decodes those exact full bytes. It tests
every retired tree present, bounded lookup and canonical precedence for both declared
device and revision identifiers, and canonical-only new writes. Retired metadata is
checked exactly but is not misrepresented as a reproducible dual-write shape. The
deterministic fixture path is
`Compatibility/Fixtures/grove-0.2.1-healthkit-sample.json`; its SHA-256 is
`46be7e8e1076af82d5fe6e0ca028da554b51de91db2605addd81342fc1d03191`.
When `GROVE_COMPATIBILITY_EXPORT` names an absolute repository-external file, the
historical writer copies its verified output there. The sequential current-reader gate
loads that exported file, requires it to equal the tracked golden byte-for-byte, and
then decodes those actual producer bytes; standalone runs fall back to the golden.

The My Heart Counts iOS proposal freezes the production study-enrollment extension
writer at `e7ae70ebbbfb335eea274cd35eacd5d3c5c93d33`, applied to a deterministic full
core-R4 heart-rate Observation with Vital Signs category, code, patient subject,
effective time, and value.
Its deterministic fixture path is
`Compatibility/Fixtures/my-heart-counts-ios-e7ae-study-enrollment.json`; its SHA-256 is
`e3e94f9068defe7801e68e1e81a741bb7624ca2431dbb0ba6da812151727e906`. This is
legacy-candidate provenance only: Grove does not consume it here, the URL is not
declared canonical, and My Heart Counts is not migrated. The accepted
ResearchStudy/PlanDefinition/ResearchSubject/Provenance graph remains a separate
Grove FHIR-owned fixture/corpus; application migration is deferred.
`MHC_COMPATIBILITY_EXPORT` may name an absolute repository-external directory; the
verified candidate is then exported as
`my-heart-counts-ios-e7ae-study-enrollment.json` for the evidence lock.

The Android proposal is a reusable adapter rather than proof that the My Heart Counts
application deploys Health Connect. The Firebase proposal is a structurally validated
receiver library; it deliberately does not expose an intake endpoint or choose an
authenticated caller-to-partition mapping. Those deployment decisions and end-to-end
evidence belong to the later conformance layer.

The temporary integration sources remain part of the unmerged Grove FHIR stack so
contract and implementation changes can be reviewed together. Once the external
changes are approved and represented by real commits, proposal patches can be
replaced with immutable commit pins and the temporary submodules can be removed in
a separately reviewed change.
