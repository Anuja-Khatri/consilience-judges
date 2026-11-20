"""Published numbers are exactly what the code produces, and the table matches them."""

import json
import os
import re
from pathlib import Path

import pytest

from study import glider_multilingual, render

ROOT = Path(__file__).resolve().parents[1]
STUDY_DATA = os.environ.get("STUDY_DATA")


def _metrics():
    return render.load()


def test_table_is_rendered_from_the_results():
    assert render.main(["--check"]) == 0


def test_preregistration_names_the_files_that_were_scored():
    prereg = (ROOT / "prereg" / "glider_multilingual_prereg.md").read_text(encoding="utf-8")
    heldout = json.loads((ROOT / "results" / "glider_multilingual_heldout.json").read_text(encoding="utf-8"))
    for rel in ("results/Full Glider Gemini results.csv", "results/Full Glider Mistal results.csv"):
        assert heldout["files_sha256"][rel] in prereg


def test_readme_counts_come_from_the_results():
    """Every 'N of M' in the README's results sections must be a count in the registry, or a sum of them."""
    metrics = _metrics()
    allowed = {(m["count"], m["n"]) for m in metrics.values() if m["n"]}

    def pooled(cells, name, files=("gemini", "mistral")):
        ms = [metrics[f"glider.{f}.{c}.{name}"] for f in files for c in cells]
        return sum(m["count"] for m in ms), sum(m["n"] for m in ms)

    primary = ["en_response.en_policy"]
    allowed |= {pooled(primary, "not_in_input"), pooled(primary, "judgments_with_any_not_in_input")}
    allowed.add(pooled(["fa_response.en_policy", "fa_response.fa_policy"], "latin_script_highlights"))
    allowed |= {pooled(["fa_response.en_policy"], "in_policy"), pooled(["fa_response.en_policy"], "in_response")}
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    section = readme.split("## What was measured", 1)[1].split("## What this does not show", 1)[0]
    found = {(int(a.replace(",", "")), int(b.replace(",", ""))) for a, b in re.findall(r"([\d,]+) of ([\d,]+)", section)}
    assert found and found <= allowed, found - allowed


def test_receipts_hold_no_study_text():
    for name in ("dev", "heldout"):
        path = ROOT / "results" / f"glider_multilingual_{name}_receipts.jsonl"
        for line in path.read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            assert set(record) == {"file", "file_sha256", "row_id", "language", "policy", "items"}
            for item in record["items"]:
                assert set(item) <= {"index", "phrase_sha256", "location", "start", "end"}


@pytest.mark.skipif(not STUDY_DATA, reason="STUDY_DATA is not set")
@pytest.mark.parametrize("split", ["dev", "heldout"])
def test_results_are_reproduced_from_the_data(split):
    stored = json.loads((ROOT / "results" / f"glider_multilingual_{split}.json").read_text(encoding="utf-8"))
    assert glider_multilingual.run(Path(STUDY_DATA), split)["results"] == stored
