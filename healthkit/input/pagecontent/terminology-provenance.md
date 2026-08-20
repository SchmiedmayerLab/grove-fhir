<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

The HealthKit-specific terminology in version 0.2.0 is case-sensitive. It contains a
closed 220-concept platform source-type inventory, one metadata key, and three adapter
motion-context codes required by the heart-rate mapping. The separately declared sleep
duration aggregate is not a platform source type and is excluded from the source-type
CodeSystem.

The version-controlled manifest is
[`healthkit/input/data/terminology-provenance.json`](https://github.com/SchmiedmayerLab/grove-fhir/blob/main/healthkit/input/data/terminology-provenance.json).
It records the following reproducibility information:

| Field | Value |
|---|---|
| Package | `org.grovealliance.fhir.healthkit#0.2.0` |
| SDK baseline | iPhoneOS 27.0, Xcode 27.0 build 27A5237l |
| Extraction date | 2026-08-20 |
| Selection method | Every declared identifier constant resolved inside an iOS simulator on the SDK baseline, plus the two sample types Apple publishes without a constant, read by `Scripts/platform_inventory.py` |
| SDK inputs | `HKTypeIdentifiers.h`, `HKObjectType.h`, `HKMetadata.h`, and `HKMetadataEnums.h`, with SHA-256 hashes in the manifest |
| Case sensitivity | Case-sensitive |
| Content scope | Complete for the 220 source-type identifiers and the adapter terminology frozen by v0.2.0 |

The retained identifiers and type names originate from Apple. The SDK baseline,
official platform documentation, and catalog together bind the source-type inventory;
the hashed metadata headers bind `HKMetadataKeyHeartRateMotionContext` and the three
motion-context cases. The mapping narrative also refers descriptively to source API
fields such as `HKObject.uuid`, `HKSource.bundleIdentifier`, `HKSourceRevision`,
`HKDevice`, and `HKMetadataKeyWasUserEntered`. All names are used only to identify source
API concepts for interoperability; the package does not copy SDK implementation,
private API, or documentation prose.
The repository's MIT license applies to Grove-authored repository material, while the
retained Apple names remain attributed in the manifest.

For `HKMetadataKeyHeartRateMotionContext`, the mapping preserves the source NSNumber:
`0` maps to the adapter code `not-set`, `1` to `sedentary`, and `2` to `active`. These
lower-case values are codes in the adapter's FHIR CodeSystem, not source numeric values.
An unknown value is rejected or omitted; it is never treated as `not-set`.
