"""Security alert investigation agent built on the independent RAG service.

Deterministic steps (validation, risk score, deduplication, budgets, report
verification) are code; the model only chooses read-only tool calls and writes the
report. See docs/agent_design.md.
"""

__version__ = "0.1.0"
