<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

# Identifier systems in the prototype

FHIR token matching uses the complete `(system, value)` pair. The current combined
prototype defines these Grove-owned system URIs:

| System | Intended value |
|---|---|
| `https://grovealliance.org/fhir/sid/healthkit-sample-id` | HealthKit object UUID |
| `https://grovealliance.org/fhir/sid/device-local-id` | Source-platform device identifier when no standard hardware identifier is available |
| `https://grovealliance.org/fhir/sid/apple-bundle-id` | Apple application bundle identifier |
| `https://grovealliance.org/fhir/sid/sensorkit-sample-id` | Prototype SensorKit sample identity |
| `https://grovealliance.org/fhir/sid/health-connect-record-id` | Prototype Health Connect record identity |
| `https://grovealliance.org/fhir/sid/android-application-id` | Android application identifier |

Only the HealthKit, device-local, and Apple bundle identifier mappings currently have
Grove Swift implementation evidence. The remaining systems do not establish a stable
exchange contract.

### Receiver behavior in the combined prototype

The current `GroveDataReceiver` CapabilityStatement is a requirements artifact. It
describes transaction uploads and conditional create for Observation and
DocumentReference resources. Under that prototype, an uploader supplies
`ifNoneExist: identifier={system}|{value}` and a receiver compares the complete token.

Grove does not implement that receiver. The CapabilityStatement and its conditional-
create behavior are therefore not part of the proposed stable contract.
