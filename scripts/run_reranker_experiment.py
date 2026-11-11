"""CLI entry point for the fixed-candidate BGE Reranker experiment."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evaluation.rag.reranker_experiment import main


if __name__ == "__main__":
    main()
