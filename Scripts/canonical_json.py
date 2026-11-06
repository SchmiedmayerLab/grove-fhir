"""Reference implementation of grove-canonical-json-v0, the byte form every Grove digest hashes."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

# grove-canonical-json-v0 (catalog/exchange-protocol.json `canonicalJson`) reads one RFC 8259 JSON
# text and writes it with members sorted by their bytes, no insignificant whitespace, strings escaped
# as RFC 8785 section 3.2.2.2 escapes them, and every number as its input lexeme. A lossless tree
# keeps each number as its exact lexeme (JSONNumber), so 72.0, 72, -0, 1E-7 and 1e2 stay distinct.
# Scripts/fhir_fixture_corpus.py formats fixtures and is never an identity input.

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from typing import Any


NAME = "grove-canonical-json-v0"
BYTE_ORDER_MARK = b"\xef\xbb\xbf"

# The RFC 8259 number grammar, ASCII digits only.
NUMBER = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?", re.ASCII)
SURROGATE = re.compile("[\ud800-\udfff]")

# RFC 8785 section 3.2.2.2: the quotation mark, the reverse solidus, short forms for U+0008, U+0009,
# U+000A, U+000C and U+000D, lowercase \u00xx for the other C0 controls, and every other scalar raw.
STRING_ESCAPES = {
    ord('"'): '\\"',
    ord("\\"): "\\\\",
    0x08: "\\b",
    0x09: "\\t",
    0x0A: "\\n",
    0x0C: "\\f",
    0x0D: "\\r",
}
STRING_ESCAPES.update(
    {code: f"\\u{code:04x}" for code in range(0x20) if code not in STRING_ESCAPES}
)

# The refusals of the catalog's `invalidCanonicalJson` vectors, plus the remaining grammar refusals.
ERROR_CODES = frozenset({
    "duplicate-member",
    "non-ascii-member-name",
    "unpaired-surrogate",
    "byte-order-mark",
    "invalid-utf8",
    "invalid-json",
    "non-json-constant",
    "invalid-number",
    "not-lossless",
    "nesting-too-deep",
})


class CanonicalJSONError(ValueError):
    """Raised when a JSON text or tree has no grove-canonical-json-v0 form."""

    def __init__(self, code: str, message: str) -> None:
        if code not in ERROR_CODES:
            raise ValueError(f"unknown canonical JSON error code {code!r}")
        super().__init__(f"{code}: {message}")
        self.code = code


class JSONNumber(str):
    """One JSON number, kept as its exact input lexeme.

    A number equals only a number with the same lexeme, never the string with those characters.
    `json.dumps` would write it as a string; serialize lossless trees with `canonical_bytes`.
    """

    __slots__ = ()

    def __new__(cls, lexeme: str) -> JSONNumber:
        if not isinstance(lexeme, str) or NUMBER.fullmatch(lexeme) is None:
            raise CanonicalJSONError(
                "invalid-number", f"{lexeme!r} is not an RFC 8259 number"
            )
        return super().__new__(cls, lexeme)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, JSONNumber) and str.__eq__(self, other)

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    __hash__ = str.__hash__

    def __repr__(self) -> str:
        return f"JSONNumber({str.__repr__(self)})"


def _refuse_constant(constant: str) -> Any:
    raise CanonicalJSONError("non-json-constant", f"{constant} is not a JSON value")


def _refuse_unpaired_surrogate(value: str, label: str) -> None:
    # Strict UTF-8 decoding admits no raw surrogate, so one left after parsing came from an
    # unpaired \uD800-\uDFFF escape; Python joins a valid escaped pair into one scalar.
    if SURROGATE.search(value) is not None:
        raise CanonicalJSONError("unpaired-surrogate", f"{label} has an unpaired surrogate escape")


def _member_name(name: str) -> str:
    _refuse_unpaired_surrogate(name, "a member name")
    if not name.isascii():
        raise CanonicalJSONError(
            "non-ascii-member-name",
            f"member name {name!r} has a scalar above U+007F",
        )
    return name


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    members: dict[str, Any] = {}
    for name, value in pairs:
        # Names are ASCII once _member_name admits them, so str equality is bytewise equality.
        if _member_name(name) in members:
            raise CanonicalJSONError("duplicate-member", f"member name {name!r} repeats")
        members[name] = value
    return members


def _refuse_unpaired_surrogates_in_values(tree: Any) -> None:
    pending = [tree]
    while pending:
        value = pending.pop()
        if isinstance(value, JSONNumber):
            continue
        if isinstance(value, str):
            _refuse_unpaired_surrogate(value, "a string")
        elif isinstance(value, dict):
            pending.extend(value.values())
        elif isinstance(value, list):
            pending.extend(value)


def loads_lossless(data: bytes) -> Any:
    """Parse one RFC 8259 JSON text in UTF-8 into a lossless tree.

    Objects become dicts, arrays lists, strings str, numbers JSONNumber lexemes, and true, false and
    null become True, False and None. Every refusal raises CanonicalJSONError with its code.
    """
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise CanonicalJSONError("invalid-json", "the input must be UTF-8 bytes")
    data = bytes(data)
    if data.startswith(BYTE_ORDER_MARK):
        raise CanonicalJSONError("byte-order-mark", "the input starts with a byte order mark")
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise CanonicalJSONError("invalid-utf8", f"the input is not UTF-8: {error}") from error
    try:
        # The json scanner hands parse_int and parse_float the exact lexeme it matched.
        tree = json.loads(
            text,
            parse_int=JSONNumber,
            parse_float=JSONNumber,
            parse_constant=_refuse_constant,
            object_pairs_hook=_object,
            strict=True,
        )
    except json.JSONDecodeError as error:
        raise CanonicalJSONError("invalid-json", str(error)) from error
    except RecursionError as error:
        raise CanonicalJSONError(
            "nesting-too-deep", "the input nests deeper than this parser can follow"
        ) from error
    _refuse_unpaired_surrogates_in_values(tree)
    return tree


def _string(value: str, label: str) -> str:
    _refuse_unpaired_surrogate(value, label)
    return '"' + value.translate(STRING_ESCAPES) + '"'


class _Token(str):
    """Punctuation the serializer emits verbatim, never a JSON string."""

    __slots__ = ()


def canonical_bytes(tree: Any) -> bytes:
    """Serialize a lossless tree in grove-canonical-json-v0: UTF-8, no trailing newline."""
    output: list[str] = []
    # An explicit stack, so any tree the parser returns serializes, however deeply it nests.
    pending: list[Any] = [tree]
    while pending:
        value = pending.pop()
        if isinstance(value, _Token):
            output.append(value)
        elif value is None:
            output.append("null")
        elif value is True:
            output.append("true")
        elif value is False:
            output.append("false")
        elif isinstance(value, JSONNumber):
            # Recheck: copy and pickle rebuild a JSONNumber without running its constructor.
            if NUMBER.fullmatch(value) is None:
                raise CanonicalJSONError(
                    "invalid-number", f"{str(value)!r} is not an RFC 8259 number"
                )
            output.append(str(value))
        elif isinstance(value, str):
            output.append(_string(value, "a string"))
        elif isinstance(value, Mapping):
            members = []
            for name in value:
                if not isinstance(name, str) or isinstance(name, (JSONNumber, _Token)):
                    raise CanonicalJSONError(
                        "not-lossless", f"member name {name!r} is not a string"
                    )
                members.append((_member_name(name).encode("ascii"), name))
            output.append("{")
            pending.append(_Token("}"))
            for index, (_, name) in reversed(list(enumerate(sorted(members)))):
                pending.append(value[name])
                pending.append(_Token(_string(name, "a member name") + ":"))
                if index:
                    pending.append(_Token(","))
        elif isinstance(value, (list, tuple)):
            output.append("[")
            pending.append(_Token("]"))
            for index in reversed(range(len(value))):
                pending.append(value[index])
                if index:
                    pending.append(_Token(","))
        else:
            raise CanonicalJSONError(
                "not-lossless",
                f"{type(value).__name__} is not a lossless JSON value; parse the JSON text with "
                "loads_lossless, which keeps every number as its JSONNumber lexeme",
            )
    return "".join(output).encode("utf-8")


def canonicalize(data: bytes) -> bytes:
    """Return the grove-canonical-json-v0 bytes of one JSON text."""
    return canonical_bytes(loads_lossless(data))
