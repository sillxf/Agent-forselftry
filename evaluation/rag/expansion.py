"""Prepare a separate, pinned Security V1 corpus and resolve source-backed designs."""
import argparse
import copy
import hashlib
import json
import re
import shutil
import urllib.request
from collections import Counter
from pathlib import Path

from evaluation.rag.dataset import Dataset, checksum, normalize

ROOT = Path(__file__).resolve().parents[2]
LEGACY = ROOT / "tests/rag_benchmark"
V1 = LEGACY / "v1"
ATTACK_COMMIT = "d4a34a19eb60dcd0a9d15a456da842a42e1003fc"
ATTACK_SHA = "0d1c347a4d584cf7e11ef46556c33b7689341443bf86299188d46c307274323b"
TECHNIQUES = {"T1059.003": 2, "T1059.005": 2, "T1059.007": 2, "T1021.006": 2,
              "T1569.002": 2, "T1110.003": 1, "T1110.004": 2, "T1550.002": 2,
              "T1003.001": 2, "T1547.001": 3, "T1218.005": 2, "T1027.010": 2}


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")


def prepare_corpus():
    cache = ROOT / ".pytest_cache/benchmark-sources/attack-v17.1.json"
    if checksum(cache) != ATTACK_SHA:
        raise ValueError("Pinned ATT&CK source hash differs; use --download-source to obtain only the pinned upstream source")
    objects = json.loads(cache.read_text(encoding="utf-8"))["objects"]
    docs = V1 / "documents"
    docs.mkdir(parents=True, exist_ok=True)
    entries = copy.deepcopy(json.loads((LEGACY/"manifest.json").read_text(encoding="utf-8"))["documents"])
    for item in entries:
        if checksum(LEGACY/"documents"/item["file"])!=item["sha256"]:
            raise ValueError("Legacy corpus changed: "+item["file"])
        shutil.copyfile(LEGACY/"documents"/item["file"], docs/item["file"])
        item["language"] = "mixed" if item["file"].endswith(".docx") else "en"
    for identifier, paragraphs in TECHNIQUES.items():
        obj = next(o for o in objects if o["type"]=="attack-pattern" and any(e.get("external_id")==identifier for e in o.get("external_references",[])))
        filename = "attack_" + identifier.lower().replace(".","_") + ".md"
        text = f"# {identifier}: {obj['name']}\n\n" + "\n\n".join(obj["description"].split("\n\n")[:paragraphs])+"\n"
        (docs/filename).write_text(text,encoding="utf-8")
        entries.append(dict(file=filename,sha256=checksum(docs/filename),language="en",
            origin=dict(kind="official_description_extract",url=f"https://raw.githubusercontent.com/mitre-attack/attack-stix-data/{ATTACK_COMMIT}/enterprise-attack/enterprise-attack.json",
                        source_sha256=ATTACK_SHA,commit=ATTACK_COMMIT,version="Enterprise ATT&CK v17.1",object_id=obj["id"],modified=obj["modified"],
                        extraction=f"Heading plus first {paragraphs} original description paragraphs; no invented or translated source content",license="MITRE ATT&CK terms; ../licenses/MITRE_LICENSE.txt")))
    write(V1/"manifest.json",dict(version="security-corpus-v1-21",documents=entries))
    print("Prepared",len(entries),"documents; legacy corpus untouched.")


def resolve_catalog(retriever, seeds):
    old={q.id:q for q in Dataset(LEGACY/"dataset/questions.jsonl").questions}
    blocks={}
    for parent in retriever.parents.values():
        name=next(d.filename for d in retriever.documents if d.document_id==parent.document_id)
        for block in parent.blocks:
            blocks[(parent.document_id,block.block_id)]=(name,block)
    catalog={}
    for key, seed in seeds.items():
        if "legacy" in seed:
            catalog[key]=old[seed["legacy"]].relevant_evidence[seed.get("index",0)].model_dump()
            continue
        matches=[(doc,block) for (doc,_),(name,block) in blocks.items() if name==seed["source"] and normalize(seed["quote"]) in normalize(block.text)]
        if not matches:
            raise ValueError(f"Unresolved design evidence {key}: {seed['quote']}")
        anchors=[]
        for doc,block in matches:
            anchor=dict(document_id=doc,source=seed["source"],source_block_ids=block.source_block_ids or [block.block_id],
                        section_path=block.section_path,page_number=block.page_number,page_end=block.page_end,text_quote=seed["quote"])
            if anchor not in anchors:
                anchors.append(anchor)
        catalog[key]=dict(evidence_id="security-v1-"+key,relevance_grade=3,**anchors[0],alternatives=anchors[1:])
    return catalog


def compose_questions(old, design, catalog):
    original_meta=design["legacy_metadata"]
    rows=[]
    for row in old:
        rows.append(dict(row,**original_meta[row["id"]]))
    for item in design["new_questions"]:
        row={k:v for k,v in item.items() if k not in {"evidence_keys","english_query"}}
        row.update(category=row["question_type"],answerable=bool(item["evidence_keys"]),relevant_evidence=[catalog[key] for key in item["evidence_keys"]],
                   review_status="pending",reviewer=None,rationale=row["design_note"])
        rows.append(row)
    return rows


def materialize(storage):
    import os
    os.environ["HF_HUB_OFFLINE"]="1"
    os.environ["TRANSFORMERS_OFFLINE"]="1"
    from app.rag.retriever import KnowledgeRetriever
    retriever=KnowledgeRetriever(knowledge_dir=V1/"documents",storage_dir=storage)
    design=json.loads((V1/"question_designs.json").read_text(encoding="utf-8"))
    seeds=json.loads((V1/"evidence_designs.json").read_text(encoding="utf-8"))
    catalog=resolve_catalog(retriever,seeds)
    old=[json.loads(line) for line in (LEGACY/"dataset/questions.jsonl").read_text(encoding="utf-8").splitlines()]
    original_meta=design["legacy_metadata"]
    rows=compose_questions(old,design,catalog)
    folder=V1/"dataset"
    folder.mkdir(exist_ok=True)
    path=folder/"questions.jsonl"
    if path.exists():
        raise FileExistsError("Refusing to replace existing labels; review edits must never be overwritten by generation")
    path.write_text("".join(json.dumps(row,ensure_ascii=False)+"\n" for row in rows),encoding="utf-8")
    write(folder/"dataset.json",dict(schema_version=2,profile="security-v1",version=design.get("dataset_version", "security-rag-benchmark-v1-100-candidate"),documents_dir="../documents",
                                   corpus_version="security-corpus-v1-21",annotation_status="AI-authored additions pending human review; inherited review states unchanged",
                                   legacy_dataset_sha256=checksum(LEGACY/"dataset/questions.jsonl")))
    write(V1/"evidence_catalog.json",catalog)
    translations={row["id"]:dict(original=row["question"],english=(design["legacy_translations"].get(row["id"],row["question"]) if row["id"] in original_meta
                                    else next(q["english_query"] for q in design["new_questions"] if q["id"]==row["id"])),review_status="pending",reviewer=None) for row in rows}
    write(V1/"english_queries.json",translations)
    dataset=Dataset(path)
    dataset.validate_corpus()
    dataset.validate_index(retriever)
    print("Validated",len(rows),"questions; all inherited states unchanged.")
    print(dict(Counter(row["question_type"] for row in rows)))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download-source",action="store_true",help="Explicitly download only the pinned ATT&CK STIX source; never rebuild legacy inputs")
    parser.add_argument("--prepare-corpus",action="store_true")
    parser.add_argument("--materialize",action="store_true")
    parser.add_argument("--storage-dir",type=Path,default=ROOT/"app/storage/security-v1-minilm")
    args=parser.parse_args()
    if args.download_source:
        url=f"https://raw.githubusercontent.com/mitre-attack/attack-stix-data/{ATTACK_COMMIT}/enterprise-attack/enterprise-attack.json"
        with urllib.request.urlopen(url,timeout=120) as response:
            data=response.read()
        if hashlib.sha256(data).hexdigest()!=ATTACK_SHA:
            raise ValueError("Downloaded upstream hash mismatch")
        cache=ROOT/".pytest_cache/benchmark-sources/attack-v17.1.json"
        cache.parent.mkdir(parents=True,exist_ok=True)
        cache.write_bytes(data)
    if args.prepare_corpus:
        prepare_corpus()
    if args.materialize:
        materialize(args.storage_dir)


if __name__=="__main__":
    main()
