"""Ground a verdict that has the shape of any-guardrail's ``GuardrailOutput``.

Works by shape: any object or dict with ``explanation`` and, optionally, ``spans``
(each with ``start``, ``end``, ``text``). This package imports no guardrail library.

Two checks:

- **Cited phrases.** GLIDER highlights if the explanation carries them, otherwise the
  double-quoted phrases in the explanation. Each is located in the inputs.
- **Spans.** A span says "characters start to end of the judged text are ``text``".
  That is checked exactly.

The verdict itself is never changed.
"""

from __future__ import annotations

from typing import Any

from .extract import parse_glider, quoted_phrases
from .grounding import Inputs, grounding_record


def _get(obj: Any, name: str) -> Any:
    return obj.get(name) if isinstance(obj, dict) else getattr(obj, name, None)


def check_spans(spans: Any, judged_text: str) -> list[dict[str, Any]]:
    """For each span: does ``judged_text[start:end]`` equal the span's ``text``?"""
    out = []
    for index, span in enumerate(spans or []):
        start, end, text = _get(span, "start"), _get(span, "end"), _get(span, "text")
        if not isinstance(start, int) or not isinstance(end, int) or isinstance(start, bool) or isinstance(end, bool):
            out.append({"index": index, "result": "UNCHECKABLE", "reason": "no_offsets"})
        elif not 0 <= start <= end <= len(judged_text):
            out.append({"index": index, "result": "OUT_OF_RANGE"})
        elif text is None:
            out.append({"index": index, "result": "UNCHECKABLE", "reason": "no_text"})
        elif judged_text[start:end] == text:
            out.append({"index": index, "result": "MATCH"})
        else:
            out.append({"index": index, "result": "MISMATCH"})
    return out


def ground_output(output: Any, segments: list[tuple[str, str]], lenient: bool = True) -> dict[str, Any]:
    """Grounding record for one verdict. ``segments[0]`` is taken as the judged text."""
    explanation = _get(output, "explanation") or ""
    glider = parse_glider(explanation)
    if glider.highlight_blocks:
        phrases, reasoning, kind = glider.highlights, glider.reasoning, "glider_highlights"
    else:
        phrases, reasoning, kind = quoted_phrases(explanation), explanation, "quoted_phrases"
    inputs = Inputs(segments, lenient)
    record = grounding_record(inputs, phrases, reasoning)
    record["evidence_kind"] = kind
    record["unparsed_highlight_blocks"] = glider.unparsed_blocks
    spans = _get(output, "spans")
    if spans:
        record["spans"] = check_spans(spans, segments[0][1] if segments else "")
    return record


def with_grounding(output: Any, segments: list[tuple[str, str]], lenient: bool = True) -> Any:
    """Return the verdict with the grounding record under ``extra["grounding"]``.

    A dict comes back as a new dict. A pydantic model comes back as a copy made with
    ``model_copy``. The original is not modified and ``valid`` is never touched.
    """
    record = ground_output(output, segments, lenient)
    extra = dict(_get(output, "extra") or {})
    extra["grounding"] = record
    if isinstance(output, dict):
        return {**output, "extra": extra}
    if hasattr(output, "model_copy"):
        return output.model_copy(update={"extra": extra})
    raise TypeError("output must be a dict or a pydantic model")
