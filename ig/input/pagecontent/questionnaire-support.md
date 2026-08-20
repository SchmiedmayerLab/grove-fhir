<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

# Prototype renderer support

Renderer feature coverage is not a FHIR conformance requirement and is not maintained
as a contract in this implementation guide. A resource can conform to a profile even
when a particular application does not render every optional extension.

The current combined prototype has the following asymmetric implementation paths:

| Prototype feature | Grove Swift behavior |
|---|---|
| Autocomplete hint | Read on import; not written on export |
| Autocapitalization hint | Read on import; not written on export |
| Image annotation | FHIR instrument import and image-answer export; no Swift-DSL instrument export |

Version-specific Grove renderer behavior belongs with the
[Grove Swift implementation](https://github.com/SchmiedmayerLab/Grove). This guide is
limited to the exchange definitions and their validation rules.
The table above explains the features in the combined prototype; it does not add those
features to the proposed stable contract.
