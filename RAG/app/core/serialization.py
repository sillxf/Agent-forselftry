def public(value):
    """Never disclose local filesystem topology through evidence or management APIs."""
    hidden = {
        "source_path",
        "source_blob_path",
        "image_path",
        "image_paths",
        "path",
        "path_key",
        "source_key",
    }
    if isinstance(value, dict):
        return {
            k: (v if k in {"table_data", "metadata"} else public(v))
            for k, v in value.items()
            if k not in hidden
        }
    if isinstance(value, list):
        return [public(v) for v in value]
    return value
