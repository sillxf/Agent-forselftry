"""Isolated legacy/managed regression and recovery acceptance (local models only)."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evaluation.rag.migration import main

if __name__ == "__main__":
    raise SystemExit(main())
