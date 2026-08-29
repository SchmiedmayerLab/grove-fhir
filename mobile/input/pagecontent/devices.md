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

Populate the device name, type, manufacturer, model, and versions when the source makes them available.
Every populated version has a type; the type remains open to an appropriate terminology.
Device identifiers must be complete `(system, value)` pairs.
Use a study- or deployment-scoped identifier unless a broader hardware identifier is both necessary and authorized; serial numbers and globally linkable hardware identifiers are not exchange defaults.

#### Stable unit and immutable snapshot

A shared recording Device is emitted only when the producer has a governed stable token for the physical acquisition unit.
Manufacturer, model, hardware version, subject, or any digest of those descriptive facts cannot establish that two records came from the same physical unit.
If no governed stable per-unit token is available, omit `Observation.device`; never mint a fresh per-sample Device or merge all devices of one model.

The per-unit token is never emitted directly.
It participates in the deployment-scoped v0 HMAC `recording-device` identity defined by [`catalog/exchange-protocol.json`](https://grovealliance.org/fhir/catalog/exchange-protocol.json).
The subject's complete Identifier pair is also part of the preimage, preventing the same device token from producing the same identity for different subjects.
The deployment decides whether source per-unit evidence may be used and manages the HMAC key, epoch, retention, and linkage policy.

Every emitted Grove Recording Device also carries an event-scoped `device-snapshot` identity, which is the Bundle entry key.
Firmware, software, operating-system, and descriptive facts are captured as immutable event-time snapshot data.
Importing older events therefore creates older snapshots instead of mutating one shared Device according to arrival order.

See the [recording-device example](Device-GroveRecordingDeviceExample.html).

### Application device

FHIR R4 represents the mobile application as a Device.
The [application-device profile](StructureDefinition-grove-application-device.html) requires an application name and identifier.
When an application version is known, the typed application-version slice uses the ISO 11073 MDC `531975` software-revision code instead of defining a Grove duplicate.
Using this standard version-type code does not make the application a Personal Health Device or require a PHD profile.
An adapter defines the identifier system; for example, a platform adapter can use the platform's application identifier namespace.

The required application identity is an immutable event-scoped `device-snapshot` v0 HMAC identifier.
When present, the marketing version and build occupy distinct typed version slices; consumers never parse a composite display convention to recover either value.
Neither value identifies an installation, host, account, or person.
Do not generate a linkable installation identifier unless an explicit use case and privacy policy require it.

The standard `observation-gatewayDevice` extension links an application only when it actually mediated or routed the measurement.
Converting a stored record into FHIR does not by itself make the converter a gateway.
The application's host hardware can be linked through `Device.parent`; it is not folded into the application's identity.
See the [application example](Device-GroveApplicationDeviceExample.html).

Operating-system and host-hardware versions belong on a separate host Device referenced through `Device.parent`; do not add them to the application-version slice.

### Conversion provenance

The gateway link records mediation when it occurred.
A [Grove Mobile Conversion Provenance](StructureDefinition-grove-mobile-conversion-provenance.html) records the transformation event itself:

- `target` identifies the resulting Observation;
- `activity` is the standard ISO 21089 lifecycle `transform` code;
- `agent.type` is the standard provenance participant type `assembler`;
- `agent.who` identifies the application Device; and
- `entity` identifies the one source record actually consumed by the transformation.

Always use the typed opaque `entity.what.identifier` source-record identity, including when the source happens to be FHIR.
A literal source Reference is prohibited because it would bypass the one deployment-scoped reconciliation identity.
A PlanDefinition, ResearchStudy, or ResearchSubject is not a Provenance source merely because it provides study context.
Those links follow the study model described on the [Study context](study.html) page.

Use exactly one conversion Provenance for one immutable source-record revision and target every output produced from that record.
A transport may batch already-complete event Bundles, but it must not merge their semantic units.
The [conversion example](Provenance-GroveMobileConversionProvenanceExample.html) shows one source record transformed into its output graph.
A later revision receives a new event identity and Provenance assertion while stable logical source/output identifiers remain usable for reconciliation.

Provenance is the correct place to describe conversion software.
The same application also appears as a gateway only when it performed that distinct mediation role.
Neither role changes the meaning of `Observation.device`, which remains the physical recording Device.
