<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

# Preview status

No Grove FHIR milestone has been published.

The site at `schmiedmayerlab.github.io/grove-fhir` is a continuous preview built from
the default branch. The `0.5.0` value identifies the current combined prototype package;
it is not a stable release and should not be used as a production dependency.

### Contract review

| Material in the current build | Status |
|---|---|
| Mobile profiles and extensions used for HealthKit observation exchange | Candidate |
| Questionnaire and QuestionnaireResponse exchange | Candidate after annotation-specific constraints are separated |
| HealthKit source-platform identifiers | Candidate pending provenance and redistribution review |
| SensorKit profiles and raw-batch format | Experimental |
| Image-annotation definitions | Outside the proposed FHIR contract |
| Health Connect definitions and receiver CapabilityStatement | No Grove Swift implementation evidence |

The generated [Artifacts](artifacts.html) page includes the complete combined prototype,
including material outside the proposed contract. The source repository's
[artifact inventory](https://github.com/SchmiedmayerLab/grove-fhir/blob/main/ARTIFACT_INVENTORY.md)
records the status of every FHIR Shorthand declaration.

### Prototype notes

These pages explain definitions that remain in the combined build; they do not expand
the proposed stable scope:

- [Identifier systems](identifiers.html)
- [Metadata mapping](metadata.html)
- [Questionnaire resources](questionnaires.html)
- [Renderer support](questionnaire-support.html)

A release requires reviewed package boundaries, an authoritative canonical host,
immutable version directories, package checksums, release notes, and a machine-readable
package list. Until then, GitHub Pages remains a continuous preview.
