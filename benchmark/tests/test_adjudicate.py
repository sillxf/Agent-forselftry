"""Import-time checks for the opt-in adjudicator; no network/model usage."""
import unittest


class AdjudicatorImportTests(unittest.TestCase):
    def test_prompt_variants_import_without_provider_configuration(self):
        from benchmark.evaluation import adjudicate

        self.assertIn("independent benchmark-label auditor", adjudicate.BASE_PROMPT)
        self.assertIn("third independent benchmark-label adjudicator", adjudicate.THIRD_PROMPT)
        self.assertEqual(adjudicate._env_config("NONEXISTENT_BENCHMARK_JUDGE_PREFIX"), None)


if __name__ == "__main__":
    unittest.main()
