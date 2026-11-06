<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Grove assigns separate FHIR Device resources to the hardware that measured a result and the software that saved or converted it.
Keeping those roles separate prevents an application, host device, and sensor from being collapsed into one ambiguous record.

| Role | Resource | Link from Observation |
|---|---|---|
| Physical recorder | [Grove Recording Device](StructureDefinition-grove-recording-device.html), or an external logical Device reference | `Observation.device` |
| Application that mediated or routed the measurement | [Grove Application Device](StructureDefinition-grove-application-device.html) | Standard `observation-gatewayDevice` extension |
| Application that converted the source record | [Grove Application Device](StructureDefinition-grove-application-device.html) | `Provenance.agent.who` |
| Host hardware for an application | [Grove Host Device](StructureDefinition-grove-host-device.html) | `GroveApplicationDevice.parent`, when useful |

### Recording device

`Observation.device` identifies the Device that actually acquired the measurement.
A watch, scale, chest strap, or phone belongs here only when the source supports that claim.
Do not use this element for an application that merely read or transmitted an existing record.
The Grove Mobile contract restricts `Observation.device` to `Device`; `DeviceMetric` is not admitted because no Grove DeviceMetric profile, identity contract, or lifecycle rules are defined.
Use the Grove Recording Device profile when recording hardware is included as a Device entry in the exchange Bundle.

Collect every device fact the source exposes: name, type, manufacturer, model, serial number, UDI, lot number, device identifiers, and every hardware, firmware, software, and operating-system version.
Each adapter catalog lists its source fields and the R4 element each maps to in `recordingDeviceIdentity.fieldMappings`.
The source does not filter its facts; a consumer filters what it does not need, and a deployment that shares or exports data applies its own policy to the sensitive ones, such as a globally linkable serial number or a name a person gave the device.
Every populated version has a type; the type remains open to an appropriate terminology.
Device identifiers must be complete `(system, value)` pairs.
A host-local device identifier that the source exposes, such as HealthKit's `HKDevice.localIdentifier` or SensorKit's `SRSourceDevice.localIdentifier`, is carried clear in the recording Device's `localIdentifier` slice: type `device-local-identifier`, under the deployment's own system.

#### Content snapshot and optional unit identity

Every Grove Recording Device carries exactly one `device-snapshot` identifier, its content key and Bundle entry key.
It is a v0 HMAC over the subject's complete Identifier pair, the node role `recording-device`, and the digest of the Device's complete canonical content minus `id` and minus that identifier, as [`catalog/exchange-protocol.json`](https://grovealliance.org/fhir/catalog/exchange-protocol.json) defines it.
The same content therefore gives the same identifier and fullUrl in every Bundle, and the records of one Bundle that share a Device share one entry.
Firmware, software, operating-system, and descriptive facts are immutable snapshot data: changed content is a new snapshot, and importing older records creates or reuses older snapshots instead of mutating one shared Device according to arrival order.

A snapshot identifier is descriptive.
Manufacturer, model, hardware version, subject, a snapshot, or any digest of those facts cannot establish that two records came from the same physical unit, and two Devices with equal snapshot content are never inferred to be one unit.
Only a `recording-device` identifier proves a physical unit, and it is optional.
A producer emits the recording Device and references it from `Observation.device` whenever the source states the hardware that acquired the measurement, whether or not a governed stable per-unit token exists; it never invents a per-sample identity, and identical content yields one shared snapshot that asserts no physical unit.

When a governed stable per-unit token exists, the Device also carries the deployment-scoped v0 HMAC `recording-device` identity minted from it.
The subject's complete Identifier pair is part of the preimage, preventing the same device token from producing the same identity for different subjects.
So is the token's scope, the authority that assigned the token: a token can be local to one host and writable by other applications, as `HKDevice.localIdentifier` is, so the same token from two writers names two units.
The deployment decides whether source per-unit evidence may be used and manages the HMAC key, epoch, retention, and linkage policy.

See the [recording-device example](Device-GroveRecordingDeviceExample.html).

### Application device

FHIR R4 represents the mobile application as a Device.
The [application-device profile](StructureDefinition-grove-application-device.html) requires an application name and identifier.
When an application version is known, the typed application-version slice uses the ISO 11073 MDC `531975` software-revision code instead of defining a Grove duplicate.
Using this standard version-type code does not make the application a Personal Health Device or require a PHD profile.
An adapter defines the identifier system; for example, a platform adapter can use the platform's application identifier namespace.

The required application identity is an immutable content `device-snapshot` v0 HMAC identifier, with node role `application`, minted over the Device's complete canonical content.
When present, the marketing version and build occupy distinct typed version slices; consumers never parse a composite display convention to recover either value.
Neither value identifies an installation, host, account, or person.
Do not generate a linkable installation identifier unless an explicit use case and privacy policy require it.

The standard `observation-gatewayDevice` extension links an application only when it actually mediated or routed the measurement.
Converting a stored record into FHIR does not by itself make the converter a gateway.
The application's host hardware can be linked through `Device.parent`.
That reference is part of the application Device's content, so the host's identity is folded into the application's: a producer builds the host Device first, and a changed host snapshot changes the application's fullUrl reference, content, and snapshot identifier.
See the [application example](Device-GroveApplicationDeviceExample.html).

Operating-system and host-hardware facts belong on a separate host Device referenced through `Device.parent`; do not add them to the application-version slice.
The host Device carries its own content `device-snapshot` identifier, with node role `host`; its operating-system name, version, and build occupy the typed `os-name`, `os-version`, and `os-build` version slices, and its hardware product type is `Device.modelNumber`.

### Conversion provenance

The gateway link records mediation when it occurred.
A [Grove Mobile Conversion Provenance](StructureDefinition-grove-mobile-conversion-provenance.html) records the transformation itself:

- `target` identifies the resulting Observation;
- `activity` is the standard ISO 21089 lifecycle `transform` code;
- `agent.type` is the standard provenance participant type `assembler`;
- `agent.who` identifies the application Device; and
- `entity` identifies the one source record actually consumed by the transformation.

Always use the typed opaque `entity.what.identifier` source-record identity, including when the source happens to be FHIR.
A literal source Reference is prohibited because it would bypass the one deployment-scoped reconciliation identity.
A PlanDefinition, ResearchStudy, or ResearchSubject is not a Provenance source merely because it provides study context.
Those links follow the study model described on the [Study context](study.html) page.

Use exactly one conversion Provenance for one immutable source-record revision and target every output produced from that record; the revision, its outputs, and that Provenance form one record.
One exchange Bundle carries one or more records, and a producer may pack, split, or repack records into Bundles without changing any of them: each record keeps its own Provenance, and the records share their Devices and other context nodes as single entries.
The [conversion example](Provenance-GroveMobileConversionProvenanceExample.html) shows one source record transformed into its outputs.
The Provenance is keyed by the record's version, the keyed `record-version` Identifier over the source record and the canonical content of the Provenance and its outputs, and repeats it in the [Grove Record Version](StructureDefinition-grove-record-version.html) extension.
A later revision or re-conversion receives a new record version and Provenance assertion while stable logical source/output identifiers remain usable for reconciliation; a receiver selects the current version as [Receiving record versions](implementation.html#receiving-record-versions) describes.

Provenance is the correct place to describe conversion software.
The same application also appears as a gateway only when it performed that distinct mediation role.
Neither role changes the meaning of `Observation.device`, which remains the physical recording Device.
