"""Bounded load test for POST /api/v1/search against a running service.

Measures what the current single-host build sustains before deciding on any
architecture change. Sends exactly --requests searches with --concurrency workers,
then prints latency percentiles, throughput and the status-code mix. 503 means the
search slots or the local model were busy; 429 means the key's per-minute quota.

Use a read-only key scoped to one knowledge base, never the administrator token:
    set RAG_LOAD_TOKEN=<key>
    python scripts/load_test.py --kb <kb_id> --concurrency 8 --requests 200

Queries come from --queries (one per line) or a short built-in list. Raise the key's
requests_per_minute above the planned volume first, or 429 will dominate the result.
"""

import argparse
import json
import os
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

import httpx

DEFAULT_QUERIES = [
    "What is credential dumping?",
    "How should an incident responder preserve evidence?",
    "SQL injection 盲注如何判断",
    "暴力破解的检测方法",
    "Which technique uses PowerShell for execution?",
]


def percentile(values, fraction):
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(fraction * len(ordered)))] if ordered else None


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", default=os.getenv("RAG_SERVICE_URL", "http://127.0.0.1:8090"))
    parser.add_argument("--kb", required=True, help="Knowledge base id")
    parser.add_argument("--concurrency", type=int, default=8)
    parser.add_argument("--requests", type=int, default=200)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--queries", help="UTF-8 file, one query per line")
    parser.add_argument("--timeout", type=float, default=60)
    parser.add_argument("--output", help="Also write the JSON summary here")
    args = parser.parse_args()
    token = os.getenv("RAG_LOAD_TOKEN")
    if not token:
        parser.error("Set RAG_LOAD_TOKEN to a read-only key")
    if not 1 <= args.concurrency <= 1000 or not 1 <= args.requests <= 100000:
        parser.error("concurrency 1-1000 and requests 1-100000")
    queries = DEFAULT_QUERIES
    if args.queries:
        with open(args.queries, encoding="utf-8") as stream:
            queries = [line.strip() for line in stream if line.strip()]

    client = httpx.Client(
        base_url=args.url.rstrip("/"),
        headers={"Authorization": "Bearer " + token},
        timeout=args.timeout,
        limits=httpx.Limits(max_connections=args.concurrency),
    )
    lock, latencies, statuses, server_ms = threading.Lock(), [], Counter(), []

    def one(index):
        body = dict(
            query=queries[index % len(queries)],
            knowledge_base_ids=[args.kb],
            top_k=args.top_k,
        )
        started = time.perf_counter()
        try:
            response = client.post("/api/v1/search", json=body)
            status = str(response.status_code)
            reported = response.json()["metadata"]["elapsed_ms"] if response.is_success else None
        except httpx.HTTPError as exc:
            status, reported = type(exc).__name__, None
        elapsed = (time.perf_counter() - started) * 1000
        with lock:
            statuses[status] += 1
            if status == "200":
                latencies.append(elapsed)
                server_ms.append(reported)

    probe = client.get("/api/v1/knowledge-bases")
    if probe.status_code != 200:
        parser.error(f"Token check failed with HTTP {probe.status_code}")
    if not any(k.get("id") == args.kb for k in probe.json()):
        parser.error("The key cannot read this knowledge base")
    started = time.perf_counter()
    with ThreadPoolExecutor(args.concurrency) as pool:
        list(pool.map(one, range(args.requests)))
    wall = time.perf_counter() - started
    client.close()
    summary = dict(
        url=args.url,
        concurrency=args.concurrency,
        requests=args.requests,
        wall_seconds=round(wall, 2),
        successful_per_second=round(len(latencies) / wall, 2),
        statuses=dict(statuses),
        client_latency_ms=dict(
            p50=round(percentile(latencies, 0.5) or 0, 1),
            p95=round(percentile(latencies, 0.95) or 0, 1),
            p99=round(percentile(latencies, 0.99) or 0, 1),
            max=round(max(latencies, default=0), 1),
        ),
        server_elapsed_ms_p50=round(percentile([x for x in server_ms if x], 0.5) or 0, 1),
        note="Single run on this machine; not a capacity guarantee.",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.output:
        with open(args.output, "w", encoding="utf-8") as stream:
            json.dump(summary, stream, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
