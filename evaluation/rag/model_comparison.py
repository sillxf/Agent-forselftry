"""A/B/C retrieval comparisons on identical frozen chunks; never changes app defaults."""
import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import sqlite3
import sys
import time
from contextlib import closing
from datetime import datetime
from pathlib import Path

from evaluation.rag.dataset import Dataset, checksum
from evaluation.rag.runner import run_benchmark, write_json, portable_record, ranking_fingerprint
from evaluation.rag.report import build_report
from evaluation.rag.provenance import code_state, model_state

ROOT=Path(__file__).resolve().parents[2]


def fuse_routes(routes, rank_constant=60):
    scores, records={},{}
    for ranking in routes:
        seen=set()
        for rank,record in enumerate(ranking,1):
            key=record['chunk_id']
            if key in seen:
                continue
            seen.add(key)
            scores[key]=scores.get(key,0)+1/(rank_constant+rank)
            records[key]={**records.get(key,{}),**record}
    keys=sorted(scores,key=lambda key:(-scores[key],-records[key].get('sparse_score',0),-records[key].get('dense_score',-1),key))
    return [{**records[key],'score':scores[key]} for key in keys]


def dual_query_rank(retriever, query, english, k):
    queries=list(dict.fromkeys([query,english]))
    dense=[retriever._rank_children(q,k,'dense') for q in queries]
    sparse=retriever._sparse_search(english,max(retriever.bm25_top_k,k*4))
    routes=[*dense,sparse]
    ranked=fuse_routes(routes)
    return dict(children=[dict(r,source_block_ids=r['block_ids']) for r in ranked[:k]],
                parents=retriever._restore_parents(ranked,k),candidate_count=len(ranked),
                query_routes=[dict(kind='dense' if i<len(dense) else 'bm25',query=queries[i] if i<len(dense) else english,
                                   candidates=[dict(chunk_id=r['chunk_id'],rank=n,score=r.get('dense_score',r.get('sparse_score'))) for n,r in enumerate(route,1)]) for i,route in enumerate(routes)])


def load_reference(dataset, baseline, config):
    from app.rag.retriever import KnowledgeRetriever
    from app.rag.indexing.vector_store import FaissVectorStore
    from app.rag.models import DocumentRecord, ParentChunk
    frozen=baseline/'index_snapshot'
    for name,key in [('chunks.jsonl','chunks_sha256'),('faiss.index','vectors_sha256')]:
        if checksum(frozen/name)!=config['index'][key]:
            raise ValueError('Frozen reference index differs: '+name)
    chunk=config['chunking']
    retriever=KnowledgeRetriever(build=False,knowledge_dir=dataset.documents_dir,model_name=config['embedding']['name'],
        parent_max_tokens=chunk['parent_max_tokens'],child_max_tokens=chunk['child_max_tokens'],overlap_tokens=chunk['overlap_tokens'],
        dense_top_k=config['retrieval']['dense_top_k'],bm25_top_k=config['retrieval']['bm25_top_k'])
    retriever.store=FaissVectorStore.load(frozen)
    with closing(sqlite3.connect(frozen/'metadata.db')) as db:
        retriever.documents=[DocumentRecord.model_validate_json(row[0]) for row in db.execute('SELECT data FROM documents')]
        retriever.parents={p.parent_id:p for p in [ParentChunk.model_validate_json(row[0]) for row in db.execute('SELECT data FROM parents')]}
    retriever._build_sparse()
    dataset.validate_index(retriever)
    return retriever


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline',type=Path,required=True,help='MiniLM run root produced with --retriever all')
    parser.add_argument('--dataset',type=Path,default=ROOT/'tests/rag_benchmark/v1/dataset/questions.jsonl')
    parser.add_argument('--translations',type=Path,default=ROOT/'tests/rag_benchmark/v1/english_queries.json')
    parser.add_argument('--model',default='BAAI/bge-m3')
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--index-batch-size',type=int,default=4,help='Index encoding batch size; does not change chunks or retrieval parameters')
    parser.add_argument('--offline',action='store_true')
    args=parser.parse_args()
    if args.offline:
        os.environ['HF_HUB_OFFLINE']='1'
        os.environ['TRANSFORMERS_OFFLINE']='1'
    os.environ['TOKENIZERS_PARALLELISM']='false'
    import numpy as np
    import torch
    if args.index_batch_size <= 0:
        parser.error('--index-batch-size must be positive')
    np.random.seed(0)
    torch.manual_seed(0)
    dataset=Dataset(args.dataset)
    dataset.validate_corpus()
    config=json.loads((args.baseline/'hybrid/config.json').read_text(encoding='utf-8'))
    if dataset.sha256!=config['dataset']['sha256'] or checksum(dataset.manifest_path)!=config['corpus']['manifest_sha256']:
        raise ValueError('Comparison requires exactly the same labels and corpus')
    translations=json.loads(args.translations.read_text(encoding='utf-8'))
    if set(translations)!={q.id for q in dataset.questions}:
        raise ValueError('Translations must cover the same complete dataset')
    for q in dataset.questions:
        if translations[q.id]['original']!=q.question or not translations[q.id]['english'].strip():
            raise ValueError('Stale or empty query translation: '+q.id)
    output=args.output_dir.resolve()
    output.mkdir(parents=True,exist_ok=False)
    status=dict(created_at=datetime.now().astimezone().isoformat(),dataset_sha256=dataset.sha256,
                ground_truth_shared=True,frozen_chunk_reference=str(args.baseline.resolve()),
                translations_sha256=checksum(args.translations),translation_review_status='pending, not human-certified',
                cross_encoder=False,production_changes=False,
                A=dict(status='completed',metrics_reference=str((args.baseline/'hybrid/multik_metrics.json').resolve())),
                B=dict(status='not_run',model=args.model),C=dict(status='not_run',model=args.model))
    write_json(output/'status.json',status)
    shutil.copyfile(args.translations,output/'english_queries.json')
    write_json(output/'code.json',code_state(output))
    from huggingface_hub import try_to_load_from_cache
    if args.offline and not Path(args.model).exists() and not isinstance(try_to_load_from_cache(args.model,'config.json'),str):
        reason='Model config/weights are not cached locally; --offline forbids downloading. No BGE vectors, scores or winning-model claim were produced.'
        for label in ('B','C'):
            status[label].update(status='unavailable',reason=reason)
        write_json(output/'status.json',status)
        print(reason)
        return
    from app.rag.embedder import get_model
    from app.rag.indexing.vector_store import FaissVectorStore
    model_started=time.perf_counter()
    print(f'Loading {args.model}...',flush=True)
    try:
        model=get_model(args.model)
        embedding=model_state(args.model)
    except OSError as error:
        for label in ('B','C'):
            status[label].update(status='unavailable',reason=f'{type(error).__name__}: {error}')
        write_json(output/'status.json',status)
        print('B/C unavailable; see status.json')
        return
    model_load_seconds=time.perf_counter()-model_started
    retriever=load_reference(dataset,args.baseline,config)
    records=retriever.store.records
    print(f'Encoding {len(records)} frozen chunks with {args.model} (batch={args.index_batch_size})...',flush=True)
    index_started=time.perf_counter()
    vectors=model.encode([r['search_text'] for r in records],batch_size=args.index_batch_size,normalize_embeddings=True,convert_to_numpy=True,show_progress_bar=True)
    store=FaissVectorStore(vectors.shape[1]);store.add(vectors,records);store.save(output/'bge_index')
    retriever.model_name=args.model
    retriever.store=store
    retriever._build_sparse()
    index_seconds=time.perf_counter()-index_started
    environment=dict(python=sys.version,platform=platform.platform(),machine=platform.machine(),
                     torch_threads=torch.get_num_threads(),seed=0,
                     dependencies={d.metadata['Name']:d.version for d in importlib.metadata.distributions() if d.metadata['Name']})
    frozen_hash=hashlib.sha256(json.dumps([portable_record(r) for r in records],sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
    if frozen_hash!=config['index']['portable_chunks_sha256']:
        raise ValueError('Model comparison must not change chunk texts/IDs')
    translated={q.question:translations[q.id]['english'] for q in dataset.questions}
    for label in ('B','C'):
        folder=output/label;folder.mkdir()
        ranker=None if label=='B' else lambda query,k,strategy:dual_query_rank(retriever,query,translated[query],k)
        strategy='hybrid' if label=='B' else 'dual_dense_en_bm25_rrf'
        print(f'Running {label}: {len(dataset.questions)} real queries...',flush=True)
        arm_started=time.perf_counter()
        started_at=datetime.now().astimezone().isoformat()
        rows=run_benchmark(dataset,retriever,top_k=config['retrieval']['top_k'],evaluation_ks=config['retrieval']['evaluation_ks'],strategy=strategy,ranker=ranker)
        arm_seconds=time.perf_counter()-arm_started
        run=dict(config,started_at=started_at,environment=environment,embedding=embedding,retrieval=dict(config['retrieval'],strategy=strategy),index=dict(config['index'],frozen_chunks_sha256=frozen_hash,
                setup_seconds=index_seconds,index_encoding_batch_size=args.index_batch_size,
                source_metadata_sha256=checksum(args.baseline/'index_snapshot/metadata.db'),
                vectors_sha256=checksum(output/'bge_index/faiss.index'),dimensions=store.index.d,
                signature=dict(config['index']['signature'],model=args.model),
                generation='frozen-'+embedding['weights_sha256'][:12]+'-'+frozen_hash[:12],
                source_reference_generation=config['index']['generation'],
                size_bytes=sum(p.stat().st_size for p in (output/'bge_index').iterdir())),
                timing=dict(model_load_and_fingerprint_seconds=model_load_seconds,shared_index_build_seconds=index_seconds,arm_wall_seconds=arm_seconds,
                            translation_generation_seconds=None,translation_policy='Frozen English queries; translation generation is not included in retrieval latency'),
                code=code_state(folder),query_policy='original query hybrid' if label=='B' else 'unique original/English dense routes + English-only BM25 + RRF60; identical English queries deduplicated',
                english_translations_sha256=checksum(args.translations),ranking_sha256=ranking_fingerprint(rows))
        write_json(folder/'config.json',run)
        (folder/'retrieval_results.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
        build_report(folder,run,rows)
        status[label].update(status='completed' if not any(r['error'] for r in rows) else 'completed_with_query_errors',metrics_reference=str(folder/'multik_metrics.json'),embedding=embedding)
        write_json(output/'status.json',status)
        print(f'{label} finished in {arm_seconds:.2f}s; query errors: {sum(bool(r["error"]) for r in rows)}',flush=True)
    from evaluation.rag.comparison_report import build_comparison_report
    build_comparison_report(args.baseline,output)
    print(f'Comparison arms completed using {args.model}; see status.json. No production embedding change.')
    if any(status[label]['status']=='completed_with_query_errors' for label in ('B','C')):
        raise SystemExit(1)


if __name__=='__main__':
    main()
