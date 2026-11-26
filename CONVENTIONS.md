<!--

This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

-->

# Naming and versioning conventions

Grove FHIR publishes contracts, not code.
A name that reaches a database, a serialized payload, or another team's source tree is part of the contract, and the cost of changing it is paid by everyone who stored it.
These conventions say when a name may still change and how a client is expected to depend on one.

## Persisted identifiers are named once

A persisted identifier is any name that outlives the process that produced it: a canonical URL, a CodeSystem or ValueSet URL, an extension URL, an identifier system, a `linkId`, a storage key or key prefix, a schema version, an identity component name, a diagnostic rule code, a package id.

Name each one once.
Rename it only with a migration that reads both spellings for a stated period, or with a recorded statement that no data exists under the old name.
Record whichever applies in the pull request that performs the rename; a rename with neither is not admitted.

Two consequences follow.
A name is worth arguing about before it ships and not after, so review the spelling when the identifier is introduced.
An asymmetry that survives review is deliberate: if two sibling artifacts are named differently on purpose, say why in the artifact's own description rather than leaving a reader to guess.

`healthkit-source-type-extension` became `healthkit-source-type` in 0.6.0 under the no-shipping-data statement: publication is CI-build-only, no immutable release had been cut, and the HealthKit CodeSystem and ValueSet already shared the plain id, so the suffix never bought uniqueness.
This was the last free window for that name.

0.8.0 replaces the exchange event with the record and renames or redefines these persisted identifiers under a no-data statement:

- the entry-key extension `grove-exchange-entry-node-key` became `grove-exchange-entry-key`, and its rule code `mobile-exchange.entry-node-key` became `mobile-exchange.entry-key`; `mobile-exchange.event-times` became `mobile-exchange.record-times`, and `mobile-exchange.event-identity`, `mobile-exchange.entry-node-digest`, `mobile-exchange.entry-node-ordinal`, and `mobile-omission.recording-device` were removed;
- the catalog keys `extensions.entryNodeKey` became `entryKey`, `event` became `bundle` (with `times.assembled` now `times.packed`), `lifecycle.active.studyContext.entryNodeRoles` became `entryIdentity.contextSnapshotRoles`, `maxPrimaryOutputsPerEvent` became `maxPrimaryOutputsPerRecord`, `duplicateElsewhereInEventAllowed` became `duplicateElsewhereInRecordAllowed`, `eventBundleEntryRequired` became `bundleEntryRequired`, `sameEventBundle` became `sameRecord`, and the recording-device status `stable-token-required` became `snapshot-required-unit-optional`; `entryIdentity.entryNode`, `recordingDevice.unknownInstance`, and every adapter's recording-device `fallback` were removed;
- the invariant keys `grove-active-event-provenance-1` and `grove-retraction-event-provenance-1` became `grove-active-bundle-provenance-1` and `grove-retraction-bundle-provenance-1`, and `grove-event-identifier-value-1` and `grove-entry-node-value-1` were removed;
- the identifier-role codes `#event` and `#entry-node` and the retraction target role `#device-snapshot` were removed, and the identifier role `#device-snapshot` was redefined; and
- the identity component names: `device-snapshot` keeps its kind name, but its components changed from [`event-system`, `event-value`, `device-role`, `source-device-token`] to [`subject-system`, `subject-value`, `node-role`, `content-digest`], `writer-record` gained `subject-system` and `subject-value` before its other components, and `recording-device` gained `token-scope` before `stable-unit-token`.

The statement is that no App Store build of any client ever emitted one of the old names.
Data under them does exist from TestFlight builds, and the project lead ruled on 2026-11-01 that TestFlight-era uploads are disregarded; for that data the statement rests on the ruling, not on there being none.
The 0.6.0 precedent above rested on no immutable release having been cut, which no longer holds: tag `0.7.0` is immutable, so this statement is about data, not releases.
The release side is settled separately: the change ships as `0.8.0`, and `0.7.0` keeps the old names for whoever pins it.
The pull request that performs the rename records the full basis of the statement.

The move of the payload formats to Mobile and of the clinical record profiles to the new Clinical Records guide renames or redefines these persisted identifiers under the same kind of statement:

- the format CodeSystem `https://grovealliance.org/fhir/sensor/CodeSystem/grove-recording-format` and ValueSet `https://grovealliance.org/fhir/sensor/ValueSet/grove-recording-format` became `https://grovealliance.org/fhir/mobile/CodeSystem/grove-payload-format` and `https://grovealliance.org/fhir/mobile/ValueSet/grove-payload-format`, and the Sensor recording document now binds `https://grovealliance.org/fhir/sensor/ValueSet/grove-sensor-recording-format`;
- the format codes `fhir-collection-bundle`, `fhir-resource`, `clinical-document`, `native-recording`, and `provider-recording` became `sensor-sample-collection-bundle`, `provider-issued-fhir-json`, `cda-document`, `native-recording-json`, and `provider-response-json`, while the `native-recording` output role keeps its name; `previousCodings` in `catalog/format-registry.json` maps every old coding to its new one for readers of stored Bundles;
- a `source-artifact` identity hashes the new format code, so an artifact whose code changed spelling gets a new identity; the identity's computation is unchanged and keeps its `v0` form, and the exchange protocol version is unchanged;
- the rule code `healthkit-clinical.attachment-graph` became `clinical-record.attachment-graph`; and
- the HealthKit clinical record document and attachment keep their URLs but derive from, and are claimed beside, `grove-clinical-record-document` and `grove-clinical-record-attachment`, and a HealthKit CDA document is a `healthkit-cda-document` instead of a `healthkit-recording-document`.

The statement is the 0.8.0 one: no App Store build of any client ever emitted one of the old names, and data under them exists only from TestFlight builds, which the project lead's ruling of 2026-11-01 disregards.
Tag `0.8.3` keeps the old names for whoever pins it.

## Clients pin tagged releases

The canonical namespace `https://grovealliance.org/fhir` is an identifier, not a download location, and the CI-build preview is not release history.
An implementation depends on a Grove FHIR **tag**: it resolves the exact package version from `catalog/release-manifest.json`, verifies the published checksum, and records the source revision it built against.
Nothing depends on `main`, on a branch build, or on a versionless preview route.

The catalogs are the machine-readable half of the same contract.
A client generating code from `catalog/` reads it out of the tagged source revision whose packages it also installed, so its generated types and the profiles it validates against always come from one release.

## 0.6.0 is the first artifact of this policy

The `0.6.0` tag of this repository and the matching `0.6.0` tags of the Grove client repositories are the first releases published under these conventions.
Every identifier they carry is now a named-once identifier: from this tag forward a rename needs its migration or its no-data statement, and a client that pins the tag is entitled to rely on the spelling.

[PUBLICATION.md](PUBLICATION.md) documents how a release is built, verified, and published.
