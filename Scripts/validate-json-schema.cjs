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
const Ajv2020 = require("ajv/dist/2020");
const addFormats = require("ajv-formats");

function usage() {
  console.error(
    "usage: validate-json-schema.cjs SCHEMA INSTANCE [INSTANCE ...]\n" +
      "       INSTANCE may be - to read one JSON document from standard input"
  );
  process.exit(2);
}

if (process.argv.length < 4) {
  usage();
}

function readJson(filename) {
  try {
    return JSON.parse(fs.readFileSync(filename === "-" ? 0 : filename, "utf8"));
  } catch (error) {
    const label = filename === "-" ? "<stdin>" : filename;
    throw new Error(`unable to read JSON ${label}: ${error.message}`);
  }
}

const schemaPath = path.resolve(process.argv[2]);
const instancePaths = process.argv
  .slice(3)
  .map((value) => (value === "-" ? value : path.resolve(value)));
if (instancePaths.filter((value) => value === "-").length > 1) {
  usage();
}

try {
  const ajv = new Ajv2020({
    allErrors: true,
    strict: true,
    validateFormats: true,
  });
  addFormats(ajv);
  const validate = ajv.compile(readJson(schemaPath));
  let valid = true;
  for (const instancePath of instancePaths) {
    if (!validate(readJson(instancePath))) {
      valid = false;
      const label = instancePath === "-" ? "<stdin>" : instancePath;
      console.error(`${label} does not satisfy ${schemaPath}:`);
      for (const error of validate.errors || []) {
        const location = error.instancePath || "/";
        console.error(`- ${location}: ${error.message}`);
      }
    }
  }
  if (!valid) {
    process.exit(1);
  }
  console.log(
    `Validated ${instancePaths.length} JSON instance(s) against ${schemaPath}`
  );
} catch (error) {
  console.error(`schema validation failed: ${error.message}`);
  process.exit(1);
}
