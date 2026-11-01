"""CLI entry point; implementation lives in evaluation.rag.answer_review."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evaluation.rag.answer_review import main


if __name__ == "__main__":
    main()
