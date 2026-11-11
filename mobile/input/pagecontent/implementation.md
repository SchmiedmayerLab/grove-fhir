<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

A Grove Mobile implementation begins with a valid clinical Observation and adds only the source context that the producing application can state accurately.

### Producer steps

1. Select the exact shared measurement profile from the normative catalog.
2. Derive exactly one typed `source-record` Identifier and one typed `source-output` Identifier as complete `(system, value)` pairs using the exchange protocol.
3. Set the Patient, effective time, status, and result.
   Add category and recording method when they are known.
4. Link the recording Device only when its acquisition role and admitted Device profile are known.
5. Link an application with `observation-gatewayDevice` only when it mediated or routed the measurement.
6. Link applicable studies with `workflow-researchStudy`.
7. Create exactly one conversion Provenance for the source-record revision, targeting every output derived from it.
   The source-record revision, its outputs, and that Provenance form one record.
8. Key every entry and derive its deterministic UUID URN: an output by its typed business identifier, each shared node (a Device, Patient, or study-context resource) by the content-snapshot Identifier minted after its body is final, and the Provenance by its record version, which it repeats in the `grove-record-version` extension.
   Use those UUID URNs for internal references.
   Every literal reference resolves to an entry in that same Bundle, either an output of the referring resource's own record or a shared node; a reference to another record's output is identifier-only, and contained resources and `#id` references are prohibited.
   At a governed path, use either that literal form or an identifier-only logical Reference—never both.
   A logical Reference carries the exact `Reference.type` and one complete Identifier with an absolute system; a logical Patient uses the deployment's pseudonym and does not require a fabricated Patient entry.
9. Place one or more records of one subject in a Grove Mobile Exchange Bundle, each shared node once.
   Allow only the resource types listed for active outputs, supporting entries, and lifecycle entries. Connect every supporting entry to at least one record. Require every output, Device, QuestionnaireResponse, and Provenance to declare exactly the profile set defined in `profile-claims.json`.
10. Validate the Bundle against FHIR R4, the Grove package, and the applicable graph and lifecycle rules.

Source-platform fields do not pass through a generic metadata container.
A platform adapter owns its identifier namespaces, source-type terminology, and a small allowlist of typed metadata that lacks a standard FHIR representation.
Add a field to that allowlist only after checking for a base FHIR element, published extension, and established terminology.

### Add the package

FHIR package tooling identifies this guide by the package ID:

```text
org.grovealliance.fhir.mobile
```

The Grove canonical is an identifier, not a package-download promise.
The Grove FHIR contracts are not hosted at the canonical URLs and are not published in a FHIR package registry.
Resolve the exact package version from `catalog/release-manifest.json` and download its archive and checksum from the [Artifacts page](artifacts.html).
Verify the checksum, install the archive in an isolated FHIR package cache, and replace the exact package directory atomically; never extract a new archive over an older copy because removed artifacts would remain.
Use that same manifest version when declaring the dependency in a FHIR Shorthand project.

### Validate a resource

Download the official FHIR Validator at the version `toolchain.fhirValidator` pins in `catalog/release-manifest.json`, download the Grove package, then run it against a real file—the [exchange Bundle example](Bundle-GroveMobileExchangeBundleExample.json) this guide publishes:

```sh
java -jar validator_cli.jar Bundle-GroveMobileExchangeBundleExample.json \
  -version 4.0.1 \
  -ig grove-mobile-package/package.tgz \
  -profile https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-exchange-bundle
```

Validation checks base FHIR rules, required fields, supported datatypes, terminology bindings, complete identifier pairs, governed reference shapes, catalog-declared quantity value domains, and the rule requiring either a result (`value[x]`, `component`, or `hasMember`) or `dataAbsentReason`.
It cannot prove that a source value was mapped to the correct clinical code or that a device truly recorded a value; implementations test those semantic mappings separately.

At minimum, test one valid example for every supported measurement mapping and one invalid example for each contract rule.
Include identity collisions, missing results, point and interval timing, exact step-count intervals, source time zones, absent devices, gateway applications, study links, conversion provenance, and Bundles of several records that share their nodes.

For graph-level validation, use a checkout of the Grove FHIR Implementation Guides source corresponding to the package version.
The structural layer runs green in seconds with no downloads:

```sh
python3 Scripts/validate-producer.py \
  --manifest Conformance/example-producer/manifest.json \
  --structural-only
```

Copy that manifest, point it at your own emitted files, and run the same command.
For the full lane, add `--validator <validator_cli.jar>` and one `--package <alias>=<package.tgz>` argument for every alias the manifest declares, all in a single invocation.
The command verifies package identity, required profile claims, deterministic UUID URNs, and internal graph resolution before invoking the official FHIR Validator.
`Conformance/README.md` in that checkout is the producer contract: the three mandatory validation layers, the negative corpus, and the semantic-vector binding.

The [heart-rate JSON](Observation-GroveMobileHeartRateExample.json) is a compact starting example.
The [step-count JSON](Observation-GroveMobileStepCountExample.json) demonstrates an interval aggregate.
The [HealthKit adapter guide](https://grovealliance.org/fhir/healthkit/) shows how a source package derives from this contract without changing its shared semantics.

### Receiving record versions

A producer converts the same source record again whenever it reads it again, and every conversion that changes a byte of the record is a new version of it.
A receiver that keeps a current view selects, for each source record, the one current version by the normative rule `lifecycle.active.versionSelection` in [`catalog/exchange-protocol.json`](https://grovealliance.org/fhir/catalog/exchange-protocol.json); this section restates it, and the catalog governs.
Selection runs within one verified subject and source binding and one complete `source-record` Identifier pair.
Each distinct `record-version` Identifier pair, system and value, of that source record is one version.

A record that arrives again is one of three things:

- **Exact retry**: the same record-version pair with the same lossless tokens for every resource of the record. It changes nothing, in whatever Bundle and under whatever `Bundle.identifier` or `Bundle.timestamp` it arrives. A replay that only reorders JSON members, changes whitespace, or escapes a string differently has the same canonical bytes and so the same record version: it is an exact retry.
- **Altered retry**: the same record-version pair with other tokens. It is a producer integrity failure: the first accepted content stays, and the later content is disregarded, may be quarantined, and never becomes a version.
- **New version**: any other change to the conversion Provenance or an output, including a re-conversion's new `Provenance.recorded` or `72.0` written for `72`, gives the record a new record-version Identifier.

The current version is selected over the whole set of accepted versions, in three steps:

1. **Writer version.** A version's writer evidence is the one complete writer-record Identifier pair and [Grove Writer Record Version](StructureDefinition-grove-writer-record-version.html) that its outputs state; no statement, a writer-record Identifier without a version, or two different statements among the outputs is no evidence. Drop every version for which another accepted version has evidence under the same complete writer-record pair with a greater writer version.
2. **Recorded instant.** Of the versions that remain, select the latest `Provenance.recorded`, compared as an exact instant on the UTC timeline at its full stated precision, never as text and never rounded to a millisecond date value.
3. **Tie-break.** Among versions with equal instants, select the greatest record-version `Identifier.value` by unsigned bytewise UTF-8 comparison, then the greatest `Identifier.system`.

For two versions this means that comparable writer versions decide, otherwise the later recorded instant, otherwise the bytewise-greater key.
Because the first step drops versions before any instant is compared, a superseded writer version never returns, whatever order the versions arrive in.

The catalog's test vectors work one tie through.
Two versions of the heart-rate source record `v0:test-key:1:ptHr751zWyYfaR2WIvrP1TfnVEK4bInC__ibP_AYfVY` differ only in the Observation's `"value":72` and `"value":72.0`, carry no writer evidence, and state the same `recorded` instant, `2026-08-20T17:30:02Z`:

| Vector | Value | `record-content-digest` | `record-version` value |
|---|---|---|---|
| `record-version-heart-rate-72` | `72` | `zQn6qLSfmufltslE_5oFb25RNjY1-XN5s547r43EumY` | `v0:test-key:1:xjbzwZqYyBE1boHxzOoS09iLXEMrvo0o8dpxtlwPQhE` |
| `record-version-heart-rate-72-0` | `72.0` | `1VvPJMtUBZEzD8DX5WFNjMr8pMVyKERNzlUyAKQLpuk` | `v0:test-key:1:z2SXdSGr63iLne5oavwMibQClshhTEABve_JEZLljCo` |

The decimal lexeme changes the canonical bytes, so the two are distinct versions, each with its own Provenance fullUrl, while the Observation keeps one fullUrl.
Both values share the prefix `v0:test-key:1:`, and `z` is greater than `x`, so the tie-break selects the `72.0` version in either arrival order.

The selected version's targets are the record's current outputs.
Every other output of the record, including one that only an earlier version emitted, leaves the current view; selection is never a maximum taken output by output.
Every accepted version stays in history.

Retraction works on the whole record.
An accepted retraction suppresses every output of every version of the source record its `Provenance.entity` names, whether the version is accepted before or after the retraction and whatever its writer version or recorded instant.
From then on the record has no current outputs, and every version stays in history.
A record is never un-retracted: a version accepted after its retraction goes to history only.
The retraction's targets are informative and bind no output (see [Retraction Bundles](observations.html#retraction-bundles)).

Receivers never parse or recompute a record-version Identifier, and they do not hold the key that minted it.
They compare the complete pair for equality, which detects a retry, and order it bytewise only for the tie-break.
Only the conformance kit recomputes a record version, and only under the published test key.
The [receiver-lifecycle corpus](https://github.com/SchmiedmayerLab/grove-fhir/tree/main/Conformance/corpora/receiver-lifecycle) exercises these rules in every arrival order.

### Vocabulary

Implementations name their public types after these terms, in each platform's casing, and add a term here before introducing a new shared concept; the module or package that holds them follows each platform's own conventions.

- **Exchange record**: one immutable source-record revision, every output derived from it, and exactly one conversion Provenance targeting those outputs, or one retraction assertion for one whole source record; the semantic unit of exchange.
- **Record version**: one immutable version of one source record, named by its keyed `record-version` Identifier, which is its conversion Provenance's entry key.
- **Exchange graph**: the validated upload Bundle, one collection Bundle that carries one or more exchange records of one kind and one subject, with its shared nodes, deterministic entry keys, and full URLs; packing records into Bundles changes no record.
- **Business identifier**: a complete `Identifier.system` and `Identifier.value` pair; never a repository-assigned resource id.
- **Identifier role**: the Grove role an identifier carries in `Identifier.type` from the `grove-identifier-role` code system.
- **Opaque identity**: an HMAC-derived business identifier of one closed identity kind in the `v0:` form, minted under deployment-owned systems for one key id and epoch; the scope that mints it holds the key, its systems and its epoch.
- **Content snapshot**: the opaque identity of a shared node that has no immutable business identifier, minted over the subject, the node role, and a digest of the node's complete canonical content, so the same content has the same identity in every Bundle and changed content a new one.
- **Entry key**: the Identifier an entry carries in the `grove-exchange-entry-key` extension and from which its fullUrl derives: an output's typed business identifier, a shared node's content snapshot, or a Provenance's record version or record retraction.
- **Subject**: the participant, referenced through a deployment-scoped pseudonym or, when the deployment supplies one, a bundled Patient entry whose only identifier without a Grove role is that pseudonym; the word pseudonym is reserved for the subject.
- **Study enrollment**: one ResearchStudy, its exact-revision PlanDefinition and one ResearchSubject for a known association.
- **Application device, host device, recording device**: the three immutable, content-addressed Device snapshots that claim the Grove application, host and recording Device profiles.
- **Retraction record and retraction target**: the lifecycle assertion, keyed by its `record-retraction` Identifier and carried in a retraction Bundle, that one whole source record is no longer exposed; its targets name what the producer emitted, or the source record as a whole, and are informative.
- **Governed source identifier**: the optional clear native identifier a deployment discloses on the designated primary output or a retraction target.
- **Writer**: the application or device that wrote the source record at its platform; it is the source agent of the conversion Provenance and, when the platform assigns them, the origin of the writer-record identity and version.
- **Producer diagnostic**: a registered rule code that a producer or the conformance kit reports, at error severity for a refused record or invalid graph and at warning severity for what an accepted record lost.

### Dependencies and terminology notices

The tables below list this guide's package dependencies and the notices for terminology used by its artifacts and examples.

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
