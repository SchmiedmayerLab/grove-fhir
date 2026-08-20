# Producer conformance kit

Grove FHIR validates its own R4 packages, examples, and negative corpora. A producer
repository validates the resources emitted by its real public API. The dependency is
one-way: this repository never checks out, patches, or executes producer code.

A producer manifest binds emitted files to the Grove FHIR package identities and
profiles they claim. During coordinated pull-request development, the producer should
build or download packages from the selected Grove FHIR branch and keep its manifest
version synchronized. An exact Git SHA or uploaded cross-repository artifact is not a
requirement for version 0.2.0.

```sh
python3 Scripts/validate-producer.py \
  --manifest path/to/grove-fhir-producer.json \
  --validator path/to/validator_cli.jar \
  --package mobile=path/to/org.grovealliance.fhir.mobile-0.2.0.tgz \
  --package healthkit=path/to/org.grovealliance.fhir.healthkit-0.2.0.tgz
```

The command verifies the manifest and package metadata, ensures each emitted resource
declares its required profiles, and invokes the official HL7 FHIR Validator offline.
The producer remains responsible for generating the files before this command runs.

`Conformance/example-producer` is an executable example of the format. The JSON Schema
is useful for editor integration; `validate-producer.py` applies the same fail-closed
rules without requiring a third-party Python package.

## Positive and negative corpus

`Conformance/corpora/mobile-exchange` is the normative producer corpus for the Mobile
exchange graph. Its positive base is byte-for-byte equal to the example producer
Bundle. Every negative case applies exactly one RFC 6902 JSON Patch operation and
names the one rule it is intended to violate.

The structural conformance kit rejects graph and deterministic-identity failures
without needing an implementation guide build. Profile terminology and cardinality
failures are intentionally delegated to the official HL7 FHIR Validator with the
exact `org.grovealliance.fhir.mobile#0.2.0` package. A producer test suite must run
both layers; structural-only success is not FHIR conformance.

An adapter Observation has one unambiguous profile claim: exactly one shared Mobile
measurement profile plus exactly one adapter profile. It does not repeat the generic
Grove Mobile Observation or an imposed standard profile in `meta.profile`. The
machine-readable rule is `catalog/profile-claims.json`; the structural conformance kit
enforces it for standalone resources and Bundle entries.
