"""CLI wrapper; evaluation implementation stays outside production app/."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evaluation.rag.multiview_experiment import main

if __name__ == "__main__":
    main()
