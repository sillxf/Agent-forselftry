"""Heading rejection rules that run without Docling models."""

import unittest

from app.ingestion.processing.structure_recovery import sentence_like_heading


class SentenceLikeHeadingTests(unittest.TestCase):
    def test_clause_split_by_a_page_break_is_body_text(self):
        # Docling labelled this page-1 tail as a section header; the sentence
        # continues on page 2 (Security V1 rag_019).
        self.assertTrue(sentence_like_heading("The authentication rule checks events,"))
        self.assertTrue(sentence_like_heading("检测规则先检查登录事件，"))
        self.assertTrue(sentence_like_heading("Collect logs from the host;"))

    def test_real_headings_are_kept(self):
        for heading in (
            "Authentication investigation",
            "T1059.001: PowerShell",
            "3.2 Detection and Analysis",
            "Tools, Techniques",  # Two words: too short to be a split sentence.
            "事件响应流程",
        ):
            self.assertFalse(sentence_like_heading(heading), heading)

    def test_definition_lead_in_is_still_body_text(self):
        self.assertTrue(sentence_like_heading("The incident response plan is:"))


if __name__ == "__main__":
    unittest.main()
