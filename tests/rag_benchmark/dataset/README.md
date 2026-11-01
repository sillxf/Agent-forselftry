# Dataset v0.1 — candidate labels, not human-certified ground truth

`questions.jsonl` contains 30 **AI-prepared candidate** questions: five each for
`exact_identifier`, `semantic`, `response`, `tables_steps`, `context` and
`unanswerable`. Twenty-five are answerable; five explicitly request unavailable
private/fictional information. Queries include English and Chinese. English corpus
text and the default English-oriented embedding make language mismatch a meaningful
failure case; no model change is hidden in this benchmark.

All 30 entries are currently `review_status: "pending"`, `reviewer: null`. Automatic
source/quote validation is complete, but it is **not human relevance review**.
Use `--require-reviewed` for acceptance runs; it refuses pending annotations. The
candidate baseline is useful for exercising the tooling and finding errors, not for
claiming general retrieval quality or a production acceptance score.

## Schema

`dataset.json` fixes schema version 1, the dataset version and the documents directory.
Every JSONL record carries:

- `id`, `question`, `category`, `difficulty`, `answerable`, `expected_answer`;
- `rationale`: why the evidence supports the answer, or why knowledge is absent;
- `review_status`, `reviewer`;
- `relevant_evidence`: zero or more source annotations with `evidence_id`, content-hash
  `document_id`, `source` filename, `source_block_ids`, `section_path`, nullable
  `page_number`/`page_end`, a verbatim `text_quote`, and `relevance_grade` (0–3).

Questions must be unique. Answerable questions need positive evidence; unanswerable
ones must have an empty evidence list. Grade 0 is nonrelevant, 1 partial, 2 useful and
3 directly supporting. Grades 1–3 are positive for binary metrics. Current labels
use grade 3; the metric tests also cover mixed graded relevance.

An `evidence_id` is an annotation identity stable across **chunk configuration**
changes; it is not a Child ID. Parser or document changes can still change original
Block IDs: validate/review/version them rather than assuming permanence.
Page numbers are null for Markdown/DOCX when Docling has no rendered page provenance.
No page numbers are invented. Merged PDF evidence retains its source IDs and range.

## Human-review checklist

1. Read the fixed source document, not the top-ranked retrieval answer alone.
2. Confirm the question is realistic, unambiguous and answerable from this corpus.
3. Confirm every quote, original Block ID, section and page range. Find any alternate
   valid source evidence; missing labels can make correct retrieval look wrong.
4. Confirm the reference answer and relevance grades. Mark multiple required facts
   separately for cross-section/context questions.
5. For unanswerable questions, review the entire frozen corpus for possible answers.
6. Keep evidence quotes short but sufficient. Matching requires a quote to be present
   in a returned slice: an excessively long quote crossing a Child boundary can
   undercount a useful partial hit. The first version measures complete evidence
   anchors, not semantic equivalence or arbitrary partial-sentence overlap.
7. Set `review_status` to `approved` and record the real human reviewer; update the
   dataset version. Never automatically approve candidates from an AI rerun.
8. Run with `--require-reviewed`. Keep a later holdout set before tuning algorithms
   repeatedly on these same 30 development questions.

The default runner sends **only `question`** into retrieval. Neither the reference
answer nor evidence text/IDs is embedded into the query or added to the knowledge
index. Candidate-question generation is not run as part of evaluation.
