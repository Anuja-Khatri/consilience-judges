"""Locate each piece of cited evidence in what the judge was given.

The caller supplies the judge's inputs as named segments, in priority order, for
example ``[("response", ...), ("conversation", ...), ("policy", ...), ("instructions", ...)]``.
Each cited phrase gets exactly one location:

- the name of the first segment that contains it verbatim (after normalisation);
- ``own_reasoning``: in none of the inputs, but in the judge's own reasoning text;
- ``nowhere``: in neither;
- ``empty``: nothing left after trimming punctuation.

``own_reasoning`` and ``nowhere`` together are "not in the input": the judge offered
as evidence something it was never given.
"""

from __future__ import annotations

import hashlib
from collections import Counter
from dataclasses import dataclass
from typing import Any

from . import METHOD_VERSION
from .normalise import NORMALISATION_VERSION, Searchable, phrase_key

OWN_REASONING = "own_reasoning"
NOWHERE = "nowhere"
EMPTY = "empty"
NOT_IN_INPUT = (OWN_REASONING, NOWHERE)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Located:
    index: int
    phrase_sha256: str
    location: str
    start: int | None = None
    end: int | None = None

    @property
    def in_input(self) -> bool:
        return self.location not in (OWN_REASONING, NOWHERE, EMPTY)

    def to_json(self) -> dict[str, Any]:
        out: dict[str, Any] = {"index": self.index, "phrase_sha256": self.phrase_sha256, "location": self.location}
        if self.start is not None:
            out["start"], out["end"] = self.start, self.end
        return out


class Inputs:
    """The judge's inputs, prepared once. Segment order is the priority order."""

    def __init__(self, segments: list[tuple[str, str]], lenient: bool = True):
        names = [name for name, _text in segments]
        if len(set(names)) != len(names) or set(names) & {OWN_REASONING, NOWHERE, EMPTY}:
            raise ValueError("segment names must be unique and must not use a reserved name")
        self.lenient = lenient
        self.segments = [(name, Searchable(text or "", lenient)) for name, text in segments]
        self.sha256 = {name: _sha(text or "") for name, text in segments}

    def locate(self, phrases: list[str], reasoning: str = "") -> list[Located]:
        own = Searchable(reasoning or "", self.lenient)
        located = []
        for index, phrase in enumerate(phrases):
            key = phrase_key(phrase, self.lenient)
            digest = _sha(key)
            if not key:
                located.append(Located(index, digest, EMPTY))
                continue
            for name, searchable in self.segments:
                span = searchable.find(key)
                if span is not None:
                    located.append(Located(index, digest, name, span[0], span[1]))
                    break
            else:
                span = own.find(key)
                if span is not None:
                    located.append(Located(index, digest, OWN_REASONING))
                else:
                    located.append(Located(index, digest, NOWHERE))
        return located


def grounding_record(inputs: Inputs, phrases: list[str], reasoning: str = "") -> dict[str, Any]:
    """The record attached to a verdict: where each cited phrase was found, with hashes.

    It holds hashes and offsets only. It holds no text from the inputs or the judge.
    """
    located = inputs.locate(phrases, reasoning)
    counts = Counter(item.location for item in located)
    cited = sum(1 for item in located if item.location != EMPTY)
    not_in_input = sum(counts[name] for name in NOT_IN_INPUT)
    body: dict[str, Any] = {
        "method": METHOD_VERSION,
        "normalisation": NORMALISATION_VERSION,
        "lenient": inputs.lenient,
        "inputs_sha256": dict(inputs.sha256),
        "reasoning_sha256": _sha(reasoning or ""),
        "cited": cited,
        "in_input": cited - not_in_input,
        "not_in_input": not_in_input,
        "by_location": dict(sorted(counts.items())),
        "items": [item.to_json() for item in located],
    }
    return body
