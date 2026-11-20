"""Two fixed normalisations for verbatim matching, each with a map back to the original.

``strict``: zero-width characters removed, runs of whitespace become one space, ends trimmed.

``lenient`` (the default for grounding): strict, plus typographic quotes and dashes
straightened and case folded. Lenient is the generous choice: it gives the judge the
benefit of the doubt on capitalisation and quote style, so anything it still cannot
find is not there in any ordinary sense.

Neither changes words, digits or their order. There is no stemming, no synonym
matching and no fuzzy distance.
"""

from __future__ import annotations

NORMALISATION_VERSION = "consilience-judges.normalise/1"

_ZERO_WIDTH = frozenset("​‌‍⁠﻿")
_STRAIGHTEN = {
    "‘": "'", "’": "'", "‚": "'", "‛": "'",
    "“": '"', "”": '"', "„": '"', "‟": '"',
    "‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-",
}
# Stripped from the two ends of a cited phrase only, never from the text searched.
_EDGE = " \t\n\r\"'`.,;:!?()[]{}<>*-_"


def normalise_with_map(text: str, lenient: bool = True) -> tuple[str, list[int]]:
    """Return the normalised text and, for each of its characters, the original index."""
    chars: list[str] = []
    origin: list[int] = []
    space_at = -1
    for i, ch in enumerate(text):
        if ch in _ZERO_WIDTH:
            continue
        if ch.isspace():
            if chars and space_at < 0:
                space_at = i
            continue
        if space_at >= 0:
            chars.append(" ")
            origin.append(space_at)
            space_at = -1
        if lenient:
            ch = _STRAIGHTEN.get(ch, ch)
            folded = ch.casefold()
            # Case folding can change length (for example the German sharp s).
            for out in folded:
                chars.append(out)
                origin.append(i)
        else:
            chars.append(ch)
            origin.append(i)
    return "".join(chars), origin


def normalise(text: str, lenient: bool = True) -> str:
    return normalise_with_map(text, lenient)[0]


def phrase_key(phrase: str, lenient: bool = True) -> str:
    """A cited phrase, normalised, with punctuation and quotes trimmed from its ends."""
    return normalise(phrase.strip(_EDGE), lenient).strip(_EDGE)


class Searchable:
    """A text prepared once for repeated verbatim searches."""

    def __init__(self, text: str, lenient: bool = True):
        self.text = text
        self.normalised, self._origin = normalise_with_map(text, lenient)

    def find(self, key: str) -> tuple[int, int] | None:
        """Original [start, end) of the first occurrence of a normalised key, or None."""
        if not key:
            return None
        at = self.normalised.find(key)
        if at < 0:
            return None
        return self._origin[at], self._origin[at + len(key) - 1] + 1
