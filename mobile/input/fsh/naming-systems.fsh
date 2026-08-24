// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT

Instance: GroveWriterRecordIdentifier
InstanceOf: NamingSystem
Usage: #definition
Title: "Grove Writer Record Identifier"
Description: "The identifier namespace for the logical record an application assigned to a measurement it wrote onto a platform store."
* id = "grove-writer-record-id"
* name = "GroveWriterRecordIdentifier"
* status = #active
* kind = #identifier
* date = "2026-08-24"
* publisher = "Schmiedmayer Lab"
* description = "Identifies the logical measurement behind a stored record, as named by the application that wrote it: HKMetadataKeySyncIdentifier on HealthKit, clientRecordId on Health Connect. A platform replaces the stored record when the same writer saves a higher version of the same logical record, and the replacement carries a new platform row identifier, so this namespace names the measurement while the platform's own namespace names the row it was read from. Writer identifiers are unique only within the writing application, so the value scopes one to its writer: the scheme version `v1:`, the writer's reverse-DNS application identifier, a vertical bar, then the writer's own identifier. Neither part may contain a vertical bar. One namespace serves every platform adapter, so the same application writing the same logical record on more than one platform produces the same complete identifier; a receiver may use that to recognise one measurement reaching it by more than one route, but must not depend on it, because nothing obliges an application to reuse either its identifier or its reverse-DNS name across platforms."
* uniqueId.type = #uri
* uniqueId.value = $groveWriterRecordId
* uniqueId.preferred = true
