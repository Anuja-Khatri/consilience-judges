# consilience-judges

Receipts for guardrail judges. When an LLM judge explains a verdict, it cites evidence: phrases it highlights or puts in quotes. This tool checks, with fixed rules, whether each cited phrase is really in what the judge was given.

**Independent work, not affiliated with or endorsed by Mozilla, Mozilla.ai, Patronus AI, or the authors of the study used below.** It reads [any-guardrail](https://github.com/mozilla-ai/any-guardrail)'s output shape as it is and needs no change to any-guardrail.

Status: pre-alpha.

No model is called. No network is used. The package has no dependencies outside the Python standard library. The same input gives the same output. The verdict is never changed.

## Why

In 2026 researchers at Mozilla.ai published a study of guardrail judges on asylum-related questions in English and Farsi, with their data ([blog post](https://blog.mozilla.ai/evaluating-multilingual-context-aware-guardrails-evidence-from-a-humanitarian-llm-use-case/), [data](https://github.com/royapakzad/multilingual_llm_guardrails)). They reported, with examples, that a judge cited terms that "never appeared in the original response". This repository adds a count to that observation and a tool that makes the same check on any verdict.

## What was measured

One judge (GLIDER) in one public study. GLIDER returns a `<highlight>` list. Its own paper defines a highlight span as "a list of words or phrases from the evaluated text that most influence the decision" (arXiv 2412.14140).

For every GLIDER judgment in the study, each highlighted phrase was searched for, verbatim, in everything the judge was given: the response, the user message and system prompt, the policy, and all instructions and rubric text. The method was fixed on one results file. The predictions were then committed (`prereg/glider_multilingual_prereg.md`) before the other two files were opened.

**Primary cell: English responses judged under the English policy.**

| | Development file | Held-out file 1 | Held-out file 2 |
|---|---|---|---|
| Highlighted phrases found in none of the judge's inputs | 136 of 329 | 52 of 310 | 35 of 300 |
| Judgments with at least one such phrase | 17 of 29 | 16 of 28 | 19 of 28 |
| Control: phrases found in a different row's response | 20 of 329 | 52 of 310 | 44 of 300 |
| Phrases found in the matching response | 140 of 329 | 188 of 310 | 185 of 300 |

Across the two held-out files: 87 of 610 highlighted phrases were in none of the judge's inputs, and 35 of 56 judgments had at least one.

**What happened to the predictions.** Two held and two failed.

| Prediction, for each held-out file | Result |
|---|---|
| H1: at least 20% of highlights are not in the input | **Failed** in both files (52 of 310 and 35 of 300) |
| H2: at least 40% of judgments have at least one | Held in both files (16 of 28 and 19 of 28) |
| H3 (control): fewer matches in a different row's response than in the matching one | Held in both files |
| H4: the share is higher under the English policy than under the Farsi policy | **Failed** in both files; it was lower |

So the plain reading is:

- The high share seen in the development file did not generalise. In the held-out files, roughly one highlighted phrase in seven was in none of the judge's inputs, not four in ten.
- What did generalise is the per-judgment picture: in more than half of the judgments, in all three files, at least one phrase offered as evidence was nowhere in the input. Most of those phrases were the judge's own reasoning quoted back.

**Descriptive only (not preregistered).** For Farsi responses the judge's highlights were almost all written in English: 2,253 of 2,270 in the held-out files. A phrase that translates the response cannot match it word for word, so no rate of invention is claimed for those cells. One thing can be counted without that problem: under the English policy, 699 of 1,193 highlights for Farsi responses were phrases from the policy text, and 25 of 1,193 were found in the response.

Every count is in `docs/tables/glider_multilingual.md`, rendered from `results/`. Per-item receipts (file hash, row, phrase hash, location, offsets) are in `results/*_receipts.jsonl`. They hold hashes and offsets only; the study's rows are not copied into this repository.

## What this does not show

- It does not show that any verdict was wrong.
- It is one judge, one prompt layout, one topic, 60 scenarios and three assistant models. It is not a statement about GLIDER in general.
- "Not in the input" means not there word for word, after a generous normalisation (case and quote style ignored). A paraphrase counts as not there. Whether a highlight should be allowed to paraphrase is a question about the judge's specification; GLIDER's says highlights are taken from the evaluated text.
- The development file's numbers were seen before the predictions were written. They are shown for completeness and are not evidence.

## Use it

```bash
pip install git+https://github.com/Anuja-Khatri/consilience-judges
```

On any verdict shaped like any-guardrail's `GuardrailOutput` (a dict or a pydantic model with `explanation` and, optionally, `spans`):

```python
from consilience_judges.guardrail import ground_output, with_grounding

segments = [("response", response_text), ("policy", policy_text)]   # the judged text first
record = ground_output(verdict, segments)
record["cited"], record["in_input"], record["not_in_input"]

checked = with_grounding(verdict, segments)   # same verdict, plus extra["grounding"]
```

- If the explanation has a GLIDER `<highlight>` list, those phrases are checked. Otherwise the phrases in double quotes are checked.
- Each phrase gets one location: the first segment that contains it, `own_reasoning` (only in the judge's explanation), or `nowhere`.
- If the verdict has `spans`, each is checked exactly: the judged text between `start` and `end` must equal the span's `text`.
- The record holds hashes and offsets. It holds no text from the inputs or the judge.

From the command line, one JSON object per line with `explanation` and `segments`:

```bash
consilience-judges ground verdicts.jsonl
```

Exit code 0 when every cited phrase is in the input, 1 when at least one is not, 2 on a usage or input error.

## Rerun the study

```bash
git clone https://github.com/royapakzad/multilingual_llm_guardrails data
```

```bash
git -C data checkout 3a6c7df1b85db55099fd1dd513e8ea531682bd79
```

```bash
python -m study.glider_multilingual run data all
```

```bash
STUDY_DATA=data python -m pytest -q
```

The last command re-runs the counts and fails if any published number differs.

## Credits

- The multilingual guardrail study and its data: Roya Pakzad and colleagues, with Mozilla.ai. This work only counts what they made public and first described.
- [any-guardrail](https://github.com/mozilla-ai/any-guardrail) by Mozilla.ai (Apache-2.0): the output shape this tool reads.
- [GLIDER](https://huggingface.co/PatronusAI/glider) by Patronus AI: the judge whose published definition of a highlight is used here.

## Licence

MIT. See `LICENSE`.
