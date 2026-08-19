<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

This page shows how to validate Mobile Data Exchange resources against the current
preview packages. Passing validation does not establish compatibility with a released
Grove FHIR contract.

### Validate a draft resource

Download both packages under distinct filenames, then pass them to the FHIR Validator:

```sh
curl -L https://schmiedmayerlab.github.io/grove-fhir/package.tgz \
  -o grove-fhir-core-preview.tgz
curl -L https://schmiedmayerlab.github.io/grove-fhir/platforms/package.tgz \
  -o grove-fhir-platforms-preview.tgz

java -jar validator_cli.jar resource.json \
  -version 4.0.1 \
  -ig grove-fhir-core-preview.tgz \
  -ig grove-fhir-platforms-preview.tgz
```

The packages are not published through a FHIR package registry. Validation confirms
that a resource matches this preview; it does not make the preview a stable contract.

### Mobile observation shape

The implemented Mobile candidates use the following FHIR elements:

| Information | FHIR representation |
|---|---|
| Measurement | `Observation.code` and `value[x]` |
| Measurement time | `Observation.effective[x]` |
| Participant | `Observation.subject` |
| Recording hardware | `Observation.device` |
| Saving application | `observation-gatewayDevice` extension |
| Source record identity | `Observation.identifier` |
| Capture method | Grove Recording Method extension |
| Remaining typed source metadata | Grove Platform Metadata extension |

Receivers compare the complete `(identifier.system, identifier.value)` pair when
deduplicating source records. A repeated source identifier is expected when a mobile
platform redelivers a sample.

### Package boundary

The packages cover Mobile Data Exchange profiles and their supporting HealthKit
terminology. They do not define questionnaire, image-annotation, SensorKit, Health
Connect, or receiver behavior. See the [overview](index.html) for the current scope.
