<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Grove assigns separate FHIR Device resources to the hardware that measured a result and
the software that saved or converted it. Keeping those roles separate prevents an app,
phone, and sensor from being collapsed into one ambiguous record.

| Role | Resource | Link from Observation |
|---|---|---|
| Physical recorder or metric | Device or DeviceMetric; [Grove Recording Device](StructureDefinition-grove-recording-device.html) when its rules fit | `Observation.device` |
| App that mediated or routed the measurement | [Grove Application Device](StructureDefinition-grove-application-device.html) | Standard `observation-gatewayDevice` extension |
| App that converted the source record | [Grove Application Device](StructureDefinition-grove-application-device.html) | `Provenance.agent.who` |
| Host hardware for an app | Base FHIR Device | `GroveApplicationDevice.parent`, when useful |

### Recording device

`Observation.device` identifies the Device or DeviceMetric that actually acquired the
measurement. A watch, scale, chest strap, or phone belongs here only when the source
supports that claim. Do not use this element for an app that merely read or transmitted
an existing record. The reference remains open to base FHIR Device and DeviceMetric;
use Grove Recording Device when its shared hardware rules apply.

Populate the device name, type, manufacturer, model, and versions when the source makes
them available. Every populated version has a type; the type remains open to an
appropriate terminology. Device identifiers must be complete `(system, value)` pairs.
Use a study- or deployment-scoped identifier unless a broader hardware identifier is
both necessary and authorized; serial numbers and globally linkable hardware
identifiers are not exchange defaults.

See the [recording-device example](Device-GroveRecordingDeviceExample.html).

### Application device

FHIR R4 represents the mobile application as a Device. The
[application-device profile](StructureDefinition-grove-application-device.html) requires
an application name and identifier. When an application version is known, the typed
application-version slice uses the ISO 11073 MDC `531975` software-revision code instead
of defining a Grove duplicate. Using this standard version-type code does not make the
application a Personal Health Device or require a PHD profile. An adapter defines the
identifier system; for example, a platform adapter can use the platform's application
identifier namespace.

The default application identifier names the application product. When present, the
typed version records one exact software-version string for provenance. A producer with
separate release and build values defines one deterministic serialization rather than
placing two ambiguous entries in the application-version slice. Neither the product
identifier nor the version identifies an installation, host, account, or person. Do not
generate a per-installation identifier by default. Add one only for an explicit use case,
under its own identifier namespace, and with the required privacy authorization.

The standard `observation-gatewayDevice` extension links an app only when it actually
mediated or routed the measurement. Converting a stored record into FHIR does not by
itself make the converter a gateway. The app's host hardware can be linked through
`Device.parent`; it is not folded into the application's identity. See the
[application example](Device-GroveApplicationDeviceExample.html).

Operating-system and host-hardware versions belong on a separate host Device referenced
through `Device.parent`; do not add them to the application-version slice.

### Conversion provenance

The gateway link records mediation when it occurred. A
[Grove Mobile Conversion Provenance](StructureDefinition-grove-mobile-conversion-provenance.html)
records the transformation event itself:

- `target` identifies the generated Observation;
- `activity` is the standard ISO 21089 lifecycle `transform` code;
- `agent.type` is the standard provenance participant type `assembler`;
- `agent.who` identifies the application Device; and
- `entity` identifies each source record actually consumed by the transformation.

Use `entity.what.identifier` for a source record that is not itself a FHIR resource;
use a Reference when the consumed source is a FHIR resource. A PlanDefinition,
ResearchStudy, or ResearchSubject is not a Provenance source merely because it provides
study context. Those links follow the study model described on the
[Study context](study.html) page.

Use one Provenance resource for one or more Observations assembled in the same operation.
Create separate Provenance resources when the converting application, source, or event
time differs. The [conversion example](Provenance-GroveMobileConversionProvenanceExample.html)
shows a source record transformed into a target. A later transformation keeps the
Observation's stable business identifier and records a separate Provenance event.

Provenance is the correct place to describe conversion software. The same application
also appears as a gateway only when it performed that distinct mediation role. Neither
role changes the meaning of `Observation.device`, which remains the physical recorder
or DeviceMetric.
