# GLIDER highlights: where the cited phrases are

Rendered from `results/glider_multilingual_*.json` by `study/render.py`. Do not edit by hand.

Data: `royapakzad/multilingual_llm_guardrails` at commit `3a6c7df`. One column per results file,
named by the assistant model whose responses were judged. `dev` is the file the method was fixed on;
`heldout` files were opened only after the preregistration (`prereg/glider_multilingual_prereg.md`).

## English response, English policy (primary cell)

| | gpt (dev) | gemini (heldout) | mistral (heldout) |
|---|---|---|---|
| Highlights | 329 | 310 | 300 |
| Not in input | 136 of 329 (41.3%) | 52 of 310 (16.8%) | 35 of 300 (11.7%) |
| Not in input (strict) | 147 of 329 (44.7%) | 64 of 310 (20.6%) | 56 of 300 (18.7%) |
| Judgments with at least one | 17 of 29 (58.6%) | 16 of 28 (57.1%) | 19 of 28 (67.9%) |
| In the response | 140 of 329 (42.6%) | 188 of 310 (60.6%) | 185 of 300 (61.7%) |
| In user message or system prompt | 5 of 329 (1.5%) | 0 of 310 (0.0%) | 5 of 300 (1.7%) |
| In the policy | 43 of 329 (13.1%) | 62 of 310 (20.0%) | 70 of 300 (23.3%) |
| In instructions or rubric | 5 of 329 (1.5%) | 8 of 310 (2.6%) | 5 of 300 (1.7%) |
| Only in the judge's own reasoning | 130 of 329 (39.5%) | 49 of 310 (15.8%) | 26 of 300 (8.7%) |
| Nowhere | 6 of 329 (1.8%) | 3 of 310 (1.0%) | 9 of 300 (3.0%) |
| Control: in a different row's response | 20 of 329 (6.1%) | 52 of 310 (16.8%) | 44 of 300 (14.7%) |
| Written in Latin script | 329 of 329 (100.0%) | 310 of 310 (100.0%) | 300 of 300 (100.0%) |
| Unparsed highlight blocks | 3 | 1 | 2 |

## English response, Farsi policy (descriptive)

| | gpt (dev) | gemini (heldout) | mistral (heldout) |
|---|---|---|---|
| Highlights | 279 | 307 | 352 |
| Not in input | 32 of 279 (11.5%) | 63 of 307 (20.5%) | 104 of 352 (29.5%) |
| Not in input (strict) | 86 of 279 (30.8%) | 77 of 307 (25.1%) | 127 of 352 (36.1%) |
| Judgments with at least one | 11 of 30 (36.7%) | 16 of 28 (57.1%) | 15 of 30 (50.0%) |
| In the response | 231 of 279 (82.8%) | 218 of 307 (71.0%) | 235 of 352 (66.8%) |
| In user message or system prompt | 9 of 279 (3.2%) | 2 of 307 (0.7%) | 4 of 352 (1.1%) |
| In the policy | 0 of 279 (0.0%) | 0 of 307 (0.0%) | 0 of 352 (0.0%) |
| In instructions or rubric | 7 of 279 (2.5%) | 24 of 307 (7.8%) | 9 of 352 (2.6%) |
| Only in the judge's own reasoning | 23 of 279 (8.2%) | 51 of 307 (16.6%) | 88 of 352 (25.0%) |
| Nowhere | 9 of 279 (3.2%) | 12 of 307 (3.9%) | 16 of 352 (4.5%) |
| Control: in a different row's response | 11 of 279 (3.9%) | 33 of 307 (10.7%) | 40 of 352 (11.4%) |
| Written in Latin script | 279 of 279 (100.0%) | 307 of 307 (100.0%) | 352 of 352 (100.0%) |
| Unparsed highlight blocks | 8 | 2 | 0 |

## Farsi response, English policy (descriptive)

| | gpt (dev) | gemini (heldout) | mistral (heldout) |
|---|---|---|---|
| Highlights | 283 | 372 | 821 |
| Not in input | 90 of 283 (31.8%) | 115 of 372 (30.9%) | 308 of 821 (37.5%) |
| Not in input (strict) | 97 of 283 (34.3%) | 117 of 372 (31.5%) | 313 of 821 (38.1%) |
| Judgments with at least one | 25 of 30 (83.3%) | 25 of 29 (86.2%) | 28 of 30 (93.3%) |
| In the response | 3 of 283 (1.1%) | 23 of 372 (6.2%) | 2 of 821 (0.2%) |
| In user message or system prompt | 0 of 283 (0.0%) | 0 of 372 (0.0%) | 0 of 821 (0.0%) |
| In the policy | 182 of 283 (64.3%) | 232 of 372 (62.4%) | 467 of 821 (56.9%) |
| In instructions or rubric | 8 of 283 (2.8%) | 2 of 372 (0.5%) | 44 of 821 (5.4%) |
| Only in the judge's own reasoning | 80 of 283 (28.3%) | 93 of 372 (25.0%) | 230 of 821 (28.0%) |
| Nowhere | 10 of 283 (3.5%) | 22 of 372 (5.9%) | 78 of 821 (9.5%) |
| Control: in a different row's response | 0 of 283 (0.0%) | 6 of 372 (1.6%) | 0 of 821 (0.0%) |
| Written in Latin script | 283 of 283 (100.0%) | 369 of 372 (99.2%) | 815 of 821 (99.3%) |
| Unparsed highlight blocks | 0 | 1 | 4 |

## Farsi response, Farsi policy (descriptive)

| | gpt (dev) | gemini (heldout) | mistral (heldout) |
|---|---|---|---|
| Highlights | 252 | 663 | 414 |
| Not in input | 186 of 252 (73.8%) | 419 of 663 (63.2%) | 281 of 414 (67.9%) |
| Not in input (strict) | 187 of 252 (74.2%) | 504 of 663 (76.0%) | 298 of 414 (72.0%) |
| Judgments with at least one | 29 of 29 (100.0%) | 29 of 29 (100.0%) | 29 of 30 (96.7%) |
| In the response | 11 of 252 (4.4%) | 71 of 663 (10.7%) | 77 of 414 (18.6%) |
| In user message or system prompt | 0 of 252 (0.0%) | 0 of 663 (0.0%) | 0 of 414 (0.0%) |
| In the policy | 6 of 252 (2.4%) | 1 of 663 (0.2%) | 1 of 414 (0.2%) |
| In instructions or rubric | 49 of 252 (19.4%) | 172 of 663 (25.9%) | 55 of 414 (13.3%) |
| Only in the judge's own reasoning | 158 of 252 (62.7%) | 336 of 663 (50.7%) | 244 of 414 (58.9%) |
| Nowhere | 28 of 252 (11.1%) | 83 of 663 (12.5%) | 37 of 414 (8.9%) |
| Control: in a different row's response | 1 of 252 (0.4%) | 4 of 663 (0.6%) | 3 of 414 (0.7%) |
| Written in Latin script | 242 of 252 (96.0%) | 657 of 663 (99.1%) | 412 of 414 (99.5%) |
| Unparsed highlight blocks | 1 | 0 | 0 |
