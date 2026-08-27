//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Instance: AndroidPackageName
InstanceOf: NamingSystem
Usage: #definition
Title: "Android Package Name"
Description: "The identifier namespace for an Android application package name used by an identifier-only Health Connect DataOrigin application Reference."
* id = "android-package-name"
* name = "AndroidPackageName"
* status = #active
* kind = #identifier
* date = "2026-08-19"
* publisher = "Schmiedmayer Lab"
* description = "Identifies an Android application product by package name. Health Connect DataOrigin.packageName uses this namespace. Together with a typed application version when that version is independently known, it identifies an application product and build, not an installation, host, account, or person."
* uniqueId.type = #uri
* uniqueId.value = $androidPackageName
* uniqueId.preferred = true
