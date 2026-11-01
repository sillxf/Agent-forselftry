# Run history and preservation

- Historical committed v0.1 and v0.2 baselines are unchanged.
- Local intermediate `evaluation_results/phase2_before_multicolumn/` is retained,
  not deleted or overwritten. It predates the added two-column regression/repair;
  the final corpus's rankings and scores stayed identical. It is ignored, not a
  deliverable baseline and not a source of cherry-picked scores.
- This v2 Phase 2 directory is the deliverable candidate, with pipeline version 5.
- As-run annotations are immutable in annotation_snapshot/. Later review-prose
  clarification is separately preserved in review_packet/ with before/after hashes;
  labels, approvals and metrics did not change.
- A fresh source/index replay used .pytest_cache/phase2-final-rebuild-run with all
  90 ranking/metric/qrel comparisons equal; frozen replay configs are included.
