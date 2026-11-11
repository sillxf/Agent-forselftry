"""CLI entry point for frozen-chunk Security RAG comparisons."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from evaluation.rag.model_comparison import main

if __name__=='__main__':
    main()
