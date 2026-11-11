"""Recreate the small frozen corpus; never regenerate question labels automatically."""
import argparse
import hashlib
import json
import re
import shutil
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "tests/rag_benchmark"
ATTACK_COMMIT = "d4a34a19eb60dcd0a9d15a456da842a42e1003fc"
WSTG_COMMIT = "dd33419e10edb22b78d89325a6c2aad9f184e3a2"
SOURCES = {
    "attack-v17.1.json": (
        f"https://raw.githubusercontent.com/mitre-attack/attack-stix-data/{ATTACK_COMMIT}/enterprise-attack/enterprise-attack.json",
        "0d1c347a4d584cf7e11ef46556c33b7689341443bf86299188d46c307274323b"),
    "mitre-license": (
        f"https://raw.githubusercontent.com/mitre-attack/attack-stix-data/{ATTACK_COMMIT}/LICENSE.txt",
        "d67e295e4a569b59ca0f728cadf99103b07680c5a9ecff302e1ee3c4ad289e06"),
    "owasp-license": (
        f"https://raw.githubusercontent.com/OWASP/wstg/{WSTG_COMMIT}/LICENSE",
        "9312b09a6848f26c6046652238ddd6b32ea2124847faed48854c375c5194238d"),
    "wstg-sqli-v4.2.md": (
        f"https://raw.githubusercontent.com/OWASP/wstg/{WSTG_COMMIT}/document/4-Web_Application_Security_Testing/07-Input_Validation_Testing/05-Testing_for_SQL_Injection.md",
        "501ea437fcce7197ff5f993fc12d16817ba3d32da7494f1df559f562fb2d7ad3"),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--proxy")
    args = parser.parse_args()
    cache = ROOT / ".pytest_cache/benchmark-sources"
    cache.mkdir(parents=True, exist_ok=True)
    docs = BENCHMARK / "documents"
    docs.mkdir(parents=True, exist_ok=True)
    if args.download:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({"https": args.proxy})) if args.proxy else urllib.request.build_opener()
        for name, (url, _) in SOURCES.items():
            with opener.open(url, timeout=120) as response:
                (cache / name).write_bytes(response.read())
    for name, (_, expected) in SOURCES.items():
        if sha(cache / name) != expected:
            raise ValueError(f"Upstream input checksum mismatch: {name}")
    licenses = BENCHMARK / "licenses"
    licenses.mkdir(exist_ok=True)
    for source, target in (("mitre-license", "MITRE_LICENSE.txt"), ("owasp-license", "OWASP_CC_BY_SA_4_0.txt")):
        text = (cache / source).read_text(encoding="utf-8")
        (licenses / target).write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8")
    entries = []

    def record(file, origin):
        entries.append(dict(file=file, sha256=sha(docs / file), origin=origin))

    for name in ("brute_force.md", "malware.md", "sql_injection.md"):
        source = ROOT / "app/knowledge" / name
        shutil.copyfile(source, docs / name)
        record(name, dict(kind="project_knowledge", path=f"app/knowledge/{name}", source_sha256=sha(source)))
    fixtures = ROOT / "tests/fixtures/rag_documents"
    original_manifest = json.loads((fixtures / "manifest.json").read_text(encoding="utf-8"))
    for file in ("pdf/text_based/nist_sp80061r3_pp10-12.pdf", "pdf/tables/continued_rules.pdf",
                 "pdf/cross_page/sentence_continuation.pdf", "docx/numbered_steps.docx"):
        name = Path(file).name
        shutil.copyfile(fixtures / file, docs / name)
        source = next(e for e in original_manifest["documents"] if e["file"] == file)
        record(name, dict(kind="existing_regression_input", path=f"tests/fixtures/rag_documents/{file}",
                          source_sha256=source["sha256"], attribution=source["origin"]))
    objects = json.loads((cache / "attack-v17.1.json").read_text(encoding="utf-8"))["objects"]
    parts = ["# MITRE ATT&CK Enterprise v17.1 — selected technique descriptions"]
    object_versions = []
    for identifier in ("T1059.001", "T1110", "T1078"):
        item = next(o for o in objects if o["type"] == "attack-pattern" and
                    any(e.get("external_id") == identifier for e in o.get("external_references", [])))
        parts += [f"## {identifier}: {item['name']}", item["description"]]
        object_versions.append(dict(id=item["id"], external_id=identifier, modified=item["modified"]))
    (docs / "mitre_attack_v17_1.md").write_text("\n\n".join(parts) + "\n", encoding="utf-8")
    record("mitre_attack_v17_1.md", dict(kind="official_description_extract", url=SOURCES["attack-v17.1.json"][0],
           source_sha256=SOURCES["attack-v17.1.json"][1], commit=ATTACK_COMMIT, version="Enterprise ATT&CK v17.1",
           objects=object_versions, license="MITRE ATT&CK terms of use; see SOURCES.md"))
    text = (cache / "wstg-sqli-v4.2.md").read_text(encoding="utf-8")
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    (docs / "owasp_wstg_v4_2_sql_injection.md").write_text(text, encoding="utf-8")
    record("owasp_wstg_v4_2_sql_injection.md", dict(kind="official_text_extract", url=SOURCES["wstg-sqli-v4.2.md"][0],
           source_sha256=SOURCES["wstg-sqli-v4.2.md"][1], commit=WSTG_COMMIT, version="WSTG v4.2",
           modifications="Removed Markdown image links to keep ingestion offline; text unchanged.",
           license="CC BY-SA 4.0; see SOURCES.md"))
    (BENCHMARK / "manifest.json").write_text(json.dumps(dict(version="corpus-v1", documents=entries),
                    ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(entries)} frozen documents; question annotations were not changed.")


if __name__ == "__main__":
    main()
