<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

FHIR separates a research study, its versioned protocol, and a participant's enrollment.
Grove uses those standard resources directly.

```text
PlanDefinition.url | PlanDefinition.version
              ^
              | ResearchStudy.protocol
              |
ResearchStudy <--------- ResearchSubject ---------> Patient
      ^                                               ^
      | workflow-researchStudy                        | Observation.subject
      +-------------------- Observation --------------+
```

### Version the protocol

A `PlanDefinition` is the canonical, versioned study protocol. Assign a stable
`PlanDefinition.url` and change `PlanDefinition.version` whenever the deployed protocol
changes in a way that must remain distinguishable. The version is part of the protocol's
canonical identity: consumers resolve `url|version` when an exact revision is required.

A `ResearchStudy` describes the study and references the governing PlanDefinition in
`ResearchStudy.protocol`. The study does not duplicate the protocol revision in a
custom extension.

The examples use:

- [Mobile Study Protocol](PlanDefinition-GroveMobileStudyPlanExample.html), version `2026.08`;
- [Mobile Research Study](ResearchStudy-GroveMobileResearchStudyExample.html); and
- [Mobile Research Subject](ResearchSubject-GroveMobileResearchSubjectExample.html).

### Link the participant and data

`ResearchSubject.individual` points to the Patient and `ResearchSubject.study` points to
the ResearchStudy. Consent, study period, and assigned or actual arm belong on the
ResearchSubject when applicable.

The standard `workflow-researchStudy` extension links an Observation to each study for
which the record is relevant. This may include a protocol-driven measurement or a
clinically relevant event collected outside the scheduled protocol. Use the extension
only when the association is known; do not infer study membership from the Patient alone.

`Observation.subject` still points directly to the Patient. The ResearchSubject carries
the enrollment relationship and does not replace that subject reference.
