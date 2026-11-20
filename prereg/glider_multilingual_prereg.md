# Preregistration: grounding of GLIDER highlights in a public multilingual guardrail study

Committed alone, before the held-out files were opened or scored.

- Date: 20 Nov 2026
- Frozen code: commit `5d5271b26a38fa5907d40fa559cb5f9a9430f5f6` (method `judge-grounding-1`, `study/glider_multilingual.py`)
- Data: `github.com/royapakzad/multilingual_llm_guardrails` at commit `3a6c7df1b85db55099fd1dd513e8ea531682bd79`. Not stored in this repository.
- Development file (method fixed while looking at it): `results/Full Glider GPT results.csv`, SHA-256 `ff1a5e555ac319bd26bb37986b0854b052a26d057ccfc95b9ae10f16a39983db`
- Held-out files (not opened before this commit; only their bytes were hashed):
  - `results/Full Glider Gemini results.csv`, SHA-256 `33768c3a861b270b16f3e1e7ecc0c885607879e6fb11458d0789135d0a90b325`
  - `results/Full Glider Mistal results.csv`, SHA-256 `09ff088b1abbbdb6b70db8d0ad6d576acec6dfa39e716cf5f9d519e1412194fb`

## Background

The study's authors reported that a judge "hallucinated terms" and gave examples. They did not report a rate. GLIDER's own paper defines a highlight span as "a list of words or phrases from the evaluated text that most influence the decision" and adds that they "must be a part of the evaluated text and not from the task instructions" (arXiv 2412.14140, section 3).

## Question

For each GLIDER judgment, where does each highlighted phrase occur in what the judge was given?

## Method (fixed)

- The judge's input is rebuilt from the study's script: the assistant response, the user message and system prompt, the policy used for that judgment, and every fixed instruction, rubric and criteria text. All of it counts as input.
- Highlights are read from the `<highlight>` list. A block that is not a list of strings is counted as unparsed and left out.
- A highlight is **in the input** if it occurs verbatim in any of those texts after the lenient normalisation (whitespace collapsed, typographic quotes and dashes straightened, case folded, punctuation trimmed from the ends of the phrase). Otherwise it is **not in the input**, split into "in the judge's own reasoning" and "nowhere".
- The strict normalisation (exact case and quote style) is reported beside it as a sensitivity check.
- Control: the same highlights searched in the response of a different row of the same language.

## Primary cell

**English response judged under the English policy.** Here the judge, the response, the policy and the highlights are all in English, so "verbatim" has its plain meaning.

Development file, this cell: 136 of 329 highlights not in the input; 17 of 29 judgments with at least one; control 20 of 329 against 140 of 329 in the matching response.

## Predictions, for each held-out file separately, in the primary cell

- **H1.** At least 20% of highlights are not in the input.
- **H2.** At least 40% of judgments that have highlights have at least one that is not in the input.
- **H3 (control).** Fewer highlights are found in a different row's response than in the matching response.
- **H4 (secondary).** The share not in the input is higher under the English policy than under the Farsi policy, for English responses.

## Decision rules

- H1 and H2 hold in both held-out files: the pattern seen in the development file is reported as general across the three assistant models in this study.
- Either fails in either file: reported as measured, and the pattern is described as not general.
- H3 fails: the matching method is not measuring what it claims, and no rate is reported.
- Whatever happens, every cell and every count is published.

## What is descriptive only

- The three other cells (English response under the Farsi policy; Farsi responses under either policy). For Farsi responses the highlights are almost all written in English, so a highlight that translates the response cannot be verbatim. Those cells are reported with that note and are never used as a headline.
- FlowJudge and AnyLLM files. Not part of this preregistration.

## What this can and cannot show

It shows how often a phrase offered as evidence is absent from everything the judge was given. It does not show that any verdict is wrong, and it is not a statement about GLIDER outside this study's setup (one prompt layout, one topic, 60 scenarios, three assistant models). It supports and puts a number on an observation the study's authors already published.
