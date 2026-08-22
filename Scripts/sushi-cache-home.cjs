#!/usr/bin/env node
/*
 * This source file is part of the Grove FHIR open-source project
 *
 * SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
 *
 * SPDX-License-Identifier: MIT
 */

'use strict';

const os = require('node:os');
const path = require('node:path');

const cacheHome = process.env.GROVE_FHIR_TOOL_HOME;
if (!cacheHome || !path.isAbsolute(cacheHome)) {
  throw new Error('GROVE_FHIR_TOOL_HOME must be an absolute path');
}

// SUSHI's package loader calls os.homedir() directly and exposes no cache-path
// option. Scope that lookup to Grove's exact offline tool home without changing
// the process HOME environment inherited by Bundler, Jekyll, or the host user.
os.homedir = () => cacheHome;
