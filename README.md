<!--

This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

-->

# Grove FHIR

[![Build and Test](https://github.com/SchmiedmayerLab/grove-fhir/actions/workflows/build-and-test.yml/badge.svg)](https://github.com/SchmiedmayerLab/grove-fhir/actions/workflows/build-and-test.yml)
[![Deployment](https://github.com/SchmiedmayerLab/grove-fhir/actions/workflows/pages.yml/badge.svg)](https://github.com/SchmiedmayerLab/grove-fhir/actions/workflows/pages.yml)
[![CodeQL](https://github.com/SchmiedmayerLab/grove-fhir/actions/workflows/codeql.yml/badge.svg)](https://github.com/SchmiedmayerLab/grove-fhir/actions/workflows/codeql.yml)
[![REUSE status](https://api.reuse.software/badge/github.com/SchmiedmayerLab/grove-fhir)](https://api.reuse.software/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.md)

Grove FHIR contains a draft FHIR R4 Mobile Data Exchange contract and the HealthKit terminology
used by its current Swift implementation. The contract is being developed for reuse across
implementations, with [Grove Swift](https://github.com/SchmiedmayerLab/Grove) as its first reference
implementation.

## Documentation

The [Mobile Data Exchange preview](https://schmiedmayerlab.github.io/grove-fhir/) publishes the
current profiles, extensions, terminology, and validation package. HealthKit identifiers referenced by
the draft are published in the separate
[HealthKit Terminology preview](https://schmiedmayerlab.github.io/grove-fhir/platforms/).

GitHub Pages is a continuous preview, not a released specification. Package identifiers,
canonical URLs, and resource definitions may change before the first stable release. Applications
should not take a dependency on the preview packages.

## Development

The build requires Node.js 22, Ruby 3.3, and Java 21. It uses lockfile-pinned SUSHI and Jekyll
dependencies and downloads checksum-pinned FHIR Publisher and Validator releases.

```sh
npm ci
npm test
npm run pages:build
```

`pages:build` builds and validates the platform and core guides in dependency order, rejects
Publisher QA errors or warnings, and assembles the previews under `.build/pages`.

## Contributing

Contributions to this project are welcome. Please make sure to read the [contribution guidelines](https://github.com/SchmiedmayerLab/.github/blob/main/CONTRIBUTING.md) and the [contributor covenant code of conduct](https://github.com/SchmiedmayerLab/.github/blob/main/CODE_OF_CONDUCT.md) first. You can find a list of contributors in the [CONTRIBUTORS.md](CONTRIBUTORS.md) file.

## License

This project is licensed under the MIT License. See [LICENSE.md](LICENSE.md) for more information.

## Citation

If you use this software, please cite it using the metadata in [CITATION.cff](CITATION.cff), which GitHub surfaces through the [*Cite this repository*](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files) button.

## Our Research

For more information, visit the [Schmiedmayer Lab GitHub organization](https://github.com/SchmiedmayerLab).

![Schmiedmayer Lab](https://raw.githubusercontent.com/SchmiedmayerLab/.github/main/assets/footer-light.png#gh-light-mode-only)
![Schmiedmayer Lab](https://raw.githubusercontent.com/SchmiedmayerLab/.github/main/assets/footer-dark.png#gh-dark-mode-only)
