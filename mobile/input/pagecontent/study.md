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
A version-specific repository reference or the immutable record's Bundle entries can preserve that history.
Here “Bundle entries” means addressable `Bundle.entry` resources, not FHIR `contained` resources, which Mobile exchange Bundles prohibit.
Resolving an old observation only through the latest ResearchStudy representation loses its original protocol identity.

Connected ResearchStudy, ResearchSubject and PlanDefinition resources are permitted supporting entries in a Mobile exchange Bundle.
Use `workflow-researchStudy` for each known association and keep each study's protocol link distinct.
A producer that knows the participant's enrollment should include one ResearchStudy, its exact-revision PlanDefinition, and one ResearchSubject as shared nodes, reference the ResearchStudy from each output through `workflow-researchStudy`, and reference the PlanDefinition from `ResearchStudy.protocol`.
An identifier-only logical ResearchStudy reference remains conformant but carries no protocol revision.
`Observation.subject` stays the identifier-only deployment pseudonym unless the deployment supplies a Patient entry; `ResearchSubject.individual` references the same subject.
A supplied Patient entry carries the pseudonym as its only identifier without a Grove role, so a literal and an identifier-only reference to it state the same subject; another business identifier of the participant, such as a medical record number, does not travel on the exchange Patient.

Each of these shared nodes is content-addressed.
It carries a typed `context-snapshot` Identifier in `Resource.identifier`, a v0 HMAC over the subject, its node role, and the digest of its complete canonical content minus `id` and minus that Identifier, and that Identifier is its entry key.
A business identifier the resource also carries, such as a ResearchStudy's study identifier, stays beside it and never selects the key, and neither does a PlanDefinition's canonical `url|version`, even when immutable.
The same content therefore gives the same entry in every Bundle, shared by every record of the Bundle whose record unit contains it, while a study revision, a changed protocol status, or a changed enrollment gives a new snapshot with its own fullUrl instead of a second body under one key.
The node roles are `patient`, `research-study`, `research-subject`, `plan-definition`, and `questionnaire-response`, as `entryIdentity.contextSnapshotRoles` in [`catalog/exchange-protocol.json`](https://grovealliance.org/fhir/catalog/exchange-protocol.json) lists them; a QuestionnaireResponse, whose one identifier holds its submission identifier, repeats its key in the `grove-context-snapshot` extension instead.
A ResearchSubject belongs to every record whose references reach the ResearchStudy it names.
A ResearchSubject that joins a record only this way is referenced by nothing in it, so it stays outside the record version, as does any node that only it reaches: a changed enrollment under an unchanged record version is a new snapshot with its own fullUrl, not a new record version. The receiver's own enrollment and withdrawal records decide, not a producer-sent ResearchSubject, as the next section describes.
These supporting resources do not turn the Bundle into a consent document or grant the sender access to a study.

### Late attribution does not rewrite a record version

A receiver can associate one retained record version with another study after accepting it.
It records that decision separately, with the exact record version, enrollment, protocol revision and authorized purpose.
Neither adding a grant nor withdrawing from a study changes the original record-version Identifier, bytes or source-output identity.
The receiver must verify subject/source ownership, consent, collection eligibility and the applicable upload window independently of producer-supplied study metadata.

The worked sequence starts with a record version that names only study A version `1`.
Study B's version `3` protocol and enrollment enter the receiver repository later; B then receives its own authorized association with the same output.
Publishing A version `2` does not silently retarget either historical grant.
Under the illustrated policy, withdrawing from A ends A's current access while B's independently authorized association remains available.
Retention for B or another governed purpose is separate from withdrawal and physical erasure.
Other approved retention/access policies can differ; the IG does not define a universal authorization policy.

### Export only the authorized study representation

A study-scoped export includes its own ResearchSubject, the appropriate historical ResearchStudy and PlanDefinition, and the supporting clinical graph needed to resolve its references.
It must not disclose other study membership through extra entries, study extensions, copied narrative or provenance metadata.
Filter supporting graphs deliberately; removing only the other study's top-level entry leaves dangling references or leaks its association elsewhere.

Filtering or adding receiver-owned study context produces a **derived export**, not an exact retry of the producer's record versions.
Give the export its own identity and derivation Provenance; do not reuse a record-version Identifier or the original conversion Provenance, and do not claim that the modified collection carries the original Mobile records.
Strip every governed source identifier and every `grove-retraction-target-native-identifier` extension from the export, so no clear native value joins the exported copy to other applications' data.
An opaque, study-scoped lineage identifier can resolve to the retained source internally without exposing its other associations or granting direct access to the raw record versions.
The source record versions and their original conversion Provenances remain immutable in custody.

The [multi-study conformance examples](https://github.com/SchmiedmayerLab/grove-fhir/tree/main/Conformance/corpora/study-attribution) include both supported producer shapes, late attribution, revision history, isolated withdrawal and derived exports.
They also separate an invalid protocol Reference from profile-valid but unauthorized subject/revision/replay cases.
FHIR validity is necessary for the exchange representation; it is not proof of authorization or correct receiver history.
