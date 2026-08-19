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

function usage() {
  console.error(
    "usage: validate-json-schema.cjs SCHEMA INSTANCE [INSTANCE ...]"
  );
  process.exit(2);
}

if (process.argv.length < 4) {
  usage();
}

function readJson(filename) {
  try {
    return JSON.parse(fs.readFileSync(filename, "utf8"));
  } catch (error) {
    throw new Error(`unable to read JSON ${filename}: ${error.message}`);
  }
}

const schemaPath = path.resolve(process.argv[2]);
const instancePaths = process.argv.slice(3).map((value) => path.resolve(value));

try {
  const ajv = new Ajv2020({
    allErrors: true,
    strict: true,
    validateFormats: false,
  });
  const validate = ajv.compile(readJson(schemaPath));
  let valid = true;
  for (const instancePath of instancePaths) {
    if (!validate(readJson(instancePath))) {
      valid = false;
      console.error(`${instancePath} does not satisfy ${schemaPath}:`);
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
