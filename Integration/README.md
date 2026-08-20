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
fetches the commit by SHA and does not follow the ref when it moves.

This first stack layer verifies the manifest, `.gitmodules`, exact Git commits,
clean submodule checkouts, and proposal metadata and checksums. It does not apply
patches or run external repository code. Later stack layers will add reviewable
patches under `Patches/` and validate them in disposable checkouts. Those checks
must not change a submodule, create an external commit, or push to an external
repository.

Run the source check after initializing the submodules:

```sh
git submodule update --init --depth 1
python3 Scripts/check-integration-sources.py --fetch-targets
```

The temporary integration sources remain part of the unmerged Grove FHIR stack so
contract and implementation changes can be reviewed together. Once the external
changes are approved and represented by real commits, proposal patches can be
replaced with immutable commit pins and the temporary submodules can be removed in
a separately reviewed change.
