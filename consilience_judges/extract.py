"""Pull the cited evidence out of a judge's raw output. Fixed rules, no judgement.

Two kinds of evidence are recognised:

- GLIDER ``<highlight>`` lists. GLIDER's own paper defines a highlight span as
  "a list of words or phrases from the evaluated text that most influence the
  decision", with the constraint that they "must be a part of the evaluated text
  and not from the task instructions" (arXiv 2412.14140, section 3).
- Quoted phrases in any explanation: text between a pair of double quotes.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field

_HIGHLIGHT_BLOCK = re.compile(r"<highlight>(.*?)(?:</highlight>|</reasoning>|<score>|\Z)", re.DOTALL)
_LIST = re.compile(r"\[.*\]", re.DOTALL)
_DOUBLE_QUOTED = re.compile(r"[\"“]([^\"“”\n]{2,300})[\"”]")


@dataclass
class GliderOutput:
    reasoning: str
    highlights: list[str] = field(default_factory=list)
    highlight_blocks: int = 0
    unparsed_blocks: int = 0


def parse_glider(raw: str) -> GliderOutput:
    """Split a raw GLIDER output into its reasoning and its highlight list.

    The reasoning is everything before the first ``<highlight>`` tag. A highlight
    block whose content is not a list of strings is counted as unparsed, never
    guessed at.
    """
    raw = raw or ""
    first = raw.find("<highlight>")
    out = GliderOutput(reasoning=raw if first < 0 else raw[:first])
    for match in _HIGHLIGHT_BLOCK.finditer(raw):
        out.highlight_blocks += 1
        found = _LIST.search(match.group(1))
        items = None
        if found:
            try:
                value = ast.literal_eval(found.group(0))
                if isinstance(value, (list, tuple)) and all(isinstance(v, str) for v in value):
                    items = list(value)
            except (ValueError, SyntaxError, MemoryError, RecursionError):
                items = None
        if items is None:
            out.unparsed_blocks += 1
        else:
            out.highlights.extend(items)
    return out


def quoted_phrases(text: str) -> list[str]:
    """Phrases between double quotes, in order of appearance."""
    return [match.group(1) for match in _DOUBLE_QUOTED.finditer(text or "")]
