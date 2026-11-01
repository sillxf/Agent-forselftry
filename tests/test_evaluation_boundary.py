"""Two architectural checks: one-way imports and complete replay source snapshots."""
import ast
from pathlib import Path
from zipfile import ZipFile

from evaluation.rag.provenance import code_state

ROOT = Path(__file__).resolve().parents[1]


def test_production_and_evaluation_have_one_way_dependencies():
    violations = []
    for directory, forbidden in [('app', {'evaluation', 'scripts', 'tests'}),
                                 ('evaluation', {'scripts', 'tests'})]:
        for path in (ROOT / directory).rglob('*.py'):
            for node in ast.walk(ast.parse(path.read_text(encoding='utf-8-sig'))):
                modules = ([node.module] if isinstance(node, ast.ImportFrom) and node.module and not node.level
                           else [alias.name for alias in node.names] if isinstance(node, ast.Import) else [])
                for module in modules:
                    if module.split('.')[0] in forbidden:
                        violations.append(f'{path.relative_to(ROOT)}:{node.lineno} imports {module}')
    assert violations == []
    assert not (ROOT / 'app/rag/evaluation').exists()


def test_run_snapshot_contains_production_and_evaluation_sources(tmp_path):
    state = code_state(tmp_path)
    assert state['source_sha256'] and state['snapshot_sha256']
    with ZipFile(tmp_path / 'source_snapshot.zip') as archive:
        for relative in ['app/rag/retriever.py', 'evaluation/rag/dataset.py',
                         'evaluation/rag/runner.py', 'evaluation/rag/metrics.py',
                         'evaluation/rag/answer_review.py', 'evaluation/rag/provenance.py',
                         'scripts/run_rag_benchmark.py']:
            assert archive.read(relative) == (ROOT / relative).read_bytes()
        assert '.env' not in archive.namelist()
