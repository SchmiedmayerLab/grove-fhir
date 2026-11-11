//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

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

Instance: HealthKitDeviceLocalIdentifierExample
InstanceOf: NamingSystem
Usage: #example
Title: "Example HealthKit Device Local Identifier Namespace"
Description: "An example deployment-owned namespace for the clear HKDevice.localIdentifier a recording Device carries. The value is local to the host that recorded it, so a deployment names its own system; production deployments define their own immutable URI."
* name = "HealthKitDeviceLocalIdentifierExample"
* status = #active
* kind = #identifier
* date = "2026-11-02"
* publisher = "Example Study"
* uniqueId.type = #uri
* uniqueId.value = "https://study.example.org/fhir/NamingSystem/healthkit-device-local-identifier"
* uniqueId.preferred = true
