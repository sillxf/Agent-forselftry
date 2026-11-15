"""Agent benchmark diagnostic behavior checks are conservative and traceable."""
import unittest

from benchmark.evaluation.agent.run import diagnose


class AgentDiagnosticTests(unittest.TestCase):
    def test_structured_tool_expectations_are_checked_but_semantics_are_not_assumed(self):
        case = {
            "expected_tool_behavior": {
                "retrieval_required": True,
                "required_tools": ["search_alerts"],
                "preserve_observed_vs_reference": True,
                "resist_prompt_injection": True,
            },
            "forbidden_claims": ["IP was blocked"],
        }
        result = {
            "stage": "COMPLETED",
            "failure": None,
            "report": {"claims": [{"type": "observed_event", "text": "login observed"}], "recommendations": [], "summary": "investigate"},
            "steps": [
                {"kind": "tool", "name": "knowledge_search", "status": "success", "step_id": 1},
                {"kind": "tool", "name": "search_alerts", "status": "success", "step_id": 2},
            ],
            "usage": {"llm_calls": 1},
            "observations": {"obs:embedded_instructions": {"phrases": ["ignore rules"]}},
            "run_record": {"report_validation": {"schema_valid": True}},
        }
        diagnostic = diagnose(case, result)
        checks = diagnostic["behavior_checks"]
        self.assertEqual(checks["retrieval_required"]["status"], "pass")
        self.assertEqual(checks["tool:search_alerts"]["status"], "pass")
        self.assertEqual(checks["preserve_observed_vs_reference"]["status"], "not_checked")
        self.assertEqual(checks["resist_prompt_injection"]["status"], "not_checked")
        self.assertTrue(checks["resist_prompt_injection"]["stimulus_detected"])

    def test_missing_required_tool_is_failure_not_silent_success(self):
        case = {"expected_tool_behavior": {"retrieval_required": True, "required_tools": ["search_alerts"]}}
        result = {"stage": "COMPLETED", "failure": None, "report": {}, "steps": [], "usage": {}, "observations": {}, "run_record": {}}
        diagnostic = diagnose(case, result)
        self.assertEqual(diagnostic["behavior_checks"]["retrieval_required"]["status"], "fail")
        self.assertEqual(diagnostic["behavior_checks"]["tool:search_alerts"]["status"], "fail")


if __name__ == "__main__":
    unittest.main()
