# consilience-judges: technical reference

Everything about how this tool is built, why, what it found, what it can and cannot do, and what to reuse. Written so that a later project does not have to rediscover any of it.

Version described: 0.1.0, method `judge-grounding-1`. Python 3.11 or later. No runtime dependencies.

## 1. What it is, in one paragraph

When an LLM judge explains a verdict it cites evidence: phrases it highlights or puts in quotes. This tool takes the judge's output and the texts the judge was given, and reports where each cited phrase occurs: in the judged text, in another input, only in the judge's own reasoning, or nowhere. It also checks span offsets exactly. It works on any verdict with an explanation; it is not tied to one judge or one vendor. It never calls a model or the network, never changes the verdict, and the same input gives the same output.

## 2. Honest status

- It works and is tested (18 tests, plus 2 that re-run the study when the data path is given; lint clean).
- It has been run on one judge (GLIDER) in one public study. The result is real and exact, and modest: see section 7.
- It says whether cited evidence exists in the input. It does not say whether a verdict is right.
- "Not in the input" means not there word for word. A paraphrase counts as not there.

## 3. Repository layout

| Path | What it holds |
|---|---|
| `consilience_judges/__init__.py` | `__version__`, `METHOD_VERSION` |
| `consilience_judges/normalise.py` | Strict and lenient normalisation with an offset map; `phrase_key`; `Searchable` |
| `consilience_judges/extract.py` | `parse_glider` (highlight lists), `quoted_phrases` |
| `consilience_judges/grounding.py` | `Inputs`, `Located`, `grounding_record` |
| `consilience_judges/guardrail.py` | `ground_output`, `with_grounding`, `check_spans` for verdicts in any-guardrail's shape |
| `consilience_judges/cli.py` | `consilience-judges ground FILE` |
| `study/glider_multilingual.py` | The study: rebuilds the judge's input and counts |
| `study/render.py` | Renders `docs/tables/glider_multilingual.md` from `results/` |
| `prereg/glider_multilingual_prereg.md` | The preregistration, committed before the held-out files were opened |
| `results/glider_multilingual_{dev,heldout}.json` | The numbers registries |
| `results/glider_multilingual_{dev,heldout}_receipts.jsonl` | One line per judgment: hashes, locations, offsets |
| `docs/tables/glider_multilingual.md` | Rendered table. Never edited by hand |
| `tests/` | See section 8 |

## 4. The method

### 4.1 Normalisation (`normalise.py`, version `consilience-judges.normalise/1`)

Two fixed normalisations, applied identically to the phrase and to the text searched.

- **Strict:** zero-width characters removed, runs of whitespace become one space, ends trimmed.
- **Lenient (default):** strict, plus typographic quotes and dashes straightened and case folded.

Lenient is the generous choice. It gives the judge the benefit of the doubt on capitalisation and quote style, so a phrase it still cannot find is not there in any ordinary sense. There is no stemming, no synonym matching and no edit distance.

`normalise_with_map` returns the normalised text and, for each of its characters, the index of the original character it came from. Case folding can change length (the German sharp s folds to two letters), so the map is built per output character. `Searchable(text)` prepares a text once and `find(key)` returns the original `[start, end)` of the first match.

`phrase_key(phrase)` normalises a cited phrase and trims punctuation, quotes and brackets from its two ends only. The text being searched is never trimmed.

### 4.2 Evidence extraction (`extract.py`)

- **`parse_glider(raw)`** splits a raw GLIDER output. The reasoning is everything before the first `<highlight>` tag. Each highlight block runs to the first of `</highlight>`, `</reasoning>`, `<score>` or the end, because real outputs close the block with the wrong tag. The block's list is read with `ast.literal_eval`, which accepts only literals, so nothing in a judge's output is ever executed. A block that is not a list of strings is counted in `unparsed_blocks` and left out, never guessed at.
- **`quoted_phrases(text)`** returns the phrases between a pair of double quotes (straight or typographic), 2 to 300 characters, on one line. Single quotes are not used, because apostrophes make them unreliable.

### 4.3 Grounding (`grounding.py`)

`Inputs(segments, lenient=True)` takes the judge's inputs as an ordered list of `(name, text)`. The order is the priority order. Names must be unique and may not be `own_reasoning`, `nowhere` or `empty`.

`Inputs.locate(phrases, reasoning)` gives each phrase exactly one `Located(index, phrase_sha256, location, start, end)`:

1. the name of the first segment that contains it, with original offsets; else
2. `own_reasoning` if it occurs in the judge's reasoning text; else
3. `nowhere`.
4. `empty` if nothing is left after trimming.

`own_reasoning` and `nowhere` together are **not in the input**.

`grounding_record(inputs, phrases, reasoning)` returns: method and normalisation versions, the SHA-256 of each input segment and of the reasoning, `cited`, `in_input`, `not_in_input`, counts by location, and one item per phrase. **It holds hashes and offsets only. It holds no text from the inputs or the judge.**

### 4.4 Verdicts in any-guardrail's shape (`guardrail.py`)

Works by shape on a dict or an object with `explanation` and optionally `spans`. This package imports no guardrail library.

- `ground_output(output, segments)`: if the explanation has a GLIDER highlight block, those phrases are grounded against the reasoning that precedes it; otherwise the double-quoted phrases are grounded, with the whole explanation as the reasoning. A quoted phrase is in the explanation by construction, so one that is in no input lands in `own_reasoning`.
- `check_spans(spans, judged_text)`: for each span, `MATCH` if `judged_text[start:end] == text`, `MISMATCH`, `OUT_OF_RANGE`, or `UNCHECKABLE` when offsets or text are missing. The first segment is taken as the judged text.
- `with_grounding(output, segments)`: returns the same verdict with the record under `extra["grounding"]`. A dict comes back as a new dict; a pydantic model comes back through `model_copy`. The original is not modified and `valid` is never touched.

### 4.5 Command line

`consilience-judges ground FILE [--strict]`. FILE has one JSON object per line with `explanation`, `segments` (an object whose key order is the priority order) and optionally `spans`. One record is printed per line. Exit 0 when every cited phrase is in the input and no span fails, 1 otherwise, 2 on a usage or input error.

## 5. The study

**Data.** `github.com/royapakzad/multilingual_llm_guardrails` at commit `3a6c7df1b85db55099fd1dd513e8ea531682bd79`, described in a post on Mozilla.ai's blog (3 Feb 2026). 60 asylum-related scenarios (30 English, 30 Farsi), answered by three assistant models, judged by three judges through any-guardrail, each under an English and a Farsi policy. The repository shows no licence, so it is not stored here: this repository holds counts, hashes and offsets, and the scripts to re-derive them from a checkout.

**Why GLIDER.** It returns an explicit `<highlight>` list, and its own paper defines what a highlight is: "a list of words or phrases from the evaluated text that most influence the decision", which "must be a part of the evaluated text and not from the task instructions" (arXiv 2412.14140, section 3). That gives the check a published specification to stand on.

**Rebuilding the judge's input.** The study's script (`run_batch_guardrails_all.py`) builds one text for the judge: a fixed preamble, the policy, the rubric, the system prompt, the user message, the assistant response, and fixed instructions. GLIDER also receives its pass criteria and rubric. `study/glider_multilingual.py` rebuilds this as four segments, in priority order:

| Segment | Content |
|---|---|
| `response` | the assistant response |
| `conversation` | the user's scenario and the system prompt |
| `policy` | the policy used for that judgment (English or Farsi) |
| `instructions` | the script's fixed strings and every rubric and criteria file in `config/` |

**Everything counts as input.** GLIDER's paper would allow only the evaluated text. This study put the policy inside the evaluated text, so a phrase found in any segment is treated as grounded. This is the conservative choice.

**Cells.** Response language by policy language: four cells. The **primary cell is English response under the English policy**, where judge, response, policy and highlights are all in English and "verbatim" has its plain meaning. The other three cells are descriptive only. For Farsi responses the judge wrote almost all highlights in English, so a highlight that translates the response cannot be verbatim, and no rate of invention is claimed.

**Control.** The same highlights are searched in the response of the next row of the same language. If highlights matched responses only because they are common words, this rate would be as high as the matched rate.

**Splits.** The method was fixed on one file (`Full Glider GPT results.csv`, the development file). The other two (`Gemini`, `Mistal`) were hashed but not opened until the preregistration was committed.

## 6. Preregistration and how the order is provable

Three commits, in order:
1. `5d5271b`: the core, the study script and the development-file results.
2. `1b806e4`: the preregistration alone, naming the frozen code commit and the SHA-256 of each held-out file.
3. `d7b6e20`: the held-out run.

Predictions, for each held-out file separately, in the primary cell:
- H1: at least 20% of highlights are not in the input.
- H2: at least 40% of judgments that have highlights have at least one that is not in the input.
- H3 (control): fewer highlights are found in a different row's response than in the matching response.
- H4 (secondary): the share not in the input is higher under the English policy than under the Farsi policy.

## 7. Results

Primary cell.

| | Development file | Held-out file 1 | Held-out file 2 |
|---|---|---|---|
| Highlights not in any input | 136 of 329 | 52 of 310 | 35 of 300 |
| Same, strict matching | 147 of 329 | 64 of 310 | 56 of 300 |
| Judgments with at least one | 17 of 29 | 16 of 28 | 19 of 28 |
| In the matching response | 140 of 329 | 188 of 310 | 185 of 300 |
| Control: in a different row's response | 20 of 329 | 52 of 310 | 44 of 300 |
| In the policy | 43 of 329 | 62 of 310 | 70 of 300 |
| Only in the judge's own reasoning | 130 of 329 | 49 of 310 | 26 of 300 |
| Nowhere | 6 of 329 | 3 of 310 | 9 of 300 |

Pooled over the two held-out files: 87 of 610 highlights not in any input; 35 of 56 judgments with at least one.

| Prediction | Outcome |
|---|---|
| H1 | **Failed** in both held-out files |
| H2 | Held in both |
| H3 | Held in both |
| H4 | **Failed** in both; the share was lower under the English policy |

**Reading.**
- The development file was an outlier. About four highlights in ten were ungrounded there; about one in seven in the held-out files.
- The per-judgment result generalised: in more than half of judgments, in all three files, at least one phrase offered as evidence was in none of the inputs. Most of those were the judge's own reasoning quoted back.
- The control held: highlights match their own response far more often than another row's.

**Descriptive, not preregistered.** For Farsi responses in the held-out files, 2,253 of 2,270 highlights were written in Latin script. Under the English policy, 699 of 1,193 were phrases from the policy and 25 of 1,193 were found in the response.

**Limits.** One judge, one prompt layout, one topic, 60 scenarios, three assistant models. Not a statement about GLIDER in general. Not evidence that any verdict was wrong. Development numbers were seen before the predictions were written and are not evidence.

## 8. Tests and what each one guarantees

| Test | Guarantees |
|---|---|
| `test_core.py` normalisation and search | Lenient and strict behave as documented; offsets map back to the original, including when case folding changes length |
| `test_core.py` parsing | Highlight lists are read; wrongly closed blocks are handled; malformed blocks are counted, not guessed; an expression in a judge's output is never evaluated |
| `test_core.py` grounding | Segment priority, then own reasoning, then nowhere; the record holds no text; same input gives the same record; reserved and duplicate names are refused |
| `test_core.py` verdicts | Spans are checked exactly; highlights are preferred over quoted phrases; the verdict and the original object are never changed |
| `test_core.py` packaging | Only standard-library imports; no runtime dependencies declared; command line exit codes |
| `test_numbers_lock.py` | The table is re-rendered and compared; the preregistration names the hashes of the files that were scored; every "N of M" in the README's results section is a count in the results (or a stated sum); receipts contain only the allowed keys; with `STUDY_DATA` set, the counts are re-run from the data and compared |

## 9. Design decisions worth keeping

1. **Lenient by default, strict beside it.** Bias every choice in the judge's favour, then report what is still missing. A critic cannot say the count is inflated by quote style.
2. **Count every input as input.** If a phrase is anywhere the judge could have read it, it is grounded.
3. **Separate "own reasoning" from "nowhere".** They mean different things: one is the judge quoting itself, the other is invention.
4. **A control that can fail.** The rotated-row rate is what shows the match rate is not an accident of common words.
5. **Fix the method on one file, predict, then open the rest.** And publish the predictions that fail in the main results, not in a footnote.
6. **Never evaluate model output.** `ast.literal_eval` only.
7. **Receipts without the data.** Hashes, row ids and offsets let anyone with the public data verify every item, without this repository copying unlicensed rows.
8. **Never change the verdict.** The tool adds a record; it does not vote.
9. **By shape, no dependency.** Works on any dict or pydantic model with an `explanation`.

## 10. What to reuse in another project

| Need | Take |
|---|---|
| Verbatim search with offsets that survives case folding | `normalise.py` |
| "Where does each cited phrase come from?" for any model output | `grounding.py` |
| Reading a list out of model output safely | `extract.parse_glider` |
| Span integrity checks | `guardrail.check_spans` |
| Adding a record to someone's result object without mutating it | `guardrail.with_grounding` |
| A study on data you may not redistribute | `study/glider_multilingual.py` (hash the files, publish hashes and offsets) |
| A rendered table and a lock on README numbers | `study/render.py`, `tests/test_numbers_lock.py` |

The method is not specific to guardrails. It applies to any model output that cites its input: evaluator rationales, review comments that quote a diff, summaries that quote a source, agent reports that quote a log.

## 11. What not to repeat

1. **Do not trust a first look at one file.** The first file showed about 41%; the held-out files showed 12% and 17%. Without the held-out step the wrong number would have been published.
2. **Do not predict a rate from one file.** The per-judgment measure was stable across files; the per-phrase rate was not. Prefer the measure that is less sensitive to how many phrases a judge happens to list.
3. **Do not claim invention across scripts or languages.** A highlight in English about Persian text may be a translation. Report where phrases come from, not that they were made up.
4. **Check what the authors already verify before proposing to verify it.** The follow-up study's own code already compares the tools a judge claims to have used with its call log.
5. **Check that the data holds what the check needs.** The follow-up data keeps only a short preview of each tool result, so a quote cannot be checked against its source.
6. **Check the licence before planning to publish rows.** Neither study repository shows one.

## 12. Known gaps

- Only double-quoted phrases and GLIDER highlight lists are recognised as cited evidence. Other judges mark evidence in other ways.
- A paraphrase is counted as not in the input. There is no notion of partial support.
- One study, one judge with highlights. FlowJudge and AnyLLM outputs in the same data were not analysed.
- No packaging on PyPI.
