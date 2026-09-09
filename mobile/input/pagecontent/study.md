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

A `PlanDefinition` is the canonical, versioned study protocol.
Assign a stable `PlanDefinition.url` and change `PlanDefinition.version` whenever the deployed protocol changes in a way that must remain distinguishable.
The version is part of the protocol's canonical identity: consumers resolve `url|version` when an exact revision is required.

A `ResearchStudy` describes the study and references the governing PlanDefinition in `ResearchStudy.protocol`.
The study does not duplicate the protocol revision in a custom extension.

The examples use:

- [Mobile Study Protocol](PlanDefinition-GroveMobileStudyPlanExample.html), version `2026.08`;
- [Mobile Research Study](ResearchStudy-GroveMobileResearchStudyExample.html); and
- [Mobile Research Subject](ResearchSubject-GroveMobileResearchSubjectExample.html).

### Link the participant and data

`ResearchSubject.individual` points to the Patient and `ResearchSubject.study` points to the ResearchStudy.
Consent, study period, and assigned or actual arm belong on the ResearchSubject when applicable.

The standard `workflow-researchStudy` extension links an Observation to each study for which the record is relevant.
This may include a protocol-driven measurement or a clinically relevant event collected outside the scheduled protocol.
Use the extension only when the association is known; do not infer study membership from the Patient alone.

`Observation.subject` still points directly to the Patient.
The ResearchSubject carries the enrollment relationship and does not replace that subject reference.

### Preserve each study's exact revision

`ResearchStudy.protocol` is a **Reference**, not a canonical string field.
Resolve that Reference to a retained `PlanDefinition` with an exact `url` and `version`.
For example, study A's historical representation can reference protocol A version `1` while study B references protocol B version `3`.
A single protocol string beside both study references cannot express those separate associations.

When study A publishes version `2`, retain the earlier ResearchStudy representation and its protocol target.
A version-specific repository reference or the immutable event's graph entries can preserve that history.
Here “graph entries” means addressable `Bundle.entry` resources, not FHIR `contained` resources, which Mobile exchange events prohibit.
Resolving an old observation only through the latest ResearchStudy representation loses its original protocol identity.

Connected ResearchStudy, ResearchSubject and PlanDefinition resources are permitted supporting entries in a Mobile exchange Bundle.
Use `workflow-researchStudy` for each known association and keep each study's protocol link distinct.
These supporting resources do not turn the Bundle into a consent document or grant the sender access to a study.

### Late attribution does not rewrite a producer event

A receiver can associate one retained output version with another study after accepting its producer event.
It records that decision separately, with the exact output version, enrollment, protocol revision and authorized purpose.
Neither adding a grant nor withdrawing from a study changes the original event identifier, bytes or source-output identity.
The receiver must verify subject/source ownership, consent, collection eligibility and the applicable upload window independently of producer-supplied study metadata.

The worked sequence starts with an event that names only study A version `1`.
Study B's version `3` protocol and enrollment enter the receiver repository later; B then receives its own authorized association with the same output.
Publishing A version `2` does not silently retarget either historical grant.
Under the illustrated policy, withdrawing from A ends A's current access while B's independently authorized association remains available.
Retention for B or another governed purpose is separate from withdrawal and physical erasure.
Other approved retention/access policies can differ; the IG does not define a universal authorization policy.

### Export only the authorized study representation

A study-scoped export includes its own ResearchSubject, the appropriate historical ResearchStudy and PlanDefinition, and the supporting clinical graph needed to resolve its references.
It must not disclose other study membership through extra entries, study extensions, copied narrative or provenance metadata.
Filter supporting graphs deliberately; removing only the other study's top-level entry leaves dangling references or leaks its association elsewhere.

Filtering or adding receiver-owned study context produces a **derived export**, not an exact retry of the producer event.
Give the export its own identity and derivation Provenance; do not reuse the original event's identifier or claim that the modified collection is the original Mobile event.
An opaque, study-scoped lineage identifier can resolve to the retained source internally without exposing its other associations or granting direct access to the raw event.
The source event and its original conversion Provenance remain immutable in custody.

The [multi-study conformance examples](https://github.com/SchmiedmayerLab/grove-fhir/tree/main/Conformance/corpora/study-attribution) include both supported producer shapes, late attribution, revision history, isolated withdrawal and derived exports.
They also separate an invalid protocol Reference from profile-valid but unauthorized subject/revision/replay cases.
FHIR validity is necessary for the exchange representation; it is not proof of authorization or correct receiver history.
