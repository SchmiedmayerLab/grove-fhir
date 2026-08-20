#!/usr/bin/env node
/*
 * This source file is part of the Grove FHIR open-source project
 *
 * SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
 *
 * SPDX-License-Identifier: MIT
 */

"use strict";

const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const Ajv2020 = require("ajv/dist/2020");

const REPOSITORY_ROOT = path.resolve(__dirname, "..");
const DEFAULT_CASES = path.join(
  REPOSITORY_ROOT,
  "Conformance/receiver-envelope/lifecycle-cases.json"
);
const MAX_SYSTEM_BYTES = 2048;
const MAX_VALUE_BYTES = 4096;
const MAX_BUNDLE_BYTES = 16 * 1024 * 1024;
const MAX_OBSERVATIONS = 50000;
const MAX_IDENTIFIER_TOKENS = 80000;

function fail(message) {
  throw new Error(message);
}

function absoluteWithoutSymlinks(rawPath, label) {
  const absolute = path.resolve(rawPath);
  const parsed = path.parse(absolute);
  let current = parsed.root;
  const parts = path.relative(parsed.root, absolute).split(path.sep).filter(Boolean);
  if (parts.length > 0) {
    const first = path.join(current, parts[0]);
    if (fs.lstatSync(first, { throwIfNoEntry: false })?.isSymbolicLink()) {
      current = fs.realpathSync(first);
      parts.shift();
    }
  }
  for (const part of parts) {
    current = path.join(current, part);
    if (fs.lstatSync(current, { throwIfNoEntry: false })?.isSymbolicLink()) {
      fail(`${label} may not traverse a symlink: ${current}`);
    }
  }
  return current;
}

function readJson(filename) {
  try {
    return JSON.parse(fs.readFileSync(filename, "utf8"));
  } catch (error) {
    fail(`unable to read JSON ${filename}: ${error.message}`);
  }
}

function clone(value) {
  return structuredClone(value);
}

function canonical(value) {
  if (Array.isArray(value)) {
    return `[${value.map(canonical).join(",")}]`;
  }
  if (value !== null && typeof value === "object") {
    return `{${Object.keys(value)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${canonical(value[key])}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

function identifierToken(identifier) {
  return (
    `${Buffer.byteLength(identifier.system, "utf8")}:${identifier.system}` +
    `${Buffer.byteLength(identifier.value, "utf8")}:${identifier.value}`
  );
}

function sourceKey(identifier) {
  return identifierToken(identifier);
}

function pointerTokens(pointer) {
  if (typeof pointer !== "string" || !pointer.startsWith("/")) {
    fail(`invalid JSON Pointer ${JSON.stringify(pointer)}`);
  }
  return pointer
    .slice(1)
    .split("/")
    .map((token) => token.replaceAll("~1", "/").replaceAll("~0", "~"));
}

function patchEnvelope(base, operations) {
  if (!Array.isArray(operations) || operations.length !== 1) {
    fail("each envelope schema case must contain exactly one RFC 6902 operation");
  }
  const operation = operations[0];
  if (
    !operation ||
    typeof operation !== "object" ||
    !["add", "remove", "replace"].includes(operation.op)
  ) {
    fail("envelope schema cases support one add, remove, or replace operation");
  }
  const result = clone(base);
  const tokens = pointerTokens(operation.path);
  let parent = result;
  for (const token of tokens.slice(0, -1)) {
    if (!parent || typeof parent !== "object" || !(token in parent)) {
      fail(`envelope schema patch parent does not exist: ${operation.path}`);
    }
    parent = parent[token];
  }
  const key = tokens.at(-1);
  if (operation.op === "remove") {
    if (!(key in parent)) {
      fail(`envelope schema remove target does not exist: ${operation.path}`);
    }
    delete parent[key];
  } else {
    if (operation.op === "replace" && !(key in parent)) {
      fail(`envelope schema replace target does not exist: ${operation.path}`);
    }
    parent[key] = clone(operation.value);
  }
  if (canonical(result) === canonical(base)) {
    fail(`envelope schema patch must change the base: ${operation.path}`);
  }
  return result;
}

function issueMessage(validate) {
  return (validate.errors || [])
    .map((error) => `${error.instancePath || "/"}: ${error.message}`)
    .join("; ");
}

function parseBundleJson(bundleJson) {
  let bundle;
  try {
    bundle = JSON.parse(bundleJson);
  } catch (_error) {
    return { failure: "bundle-json-invalid" };
  }
  if (!bundle || bundle.resourceType !== "Bundle" || bundle.type !== "collection") {
    return { failure: "bundle-collection-required" };
  }
  if (!Array.isArray(bundle.entry)) {
    return { failure: "bundle-entry-required" };
  }
  const resources = bundle.entry
    .map((entry) => entry && entry.resource)
    .filter((resource) => resource && resource.resourceType === "Observation");
  if (resources.length === 0) {
    return { failure: "missing-observation" };
  }
  if (resources.length > MAX_OBSERVATIONS) {
    return { failure: "too-many-observations" };
  }

  const observations = [];
  const tokenOwners = new Map();
  for (const [observationIndex, resource] of resources.entries()) {
    if (!Array.isArray(resource.identifier) || resource.identifier.length === 0) {
      return { failure: "observation-identifiers-required" };
    }
    const identifiers = [];
    const tokens = [];
    const seen = new Set();
    for (const identifier of resource.identifier) {
      if (
        !identifier ||
        typeof identifier.system !== "string" ||
        identifier.system.length === 0 ||
        typeof identifier.value !== "string" ||
        identifier.value.length === 0
      ) {
        return { failure: "observation-identifier-incomplete" };
      }
      const copied = { system: identifier.system, value: identifier.value };
      const token = identifierToken(copied);
      if (seen.has(token)) {
        return { failure: "duplicate-observation-identifier" };
      }
      seen.add(token);
      identifiers.push(copied);
      tokens.push(token);
      const owners = tokenOwners.get(token) || [];
      owners.push(observationIndex);
      tokenOwners.set(token, owners);
    }
    observations.push({ resource, identifiers, tokens });
  }
  if (tokenOwners.size > MAX_IDENTIFIER_TOKENS) {
    return { failure: "too-many-observation-identifiers" };
  }
  for (const observation of observations) {
    if (!observation.tokens.some((token) => tokenOwners.get(token).length === 1)) {
      return { failure: "ambiguous-observation-identifier" };
    }
  }
  return { bundle, observations };
}

function parseEnvelope(envelope) {
  if (Buffer.byteLength(envelope.sourceIdentifier.system, "utf8") > MAX_SYSTEM_BYTES) {
    return { failure: "source-identifier-system-bytes" };
  }
  if (Buffer.byteLength(envelope.sourceIdentifier.value, "utf8") > MAX_VALUE_BYTES) {
    return { failure: "source-identifier-value-bytes" };
  }
  if (Buffer.byteLength(envelope.bundleJson, "utf8") > MAX_BUNDLE_BYTES) {
    return { failure: "bundle-json-bytes" };
  }
  const parsed = parseBundleJson(envelope.bundleJson);
  if (parsed.failure) {
    return parsed;
  }
  for (const observation of parsed.observations) {
    const underSourceSystem = observation.identifiers.filter(
      (identifier) => identifier.system === envelope.sourceIdentifier.system
    );
    if (
      underSourceSystem.length !== 1 ||
      underSourceSystem[0].value !== envelope.sourceIdentifier.value
    ) {
      return { failure: "bundle-source-identifier-mismatch" };
    }
  }
  return parsed;
}

function sameEvent(first, second) {
  return (
    first.operation === second.operation &&
    first.sourceVersion === second.sourceVersion &&
    first.eventSequence === second.eventSequence &&
    first.bundleJson === second.bundleJson &&
    first.sourceIdentifier.system === second.sourceIdentifier.system &&
    first.sourceIdentifier.value === second.sourceIdentifier.value
  );
}

function tokenCounts(observations) {
  const counts = new Map();
  observations.forEach((observation) => {
    observation.tokens.forEach((token) => counts.set(token, (counts.get(token) || 0) + 1));
  });
  return counts;
}

function matchCurrentToSubmitted(current, submitted) {
  const currentCounts = tokenCounts(current);
  const submittedCounts = tokenCounts(submitted);
  const matches = current.map((observation) => {
    const candidates = new Set();
    observation.tokens.forEach((token) => {
      if (currentCounts.get(token) !== 1 || submittedCounts.get(token) !== 1) {
        return;
      }
      submitted.forEach((candidate, index) => {
        if (candidate.tokens.includes(token)) {
          candidates.add(index);
        }
      });
    });
    if (candidates.size > 1) {
      return { failure: "ambiguous-observation-replacement" };
    }
    return { index: candidates.size === 1 ? [...candidates][0] : undefined };
  });
  const failure = matches.find((match) => match.failure);
  if (failure) {
    return failure;
  }
  const submittedOwners = new Map();
  matches.forEach((match, currentIndex) => {
    if (match.index === undefined) {
      return;
    }
    if (submittedOwners.has(match.index)) {
      submittedOwners.set(match.index, -1);
    } else {
      submittedOwners.set(match.index, currentIndex);
    }
  });
  if ([...submittedOwners.values()].includes(-1)) {
    return { failure: "ambiguous-observation-replacement" };
  }
  return { matches: matches.map((match) => match.index), submittedOwners };
}

function sameTokenSet(first, second) {
  return canonical([...first.tokens].sort()) === canonical([...second.tokens].sort());
}

function replacementResult(current, submitted, operation) {
  const tombstones = submitted.filter(
    (observation) => observation.resource.status === "entered-in-error"
  );
  if (!current) {
    if (operation === "delete") {
      return { failure: "deletion-without-active-source" };
    }
    if (tombstones.length > 0) {
      return { failure: "tombstone-without-active-source" };
    }
    return {
      next: submitted.filter(
        (observation) => observation.resource.status !== "entered-in-error"
      ),
    };
  }
  if (operation === "delete" && tombstones.length !== submitted.length) {
    return { failure: "invalid-deletion-bundle" };
  }
  const matching = matchCurrentToSubmitted(current, submitted);
  if (matching.failure) {
    return matching;
  }
  if (matching.matches.some((index) => index === undefined)) {
    return {
      failure:
        operation === "delete"
          ? "incomplete-deletion-bundle"
          : "incomplete-replacement-bundle",
    };
  }
  if (operation === "delete" && matching.submittedOwners.size !== submitted.length) {
    return { failure: "incomplete-deletion-bundle" };
  }
  for (const [currentIndex, submittedIndex] of matching.matches.entries()) {
    const prior = current[currentIndex];
    const candidate = submitted[submittedIndex];
    if (!prior.tokens.every((token) => candidate.tokens.includes(token))) {
      return { failure: "dropped-observation-identifier" };
    }
    if (candidate.resource.status === "entered-in-error" && !sameTokenSet(prior, candidate)) {
      return { failure: "inconsistent-tombstone-identity" };
    }
  }
  for (const [submittedIndex, candidate] of submitted.entries()) {
    if (
      candidate.resource.status === "entered-in-error" &&
      !matching.submittedOwners.has(submittedIndex)
    ) {
      return { failure: "unmatched-observation-tombstone" };
    }
  }
  return {
    next:
      operation === "delete"
        ? []
        : submitted.filter(
            (observation) => observation.resource.status !== "entered-in-error"
          ),
  };
}

function newModel() {
  return { sources: new Map(), owners: new Map() };
}

function observationTokens(observations) {
  return new Set(observations.flatMap((observation) => observation.tokens));
}

function commitAccepted(model, key, envelope, nextObservations) {
  const current = model.sources.get(key);
  if (current) {
    observationTokens(current.active).forEach((token) => {
      if (model.owners.get(token) === key) {
        model.owners.delete(token);
      }
    });
  }
  observationTokens(nextObservations).forEach((token) => model.owners.set(token, key));
  model.sources.set(key, { lastEnvelope: clone(envelope), active: clone(nextObservations) });
}

function decide(envelope, model) {
  const parsed = parseEnvelope(envelope);
  if (parsed.failure) {
    return { decision: "rejected", reason: parsed.failure };
  }
  const key = sourceKey(envelope.sourceIdentifier);
  const current = model.sources.get(key);
  if (current) {
    const sequence = BigInt(envelope.eventSequence);
    const currentSequence = BigInt(current.lastEnvelope.eventSequence);
    if (sequence < currentSequence) {
      return { decision: "rejected-older" };
    }
    if (sequence === currentSequence) {
      return sameEvent(envelope, current.lastEnvelope)
        ? { decision: "replayed" }
        : { decision: "conflict", reason: "event-sequence-conflict" };
    }
    if (
      envelope.operation === "delete" &&
      envelope.sourceVersion !== current.lastEnvelope.sourceVersion
    ) {
      return { decision: "rejected", reason: "deletion-source-version-mismatch" };
    }
  }
  const replacement = replacementResult(
    current && current.lastEnvelope.operation !== "delete" ? current.active : undefined,
    parsed.observations,
    envelope.operation
  );
  if (replacement.failure) {
    return { decision: "rejected", reason: replacement.failure };
  }
  for (const token of observationTokens(replacement.next)) {
    const owner = model.owners.get(token);
    if (owner !== undefined && owner !== key) {
      return { decision: "rejected", reason: "observation-identifier-conflict" };
    }
  }
  commitAccepted(model, key, envelope, replacement.next);
  return { decision: "accepted" };
}

function boundaryEnvelope(base, specification) {
  const envelope = clone(base);
  const value = specification.prefix + specification.codePoint.repeat(specification.count);
  if (specification.field === "sourceIdentifier.system") {
    const priorSystem = envelope.sourceIdentifier.system;
    envelope.sourceIdentifier.system = value;
    const bundle = JSON.parse(envelope.bundleJson);
    for (const entry of bundle.entry || []) {
      for (const identifier of entry.resource?.identifier || []) {
        if (identifier.system === priorSystem) {
          identifier.system = value;
        }
      }
    }
    envelope.bundleJson = JSON.stringify(bundle);
  } else if (specification.field === "sourceIdentifier.value") {
    const priorValue = envelope.sourceIdentifier.value;
    envelope.sourceIdentifier.value = value;
    const bundle = JSON.parse(envelope.bundleJson);
    for (const entry of bundle.entry || []) {
      for (const identifier of entry.resource?.identifier || []) {
        if (identifier.system === envelope.sourceIdentifier.system && identifier.value === priorValue) {
          identifier.value = value;
        }
      }
    }
    envelope.bundleJson = JSON.stringify(bundle);
  } else if (specification.field === "bundleJson.code.text") {
    const bundle = JSON.parse(envelope.bundleJson);
    bundle.entry[0].resource.code.text = value;
    envelope.bundleJson = JSON.stringify(bundle);
  } else {
    fail(`unsupported byte-boundary field: ${specification.field}`);
  }
  return envelope;
}

function validateCollectionLimits() {
  const observations = (count) =>
    JSON.stringify({
      resourceType: "Bundle",
      type: "collection",
      entry: Array.from({ length: count }, (_item, index) => ({
        resource: {
          resourceType: "Observation",
          identifier: [{ system: "https://example.org/output", value: `o-${index}` }],
        },
      })),
    });
  if (parseBundleJson(observations(MAX_OBSERVATIONS)).failure) {
    fail("receiver must accept exactly MAX_OBSERVATIONS");
  }
  if (parseBundleJson(observations(MAX_OBSERVATIONS + 1)).failure !== "too-many-observations") {
    fail("receiver must reject one Observation above MAX_OBSERVATIONS");
  }
  const identifiers = (count) =>
    JSON.stringify({
      resourceType: "Bundle",
      type: "collection",
      entry: [{
        resource: {
          resourceType: "Observation",
          identifier: Array.from({ length: count }, (_item, index) => ({
            system: "https://example.org/output",
            value: `i-${index}`,
          })),
        },
      }],
    });
  if (parseBundleJson(identifiers(MAX_IDENTIFIER_TOKENS)).failure) {
    fail("receiver must accept exactly MAX_IDENTIFIER_TOKENS");
  }
  if (
    parseBundleJson(identifiers(MAX_IDENTIFIER_TOKENS + 1)).failure !==
    "too-many-observation-identifiers"
  ) {
    fail("receiver must reject one identifier above MAX_IDENTIFIER_TOKENS");
  }
  return 4;
}

function substituteSource(value, sourceValue) {
  if (value === "$source") {
    return sourceValue;
  }
  if (Array.isArray(value)) {
    return value.map((item) => substituteSource(item, sourceValue));
  }
  if (value !== null && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value).map(([key, item]) => [key, substituteSource(item, sourceValue)])
    );
  }
  return value;
}

function staticEnvelope(fixture, event) {
  const source = fixture.sources[event.source];
  const bundle = fixture.bundleTemplates[event.bundle];
  if (!source || !bundle) {
    fail(`event ${event.id} references an unknown source or Bundle template`);
  }
  return {
    operation: event.operation,
    sourceIdentifier: clone(source),
    sourceVersion: event.sourceVersion,
    eventSequence: event.eventSequence,
    bundleJson: JSON.stringify(substituteSource(bundle, source.value)),
  };
}

function activeOutputValues(model, sourceIdentifier, outputSystem) {
  const current = model.sources.get(sourceKey(sourceIdentifier));
  if (!current) {
    return [];
  }
  return [
    ...new Set(
      current.active.flatMap((observation) =>
        observation.identifiers
          .filter((identifier) => identifier.system === outputSystem)
          .map((identifier) => identifier.value)
      )
    ),
  ].sort();
}

function assertDecision(event, result, label) {
  if (result.decision !== event.decision || result.reason !== event.reason) {
    fail(
      `${label} expected ${event.decision}${event.reason ? `/${event.reason}` : ""}, got ` +
        `${result.decision}${result.reason ? `/${result.reason}` : ""}`
    );
  }
}

function parseArguments(argv) {
  const result = {
    cases: DEFAULT_CASES,
    externalEvidence: new Map(),
    requireExternalEvidence: false,
  };
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === "--cases") {
      result.cases = path.resolve(argv[++index] || fail("--cases requires a path"));
    } else if (argument === "--external-evidence") {
      const raw = argv[++index] || fail("--external-evidence requires ID=PATH");
      const separator = raw.indexOf("=");
      if (separator < 1 || separator === raw.length - 1) {
        fail("--external-evidence must use EVIDENCE_SET_ID=PATH");
      }
      const id = raw.slice(0, separator);
      if (result.externalEvidence.has(id)) {
        fail(`duplicate external evidence set ${id}`);
      }
      result.externalEvidence.set(
        id,
        absoluteWithoutSymlinks(raw.slice(separator + 1), `external evidence set ${id}`)
      );
    } else if (argument === "--require-external-evidence") {
      result.requireExternalEvidence = true;
    } else {
      fail(`unsupported argument ${argument}`);
    }
  }
  return result;
}

function deriveSourceIdentifier(bundleJson, system) {
  const parsed = parseBundleJson(bundleJson);
  if (parsed.failure) {
    fail(`external Bundle cannot derive its source: ${parsed.failure}`);
  }
  const values = new Set(
    parsed.observations.flatMap((observation) =>
      observation.identifiers
        .filter((identifier) => identifier.system === system)
        .map((identifier) => identifier.value)
    )
  );
  if (values.size !== 1) {
    fail(`external Bundle must carry exactly one shared source value under ${system}`);
  }
  return { system, value: [...values][0] };
}

function seedActiveFromTombstones(model, envelope) {
  const parsed = parseEnvelope(envelope);
  if (parsed.failure) {
    fail(`cannot seed deletion state from invalid Bundle: ${parsed.failure}`);
  }
  if (!parsed.observations.every((item) => item.resource.status === "entered-in-error")) {
    fail("deletion seed Bundle must contain only tombstones");
  }
  const active = clone(parsed.observations);
  active.forEach((item) => {
    item.resource.status = "final";
  });
  const priorSequence = (BigInt(envelope.eventSequence) - 1n).toString();
  if (priorSequence === "0") {
    fail("deletion seed needs an event sequence greater than one");
  }
  commitAccepted(
    model,
    sourceKey(envelope.sourceIdentifier),
    {
      ...clone(envelope),
      operation: "upsert",
      eventSequence: priorSequence,
      bundleJson: "seeded-active-manifest",
    },
    active
  );
}

function validateExternalEvidence(fixture, validate, supplied, required) {
  const declaration = fixture.externalEvidence;
  if (!declaration || typeof declaration !== "object") {
    fail("receiver fixture must declare externalEvidence");
  }
  const sets = new Map();
  for (const item of declaration.sets || []) {
    if (!item || typeof item.id !== "string" || sets.has(item.id) || !Array.isArray(item.files)) {
      fail("external evidence set declarations need unique ids and file arrays");
    }
    if (
      new Set(item.files).size !== item.files.length ||
      item.files.some(
        (filename) =>
          typeof filename !== "string" ||
          filename.length === 0 ||
          filename.includes("/") ||
          filename.includes("\\")
      )
    ) {
      fail(`external evidence set ${item.id} has invalid filenames`);
    }
    sets.set(item.id, item);
  }
  if (supplied.size === 0 && !required) {
    return 0;
  }
  if (
    supplied.size !== sets.size ||
    [...sets.keys()].some((identifier) => !supplied.has(identifier)) ||
    [...supplied.keys()].some((identifier) => !sets.has(identifier))
  ) {
    fail("external evidence arguments must exactly match the receiver evidence-set inventory");
  }
  const resolvedFiles = new Map();
  for (const [identifier, item] of sets) {
    const root = supplied.get(identifier);
    if (!fs.statSync(root, { throwIfNoEntry: false })?.isDirectory() || fs.lstatSync(root).isSymbolicLink()) {
      fail(`external evidence set ${identifier} must be a regular directory`);
    }
    const entries = fs.readdirSync(root, { withFileTypes: true });
    const nonFiles = entries.filter((entry) => !entry.isFile()).map((entry) => entry.name).sort();
    if (nonFiles.length !== 0) {
      fail(
        `external evidence set ${identifier} contains non-regular entries: ` +
          nonFiles.join(", ")
      );
    }
    const actual = entries.map((entry) => entry.name).sort();
    const expected = [...item.files].sort();
    if (canonical(actual) !== canonical(expected)) {
      fail(`external evidence set ${identifier} does not match its exact file allowlist`);
    }
    item.files.forEach((filename) => {
      const target = path.join(root, filename);
      if (fs.lstatSync(target).isSymbolicLink() || !fs.statSync(target).isFile()) {
        fail(`external evidence file must be regular: ${target}`);
      }
      resolvedFiles.set(`${identifier}/${filename}`, target);
    });
  }

  let count = 0;
  for (const stream of declaration.streams || []) {
    const model = newModel();
    let seeded = false;
    for (const event of stream.events || []) {
      count += 1;
      const target = resolvedFiles.get(`${event.set}/${event.file}`);
      if (!target) {
        fail(`external event ${stream.id}/${event.id} references an undeclared file`);
      }
      const bundleJson = fs.readFileSync(target, "utf8");
      const bundleSize = Buffer.byteLength(bundleJson, "utf8");
      if (bundleSize !== event.bundleSize) {
        fail(
          `external event ${stream.id}/${event.id} Bundle size is ${bundleSize}, ` +
            `expected ${event.bundleSize}`
        );
      }
      const bundleSha256 = crypto.createHash("sha256").update(bundleJson, "utf8").digest("hex");
      if (bundleSha256 !== event.bundleSha256) {
        fail(
          `external event ${stream.id}/${event.id} Bundle SHA-256 is ${bundleSha256}, ` +
            `expected ${event.bundleSha256}`
        );
      }
      const sourceIdentifier = deriveSourceIdentifier(
        bundleJson,
        declaration.sourceIdentifierSystem
      );
      if (canonical(sourceIdentifier) !== canonical(event.sourceIdentifier)) {
        fail(
          `external event ${stream.id}/${event.id} source identifier is ` +
            `${canonical(sourceIdentifier)}, expected ${canonical(event.sourceIdentifier)}`
        );
      }
      const envelope = {
        operation: event.operation,
        sourceIdentifier,
        sourceVersion: event.sourceVersion,
        eventSequence: event.eventSequence,
        bundleJson,
      };
      if (!validate(envelope)) {
        fail(`external event ${stream.id}/${event.id} violates envelope schema: ${issueMessage(validate)}`);
      }
      if (stream.seedActiveFromFirstTombstoneBundle && !seeded) {
        seedActiveFromTombstones(model, envelope);
        seeded = true;
      }
      const result = decide(envelope, model);
      assertDecision(event, result, `external event ${stream.id}/${event.id}`);
      const activeCount =
        model.sources.get(sourceKey(sourceIdentifier))?.active.length || 0;
      if (activeCount !== event.expectedActiveCount) {
        fail(
          `external event ${stream.id}/${event.id} expected ${event.expectedActiveCount} active ` +
            `Observations, got ${activeCount}`
        );
      }
    }
  }
  return count;
}

function main(argv = process.argv.slice(2)) {
  const argumentsValue = parseArguments(argv);
  const casesPath = path.resolve(argumentsValue.cases);
  const fixture = readJson(casesPath);
  if (fixture.schemaVersion !== 2 || typeof fixture.schema !== "string") {
    fail("receiver lifecycle fixture must use schemaVersion 2 and name its schema");
  }
  const expectedModelScope = {
    partition: "trusted-test-partition",
    partitionSource: "server-derived",
    outputOwnership: "partition-local",
  };
  if (canonical(fixture.modelScope) !== canonical(expectedModelScope)) {
    fail("receiver lifecycle model must represent one server-derived trusted partition");
  }
  const schemaPath = path.resolve(path.dirname(casesPath), fixture.schema);
  const ajv = new Ajv2020({ allErrors: true, strict: true, validateFormats: false });
  const validate = ajv.compile(readJson(schemaPath));
  if (!validate(fixture.baseEnvelope)) {
    fail(`base envelope is not schema-valid: ${issueMessage(validate)}`);
  }

  const schemaCaseIds = new Set();
  for (const testCase of fixture.schemaCases || []) {
    if (!testCase || typeof testCase.id !== "string" || schemaCaseIds.has(testCase.id)) {
      fail("envelope schema case ids must be unique nonempty strings");
    }
    schemaCaseIds.add(testCase.id);
    const candidate = patchEnvelope(fixture.baseEnvelope, testCase.patch);
    const valid = validate(candidate);
    if (valid !== testCase.valid) {
      fail(
        `schema case ${testCase.id} expected valid=${testCase.valid}, got ${valid}: ` +
          issueMessage(validate)
      );
    }
  }

  for (const boundary of fixture.byteBoundaryCases || []) {
    const candidate = boundaryEnvelope(fixture.baseEnvelope, boundary);
    let byteValue;
    if (boundary.field === "sourceIdentifier.system") {
      byteValue = candidate.sourceIdentifier.system;
    } else if (boundary.field === "sourceIdentifier.value") {
      byteValue = candidate.sourceIdentifier.value;
    } else {
      byteValue = candidate.bundleJson;
    }
    if (
      boundary.expectedBytes !== undefined &&
      Buffer.byteLength(byteValue, "utf8") !== boundary.expectedBytes
    ) {
      fail(
        `byte-boundary case ${boundary.id} expected ${boundary.expectedBytes} bytes, got ` +
          Buffer.byteLength(byteValue, "utf8")
      );
    }
    const schemaValid = validate(candidate);
    if (schemaValid !== boundary.schemaValid) {
      fail(
        `byte-boundary case ${boundary.id} expected schemaValid=${boundary.schemaValid}, ` +
          `got ${schemaValid}: ${issueMessage(validate)}`
      );
    }
    const reason = parseEnvelope(candidate).failure || null;
    if (reason !== boundary.reason) {
      fail(`byte-boundary case ${boundary.id} expected ${boundary.reason}, got ${reason}`);
    }
  }

  let eventCount = 0;
  const streamIds = new Set();
  for (const stream of fixture.streams || []) {
    if (!stream || typeof stream.id !== "string" || streamIds.has(stream.id)) {
      fail("receiver lifecycle stream ids must be unique nonempty strings");
    }
    streamIds.add(stream.id);
    const model = newModel();
    const eventIds = new Set();
    for (const event of stream.events || []) {
      eventCount += 1;
      if (!event || typeof event.id !== "string" || eventIds.has(event.id)) {
        fail(`event ids in stream ${stream.id} must be unique nonempty strings`);
      }
      eventIds.add(event.id);
      const envelope = staticEnvelope(fixture, event);
      if (!validate(envelope)) {
        fail(`event ${stream.id}/${event.id} is not schema-valid: ${issueMessage(validate)}`);
      }
      const result = decide(envelope, model);
      assertDecision(event, result, `event ${stream.id}/${event.id}`);
      const actualOutputs = activeOutputValues(
        model,
        envelope.sourceIdentifier,
        fixture.identifierSystems.output
      );
      const expectedOutputs = [...event.expectedActiveOutputValues].sort();
      if (canonical(actualOutputs) !== canonical(expectedOutputs)) {
        fail(
          `event ${stream.id}/${event.id} expected active outputs ` +
            `${canonical(expectedOutputs)}, got ${canonical(actualOutputs)}`
        );
      }
    }
  }
  const externalCount = validateExternalEvidence(
    fixture,
    validate,
    argumentsValue.externalEvidence,
    argumentsValue.requireExternalEvidence
  );
  const collectionLimitCount = validateCollectionLimits();
  console.log(
    `Validated ${schemaCaseIds.size + 1} envelope schema fixtures, ` +
      `${(fixture.byteBoundaryCases || []).length} UTF-8 byte-boundary fixtures, ` +
      `${eventCount} lifecycle events, and ${externalCount} exact implementation events`
      + `, ${collectionLimitCount} collection-limit assertions in one server-derived trusted partition`
  );
}

if (require.main === module) {
  try {
    main();
  } catch (error) {
    console.error(`Receiver evidence validation failed: ${error.message}`);
    process.exitCode = 1;
  }
}

module.exports = {
  decide,
  main,
  newModel,
  parseBundleJson,
  parseEnvelope,
  replacementResult,
};
