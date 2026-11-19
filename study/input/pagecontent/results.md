<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

A completed occurrence links its accepted result from `Task.output[result]`.
The result is a [Grove Questionnaire Response](https://grovealliance.org/fhir/questionnaire/StructureDefinition-grove-questionnaire-response.html), and every rule of the Questionnaire Exchange applies to it unchanged.

### Result link

`output[result]` has the `type` `questionnaire-response` from the Structured Data Capture code system and a `valueReference` whose `reference` is version-specific: `QuestionnaireResponse/<id>/_history/<versionId>`, optionally preceded by a server base URL.
In a Bundle, the reference resolves to the entry whose `fullUrl` matches without the `_history` part and whose `meta.versionId` equals the referenced version.
A relative reference from a Task whose `fullUrl` is not a RESTful URL, such as a `urn:uuid`, resolves by type and `id` to a response whose `fullUrl` is not a RESTful URL either.

The link runs from the Task to the response.
`QuestionnaireResponse.partOf` does not reference the Task, and a response carries no other pointer to its occurrence.

### Accepted response

The linked response agrees with its occurrence:

| Response element | Agrees with |
|---|---|
| `questionnaire` | The Task's questionnaire input, exactly |
| `subject` | The participant in `Task.for` |
| `status` | `completed` for the first accepted result; `amended` for a correction |
| `authored` | Lies within the performance window for a `completed` response; an `amended` version records when the correction was made, which is never before the window opened or before the version it corrects |
| `language` | The administration language: the instrument's base language or one of its translations |
| `identifier` | The submission identifier, which no other occurrence links |

The answers themselves follow the paired Questionnaire rules, which the [graph validation](conformance.html#graph-validation) applies to every linked response.
Scientific validation of the answers is separate from this exchange.

### One completion per occurrence

An occurrence is completed once.
A response with another submission identifier never completes an occurrence that is already completed, and one response never completes two occurrences.

A response still in progress, or a completion recorded on a device and not yet accepted, is application state.
Its occurrence stays `ready`, and a `ready` Task links no result.

### Corrected results

A correction is a new version of the same response resource: it keeps the resource `id` and the submission identifier, carries a new `meta.versionId`, and has the status `amended`.
Its `authored` is when the answers last changed, so it can lie after the performance window.
The Task keeps its occurrence identifier and its `completed` status, and its result link changes to the new version.
The occurrence is still completed once.
A receiver accepts a correction only after the version it corrects, so a sender whose result was corrected sends the completed version first and the correction after it.

The earlier response version stays retained under its own `meta.versionId`, so a consumer that holds the earlier result link can still resolve exactly what it accepted then.

### Example

The [completed occurrence](Task-GroveStudyCompletedTaskExample.html) links version `1` of the [accepted response](QuestionnaireResponse-GroveStudyDailyCheckInResponseExample.html).
