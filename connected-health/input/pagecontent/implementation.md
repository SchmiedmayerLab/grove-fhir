<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Pass already-obtained provider records into a mapper that consumes the exact contract in
`catalog/connected-health-adapter.json`. Provider API clients, credentials, token refresh,
subscriptions, and network retries belong to the calling application and are outside this
package.

A producer must:

1. match an exact provider/source token and element in the closed catalog;
2. fail closed unless its status admits the listed output;
3. normalize units without changing the source interval or inventing an instant;
4. assign complete source and output business identifiers;
5. declare exactly the shared semantic profile plus the adapter profile; and
6. exchange a complete resource graph in a Grove Mobile collection Bundle using
   deterministic `urn:uuid` full URLs for internal references.

`Resource.id` remains optional and repository-assigned. Provider-native keys are not
copied into `Resource.id`. Implementations validate their own emitted resources with the
generic producer kit under `Scripts/validate-producer.py`; this repository does not run
consumer implementations.

Canonical URLs identify artifacts. They do not promise that Grove hosts a package or a
FHIR endpoint at the canonical origin.
