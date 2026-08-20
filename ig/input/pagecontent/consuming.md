<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

This page shows how to inspect resources against the current combined preview packages.
Validation against them is useful for review, but does not establish compatibility with
a released Grove FHIR contract.

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

### Questionnaire resources

The current package contains draft `Questionnaire` and `QuestionnaireResponse` profiles.
A response identifies its source instrument through the `questionnaire` canonical;
receivers need the corresponding Questionnaire to interpret its items and coded answers.
The combined prototype still includes annotation-specific constraints, so these profiles
are not yet the independent Questionnaire contract described on the overview.

### Excluded from the receiver contract

SensorKit resources and batch formats remain experimental. Health Connect examples do
not have a Grove Swift implementation. The receiver CapabilityStatement has no
corresponding Grove server implementation. None of these establish a supported receiver
or exchange contract.

See [Preview Status](publication-status.html) for the current scope and release status.
