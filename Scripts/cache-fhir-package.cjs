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
const os = require("node:os");
const path = require("node:path");
const { pipeline } = require("node:stream/promises");
const zlib = require("node:zlib");
const { DiskBasedPackageCache } = require("fhir-package-loader");
const tarStream = require("tar-stream");

const PACKAGE_ID = /^[a-z0-9][a-z0-9.-]*$/;
const PACKAGE_VERSION = /^[0-9A-Za-z][0-9A-Za-z.+-]*$/;
const MAX_METADATA_BYTES = 1024 * 1024;

function usage() {
  console.error(
    "Usage: cache-fhir-package.cjs [--cache-root <directory>] <package.tgz>"
  );
}

function parseArguments(argv) {
  let cacheRoot = path.join(os.homedir(), ".fhir", "packages");
  const positional = [];
  for (let index = 0; index < argv.length; index += 1) {
    if (argv[index] === "--cache-root") {
      index += 1;
      if (index >= argv.length) {
        throw new Error("--cache-root requires a directory");
      }
      cacheRoot = argv[index];
    } else {
      positional.push(argv[index]);
    }
  }
  if (positional.length !== 1) {
    usage();
    throw new Error("expected one package archive");
  }
  return {
    archive: path.resolve(positional[0]),
    cacheRoot: path.resolve(cacheRoot),
  };
}

async function readPackageMetadata(archive) {
  const extractor = tarStream.extract();
  let metadata = null;
  extractor.on("entry", (header, stream, next) => {
    if (header.name !== "package/package.json") {
      stream.resume();
      stream.once("end", next);
      return;
    }

    const chunks = [];
    let size = 0;
    stream.on("data", (chunk) => {
      size += chunk.length;
      if (size > MAX_METADATA_BYTES) {
        stream.destroy(new Error("package/package.json exceeds the size limit"));
        return;
      }
      chunks.push(chunk);
    });
    stream.on("end", () => {
      if (metadata !== null) {
        extractor.destroy(new Error("archive contains duplicate package/package.json entries"));
        return;
      }
      try {
        metadata = JSON.parse(Buffer.concat(chunks).toString("utf8"));
        next();
      } catch (error) {
        extractor.destroy(new Error(`invalid package/package.json: ${error.message}`));
      }
    });
  });

  await pipeline(fs.createReadStream(archive), zlib.createGunzip(), extractor);
  if (metadata === null) {
    throw new Error("archive has no package/package.json");
  }
  return metadata;
}

async function main() {
  const { archive, cacheRoot } = parseArguments(
    process.argv.slice(2)
  );
  const archiveStat = fs.lstatSync(archive);
  if (!archiveStat.isFile() || archiveStat.isSymbolicLink()) {
    throw new Error("package archive must be a regular file");
  }

  const metadata = await readPackageMetadata(archive);
  const packageId = metadata.name;
  const version = metadata.version;
  if (typeof packageId !== "string" || !PACKAGE_ID.test(packageId)) {
    throw new Error(`archive has invalid package id: ${packageId}`);
  }
  if (typeof version !== "string" || !PACKAGE_VERSION.test(version)) {
    throw new Error(`archive has invalid package version: ${version}`);
  }

  fs.mkdirSync(cacheRoot, { recursive: true });
  const cache = new DiskBasedPackageCache(cacheRoot);
  const installed = await cache.cachePackageTarball(
    packageId,
    version,
    fs.createReadStream(archive)
  );
  const expected = path.join(cacheRoot, `${packageId}#${version}`);
  if (path.resolve(installed) !== expected) {
    throw new Error(`package cache returned unexpected path: ${installed}`);
  }
  const installedMetadata = JSON.parse(
    fs.readFileSync(path.join(installed, "package", "package.json"), "utf8")
  );
  if (installedMetadata.name !== packageId || installedMetadata.version !== version) {
    throw new Error("cached package metadata changed during installation");
  }
  console.log(`Cached ${packageId}#${version} at ${installed}`);
}

main().catch((error) => {
  console.error(`Unable to cache FHIR package: ${error.message}`);
  process.exitCode = 1;
});
