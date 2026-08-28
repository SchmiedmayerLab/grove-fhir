<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

An implementation guide, or IG, is a set of rules layered on the base FHIR standard.
A **profile** is the machine-readable definition of those rules. An **example** is a
FHIR resource that conforms to a profile. A **package** contains the profiles and their
dependencies so validation tools can apply them without scraping this website.

Use this sequence when learning the guide or integrating a new instrument.

### 1. Read the exchanged JSON

Open the [Questionnaire JSON](Questionnaire-GroveWeeklySymptomCheckInExample.json) and
the matching [QuestionnaireResponse JSON](QuestionnaireResponse-GroveWeeklySymptomCheckInResponseExample.json).
The rendered profile pages are a reference; these JSON resources are the data exchanged
between applications.

The instrument declares a stable canonical URL, a Semantic Versioning version, and the
standard version-algorithm extension:

```json
{
  "url": "https://grovealliance.org/fhir/questionnaire/Questionnaire/GroveWeeklySymptomCheckInExample",
  "version": "1.0.0",
  "status": "active"
}
```

The response joins URL and version with one `|`:

```json
{
  "questionnaire": "https://grovealliance.org/fhir/questionnaire/Questionnaire/GroveWeeklySymptomCheckInExample|1.0.0"
}
```

Resolve this exact pair before rendering or accepting answers.

### 2. Follow one item through the pair

Each Questionnaire item has a durable `linkId`. The response repeats the same `linkId`
and hierarchy. Its optional `text` may repeat the prompt for readability or carry the
wording shown in another locale; conformance and matching never depend on that text. A
follow-up defined under a question belongs under the particular answer that supplied
its context:

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

Groups nest their children directly in `item`. Questions nest follow-ups inside
`answer.item`. This distinction matters whenever a question can have more than one
answer.

### 3. Read a profile page

On a profile page:

- **Differential** shows the rules added by Grove;
- **Snapshot** shows the complete structure after inherited FHIR and SDC rules;
- **Must Support** identifies content that conforming actors must understand and handle;
- `1..1` means exactly one value, `0..1` means optional and singular, and `0..*` means
  optional and repeatable;
- an invariant name such as `qg-version-1` is a stable rule identifier that tests can
  assert.

### 4. Validate each resource with the package

The canonical namespace is deliberately not hosted; this guide's publication root exposes the archive beside this page.
Download `package.tgz` and `package.tgz.sha256` from the [Artifacts page](artifacts.html), then verify the checksum:

```sh
(cd grove-questionnaire-package && shasum -a 256 --check package.tgz.sha256)
```

Run the official FHIR Validator once for each resource:

```sh
java -jar validator_cli.jar questionnaire.json \
  -version 4.0.1 \
  -ig grove-questionnaire-package/package.tgz \
  -profile https://grovealliance.org/fhir/questionnaire/StructureDefinition/grove-questionnaire

java -jar validator_cli.jar questionnaire-response.json \
  -version 4.0.1 \
  -ig grove-questionnaire-package/package.tgz \
  -profile https://grovealliance.org/fhir/questionnaire/StructureDefinition/grove-questionnaire-response
```

In a checkout of this repository, the wrapper supplies the exact package and profile:

```sh
python3 Scripts/validate-questionnaire-fhir.py \
  --allow-example-urls \
  --resource questionnaire.json \
  --resource questionnaire-response.json
```

The flag is needed only for the `example.org` identifiers in tutorial data. Omit it for
production resources so the Validator continues to reject placeholder identifiers.

### 5. Validate the pair

Profile validation cannot prove that response items and answers agree with the
referenced Questionnaire. Run the paired validator with every ValueSet used by
`answerValueSet` or `unitValueSet`:

```sh
python3 Scripts/validate-questionnaire.py \
  --questionnaire questionnaire.json \
  --response questionnaire-response.json \
  --value-set mood-valueset.json
```

The command exits nonzero for any blocking rule and prints stable rule codes such as
`pair-answer-type` and `pair-valueset-membership`. Add it to the same acceptance path
that stores or submits a completed response.
