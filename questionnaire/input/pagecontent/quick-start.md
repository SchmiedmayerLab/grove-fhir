<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

An implementation guide, or IG, is a set of rules layered on the base FHIR standard.
A **profile** is the machine-readable definition of those rules.
An **example** is a FHIR resource that conforms to a profile.
A **package** contains the profiles and declares the dependency packages that validation tools must load so they can apply the machine-readable rules directly rather than deriving them from rendered web pages.

The following sequence introduces the exchange contract and provides the validation workflow for a new instrument.

### 1. Examine the exchanged resources

Open the [Questionnaire JSON](Questionnaire-GroveWeeklySymptomCheckInExample.json) and the matching [QuestionnaireResponse JSON](QuestionnaireResponse-GroveWeeklySymptomCheckInResponseExample.json).
The rendered profile pages are a reference; these JSON resources are the data exchanged between applications.

The instrument declares a stable canonical URL and a Semantic Versioning version; the profile also requires the standard version-algorithm extension fixed to `semver`.
The following excerpt highlights the identity fields:

```json
{
  "url": "https://grovealliance.org/fhir/questionnaire/Questionnaire/GroveWeeklySymptomCheckInExample",
  "version": "0.6.0",
  "status": "active"
}
```

The response joins the canonical URL and version with one `|`:

```json
{
  "questionnaire": "https://grovealliance.org/fhir/questionnaire/Questionnaire/GroveWeeklySymptomCheckInExample|0.6.0"
}
```

An implementation resolves this exact pair before rendering the instrument or accepting its answers.

### 2. Trace an item through the pair

Each Questionnaire item has a durable `linkId`.
The response repeats the same `linkId` and hierarchy.
Its optional `text` may repeat the prompt for readability or carry the wording shown in another locale; conformance and matching never depend on that text.
A follow-up defined under a question belongs under the particular answer that supplied its context.
The example pair represents that structure as follows:

```json
{
  "linkId": "pain-present",
  "text": "Have you had pain during the last week?",
  "answer": [{
    "valueBoolean": true,
    "item": [{
      "linkId": "pain-severity",
      "text": "How severe was the pain?",
      "answer": [{
        "valueCoding": {
          "system": "http://snomed.info/sct",
          "code": "6736007",
          "display": "Moderate severity"
        }
      }]
    }]
  }]
}
```

Groups nest their children directly in `item`.
Questions nest follow-ups inside `answer.item`.
This distinction matters whenever a question can have more than one answer.

### 3. Interpret a profile page

On a profile page:

- **Differential** shows the rules added by Grove;
- **Snapshot** shows the complete structure after inherited FHIR and SDC rules;
- **Must Support** identifies content that conforming actors must understand and handle;
- `1..1` means exactly one value, `0..1` means optional and singular, and `0..*` means optional and repeatable;
- an invariant name such as `qg-version-1` is a stable rule identifier that may appear in validation messages.

### 4. Validate each resource

This guide is published as the package `org.grovealliance.fhir.questionnaire`; download `package.tgz` and `package.tgz.sha256` from the [Artifacts page](artifacts.html).
The [Mobile guide states the complete download, checksum, and atomic-install procedure](https://grovealliance.org/fhir/mobile/implementation.html#add-the-package) once for every Grove package, including why a new archive is never extracted over an older copy.

Run the official FHIR Validator, at the version `toolchain.fhirValidator` pins in `catalog/release-manifest.json`, once for each resource:

```sh
java -jar validator_cli.jar Questionnaire-GroveWeeklySymptomCheckInExample.json \
  -version 4.0.1 \
  -ig package.tgz \
  -profile https://grovealliance.org/fhir/questionnaire/StructureDefinition/grove-questionnaire

java -jar validator_cli.jar QuestionnaireResponse-GroveWeeklySymptomCheckInResponseExample.json \
  -version 4.0.1 \
  -ig package.tgz \
  -ig Questionnaire-GroveWeeklySymptomCheckInExample.json \
  -allow-example-urls true \
  -profile https://grovealliance.org/fhir/questionnaire/StructureDefinition/grove-questionnaire-response
```

The second command carries two arguments the first does not.
The Validator rejects reserved `example.org` URLs by default, and this published response uses them for its submission identifier and its application naming system, so it opts in explicitly; real deployment resources use resolvable systems and omit the flag.
It also names the instrument as a second `-ig` source, because a package's examples are not indexed as resolvable canonicals: without it the Validator reports that it cannot resolve `…GroveWeeklySymptomCheckInExample|0.6.0` and skips every check against the instrument.
Supply the exact instrument the response names, whatever its source.

### 5. Validate the resource pair

Profile validation cannot prove that response items and answers agree with the referenced Questionnaire.
From a checkout of the Grove FHIR Implementation Guides source corresponding to the package version, run the paired validator on the same two files:

```sh
python3 Scripts/validate-questionnaire.py \
  --questionnaire Questionnaire-GroveWeeklySymptomCheckInExample.json \
  --response QuestionnaireResponse-GroveWeeklySymptomCheckInResponseExample.json
```

This pair states its answer options inline, so it needs no ValueSet.
Add one `--value-set <file>` argument for every ValueSet an instrument reaches through `answerValueSet` or `unitValueSet`; membership rules cannot be checked against a set the validator cannot read.

The command exits nonzero for any blocking rule and prints stable rule codes such as `pair-answer-type` and `pair-valueset-membership`.
Run it in the same acceptance workflow that stores, forwards, or otherwise accepts a completed response.
