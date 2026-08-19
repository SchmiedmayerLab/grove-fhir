<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

The generated guide is both documentation and an executable set of FHIR rules. Use the
human-readable pages to understand a resource, the raw JSON to implement it, and the
packages to validate it.

### Start from an example

Choose the example closest to your use case:

| Use case | Rendered resource | Raw JSON |
|---|---|---|
| Step count | [Example](Observation-GroveStepCountObservationExample.html) | [JSON](Observation-GroveStepCountObservationExample.json) |
| Heart rate with device and metadata | [Example](Observation-GroveHeartRateObservationExample.html) | [JSON](Observation-GroveHeartRateObservationExample.json) |
| Sleep stage | [Example](Observation-GroveSleepObservationExample.html) | [JSON](Observation-GroveSleepObservationExample.json) |
| Follow-up questionnaire | [Example](Questionnaire-GroveFollowUpQuestionnaireExample.html) | [JSON](Questionnaire-GroveFollowUpQuestionnaireExample.json) |
| Completed questionnaire | [Example](QuestionnaireResponse-GroveFollowUpQuestionnaireResponseExample.html) | [JSON](QuestionnaireResponse-GroveFollowUpQuestionnaireResponseExample.json) |

Each example links to the profile it conforms to. Add that profile's canonical URL to
`meta.profile` in resources produced by your application.

### Read a profile page

A generated profile page offers several views of the same definition:

| View | Use it for |
|---|---|
| Overview | A summary of the profile and its purpose |
| Differential Table | Only the rules added or changed by Grove FHIR |
| Snapshot Table | The complete resource after inherited FHIR rules are applied |
| Examples | Complete resources that declare the profile |
| JSON | The machine-readable `StructureDefinition` |

Cardinality appears as `minimum..maximum`. For example, `1..1` means exactly one value,
`0..1` means optional and singular, and `0..*` means optional and repeatable.

**Must Support** does not make an optional element required. In this guide, a producer
populates a Must Support element when the source information is available; a consumer
accepts and preserves or interprets it when present.

### Download the packages

The core package contains the profiles, extensions, terminology, and examples. The
platform package contains the HealthKit code systems referenced by mobile observations.

```sh
curl -L https://schmiedmayerlab.github.io/grove-fhir/fhir/core/package.tgz \
  -o grove-fhir-core.tgz
curl -L https://schmiedmayerlab.github.io/grove-fhir/fhir/platforms/package.tgz \
  -o grove-fhir-platforms.tgz
```

The corresponding SHA-256 files are published beside each package:

- `https://schmiedmayerlab.github.io/grove-fhir/fhir/core/package.tgz.sha256`
- `https://schmiedmayerlab.github.io/grove-fhir/fhir/platforms/package.tgz.sha256`

### Run the FHIR Validator

Use the official FHIR Validator with FHIR R4 and load both packages:

```sh
java -jar validator_cli.jar resource.json \
  -version 4.0.1 \
  -ig grove-fhir-platforms.tgz \
  -ig grove-fhir-core.tgz
```

Run the same command for a `Questionnaire` and its `QuestionnaireResponse`. Validation
checks base FHIR, the selected Grove profile, terminology bindings, cardinalities, data
types, and invariants. It does not check whether two separate resources belong to the
same participant or business workflow; applications enforce those relationships.

If the Validator cannot resolve a Grove canonical, confirm that both packages were
loaded and that the resource uses the exact profile URL shown on its generated profile
page. When diagnosing an error, compare the failing path with the Differential Table
first, then use the Snapshot Table for inherited base-FHIR rules.

<details markdown="1">
<summary><strong>Package dependencies and licensing</strong></summary>

{% include dependency-table.xhtml %}

{% include globals-table.xhtml %}

{% include cross-version-analysis.xhtml %}

{% include ip-statements.xhtml %}

</details>
