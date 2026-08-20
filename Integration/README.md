<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

# Integration proposals

This directory pins the public source evidence used to design cross-repository
contract changes. There is one submodule per external repository. `sources.json`
records its exact gitlink plus any additional commits that participate in the Grove
FHIR work. A target's `ref` identifies where that commit was observed; validation
fetches the ref only to prove that the pinned commit remains in its history, then
materializes the proposal at the exact SHA rather than the moving ref tip.

The source check verifies the manifest, `.gitmodules`, exact Git commits, clean
submodule checkouts, and proposal metadata and checksums. The proposal check then
creates a new detached repository for each proposal at its declared target commit.
It runs `git apply --check` before applying every patch, runs only explicitly
declared test commands, and deletes the repository afterward. The validator does
not give a temporary repository a remote, create a branch or commit, follow a
mutable ref, or write into a submodule checkout. It disables Git lazy fetching;
every target object must already be present after the source check fetches its
declared SHA.

Run the source check after initializing the submodules:

```sh
git submodule update --init --depth 1
python3 Scripts/check-integration-sources.py --fetch-targets
python3 Scripts/validate-integration-proposals.py \
  --platform linux \
  --test-group portable
```

## Proposal dependencies

`dependsOn` controls validation order and may refer to a proposal for any source.
It does not compose patches. `appliesAfter` opts into patch composition: each named
proposal must also be in `dependsOn` and must use the same source repository. The
validator materializes the child proposal's exact target, then checks and applies
the declared patch chain there. This makes a rebase across two pinned commits an
explicit, tested claim rather than an assumption.

Tests are optional. When present, each command names an explicit execution `group`,
the platforms on which that complete group may run, a repository-relative `cwd`,
and an `argv` array. The validator requires both `--platform` and `--test-group`;
it refuses to run a group on another platform. An optional, repeatable `--proposal`
selects one proposal and its dependency closure. For example:

```json
{
  "id": "grove-sensor-contract",
  "source": "grove",
  "target": "sensorkit",
  "patch": "Integration/Patches/grove-sensor-contract.patch",
  "sha256": "<64 lowercase hexadecimal characters>",
  "dependsOn": ["grove-mobile-contract"],
  "appliesAfter": ["grove-mobile-contract"],
  "tests": [
    {
      "group": "portable",
      "platforms": ["linux", "macos"],
      "cwd": ".",
      "argv": ["git", "diff", "--check"]
    }
  ],
  "claims": ["Grove emits resources conforming to the sensor contract."]
}
```

The manifest contains the reviewable Grove Swift Mobile contract, My Heart Counts
Android Health Connect adapter, and My Heart Counts Firebase receiver proposals with
their exact checksums. Portable checks may run on Linux or macOS. The Swift contract
and emitted-resource checks run only on macOS. Android and Firebase contract tests
run on either platform. The Android proposal is a reusable adapter rather than proof
that the My Heart Counts application deploys Health Connect. The Firebase proposal is
a structurally validated receiver library; it deliberately does not expose an intake
endpoint or choose an authenticated caller-to-partition mapping. Those deployment
decisions and end-to-end evidence belong to the later conformance layer.

The temporary integration sources remain part of the unmerged Grove FHIR stack so
contract and implementation changes can be reviewed together. Once the external
changes are approved and represented by real commits, proposal patches can be
replaced with immutable commit pins and the temporary submodules can be removed in
a separately reviewed change.
