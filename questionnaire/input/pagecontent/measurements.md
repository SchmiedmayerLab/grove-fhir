<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

A Questionnaire can capture a measurement entered by a respondent.
A system that performs the standard [SDC `$extract` operation](https://hl7.org/fhir/uv/sdc/OperationDefinition-QuestionnaireResponse-extract.html) can transform those answers into Observation resources.
The Questionnaire and QuestionnaireResponse must provide the clinical context that the later Grove projection stage needs to produce Observations conforming to their target measurement profiles.

This page describes SDC Observation-based extraction.
It does not define a Grove-specific extraction operation or a hybrid extraction mechanism.
The workflow has two distinct stages:

1. SDC `$extract` returns one extracted resource or, for multiple resources, a transaction Bundle.
2. The Grove projection stage adds exchange-scoped identity, device snapshots, and conversion Provenance, then packages the complete graph as a Grove Mobile collection Bundle.

The collection Bundle shown below is therefore the final Grove exchange artifact, not the literal response returned by `$extract`.

### Extraction declarations

Extraction is declared with standard SDC extensions.
The source item supplies the clinical or measurement concept in `Questionnaire.item.code`, while `observationExtract` determines how the item contributes to the output:

| `observationExtract` value | Result |
|---|---|
| `true` | Extract the item as a standalone Observation. |
| `component` | Add the child item as a component of its parent Observation. |
| `member` | Extract the child as a separate Observation and reference it from the parent through `hasMember`. |
| `derived` | Extract the child as a separate Observation and reference the parent from the child's `derivedFrom`. |
| `independent` | Extract the child separately without a relationship to the parent Observation. |

One item carries either the Boolean declaration or one relationship code, never both.
For example, a blood-pressure group marked `true` produces one panel Observation when its systolic and diastolic children are marked `component`.

`observationExtractCategory` supplies `Observation.category`.
When the target profile requires a category, such as `vital-signs`, omitting that declaration produces an Observation that does not conform to the target profile.

### Response prerequisites

The response references the exact versioned Questionnaire and carries the answers in the corresponding hierarchy.
Its required `subject` references the Patient who becomes the subject of each extracted Observation.
Its explicit `author` identifies the person who recorded the answers and becomes `Observation.performer`; the example does not infer this role from `subject`.
Under Observation-based extraction, `QuestionnaireResponse.authored` supplies both the effective time and the issued time described in [Measurement time](#measurement-time).

The [Grove Questionnaire Writer Context extension](StructureDefinition-grove-questionnaire-writer-context.html) records plain facts about the application and host that captured the response.
The response producer does not create a Grove device snapshot because snapshot identity is scoped to an exchange event that does not yet exist when the response is authored.
After an exchange event and identity key are available, the Grove projection stage creates the application and host snapshots from these facts.

### Unit declarations

Unit semantics originate in the Questionnaire; a form filler must not invent them.

| Questionnaire item | Unit declaration | Response representation |
|---|---|---|
| `quantity` | `questionnaire-unitOption`, or `questionnaire-unitValueSet` for a maintained set | The selected unit is carried in `valueQuantity.system` and `valueQuantity.code`. |
| `integer`, `decimal` | One fixed `questionnaire-unit` | The answer remains numeric, and extraction applies the declared unit to the Observation value. |

The form filler presents the declared units and preserves the selected coded unit in the response.
An item without a usable unit declaration cannot safely target a measurement profile that fixes a unit.
Likewise, a body-weight item that permits only UCUM `[lb_av]` cannot produce an Observation conforming to a body-weight profile fixed to UCUM `kg` without an explicitly defined conversion.

### Home Vitals extraction example

#### Questionnaire declaration

The [Home Vitals Questionnaire](Questionnaire-GroveHomeVitalsExample.html) and its [JSON representation](Questionnaire-GroveHomeVitalsExample.json) provide the complete extraction declaration.

{% json fixtures/extraction/questionnaire.json liquid/questionnaire-summary.liquid %}

Its hierarchy contains standalone body-weight and step-count items plus a blood-pressure group whose systolic and diastolic children contribute components to one panel Observation.
The Questionnaire shows the item codes, extraction relationships, categories, and units required for those results.

#### Completed response

The [Home Vitals Response](QuestionnaireResponse-GroveHomeVitalsResponseExample.html) and its [JSON representation](QuestionnaireResponse-GroveHomeVitalsResponseExample.json) contain the corresponding answers, Patient subject and author, authored time, and writer context.

{% json fixtures/extraction/questionnaire-response.json liquid/questionnaire-response-summary.liquid %}

The response shows how group children align with the instrument hierarchy and how numeric answers and coded units are represented.

#### Resulting Grove exchange Bundle

{% json fixtures/extraction/exchange-bundle.json liquid/extraction-bundle.liquid %}

The Grove exchange Bundle contains the Patient and QuestionnaireResponse, application and host Device snapshots, three Observations, and the conversion Provenance that joins the graph.
The body-weight and step-count items become standalone Observations; systolic and diastolic pressure become components of one blood-pressure Observation.
The two vital-sign Observations receive `vital-signs` from the Questionnaire declaration.
All three Observations receive `effectiveDateTime` and `issued` from the response's exact `authored` value, and copy their `performer` from the response's explicit `author`.

SDC extraction also places the QuestionnaireResponse in each Observation's `derivedFrom`.
The Grove projection stage adds the identity, device context, and Provenance required by the target measurement profiles.
Each Observation receives `source-record` and `source-output` identifiers, `manual-entry` as its recording method, and a gateway-device reference to the application Device.

The Grove Questionnaire Writer Context extension supplies the facts used to create a [Grove Application Device](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-application-device.html) and its parent [Grove Host Device](https://grovealliance.org/fhir/mobile/StructureDefinition-grove-host-device.html).
The application identifier, name, version, and build populate the application Device; the host model and operating-system version populate its parent.
Both Devices receive event-scoped snapshot identifiers during the Grove projection stage.

### Information unavailable to QuestionnaireResponse projection

Projection from a QuestionnaireResponse cannot reconstruct several facts that may be available to an adapter reading a native health data source:

| Information | Native-source conversion | QuestionnaireResponse projection |
|---|---|---|
| Writer revision | Can carry a writer record identifier and revision so a later correction supersedes the earlier record. | The response does not provide a writer revision from which to derive that identity. |
| Measurement time | Can preserve the exact instant or period recorded by the source. | Observation-based extraction uses `QuestionnaireResponse.authored`. |
| Native source and recording device | Can identify the native record type and a recording device when supplied by the source. | Identifies manual entry and the application that captured the response; these are different facts. |

### Measurement time

`QuestionnaireResponse.authored` records when the answers were gathered or authored, which may differ from when a measurement was taken.
Standard Observation-based extraction uses `authored` as the Observation effective time and should also use it as `Observation.issued`.
The result is exact when the reading is taken while answering and inaccurate when an earlier reading is entered later.

Every Observation extracted from one response receives the same time.
For example, a weight and blood pressure measured twenty minutes apart would both receive the response's authored time.

`Home Vitals` asks for measurements taken or displayed at the time of the response.
It remains within standard Observation-based extraction and does not mix in `definitionExtractValue`; all three Observations therefore use the exact `authored` value.

When a distinct measurement instant or period is clinically required, use a separate, complete SDC definition-based extraction design or an explicit StructureMap-based extraction flow.
That flow must initiate and populate each output resource according to the selected SDC mechanism, including its code, value, subject, status, category, and `effective[x]`.
A lone `definitionExtractValue` on an Observation-extraction item is not a hybrid shortcut and is not part of this example.

Do not use this Observation-based flow when the measurement time differs materially from `authored`; select or define the complete richer extraction flow first.
