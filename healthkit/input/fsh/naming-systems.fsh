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
