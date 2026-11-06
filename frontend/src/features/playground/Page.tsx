import { usePlayground } from "./usePlayground";
import { useState } from "react";
import { Json, short, type Data } from "../../shared/ui";

// Show the parent with the matched chunk marked, so the reader sees why it was hit.
function Highlighted({ text, match }: { text: string; match?: string }) {
  const at = match ? text.indexOf(match) : -1;
  if (!match || at < 0 || match === text) return <pre>{text}</pre>;
  return (
    <pre>
      {text.slice(0, at)}
      <mark>{match}</mark>
      {text.slice(at + match.length)}
    </pre>
  );
}

function Neighbours({ kb, r, api }: { kb: string; r: Data; api: (p: string) => Promise<Data> }) {
  const [context, setContext] = useState<Data | null>(null);
  return (
    <details
      onToggle={(e) => {
        if ((e.target as HTMLDetailsElement).open && !context)
          void api(
            "/knowledge-bases/" + kb + "/chunks/" + r.chunk_id + "/context?before=2&after=2",
          ).then(setContext, (err) => setContext({ error: String(err) }));
      }}
    >
      <summary>前后文（同一文档中相邻的片段）</summary>
      {!context ? (
        <small>读取中…</small>
      ) : context.error ? (
        <small>{context.error}</small>
      ) : (
        context.items.map((item: Data) => (
          <div key={item.chunk_id} className={item.offset === 0 ? "neighbour hit" : "neighbour"}>
            <small>
              {item.offset === 0 ? "命中" : item.offset > 0 ? "后 " + item.offset : "前 " + -item.offset}
              {" · "}第 {item.page_start ?? "—"} 页
            </small>
            <pre>{item.content}</pre>
          </div>
        ))
      )}
    </details>
  );
}

export default function PlaygroundPage() {
  const {
    act,
    api,
    kb,
    minScore,
    setMinScore,
    asOf,
    busy,
    comparison,
    extraQueries,
    filter,
    k,
    query,
    result,
    runSearch,
    setAsOf,
    setExtraQueries,
    setFilter,
    setK,
    setQuery,
    setSupplement,
    supplement,
  } = usePlayground();

  return (
    <>
      <section className="panel">
        <div className="section-label">RETRIEVAL PLAYGROUND</div>
        <h2>查看一次检索实际发生了什么</h2>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            void act(() => runSearch());
          }}
        >
          <div className="search-bar">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              aria-label="检索问题"
              placeholder="输入问题，查看原始证据、来源和阶段耗时…"
              required
              maxLength={4000}
            />
            <button className="primary" disabled={busy}>
              检索 →
            </button>
          </div>
          <div className="form-grid">
            <label>
              最终 Top K
              <input
                type="number"
                min={1}
                max={20}
                value={k}
                onChange={(e) => setK(Number(e.target.value))}
              />
            </label>
            <label>
              元数据过滤
              <input
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                placeholder='file_type=pdf 或 {"metadata.year": {"$gte": "2024"}}'
              />
            </label>
            <label>
              最低相关度（可选，0–1）
              <input
                type="number"
                min={0}
                max={1}
                step={0.05}
                value={minScore}
                onChange={(e) => setMinScore(e.target.value)}
                placeholder="不设"
              />
            </label>
            <label>
              历史发布时间（可选）
              <input
                value={asOf}
                onChange={(e) => setAsOf(e.target.value)}
                placeholder="2026-11-03T08:00:00Z"
              />
            </label>
          </div>
          <label>
            附加查询（可选，每行一条，最多 4 条）
            <textarea
              rows={2}
              value={extraQueries}
              onChange={(e) => setExtraQueries(e.target.value)}
              placeholder="例如问题的英文翻译，或改用文档中的术语"
            />
          </label>
          <label className="check">
            <input
              type="checkbox"
              checked={supplement}
              onChange={(e) => setSupplement(e.target.checked)}
            />
            本次明确请求补检（受知识库开关控制）
          </label>
          <button
            type="button"
            disabled={busy || !query}
            onClick={() => void act(() => runSearch(true))}
          >
            比较本次：主检索 / 明确补检
          </button>
        </form>
        <div className="note">
          这是手动链路检查，不是效果评测。单题不能证明整体质量提高；查询日志默认只记录哈希与统计。
        </div>
      </section>
      {result && (
        <>
          <div className="result-meta">
            <span>结果 {result.results.length}</span>
            <span>耗时 {result.metadata.elapsed_ms.toFixed(1)} ms</span>
            <span>请求 {short(result.request_id)}</span>
            <span>{result.metadata.warnings.join(" · ") || "无降级"}</span>
          </div>
          {result.results.map((r: Data, i: number) => (
            <section
              className="panel evidence"
              key={r.knowledge_base_id + r.chunk_id}
            >
              <div className="section-heading">
                <h2>
                  <span className="rank">{i + 1}</span>
                  {r.source || r.source_name}
                </h2>
                <span className="badge">
                  相关度 {r.relevance != null ? r.relevance.toFixed(3) : "—"}
                  {r.relevance_source === "reranker" ? "（重排）" : ""}
                </span>
              </div>
              <div className="chips">
                <span>{r.context_scope === "child" ? "片段" : "所在段落"}</span>
                {r.section_path?.length > 0 && <span>{r.section_path.join(" › ")}</span>}
                <span>版本 {short(r.version_id)}</span>
                <span>
                  页码 {r.page_start || "—"}–{r.page_end || "—"}
                </span>
                <span>Dense {r.dense_score?.toFixed(4) ?? "—"}</span>
                <span>BM25 {r.sparse_score?.toFixed(4) ?? "—"}</span>
                <span>融合 {r.score?.toFixed(5) ?? "—"}</span>
                <span>重排 {r.reranker_score?.toFixed(4) ?? "—"}</span>
              </div>
              <Highlighted text={r.content} match={r.chunk_content} />
              {kb && <Neighbours kb={kb} r={r} api={api} />}
              <details>
                <summary>引用和完整元数据</summary>
                <Json value={r} />
              </details>
            </section>
          ))}
          <section className="panel">
            <details open>
              <summary>阶段 Trace：候选、重排前后、耗时和降级原因</summary>
              <Json value={result.trace} />
            </details>
            {comparison.length > 0 && (
              <details>
                <summary>两次请求对比（不是质量评分）</summary>
                <Json
                  value={comparison.map((r) => ({
                    metadata: r.metadata,
                    trace: r.trace,
                    results: r.results.map((x: Data) => ({
                      document_id: x.document_id,
                      chunk_id: x.chunk_id,
                    })),
                  }))}
                />
              </details>
            )}
          </section>
        </>
      )}
    </>
  );
}
