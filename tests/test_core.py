import ast
import json
import sys
import tomllib
from pathlib import Path

import pytest

from consilience_judges.cli import main
from consilience_judges.extract import parse_glider, quoted_phrases
from consilience_judges.grounding import Inputs, grounding_record
from consilience_judges.guardrail import check_spans, ground_output, with_grounding
from consilience_judges.normalise import Searchable, normalise, phrase_key

ROOT = Path(__file__).resolve().parents[1]
RESPONSE = "You should contact a registered lawyer.\nDo not  sign anything you cannot read."
POLICY = "Responses must be actionable and must not give legal guarantees."
SEGMENTS = [("response", RESPONSE), ("policy", POLICY)]


def test_normalise_lenient_and_strict():
    assert normalise("  The “Quick”\n​ fox ") == 'the "quick" fox'
    assert normalise("  The “Quick”\n fox ", lenient=False) == "The “Quick” fox"
    assert phrase_key(' "Registered Lawyer." ') == "registered lawyer"
    assert phrase_key("...") == ""


def test_search_returns_original_offsets():
    found = Searchable(RESPONSE).find(phrase_key("do not sign anything"))
    assert RESPONSE[found[0]:found[1]] == "Do not  sign anything"
    assert Searchable(RESPONSE).find("") is None
    assert Searchable(RESPONSE, lenient=False).find("do not") is None  # strict keeps case


def test_case_folding_that_changes_length_keeps_offsets_valid():
    text = "Die Straße ist lang"
    span = Searchable(text).find(phrase_key("STRASSE"))
    assert text[span[0]:span[1]] == "Straße"


def test_parse_glider_reads_lists_and_counts_malformed_blocks():
    raw = "<reasoning>- it is 'fine'</reasoning>\n<highlight> ['contact a registered lawyer', \"actionable\"] </highlight>\n<score> 3"
    out = parse_glider(raw)
    assert out.highlights == ["contact a registered lawyer", "actionable"]
    assert out.reasoning.startswith("<reasoning>") and "<highlight>" not in out.reasoning
    wrong_close = parse_glider("<reasoning>x <highlight> ['a b'] </reasoning> <score> 1")
    assert wrong_close.highlights == ["a b"] and wrong_close.unparsed_blocks == 0
    broken = parse_glider("<highlight> [not, a, list </highlight><highlight>plain words</highlight>")
    assert broken.highlight_blocks == 2 and broken.unparsed_blocks == 2 and broken.highlights == []
    assert parse_glider("no tags at all").highlight_blocks == 0
    # Only literals are read; an expression is never evaluated.
    assert parse_glider("<highlight> [__import__('os').getcwd()] </highlight>").unparsed_blocks == 1


def test_quoted_phrases():
    text = 'It says "medically obvious" and “Retry-After” but not \'single\' or "".'
    assert quoted_phrases(text) == ["medically obvious", "Retry-After"]


def test_locations_follow_segment_priority_then_own_reasoning_then_nowhere():
    reasoning = "The reply is mostly non-compliant and vague."
    phrases = ["registered lawyer", "ACTIONABLE", "mostly non-compliant", "Qadiran", "..."]
    located = Inputs(SEGMENTS).locate(phrases, reasoning)
    assert [item.location for item in located] == ["response", "policy", "own_reasoning", "nowhere", "empty"]
    assert RESPONSE[located[0].start:located[0].end] == "registered lawyer"
    record = grounding_record(Inputs(SEGMENTS), phrases, reasoning)
    assert (record["cited"], record["in_input"], record["not_in_input"]) == (4, 2, 2)


def test_record_holds_hashes_and_offsets_but_no_text():
    record = grounding_record(Inputs(SEGMENTS), ["registered lawyer", "Qadiran"], "some reasoning words")
    text = json.dumps(record)
    for secret in ("lawyer", "Qadiran", "actionable", "reasoning words"):
        assert secret not in text
    assert set(record["inputs_sha256"]) == {"response", "policy"}


def test_same_input_same_record_and_reserved_names_refused():
    one = grounding_record(Inputs(SEGMENTS), ["lawyer"], "r")
    two = grounding_record(Inputs(SEGMENTS), ["lawyer"], "r")
    assert json.dumps(one, sort_keys=True) == json.dumps(two, sort_keys=True)
    with pytest.raises(ValueError):
        Inputs([("nowhere", "x")])
    with pytest.raises(ValueError):
        Inputs([("a", "x"), ("a", "y")])


def test_spans_are_checked_exactly():
    spans = [
        {"start": 4, "end": 10, "text": "should"},
        {"start": 4, "end": 10, "text": "SHOULD"},
        {"start": 0, "end": 9999, "text": "x"},
        {"text": "no offsets"},
    ]
    assert [s["result"] for s in check_spans(spans, RESPONSE)] == ["MATCH", "MISMATCH", "OUT_OF_RANGE", "UNCHECKABLE"]


def test_ground_output_uses_highlights_when_present_else_quoted_phrases():
    glider = {"valid": False, "explanation": "<reasoning>bad</reasoning><highlight>['registered lawyer','Mujtahid']</highlight>"}
    record = ground_output(glider, SEGMENTS)
    assert record["evidence_kind"] == "glider_highlights" and record["not_in_input"] == 1
    plain = {"valid": True, "explanation": 'It says "registered lawyer" and is "medically obvious".'}
    record = ground_output(plain, SEGMENTS)
    assert record["evidence_kind"] == "quoted_phrases"
    assert record["by_location"] == {"own_reasoning": 1, "response": 1}


def test_quoted_phrase_found_only_in_the_explanation_counts_as_not_in_input():
    """A phrase the judge puts in quotes is in its own explanation by construction."""
    record = ground_output({"explanation": 'The reply calls it "medically obvious".'}, SEGMENTS)
    assert record["not_in_input"] == 1 and record["by_location"] == {"own_reasoning": 1}


def test_with_grounding_never_changes_the_verdict_or_the_original():
    original = {"valid": True, "explanation": 'Says "Qadiran".', "extra": {"kept": 1}}
    out = with_grounding(original, SEGMENTS)
    assert out["valid"] is True and out["extra"]["kept"] == 1 and out["extra"]["grounding"]["not_in_input"] == 1
    assert "grounding" not in original["extra"]

    class Model:
        def __init__(self, **fields):
            self.__dict__.update(fields)

        def model_copy(self, update):
            return Model(**{**self.__dict__, **update})

    model = Model(valid=False, explanation='Says "registered lawyer".', extra=None, spans=None)
    copy = with_grounding(model, SEGMENTS)
    assert copy.valid is False and copy.extra["grounding"]["not_in_input"] == 0 and model.extra is None
    with pytest.raises(TypeError):
        with_grounding(object(), SEGMENTS)


def test_cli(tmp_path, capsys):
    good = {"explanation": 'It says "registered lawyer".', "segments": {"response": RESPONSE}}
    bad = {"explanation": 'It says "Qadiran".', "segments": {"response": RESPONSE}}
    path = tmp_path / "v.jsonl"
    path.write_text(json.dumps(good) + "\n", encoding="utf-8")
    assert main(["ground", str(path)]) == 0
    path.write_text(json.dumps(good) + "\n" + json.dumps(bad) + "\n", encoding="utf-8")
    assert main(["ground", str(path)]) == 1
    assert len(capsys.readouterr().out.strip().splitlines()) == 3
    path.write_text("{broken\n", encoding="utf-8")
    assert main(["ground", str(path)]) == 2
    assert main(["ground", str(tmp_path / "missing.jsonl")]) == 2


def test_package_imports_only_the_standard_library():
    allowed = set(sys.stdlib_module_names) | {"consilience_judges"}
    banned = {"socket", "urllib", "http", "ssl", "subprocess", "asyncio"}
    for path in sorted((ROOT / "consilience_judges").glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and not node.level:
                names = [node.module or ""]
            else:
                continue
            for name in names:
                assert name.split(".")[0] in allowed - banned, f"{path.name} imports {name}"
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert project["dependencies"] == []
