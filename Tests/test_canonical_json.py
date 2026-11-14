"""Conformance tests for grove-canonical-json-v0, the byte form behind every Grove digest."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import copy
import hashlib
import json
import pickle
import unittest
from unittest import mock
from decimal import Decimal
from pathlib import Path

from Scripts import canonical_json as CANONICAL


ROOT = Path(__file__).parents[1]

# The catalog's `canonicalJson` vectors, stated literally so the reference is pinned to the spec
# even if the catalog copy drifts.
CANONICAL_VECTORS = (
    (
        "numbers",
        b'{"v" : [72.0, 72, -0, 1E-7, 1e2, 0.10]}',
        b'{"v":[72.0,72,-0,1E-7,1e2,0.10]}',
        "42051e54d78d891b33e023b66429044312e8c99b8430af3ca1b6b4f7be34d82c",
    ),
    (
        "members-and-escapes",
        '{"b":"é\\/","c":"ｚ😀","a":"q\\"\\\\\\u0001\\t","A":2}'.encode("utf-8"),
        '{"A":2,"a":"q\\"\\\\\\u0001\\t","b":"é/","c":"ｚ😀"}'.encode("utf-8"),
        "79e56476cbdc80332cc8dc46c5d24578aec04aad5ffc94427e7d8a5346c45e94",
    ),
)

# The catalog's `invalidCanonicalJson` vectors.
INVALID_VECTORS = (
    ("duplicate-member-with-equal-values", b'{"a":1,"a":1}', "duplicate-member"),
    ("raw-non-ascii-member-name", b'{"\xc3\xa9":1}', "non-ascii-member-name"),
    ("escaped-non-ascii-member-name", b'{"\\u00e9":1}', "non-ascii-member-name"),
    ("unpaired-surrogate", b'{"a":"\\ud800"}', "unpaired-surrogate"),
    ("byte-order-mark", bytes.fromhex("EFBBBF7B7D"), "byte-order-mark"),
    ("invalid-utf8", b'{"a":"\xff"}', "invalid-utf8"),
)


class CanonicalJSONVectorTests(unittest.TestCase):
    def assert_refused(self, data: bytes, code: str) -> None:
        with self.assertRaises(CANONICAL.CanonicalJSONError) as context:
            CANONICAL.canonicalize(data)
        self.assertEqual(context.exception.code, code)

    def test_canonical_vectors_are_exact(self) -> None:
        for name, data, expected, sha256 in CANONICAL_VECTORS:
            with self.subTest(vector=name):
                actual = CANONICAL.canonicalize(data)
                self.assertEqual(actual, expected)
                self.assertEqual(hashlib.sha256(actual).hexdigest(), sha256)

    def test_invalid_vectors_are_refused_with_their_code(self) -> None:
        for name, data, code in INVALID_VECTORS:
            with self.subTest(vector=name):
                self.assert_refused(data, code)

    def test_the_non_ascii_name_vectors_hold_the_stated_bytes(self) -> None:
        by_name = {name: data for name, data, _ in INVALID_VECTORS}
        self.assertEqual(by_name["raw-non-ascii-member-name"][2:4], bytes.fromhex("C3A9"))
        self.assertEqual(by_name["escaped-non-ascii-member-name"], b'{"\\u00e9":1}')

    def test_catalog_vectors_match_the_reference(self) -> None:
        vectors = json.loads(
            (ROOT / "catalog/exchange-protocol.json").read_text(encoding="utf-8")
        )["testVectors"]
        literal = {expected: sha256 for _, _, expected, sha256 in CANONICAL_VECTORS}
        self.assertEqual(len(vectors["canonicalJson"]), len(CANONICAL_VECTORS))
        for vector in vectors["canonicalJson"]:
            with self.subTest(vector=vector["id"]):
                actual = CANONICAL.canonicalize(vector["input"].encode("utf-8"))
                self.assertEqual(actual.decode("utf-8"), vector["canonical"])
                self.assertEqual(hashlib.sha256(actual).hexdigest(), vector["sha256"])
                self.assertEqual(literal[actual], vector["sha256"])
        self.assertEqual(
            sorted(bytes.fromhex(vector["inputHex"]) for vector in vectors["invalidCanonicalJson"]),
            sorted(data for _, data, _ in INVALID_VECTORS),
        )
        for vector in vectors["invalidCanonicalJson"]:
            with self.subTest(vector=vector["id"]):
                self.assert_refused(bytes.fromhex(vector["inputHex"]), vector["expectedError"])


class CanonicalJSONFormTests(unittest.TestCase):
    def test_member_order_whitespace_and_escapes_change_no_byte(self) -> None:
        forms = (
            b'{"resourceType":"Observation","valueQuantity":{"value":72,"unit":"/min"}}',
            b' {\n\t"valueQuantity" : { "unit" : "\\/min" , "value" : 72 } ,\r\n'
            b'  "resourceType" : "Observation" }\n',
            b'{"\\u0072esourceType":"\\u004fbservation","valueQuantity":{"\\u0075nit":"\\u002fmin",'
            b'"value":72}}',
        )
        expected = b'{"resourceType":"Observation","valueQuantity":{"unit":"/min","value":72}}'
        for form in forms:
            with self.subTest(form=form):
                self.assertEqual(CANONICAL.canonicalize(form), expected)

    def test_an_escaped_ascii_name_equals_its_raw_form(self) -> None:
        self.assertEqual(CANONICAL.canonicalize(b'{"\\u0061":1}'), b'{"a":1}')
        with self.assertRaises(CANONICAL.CanonicalJSONError) as context:
            CANONICAL.canonicalize(b'{"\\u0061":1,"a":1}')
        self.assertEqual(context.exception.code, "duplicate-member")

    def test_number_lexemes_are_significant(self) -> None:
        for first, second in (("72", "72.0"), ("-0", "0"), ("1e2", "1E2"), ("1e2", "100"), ("0.10", "0.1")):
            with self.subTest(first=first, second=second):
                self.assertNotEqual(
                    CANONICAL.canonicalize(f'{{"value":{first}}}'.encode()),
                    CANONICAL.canonicalize(f'{{"value":{second}}}'.encode()),
                )
                self.assertEqual(
                    CANONICAL.canonicalize(f'{{"value":{first}}}'.encode()),
                    f'{{"value":{first}}}'.encode(),
                )

    def test_python_hands_the_hooks_the_exact_lexeme(self) -> None:
        lexemes = ["72.0", "72", "-0", "1E-7", "1e2", "0.10", "1E+2", "-0.0e-0", "1" * 5000]
        seen: list[str] = []

        def record(lexeme: str) -> str:
            seen.append(lexeme)
            return lexeme

        json.loads(f"[{', '.join(lexemes)}]", parse_int=record, parse_float=record)
        self.assertEqual(seen, lexemes)
        tree = CANONICAL.loads_lossless(f"[{','.join(lexemes)}]".encode())
        self.assertTrue(all(isinstance(value, CANONICAL.JSONNumber) for value in tree))
        self.assertEqual([str(value) for value in tree], lexemes)

    def test_non_ascii_member_names_are_refused_raw_or_escaped(self) -> None:
        precomposed = "é".encode("utf-8")
        decomposed = "é".encode("utf-8")
        self.assertEqual(precomposed, bytes.fromhex("C3A9"))
        self.assertEqual(decomposed, bytes.fromhex("65CC81"))
        for data in (
            b'{"' + precomposed + b'":1}',
            b'{"' + decomposed + b'":1}',
            b'{"' + precomposed + b'":1,"' + decomposed + b'":2}',
            b'{"\\u00e9":1}',
            b'{"e\\u0301":1}',
            b'{"\\u007f\\u0080":1}',
            b'{"\\ud83d\\ude00":1}',
            b'{"a":{"\xef\xbd\x9a":1}}',
        ):
            with self.subTest(data=data), self.assertRaises(CANONICAL.CanonicalJSONError) as context:
                CANONICAL.canonicalize(data)
            self.assertEqual(context.exception.code, "non-ascii-member-name")
        self.assertEqual(CANONICAL.canonicalize(b'{"\\u007f":1}'), b'{"\x7f":1}')

    def test_strings_escape_exactly_as_rfc_8785(self) -> None:
        short = {0x08: b"\\b", 0x09: b"\\t", 0x0A: b"\\n", 0x0C: b"\\f", 0x0D: b"\\r"}
        for code in range(0x20):
            with self.subTest(code=code):
                expected = short.get(code, f"\\u{code:04x}".encode("ascii"))
                self.assertEqual(
                    CANONICAL.canonicalize(f'"\\u{code:04X}"'.encode("ascii")), b'"' + expected + b'"'
                )
        self.assertEqual(CANONICAL.canonicalize(b'"\\"\\\\\\/"'), b'"\\"\\\\/"')
        raw = "\u007f  é東京😀﻿"
        self.assertEqual(
            CANONICAL.canonicalize(json.dumps(raw).encode("ascii")), b'"' + raw.encode("utf-8") + b'"'
        )
        self.assertEqual(CANONICAL.canonicalize(b'"\\ud83d\\ude00"'), '"😀"'.encode("utf-8"))
        self.assertEqual(
            CANONICAL.canonicalize('"é"'.encode("utf-8")), '"é"'.encode("utf-8")
        )

    def test_members_sort_by_unsigned_bytes(self) -> None:
        self.assertEqual(
            CANONICAL.canonicalize(b'{"b":1,"_b":2,"B":3,"a":4,"aa":5,"A":6,"\\u0001":7}'),
            b'{"\\u0001":7,"A":6,"B":3,"_b":2,"a":4,"aa":5,"b":1}',
        )

    def test_literals_arrays_and_top_level_values(self) -> None:
        self.assertEqual(
            CANONICAL.canonicalize(b' [ true , false , null , [ ] , { } , "x" , 3 ] '),
            b'[true,false,null,[],{},"x",3]',
        )
        for data in (b"true", b"null", b'"x"', b"-0", b"1E-7"):
            with self.subTest(data=data):
                self.assertEqual(CANONICAL.canonicalize(b" " + data + b"\n"), data)

    def test_every_parsed_depth_serializes(self) -> None:
        deep = b"[" * 5000 + b'{"a":-0}' + b"]" * 5000
        self.assertEqual(CANONICAL.canonicalize(deep), deep)
        # The parser's limit is runtime-dependent. Newer Python versions can
        # accept this depth; anything accepted must still serialize exactly.
        deeper = b"[" * 100000 + b"]" * 100000
        try:
            result = CANONICAL.canonicalize(deeper)
        except CANONICAL.CanonicalJSONError as error:
            self.assertEqual(error.code, "nesting-too-deep")
        else:
            self.assertEqual(result, deeper)

    def test_parser_recursion_failure_has_a_stable_diagnostic(self) -> None:
        with mock.patch.object(CANONICAL.json, "loads", side_effect=RecursionError), \
             self.assertRaises(CANONICAL.CanonicalJSONError) as context:
            CANONICAL.canonicalize(b"[]")
        self.assertEqual(context.exception.code, "nesting-too-deep")

    def test_output_has_no_whitespace_or_trailing_newline_and_is_idempotent(self) -> None:
        data = b'{\n  "a" : [ 1 , { "b" : "c" } ]\n}\n'
        once = CANONICAL.canonicalize(data)
        self.assertEqual(once, b'{"a":[1,{"b":"c"}]}')
        self.assertEqual(CANONICAL.canonicalize(once), once)

    def test_grammar_refusals(self) -> None:
        for data, code in (
            (b"NaN", "non-json-constant"),
            (b"[Infinity]", "non-json-constant"),
            (b'{"a":-Infinity}', "non-json-constant"),
            (b"01", "invalid-json"),
            (b"+1", "invalid-json"),
            (b"1.", "invalid-json"),
            (b".5", "invalid-json"),
            (b'{"a":1,}', "invalid-json"),
            (b"[1] [2]", "invalid-json"),
            (b"", "invalid-json"),
            (b"{'a':1}", "invalid-json"),
            (b'"\\x41"', "invalid-json"),
            (b'"\\u 041"', "invalid-json"),
            (b'"a\x01"', "invalid-json"),
            (b"\x0b1", "invalid-json"),
            (b"[1]\xc2\xa0", "invalid-json"),
            ('[٣]'.encode("utf-8"), "invalid-json"),
            (b'"\xc0\xaf"', "invalid-utf8"),
            (b'"\xed\xa0\x80"', "invalid-utf8"),
            (b'"\\udc00"', "unpaired-surrogate"),
            (b'["\\ud800x"]', "unpaired-surrogate"),
            (b'{"\\ud800":1}', "unpaired-surrogate"),
        ):
            with self.subTest(data=data), self.assertRaises(CANONICAL.CanonicalJSONError) as context:
                CANONICAL.canonicalize(data)
            self.assertEqual(context.exception.code, code)
        with self.assertRaises(CANONICAL.CanonicalJSONError) as context:
            CANONICAL.loads_lossless('{"a":1}')  # type: ignore[arg-type]
        self.assertEqual(context.exception.code, "invalid-json")


class LosslessTreeTests(unittest.TestCase):
    def test_numbers_equal_only_numbers_with_the_same_lexeme(self) -> None:
        number = CANONICAL.JSONNumber("72")
        self.assertEqual(number, CANONICAL.JSONNumber("72"))
        self.assertNotEqual(number, CANONICAL.JSONNumber("72.0"))
        self.assertNotEqual(number, "72")
        self.assertNotEqual("72", number)
        self.assertNotEqual(
            CANONICAL.loads_lossless(b'{"a":72}'), CANONICAL.loads_lossless(b'{"a":"72"}')
        )
        self.assertNotEqual(
            CANONICAL.loads_lossless(b'{"a":72}'), CANONICAL.loads_lossless(b'{"a":72.0}')
        )
        self.assertEqual(len({number, CANONICAL.JSONNumber("72")}), 1)

    def test_number_constructor_checks_the_rfc_8259_grammar(self) -> None:
        for lexeme in ("72", "-0", "0.10", "1E-7", "1e+2", "-12.5e10"):
            with self.subTest(lexeme=lexeme):
                self.assertEqual(str(CANONICAL.JSONNumber(lexeme)), lexeme)
        for lexeme in ("01", "+1", "1.", ".5", "1e", "-", "1_0", " 1", "1 ", "٣", "NaN", ""):
            with self.subTest(lexeme=lexeme), self.assertRaises(CANONICAL.CanonicalJSONError) as context:
                CANONICAL.JSONNumber(lexeme)
            self.assertEqual(context.exception.code, "invalid-number")

    def test_copies_keep_lexemes(self) -> None:
        tree = CANONICAL.loads_lossless(b'{"a":[72.0,-0,{"b":1e2}]}')
        for copied in (copy.deepcopy(tree), pickle.loads(pickle.dumps(tree))):
            with self.subTest(copied=copied):
                self.assertEqual(copied, tree)
                self.assertEqual(CANONICAL.canonical_bytes(copied), b'{"a":[72.0,-0,{"b":1e2}]}')

    def test_serializer_refuses_values_without_a_lexeme(self) -> None:
        for value in (72, 72.0, Decimal("72.0"), {"a": 1}, [True, 0.5], {1: "a"}, {"a": {"b"}}):
            with self.subTest(value=value), self.assertRaises(CANONICAL.CanonicalJSONError) as context:
                CANONICAL.canonical_bytes(value)
            self.assertEqual(context.exception.code, "not-lossless")

    def test_serializer_refuses_trees_without_a_canonical_form(self) -> None:
        for value, code in (
            ({"é": "a"}, "non-ascii-member-name"),
            ({"a": "\ud800"}, "unpaired-surrogate"),
            (["\udfff"], "unpaired-surrogate"),
            ({CANONICAL.JSONNumber("1"): "a"}, "not-lossless"),
        ):
            with self.subTest(value=value), self.assertRaises(CANONICAL.CanonicalJSONError) as context:
                CANONICAL.canonical_bytes(value)
            self.assertEqual(context.exception.code, code)

    def test_serializer_writes_trees_built_in_code(self) -> None:
        tree = {
            "valueQuantity": {"value": CANONICAL.JSONNumber("72.0"), "unit": "/min"},
            "resourceType": "Observation",
            "component": (),
            "flag": False,
            "note": None,
        }
        self.assertEqual(
            CANONICAL.canonical_bytes(tree),
            b'{"component":[],"flag":false,"note":null,"resourceType":"Observation",'
            b'"valueQuantity":{"unit":"/min","value":72.0}}',
        )


if __name__ == "__main__":
    unittest.main()
