"""Render docs/tables/glider_multilingual.md from the results files. Nothing is typed by hand.

Usage:
    python -m study.render          # write the table
    python -m study.render --check  # fail if the table is out of date
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "docs" / "tables" / "glider_multilingual.md"
SOURCES = ["glider_multilingual_dev.json", "glider_multilingual_heldout.json"]
SHOWN = [
    ("highlights", "Highlights"),
    ("not_in_input", "Not in input"),
    ("not_in_input_strict", "Not in input (strict)"),
    ("judgments_with_any_not_in_input", "Judgments with at least one"),
    ("in_response", "In the response"),
    ("in_conversation", "In user message or system prompt"),
    ("in_policy", "In the policy"),
    ("in_instructions", "In instructions or rubric"),
    ("in_own_reasoning", "Only in the judge's own reasoning"),
    ("in_nowhere", "Nowhere"),
    ("rotated_in_response", "Control: in a different row's response"),
    ("latin_script_highlights", "Written in Latin script"),
    ("unparsed_blocks", "Unparsed highlight blocks"),
]
CELLS = [
    ("en_response.en_policy", "English response, English policy (primary cell)"),
    ("en_response.fa_policy", "English response, Farsi policy (descriptive)"),
    ("fa_response.en_policy", "Farsi response, English policy (descriptive)"),
    ("fa_response.fa_policy", "Farsi response, Farsi policy (descriptive)"),
]
FILES = [("gpt", "dev"), ("gemini", "heldout"), ("mistral", "heldout")]


def load() -> dict[str, dict]:
    metrics: dict[str, dict] = {}
    for name in SOURCES:
        for metric in json.loads((ROOT / "results" / name).read_text(encoding="utf-8"))["metrics"]:
            metrics[metric["metric_id"]] = metric
    return metrics


def _cell(metric: dict) -> str:
    if metric["n"]:
        return f"{metric['count']} of {metric['n']} ({metric['value'] * 100:.1f}%)"
    return str(metric["count"])


def render(metrics: dict[str, dict]) -> str:
    lines = [
        "# GLIDER highlights: where the cited phrases are",
        "",
        "Rendered from `results/glider_multilingual_*.json` by `study/render.py`. Do not edit by hand.",
        "",
        "Data: `royapakzad/multilingual_llm_guardrails` at commit `3a6c7df`. One column per results file,",
        "named by the assistant model whose responses were judged. `dev` is the file the method was fixed on;",
        "`heldout` files were opened only after the preregistration (`prereg/glider_multilingual_prereg.md`).",
        "",
    ]
    for cell, title in CELLS:
        lines += [f"## {title}", "", "| | " + " | ".join(f"{f} ({s})" for f, s in FILES) + " |", "|---|---|---|---|"]
        for name, label in SHOWN:
            row = [_cell(metrics[f"glider.{f}.{cell}.{name}"]) for f, _s in FILES]
            lines.append(f"| {label} | " + " | ".join(row) + " |")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    text = render(load())
    if argv == ["--check"]:
        if not TABLE.exists() or TABLE.read_text(encoding="utf-8") != text:
            print("docs/tables/glider_multilingual.md is out of date; run python -m study.render", file=sys.stderr)
            return 1
        return 0
    TABLE.parent.mkdir(parents=True, exist_ok=True)
    TABLE.write_text(text, encoding="utf-8")
    print(f"wrote {TABLE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
