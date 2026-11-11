"""Knowledge-grounded design demo tests."""

import json
import unittest

from agent.demo import DemoBudget, DesignAdvisor


class Knowledge:
    def __init__(self, results):
        self.results = results
        self.calls = []

    def search(self, query, *, queries=(), top_k=5, min_score=None, include_trace=False):
        self.calls.append((query, list(queries), top_k, min_score, include_trace))
        return {"results": self.results, "metadata": {"elapsed_ms": 12.3, "warnings": []}}


class LLM:
    def __init__(self, content):
        self.content = content
        self.calls = []

    def chat(self, messages):
        self.calls.append(messages)
        return {"content": self.content, "usage": {"prompt_tokens": 10, "completion_tokens": 20}}


def result(chunk_id="c1", relevance=0.8):
    return {
        "chunk_id": chunk_id,
        "source_name": "agent.md",
        "section_path": ["Workflow"],
        "page_start": 1,
        "page_end": 2,
        "content": "Use explicit state, bounded tools, checkpoints and recovery.",
        "relevance": relevance,
        "relevance_source": "similarity",
    }


def design(source="ev:c1"):
    return json.dumps({
        "summary": "Use a bounded workflow with code-owned controls.",
        "components": [{"name": "orchestrator", "responsibility": "Own stages and budgets.", "owner": "code", "sources": [source]}],
        "workflow": [{"name": "plan", "input": "goal", "output": "bounded steps", "failure_handling": "stop and report", "owner": "model", "sources": [source]}],
        "failure_modes": [{"failure": "tool timeout", "detection": "timeout status", "recovery": "retry once then ask operator", "sources": [source]}],
        "implementation_order": ["schema", "read-only tools", "verification"],
        "open_questions": ["Which tools are allowed?"],
        "claims": [{"type": "reference_knowledge", "text": "A checkpoint supports recovery.", "sources": [source]}],
    })


class DemoTests(unittest.TestCase):
    def test_retrieval_gate_and_source_verification(self):
        llm = LLM(design("ev:unknown"))
        knowledge = Knowledge([result("c1", 0.8), result("c2", 0.2)])
        output = DesignAdvisor(llm, knowledge, DemoBudget(min_relevance=0.45)).design("Build a reliable agent")
        self.assertEqual(output["status"], "completed")
        self.assertEqual(output["retrieval"]["accepted"], 1)
        self.assertEqual(output["retrieval"]["dropped"][0]["reason"], "below_min_relevance")
        self.assertEqual(output["design"]["claims"][0]["type"], "unverified_hypothesis")
        self.assertEqual(output["design"]["verification"]["unknown_sources"], ["ev:unknown"])
        self.assertEqual(knowledge.calls[0][3:], (0.45, True))

    def test_skips_model_when_rag_has_no_relevant_evidence(self):
        llm = LLM(design())
        output = DesignAdvisor(llm, Knowledge([result("c1", 0.1)])).design("Build a reliable agent")
        self.assertEqual(output["status"], "failed")
        self.assertIsNone(output["design"])
        self.assertEqual(llm.calls, [])
        self.assertEqual(output["retrieval"]["accepted"], 0)

    def test_search_forwards_relevance_gate_and_trace(self):
        import httpx

        from agent.knowledge import RAGKnowledge

        seen = {}

        def handler(request):
            seen["json"] = json.loads(request.content)
            return httpx.Response(200, json={"results": [], "metadata": {}})

        knowledge = RAGKnowledge(
            "http://rag.test", "token", ["kb"], transport=httpx.MockTransport(handler)
        )
        knowledge.search("q", queries=["rewrite"], top_k=3, min_score=0.45, include_trace=True)
        knowledge.close()
        self.assertEqual(
            seen["json"],
            {
                "query": "q",
                "queries": ["rewrite"],
                "knowledge_base_ids": ["kb"],
                "top_k": 3,
                "include_trace": True,
                "min_score": 0.45,
            },
        )

    def test_model_timeout_preserves_retrieval_diagnostics(self):
        from app.models.llm.error import LLMRequestError

        class BrokenLLM(LLM):
            def chat(self, messages):
                raise LLMRequestError("provider timeout")

        output = DesignAdvisor(BrokenLLM(design()), Knowledge([result()])).design(
            "Build a reliable agent"
        )
        self.assertEqual(output["status"], "failed")
        self.assertEqual(output["retrieval"]["accepted"], 1)
        self.assertEqual(output["retrieval"]["status"], "model_error")
        self.assertIn("LLMRequestError", output["failure"])
        self.assertIn("provider timeout", output["failure_detail"])


if __name__ == "__main__":
    unittest.main()
