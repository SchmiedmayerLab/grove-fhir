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
historical Grove and StudyDefinitions revisions are retained this way.

The source check requires the manifest source set, `.gitmodules` source set, and
stage-zero gitlink set to match exactly. It verifies every initialized checkout's
detached `HEAD`, clean status, origin URL, exact commit, proposal metadata, and patch
checksum without resolving or fetching any branch, tag, pull-request ref, or target.
The proposal check then creates a new detached repository from the selected physical
source. It runs `git apply --check` before applying every patch, runs only explicitly
declared test commands, and deletes the repository afterward. The validator does not
give a temporary repository a remote, create a branch or commit, follow a mutable ref,
or write into a source checkout. Git lazy fetching is disabled, so every required
object must already be present in the exact physical checkout.

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
the My Heart Counts Android Health Connect adapter, and the My Heart Counts Firebase
receiver proposals with their exact checksums. The Questionnaire patch is applied
before the Mobile patch when the later Grove revision is tested, making that composition
an explicit gate. Portable checks may run on Linux or macOS. The Swift contract and
emitted-resource checks run only on macOS. Android and Firebase contract tests run on
either platform. The Android proposal is a reusable adapter rather than proof that the
My Heart Counts application deploys Health Connect. The Firebase proposal is a
structurally validated receiver library; it deliberately does not expose an intake
endpoint or choose an authenticated caller-to-partition mapping. Those deployment
decisions and end-to-end evidence belong to the later conformance layer.

The temporary integration sources remain part of the unmerged Grove FHIR stack so
contract and implementation changes can be reviewed together. Once the external
changes are approved and represented by real commits, proposal patches can be
replaced with immutable commit pins and the temporary submodules can be removed in
a separately reviewed change.
