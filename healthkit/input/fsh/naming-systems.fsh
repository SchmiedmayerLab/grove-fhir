//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Instance: HealthKitObjectIdentifier
InstanceOf: NamingSystem
Usage: #definition
Title: "HealthKit Object Identifier"
Description: "The identifier namespace for HKObject.uuid values carried by HealthKit-derived Observations."
* id = "healthkit-object-id"
* name = "HealthKitObjectIdentifier"
* status = #active
* kind = #identifier
* date = "2026-08-19"
* publisher = "Schmiedmayer Lab"
* description = "Identifies the source HealthKit object by the UUID exposed through HKObject.uuid. The value uses lowercase 8-4-4-4-12 hyphenated UUID text. Compare the complete system and value pair; this namespace does not assert identity of a universal clinical record."
* uniqueId.type = #uri
* uniqueId.value = $healthKitObjectId
* uniqueId.preferred = true

Instance: AppleBundleIdentifier
InstanceOf: NamingSystem
Usage: #definition
Title: "Apple Bundle Identifier"
Description: "The identifier namespace for an Apple application bundle identifier used on a Grove Application Device."
* id = "apple-bundle-id"
* name = "AppleBundleIdentifier"
* status = #active
* kind = #identifier
* date = "2026-08-19"
* publisher = "Schmiedmayer Lab"
* description = "Identifies an Apple application product by its bundle identifier. Together with a typed Device version it identifies the product and build for provenance, not an installation, host, account, or person."
* uniqueId.type = #uri
* uniqueId.value = $appleBundleId
* uniqueId.preferred = true

Instance: HealthKitSourceDeviceIdentifier
InstanceOf: NamingSystem
Usage: #definition
Title: "HealthKit Source Device Identifier"
Description: "The identifier namespace for a device UUID supplied through HKSource.bundleIdentifier for a supported Bluetooth Low Energy source."
* id = "healthkit-source-device-id"
* name = "HealthKitSourceDeviceIdentifier"
* status = #active
* kind = #identifier
* date = "2026-08-19"
* publisher = "Schmiedmayer Lab"
* description = "Carries the opaque device UUID HealthKit supplies through HKSource.bundleIdentifier for a supported Bluetooth Low Energy source. The identifier is linkable wherever the exact value recurs, but HealthKit does not specify a broader stability or hardware-identity scope. Exchange it only when the use case and privacy policy authorize that linkability. Application sources use the Apple Bundle Identifier namespace instead."
* uniqueId.type = #uri
* uniqueId.value = $healthKitSourceDeviceId
* uniqueId.preferred = true
