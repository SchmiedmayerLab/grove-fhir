<!--

This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

-->

# grove-ts PR #47 FHIR audit

- Audit date: 2026-08-26
- Pull request: [SchmiedmayerLab/grove-ts#47](https://github.com/SchmiedmayerLab/grove-ts/pull/47)
- Head branch: `feature/consume-grove-fhir-catalogs`
- Reviewed head: [`5a5b225220b7c10cf8ee7f73206cf48b7d529d68`](https://github.com/SchmiedmayerLab/grove-ts/tree/5a5b225220b7c10cf8ee7f73206cf48b7d529d68)
- Base at review time: `de26cfa7cf68029a86afc215d29354dd41a974e2`
- Nested workspace checkout: `/Users/paulschmiedmayer/Developer/grove-fhir/stack/grove-ts` (clean at the reviewed HEAD)
- Scope: FHIR-related TypeScript, generated R4 schemas, provider/recording conversion, questionnaire contracts, and conformance automation. This was a read-only audit; nothing was posted to or changed in the PR.

## Executive assessment

PR #47 is ambitious and has several senior-quality foundations: immutable results, strict input boundaries, branded primitive types, a generated catalog, reproducible generation checks, a bounded R4 surface, browser and package smoke tests, official-validator automation, and an especially thoughtful Questionnaire/QuestionnaireResponse preflight layer.

The PR is not ready to establish the 0.6.0 public contract. Its most important problems are not stylistic. The provider identity implementation emits raw account/native components while public docs promise digests; the account `Identifier.system` is validated but omitted from identity derivation; event identity implements one side of a contradictory IG contract; one public parser's TypeScript return type includes Bundle while its runtime schema rejects every Bundle; the “Grove exchange Bundle” parser accepts objects that lack required Grove identity and graph invariants; and generated R4 JSON schemas mishandle repeating primitive null placeholders, primitive-only choice extensions, empty string primitives, and lossless decimals.

The PR is also very large—896 changed files at the review snapshot—and generated schema churn obscures the clinically meaningful provider changes. Split the work before final review even if it ultimately ships in one coordinated release.

Priority scale: **P0** is a 0.6.0 release blocker; **P1** is a high FHIR, data-integrity, privacy, or interoperability defect; **P2** is a material API/design/maintainability issue; **P3** is release hygiene.

## CI snapshot

At the exact reviewed head:

- all 434 FHIR package unit tests passed;
- package/build/lint/typecheck, general CI, Node 26 compatibility, CodeQL, and coverage checks passed;
- `Readiness — Public API, Browser, and Official Validator` failed in the browser smoke test before the official validator step ran; and
- the aggregate `FHIR R4 — Full Release Readiness` check consequently failed.

The browser result had `recordingGraph: false` while every other asserted field passed. The smoke fixture still supplies `format: "provider-json-1"` and `contentType: "application/json"` ([fixture](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/scripts/browser-smoke.mjs#L150-L193)), but the generated registry admits `provider-recording` with `application/vnd.grovealliance.provider+json` ([registry](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/src/providers/contract.generated.ts#L6064-L6077)). This appears to be a stale smoke fixture, not a browser-runtime incompatibility. It still blocks merge, and the job should run the official validator with `if: always()` or as an independent job so one smoke failure does not erase conformance evidence.

## Selected highest-risk findings

| Priority | Finding | 0.6.0 disposition |
| --- | --- | --- |
| P0 | Clear provider identifiers contradict digest/privacy claims | Choose and implement one cross-language identity threat model |
| P0 | Provider account systems are discarded, and `scope:none` can collide under a shared NamingSystem | Redesign provider source identity |
| P0 | Conversion/exchange event identity contract contradicts its implementation | Select one event model and one formula |
| P1 | `SupportedR4Resource` includes Bundle at type level but the runtime union excludes it | Repair public type/runtime parity |
| P1 | “Grove exchange Bundle” parser accepts missing Grove-required identity, timestamp, entries, and entry invariants | Separate generic R4 and profile-aware parsers |
| P1 | Generated repeating primitive arrays reject legal FHIR JSON null alignment | Fix generator and add official fixtures |
| P1 | Generated choice checks ignore primitive shadow properties | Count value and shadow as one alternative |
| P1 | `canonical`, `uri`, and `url` accept empty strings; `Reference` can be non-resolvable | Enforce FHIR JSON presence semantics |
| P1 | JavaScript `number` cannot preserve FHIR decimal lexical precision | Define non-lossless scope or add a lossless layer |
| P1 | All non-vital measurements are labeled `activity` | Make category catalog-driven or omit it |
| P2 | The builder rejects legitimate reuse of one Device across multiple Provenance roles | Deduplicate resources independently of roles |
| P2 | Privacy scanner and structural-schema naming overstate guarantees | Narrow claims and publish exact conformance boundaries |
| P2 | Generated R4/R4B and provider changes are intermixed in one huge PR | Split review units and publish generation manifests |

## Release-blocking identity findings

### P0 — The implementation emits the values the documentation calls private

Public types say the native ID is hashed and never copied to FHIR output:

- [`providers/types.ts` lines 63–77](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/src/providers/types.ts#L63-L77)

The README says account/native values are digest inputs only and never emitted:

- [`packages/fhir/README.md` lines 271–278](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/README.md#L271-L278)
- the raw-recording section repeats the same claim ([lines 249–254](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/README.md#L249-L254)).

The actual derivation joins the clear values and emits them as the source business identifier:

- [`providers/identity.ts` lines 126–145](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/src/providers/identity.ts#L126-L145)
- the generated contract itself says the native ID is carried as supplied ([`contract.generated.ts` lines 593–613](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/src/providers/contract.generated.ts#L593-L613)).

Tests even assert that the serialized graph contains the native ID. This is not a minor comment mismatch: integrators may make privacy decisions based on the public promise.

Required 0.6.0 decision:

- If non-disclosure is required, use one versioned, domain-separated, deployment-keyed algorithm such as HMAC-SHA-256 over an unambiguous length-framed UTF-8 tuple, with explicit key lifecycle, public non-secret golden vectors, and deployment-owned or explicit key-epoch identifier systems.
- If clear identifiers are required for interoperability, retain a clear canonical tuple but remove every digest/pseudonym/non-exposure claim and document exactly where the values appear.

UUIDv5 `fullUrl` derivation does not make a clear business identifier private. Do not call an unkeyed hash of a guessable vendor identifier private either, and do not change algorithms beneath an old NamingSystem. HMAC reduces disclosure of these source identifiers; it does not de-identify patient references, timestamps, clinical content, or attachments in the graph. Apply the chosen design identically in the IG, TypeScript, Swift, Kotlin, examples, and threat model.

### P0 — Provider source identity can collide

The input correctly requires a complete provider-account Identifier and validates `system` as an absolute URI. The derivation then uses only `.value`:

- input and validation: [`identity.ts` lines 69–103](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/src/providers/identity.ts#L69-L103)
- composition: [`identity.ts` lines 126–145](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/src/providers/identity.ts#L126-L145)

Two deployments can therefore use the same pseudonym value under different account systems and produce the same Grove source Identifier. The output system is a shared Grove NamingSystem, so the omitted input system cannot disambiguate the collision.

The `identifierScope: none` branch is worse: it emits only `sourceNativeId`, even though all providers share the same Grove source-record NamingSystem. Identical keys from two providers or source key spaces collide.

Required change:

1. Always include provider code and the exact source-type/key-space token.
2. For account-scoped sources, include the complete account pair in the selected HMAC/clear canonical preimage—not value alone.
3. Remove raw pass-through under a shared NamingSystem. Alternatively define a distinct NamingSystem per provider/key space, but do not claim the current shared system already conveys provider identity.
4. Add collision vectors for same native key across providers, source types, account systems, and accounts.

### P0 — Conversion and exchange identities implement contradictory normative rules

The generated contract says both:

- event values are `<providerCode>|<eventSequence>|<role>`; and
- for a single conversion, exchange and conversion identifier values are byte-for-byte equal and only their NamingSystems distinguish them.

See [`contract.generated.ts` lines 657–667](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/src/providers/contract.generated.ts#L657-L667).

The implementation follows the first rule and produces different role-suffixed values under the same caller-owned graph system:

- [`providers/identity.ts` lines 162–180](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/src/providers/identity.ts#L162-L180)

The API merely accepts a positive integer; uniqueness depends on an undocumented/unenforced durable producer-wide allocator. Reusing the examples' `1` for multiple events collides.

Recommended breaking design: adopt one source record per exchange event and make `Bundle.identifier` the sole event business identifier. Partition it by a durable producer-instance/deployment scope plus monotonic sequence, not provider code; exact retry reuses it and all event timestamps/payload, while changed content receives a new sequence. R4 `Provenance` has no business `identifier`, so give its Bundle entry a typed event-scoped node key only through a new/redefined Grove entry-key extension for `fullUrl` derivation—the current extension's “complete business identifier” definition is not suitable. Delete the impossible equality rule and publish concurrency, reset, and collection-Bundle sink behavior.

## Public parser and FHIR JSON correctness

### P1 — `parseSupportedR4Resource` lies at the type boundary

`SupportedR4Resource` is `CollectionBundle | GraphResource`:

- [`r4/types.ts` lines 47–64](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/src/r4/types.ts#L47-L64)

Its runtime schema is only the union of graph resource members and contains no Bundle schema:

- [`r4/schemas.ts` lines 89–99 and 136–138](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/src/r4/schemas.ts#L89-L99)
- the public parser delegates directly to that schema ([`r4/parse.ts` lines 72–78](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/src/r4/parse.ts#L72-L78)).

Thus a caller is promised `Result<SupportedR4Resource>` while every valid Bundle follows the failure branch. Add the bundle schema to the union or remove Bundle from the type and rename the API. Add a type/runtime parity table test that exercises every union member, not only Device.

### P1 — The collection parser is neither a sound `CollectionBundle` parser nor a Grove profile parser

The TypeScript `CollectionBundle` type requires `entry`, and each entry requires `fullUrl` and a graph resource. The Zod schema makes `entry` optional, then casts the incompatible schema to `ZodType<CollectionBundle>`:

- type: [`r4/types.ts` lines 50–62](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/src/r4/types.ts#L50-L62)
- runtime schema/cast: [`r4/schemas.ts` lines 101–138](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/src/r4/schemas.ts#L101-L138)

Despite being documented as “A Grove exchange bundle,” it also permits missing profile, Bundle identifier, timestamp, and entry-identifier extension; accepts any UUID case/version instead of the Grove lowercase UUIDv5 contract; and checks neither duplicate `fullUrl` values nor internal reference resolution nor entry identity equality. The test named “validates collection graphs and internal fullUrls” only checks one entry's superficial shape ([test](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/test/foundation.test.ts#L157-L171)).

Required change: expose two deliberately named layers:

- a generic bounded `parseR4CollectionBundle`, truthful to base R4 and its optional fields; and
- `parseGroveMobileExchangeBundle`, enforcing the claimed profile, complete Bundle/event identity, timestamp, non-empty unique entries, exact entry-identifier extension, UUIDv5 derivation, allowed resources, reference closure, and graph-specific rules.

Do not silence schema/type disagreement with `as unknown as` at a public trust boundary.

### P1 — Repeating primitive arrays do not support legal FHIR JSON

FHIR R4 JSON uses parallel arrays for repeated primitive values and their `_field` Element metadata. A legal value array may contain `null` as a positional placeholder when the primitive has only an extension, and the value/shadow arrays must remain positionally aligned ([official FHIR R4 JSON representation](https://hl7.org/fhir/R4/json.html)).

The generator emits non-null primitive arrays and non-null shadow arrays with no cross-array alignment refinement:

- [`generate-zod-schemas.mjs` lines 241–340](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/scripts/generate-zod-schemas.mjs#L241-L340)
- shadow generation ([lines 663–710](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/scripts/generate-zod-schemas.mjs#L663-L710)); and
- generated `HumanName.given/_given` demonstrates the result ([`zod/r4/schemas.ts` lines 1454–1471](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/src/zod/r4/schemas.ts#L1454-L1471)).

Fix the generator to accept the correct nullable slot shapes and enforce array parity. Test value-only, extension-only, mixed, leading/middle/trailing null, length mismatch, and both R4/R4B official examples.

### P1 — Primitive shadow properties are invisible to choice cardinality

For `value[x]`, the generator's refinement counts only concrete value property names:

- [`generate-zod-schemas.mjs` lines 387–409](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/scripts/generate-zod-schemas.mjs#L387-L409)

FHIR permits a primitive element with extensions and no value, represented by `_valueString` without `valueString`. A required choice containing such an element is rejected as absent. Conversely, multiple primitive shadow alternatives can be present without being counted as conflicting.

Treat `(valueX, _valueX)` as one alternative, require at least one member for a required choice, and forbid either member of a second alternative. Add extension-only positive and multi-shadow negative fixtures.

### P1 — Empty string primitives and weak References are accepted

Generated `canonical`, `uri`, and `url` use `\S*`, which admits `""`:

- [`zod/r4/schemas.ts` lines 3413–3415 and 3521–3527](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/src/zod/r4/schemas.ts#L3413-L3415)

In FHIR JSON, an absent string-based primitive is omitted; an emitted primitive value is not an empty string. Use `+` or an explicit non-empty refinement where the R4 lexical rule otherwise permits zero characters.

The Grove `resolvableReferenceSchema` checks only whether `reference` or `identifier` is not `undefined` ([`r4/schemas.ts` lines 60–75](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/src/r4/schemas.ts#L60-L75)). It therefore accepts whitespace references and empty Identifier objects. Require a nonblank syntactically admitted reference or a complete `(system, value)` identifier; for profile-aware graph parsing, require an actually resolvable internal `fullUrl` when the IG does.

### P1 — `number` is not a lossless FHIR decimal representation

The generated decimal schema accepts a JavaScript `number` and re-stringifies it for lexical checking:

- [`zod/r4/schemas.ts` lines 3439–3449](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/src/zod/r4/schemas.ts#L3439-L3449)

FHIR states that decimal precision is significant, while normal JavaScript JSON parsing loses trailing zeros and may round large/high-precision decimals ([FHIR R4 decimal](https://hl7.org/fhir/R4/datatypes.html#decimal)). The schema cannot restore what `JSON.parse` has already erased.

Make the contract explicit:

- If these schemas are structural validators for already-materialized JS objects, state that decimal lexical precision and lossless round-trip are out of scope and require the official validator at the wire boundary.
- If arbitrary FHIR JSON round-trip is a public promise, add a lossless tokenizer/decimal representation and controlled serializer; do not pretend `number` is lossless.

The existing `unsignedInt` upper bound of 2,147,483,647 is correct for FHIR R4 and should remain.

## Provider graph semantics and API design

### P1 — Non-vital measurements are mislabeled as activity

The builder maps seven hard-coded vital kinds to `vital-signs` and maps every other measurement to `activity`:

- [`providers/builder.ts` lines 46–54 and 85–90](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/src/providers/builder.ts#L46-L54)

That assigns `activity` to glucose, sleep, body composition, reproductive, and other measurements for which the IG has not asserted that category. A syntactically valid category can still be clinically misleading.

Required change: make category an reviewed catalog property per measurement/source, or omit it where no appropriate category is required. Do not use a catch-all clinical category.

### P2 — The builder rejects legitimate Device reuse across roles (**Recommendation / API limitation**)

The builder creates identities for assembler, source/data-origin app, gateway, and recording Device, then rejects the graph if any two derive the same `fullUrl`:

- measurement graph check ([`builder.ts` lines 415–466](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/src/providers/builder.ts#L415-L466));
- recording graph equivalent ([`recording.ts` lines 510–543](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/src/providers/recording.ts#L510-L543)).

It is legitimate for the same application Device to be both source enterer and converter, or converter and gateway. FHIR Provenance represents roles on agent relationships; it does not require duplicate Device resources for role multiplicity.

Required change: deduplicate identical resources by business identifier and let multiple roles reference the one entry. Reject only conflicting representations of the same identity, not repeated role use.

### P2 — Privacy scanning is a narrow leakage heuristic, not a proof

`containsReversibleIdentityRepresentation` checks raw, form-decoded, and recursively percent-decoded substring representations ([`privacy.ts`](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/src/providers/privacy.ts#L9-L40)). This is useful defense-in-depth for caller-controlled metadata, but it does not detect base64, case transformations, Unicode normalization, encryption with a caller-visible key, structured fragmentation, or leakage inside opaque attachment bytes. Meanwhile, the builder deliberately emits the identity in its own Identifier.

Rename/document this as a narrow raw/URL-encoding leakage check. Do not treat it as evidence that a graph or opaque payload is de-identified. Keep the explicit raw-payload responsibility warning.

### P2 — Generated schemas are bounded structural schemas, not full conformance

The generator implements a small explicit set of FHIRPath invariants and publishes `UNCHECKED_CONSTRAINTS`, stating that official validation is normative ([generator lines 413–480](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/scripts/generate-zod-schemas.mjs#L413-L480), [gap export lines 786–804](https://github.com/SchmiedmayerLab/grove-ts/blob/5a5b225220b7c10cf8ee7f73206cf48b7d529d68/packages/fhir/scripts/generate-zod-schemas.mjs#L786-L804)). This transparency is a strength.

Align names and docs with that reality: `strict` should mean unknown-property/shape strictness, not full FHIR conformance. Keep official validation as a release gate, publish the skipped-invariant manifest in the package, and ensure the validator runs even when browser smoke fails.

## Questionnaire assessment

The Questionnaire subsystem is the strongest FHIR area in this PR. It has a bounded public surface, exact canonical/version pairing, recursive linkId checks, type-aware answer validation, option/value-set handling, temporal comparisons, SDC expression awareness, and explicit preflight between instrument and response. Preserve this shape.

For 0.6.0, add only the IG-level strengthening identified elsewhere: ensure `QuestionnaireResponse.questionnaire` resolves to the exact known Questionnaire canonical and SemVer version, test extension-only primitive answers after the generator fix, and keep official validator fixtures for every supported item/answer type. Do not broaden into an incomplete generic Questionnaire engine unless that becomes an explicit product goal.

## Maintainability and PR structure

The reviewed PR mixes provider conversion, raw recording support, questionnaire logic, new generated R4/R4B schemas, catalog snapshots, tens of thousands of generated lines, and conformance infrastructure. Even with excellent automation, this is too much semantic surface for one meaningful human review.

Recommended split:

1. generator + pinned FHIR release artifacts + generator invariants;
2. bounded R4 parser/public API corrections;
3. Questionnaire support;
4. shared Mobile catalog/identity consumption;
5. provider scalar/fan-out conversion;
6. provider raw recording conversion; and
7. official-validator fixtures/CI.

For every generated change, commit a compact manifest containing source package/version/hash, structure count, added/removed roots, skipped constraints, and deterministic output hash. Reviewers should be able to focus on generator logic and the manifest rather than line-reviewing generated code.

The explicit `./zod/r4b` export inside a package described as R4 is not inherently wrong, but label it as a separate structural surface or move it to a separate package if consumers could mistake R4B acceptance for Grove R4 conformance.

## Strengths to retain

- Immutable, deeply frozen plain-object output and `Result<T>` failures with stable paths/codes.
- Branded primitives and strict parsing at caller-owned boundaries.
- Exact catalog fetching/generation checks and frozen generated contracts.
- Separation of `Resource.id`, business Identifier, and UUIDv5 Bundle `fullUrl`.
- Closed provider source/output discriminators rather than caller-selected profile/code strings.
- Strong attachment format/content-type matching and explicit payload-admission assertions.
- Clear separation of converter, gateway, data-origin application, and recording-device roles—even though resource deduplication needs adjustment.
- Package entry-point, browser, Node compatibility, generated parity, unit, and official-validator lanes.
- Transparent `UNCHECKED_CONSTRAINTS` rather than silently claiming complete FHIRPath support.
- A disciplined Questionnaire/QuestionnaireResponse preflight design.

## Required 0.6.0 work package

1. Resolve source identity privacy, provider collision, event identity, event granularity, and role/resource deduplication in the IG.
2. Repair public type/runtime parity and introduce a true profile-aware Grove Bundle parser.
3. Correct the R4/R4B generator for repeated primitive arrays, choice shadows, empty primitives, and lossless-decimal scope.
4. Make Observation category and all other clinical qualifiers catalog-driven and terminology-reviewed.
5. Replace privacy overclaims with an explicit threat model and bounded guarantees.
6. Split the PR into reviewable semantic units with generated manifests.
7. Share one positive/negative identity and graph corpus with Swift, Kotlin, Python, and the official validator.
8. Fix the browser recording fixture and decouple official validation so every release candidate produces validator evidence.

## Acceptance gates

- No public TypeScript type includes a runtime-rejected union member; automated parity covers every member.
- Base R4 parsers and Grove-profile parsers have distinct names, guarantees, and fixtures.
- Official FHIR R4 primitive-array and primitive-choice extension examples pass; malformed alignment fails.
- Empty string URI/canonical/url values and non-resolvable References fail.
- Decimal handling has an explicit, tested losslessness contract.
- Identical provider native values cannot collide across provider, source type, account system, or account.
- Documentation and emitted identity behavior agree byte-for-byte.
- One Device can fill multiple Provenance roles without duplicate entries.
- No unreviewed catch-all Observation category is emitted.
- Browser/package tests and official validator all run and pass independently.
- The cross-language corpus produces byte-identical identifiers, fullUrls, profile claims, and expected rejection codes.

## Review limits

This review inspected the exact PR head and current IG contracts. It did not assess unrelated design-system, Firebase, Pages, or general monorepo code. Generated schemas were audited at the generator and representative-output level rather than by manually reviewing every generated file. Base FHIR conclusions use the official FHIR R4 JSON and datatype specifications linked above; the Grove release must continue to pin R4 `4.0.1` artifacts and record exact validator/package versions.
