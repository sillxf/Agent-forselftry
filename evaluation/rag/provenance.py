"""Source/model fingerprints shared by evaluation entry points."""
import hashlib
import json
import subprocess
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

from evaluation.rag.dataset import checksum

ROOT = Path(__file__).resolve().parents[2]


def code_state(output):
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, encoding="utf-8").strip()
    digest = hashlib.sha256()
    paths = [*ROOT.glob("app/**/*.py"), *ROOT.glob("evaluation/**/*.py"),
             *ROOT.glob("scripts/*.py"), ROOT / "requirements.txt"]
    with ZipFile(output / "source_snapshot.zip", "w", compression=ZIP_DEFLATED) as archive:
        for path in sorted(paths):
            relative = path.relative_to(ROOT).as_posix()
            data = path.read_bytes()
            digest.update(relative.encode())
            digest.update(b"\0" + data + b"\0")
            info = ZipInfo(relative, date_time=(2026, 11, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, data)
    return dict(commit=git("rev-parse", "HEAD"), dirty=bool(git("status", "--porcelain")),
                source_sha256=digest.hexdigest(), snapshot_sha256=checksum(output / "source_snapshot.zip"))


def model_state(name):
    from app.rag.embedder import get_model
    from huggingface_hub import try_to_load_from_cache

    model = get_model(name)
    digest = hashlib.sha256(str(model).encode())
    for key, tensor in sorted(model.state_dict().items()):
        digest.update(key.encode())
        digest.update(memoryview(tensor.detach().cpu().contiguous().numpy()).cast("B"))
    tokenizer = model.tokenizer
    tokenizer_definition = json.loads(tokenizer.backend_tokenizer.to_str())
    # encode() changes these transient execution settings; they are not the tokenizer definition.
    tokenizer_definition.pop("padding", None)
    tokenizer_definition.pop("truncation", None)
    repository = name if "/" in name else "sentence-transformers/" + name
    cached_config = try_to_load_from_cache(repository, "config.json") if not Path(name).exists() else None
    revision = Path(cached_config).parent.name if isinstance(cached_config, str) else None
    return dict(name=name, resolved_revision=revision,
                weights_sha256=digest.hexdigest(),
                tokenizer_sha256=hashlib.sha256(json.dumps(tokenizer_definition, sort_keys=True,
                    ensure_ascii=False, separators=(",", ":")).encode()).hexdigest(),
                max_sequence_length=model.max_seq_length, device=str(model.device))
