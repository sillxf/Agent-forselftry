"""The answer evaluation links retrieval, optional generation and grading offline."""

from pathlib import Path
import json
import tempfile
import unittest

from benchmark.evaluation import answer_eval
from RAG.tests.support import FakeEmbedding, Parser

ROOT = Path(__file__).resolve().parents[2]
SAMPLES = ROOT / "benchmark/evaluation/answer"
DOCUMENTS = ROOT / "benchmark/datasets/security-v1/documents"


class AnswerEvalTests(unittest.TestCase):
    def setUp(self):
        self.questions = answer_eval.validate(
            answer_eval.load_jsonl(SAMPLES / "sample_questions.jsonl")
        )

    def test_grading_catches_confusion_distractor_and_unwarranted_answer(self):
        answers = answer_eval.load_jsonl(SAMPLES / "sample_answers.jsonl")
        grades = {g["id"]: g for g in answer_eval.grade(self.questions, answers)}
        self.assertEqual(grades["sample_001"]["status"], "correct")
        self.assertEqual(grades["sample_002"]["status"], "incorrect")  # Run vs RunOnce.
        self.assertEqual(grades["sample_004"]["forbidden"], ["封禁可疑 IP"])
        self.assertEqual(grades["sample_005"]["status"], "correct")  # Refused.
        self.assertEqual(grades["sample_006"]["status"], "incorrect")  # Answered anyway.
        summary = answer_eval.summarize(self.questions, list(grades.values()))
        self.assertTrue(summary["unreviewed_warning"])
        self.assertEqual(summary["answerable_correct"], 0.5)

    def test_retrieve_generate_grade_against_the_service(self):
        from app.bootstrap import create_services
        from app.core.contracts import JobRequest
        from app.indexing.worker import Worker

        temporary = tempfile.TemporaryDirectory(prefix="rag-answer-eval-")
        self.addCleanup(temporary.cleanup)
        service = create_services(
            Path(temporary.name) / "data",
            admin_token="answer-eval-test-token-0123456789",
            embedding_factory=FakeEmbedding,
            parser_factory=lambda workspace, configuration: Parser(),
        )
        admin = service.access.authenticate("answer-eval-test-token-0123456789")
        kb = service.knowledge.repository.create_kb(
            {"name": "eval", "build": {"ocr_enabled": False}}
        )["id"]
        upload = service.documents.upload_directory(admin, kb)
        for name in ("attack_t1110_003.md", "attack_t1547_001.md", "malware.md"):
            temp = Path(upload) / (name + ".upload")
            temp.write_bytes((DOCUMENTS / name).read_bytes())
            service.documents.upload(admin, kb, name, temp)
        service.indexing.submit(admin, kb, JobRequest())
        self.assertTrue(Worker(service.indexing).run_once())

        def search(question):
            return service.retrieval.search(
                admin, dict(query=question["question"], knowledge_base_ids=[kb], top_k=3)
            )

        retrieved = answer_eval.retrieve(self.questions, search)
        by_id = {r["id"]: r for r in retrieved}
        self.assertTrue(by_id["sample_002"]["context_has_all_points"])
        self.assertTrue(by_id["sample_002"]["source_hit"])

        prompts = []

        def chat(prompt):
            prompts.append(prompt)
            return "知识库中没有找到", {"total_tokens": 1}

        with self.assertRaises(ValueError):  # Budget is checked before any call.
            answer_eval.generate(self.questions, retrieved, chat, max_requests=2)
        self.assertEqual(prompts, [])
        answers = answer_eval.generate(self.questions, retrieved, chat, max_requests=10)
        self.assertIn("[1] (", prompts[1])
        grades = answer_eval.grade(self.questions, answers, retrieved)
        summary = answer_eval.summarize(self.questions, grades, retrieved)
        self.assertEqual(summary["unanswerable_refused"], 1.0)
        self.assertEqual(summary["answerable_refused"], 1.0)
        self.assertIsNotNone(summary["context_has_all_points"])
        json.dumps(summary)  # Serializable report.


if __name__ == "__main__":
    unittest.main()
