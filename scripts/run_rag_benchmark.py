"""CLI entry point; implementation lives in evaluation.rag.benchmark."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evaluation.rag.benchmark import main


if __name__ == "__main__":
    main()
