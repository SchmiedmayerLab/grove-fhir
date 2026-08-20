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

Grove FHIR defines reusable FHIR R4 contracts for mobile health data. The Mobile Data
Exchange guide describes source-neutral Observations, recording and application Device
roles, study context, and conversion provenance. Platform adapters add the identifiers and
mappings needed by a specific source without changing the shared resource shape.
[Grove Swift](https://github.com/SchmiedmayerLab/Grove) is the reference implementation for
the HealthKit adapter. The Health Connect adapter defines the corresponding Android exchange
and synchronization contract. The Questionnaire Exchange guide defines a separate SDC-based
contract for versioned instruments and responses.

## Documentation

Start with the [Mobile Data Exchange guide](https://schmiedmayerlab.github.io/grove-fhir/)
to understand the common resource model and copy a complete example. Use the
[HealthKit adapter guide](https://schmiedmayerlab.github.io/grove-fhir/healthkit/) when
converting Apple HealthKit samples. Use the
[Health Connect adapter guide](https://schmiedmayerlab.github.io/grove-fhir/health-connect/)
when converting and synchronizing Android Health Connect records. Use the
[Questionnaire Exchange guide](https://schmiedmayerlab.github.io/grove-fhir/questionnaire/)
to publish instruments and exchange their responses.

## Development

The build requires Node.js 22, Ruby 3.3, and Java 21. It uses lockfile-pinned SUSHI and Jekyll
dependencies and downloads checksum-pinned FHIR Publisher and Validator releases.

```sh
npm ci
npm test
npm run pages:build
```

`pages:build` builds and validates the guides in dependency order, rejects
Publisher QA errors or warnings, and assembles the published guides under `.build/pages`.

The [publication model](PUBLICATION.md) documents canonical routes, package checksums, and the
release process.

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
