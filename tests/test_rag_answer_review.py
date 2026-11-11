"""Keep answer generation blind to labels and reports honest about evidence coverage."""
import json

from evaluation.rag.answer_review import answer_messages, render_review, retrieval_reference, summarize


def test_answer_prompt_contains_only_question_and_unabridged_retrieval():
    content = '<script>source text</script>\n' + 'long evidence ' * 1500
    messages = answer_messages('What happened?', [dict(source='source.md', page_start=None, page_end=None, content=content)])
    assert messages[1]['content'].startswith('问题：What happened?')
    assert content in messages[1]['content']
    assert all(label not in json.dumps(messages) for label in ['expected_answer', 'review_status', 'answerable', 'relevant_evidence'])


def test_review_preserves_actual_answer_and_source_without_auto_approval(tmp_path):
    row = dict(question_id='rag_010', question='Question', expected_answer='Reference',
               review_status='pending', answerable=True, http_status=200,
               http_response={'results': [dict(source='source.md', page_start=1, page_end=2,
                                               section_path=['Section'], content='<script>not executable</script>')]},
               coverage_status='missing', required_evidence=['fact'], matched_evidence=[],
               expected_evidence=[], actual_answer='Actual answer', generation_error=None)
    metadata = dict(started_at='2026-11-01', top_k=3, documents=9, summary=summarize([row]))
    render_review([row], metadata, tmp_path)
    page = (tmp_path / 'review.html').read_text(encoding='utf-8')
    report = (tmp_path / 'review.md').read_text(encoding='utf-8')
    assert 'Reference' in page and 'Actual answer' in page
    assert 'pending' not in page and '参考标注：' not in page and '未命中' in page
    assert '<script>' not in page and '&lt;script&gt;' in page
    assert '<script>not executable</script>' in report
    assert metadata['summary']['http_ok'] == 1
    assert metadata['summary']['missing'] == 1
    assert metadata['summary']['generated_answers'] == 1


def test_reference_separates_macro_micro_coverage_and_answer_accuracy():
    def row(identifier, required, hits, answerable=True):
        return dict(question_id=identifier, question=identifier, expected_answer="reference", answerable=answerable,
                    expected_evidence=[], required_evidence=required, matched_evidence=hits)
    rows = [row("a", ["a1", "a2", "a3"], ["a1"]), row("b", ["b1"], ["b1"]), row("c", [], [], False)]
    metadata = dict(strategy="hybrid", top_k=3, results_sha256="raw-results", model={}, index={"signature": {}})
    reference = retrieval_reference(rows, metadata)
    assert reference["answerable_questions"] == 2 and reference["unanswerable_questions"] == 1
    assert abs(reference["macro_evidence_recall"] - 2/3) < 1e-12
    assert reference["micro_evidence_recall"] == .5
    assert reference["complete_evidence_question_rate"] == .5
    assert reference["answer_accuracy"] is None and reference["refusal_rate"] is None
    for item in rows:
        item["review_status"] = "pending"
        item["reviewer"] = None
    assert retrieval_reference(rows, metadata)["evaluation_definition_sha256"] == reference["evaluation_definition_sha256"]
