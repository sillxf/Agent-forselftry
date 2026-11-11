"""Use cached model assets without requiring an entire model repository download."""

from pathlib import Path
from huggingface_hub import try_to_load_from_cache


def model_source(model, revision="default", *, require_weights=True):
    revision = None if revision == "default" else revision
    if Path(model).expanduser().is_dir():
        return str(Path(model).expanduser().resolve()), None
    # snapshot_download(local_files_only=True) requires unrelated repository assets too;
    # resolve the cached model config directly instead.
    for filename in ("config.json", "modules.json", "tokenizer_config.json"):
        cached = try_to_load_from_cache(model, filename, revision=revision)
        if not isinstance(cached, str):
            continue
        snapshot = Path(cached).parent
        if require_weights and not (
            any(snapshot.rglob("*.safetensors"))
            or any(snapshot.rglob("pytorch_model*.bin"))
        ):
            continue
        return str(snapshot), None
    return model, revision
