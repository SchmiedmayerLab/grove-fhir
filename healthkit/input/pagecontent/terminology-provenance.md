<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

The HealthKit-specific terminology in version 0.1.0 is a case-sensitive allowlist. It
contains one metadata key and three adapter motion-context codes required by the
heart-rate mapping; it is not a copy of the HealthKit SDK vocabulary.

The version-controlled manifest is
[`healthkit/input/data/terminology-provenance.json`](https://github.com/SchmiedmayerLab/grove-fhir/blob/main/healthkit/input/data/terminology-provenance.json).
It records the following reproducibility information:

| Field | Value |
|---|---|
| Package | `org.grovealliance.fhir.healthkit#0.1.0` |
| SDK baseline | iPhoneOS 27.0, Xcode 27.0 build 27A5237l |
| Extraction date | 2026-08-19 |
| Selection method | Manual allowlist using ripgrep 15.2.0 |
| SDK inputs | `HKMetadata.h` and `HKMetadataEnums.h`, with SHA-256 hashes in the manifest |
| Case sensitivity | Case-sensitive |
| Content scope | Complete for this adapter version's allowlist, not for the HealthKit SDK |

The retained identifiers and type names originate from Apple. The hashed SDK headers
support the terminology allowlist: `HKMetadataKeyHeartRateMotionContext` and the three
motion-context cases. The mapping narrative also refers descriptively to source API
fields such as `HKObject.uuid`, `HKSource.bundleIdentifier`, `HKSourceRevision`,
`HKDevice`, and `HKMetadataKeyWasUserEntered`; those references are not a copied platform
vocabulary. All names are used only to identify source API concepts for interoperability;
the package does not copy SDK implementation, documentation prose, or a general
HealthKit vocabulary.
The repository's MIT license applies to Grove-authored repository material, while the
retained Apple names remain attributed in the manifest.

For `HKMetadataKeyHeartRateMotionContext`, the mapping preserves the source NSNumber:
`0` maps to the adapter code `not-set`, `1` to `sedentary`, and `2` to `active`. These
lower-case values are codes in the adapter's FHIR CodeSystem, not source numeric values.
An unknown value is rejected or omitted; it is never treated as `not-set`.
