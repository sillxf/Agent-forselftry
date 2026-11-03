import { short, type Data } from "../../shared/ui";
import { MultiViewPolicyFields } from "../multiview/PolicyFields";
export function RetrievalFields({
  current,
  models,
}: {
  current: Data;
  models: Data[];
}) {
  return (
    <>
      <h3>
        在线检索策略 <small>保存后对新请求生效</small>
      </h3>
      <div className="form-grid">
        <label>
          检索模式
          <select
            name="strategy"
            defaultValue={current.profile.default_strategy}
          >
            {["dense", "bm25", "hybrid", "hybrid_rerank"].map((x) => (
              <option key={x}>{x}</option>
            ))}
          </select>
        </label>
        <label>
          Reranker
          <select name="reranker_id" defaultValue={current.profile.reranker_id}>
            {models
              .filter((m) => m.config.kind === "reranker" && m.enabled)
              .map((m) => (
                <option key={m.id} value={m.id}>
                  {m.config.model} · {short(m.id)}
                </option>
              ))}
          </select>
        </label>
        {[
          ["candidate_k", "主检索重排候选数"],
          ["supplement_candidate_k", "补检额外候选数"],
          ["reranker_timeout_seconds", "重排超时（秒）"],
          ["max_top_k", "最终返回数上限"],
          ["max_context_chars", "上下文字符预算"],
        ].map(([name, label]) => (
          <label key={name}>
            {label}
            <input
              name={name}
              type="number"
              defaultValue={current.profile[name]}
              required
            />
          </label>
        ))}
      </div>
      <MultiViewPolicyFields current={current} />
      <label className="check">
        <input
          name="parent_context"
          type="checkbox"
          defaultChecked={current.profile.parent_context}
        />
        返回 Parent 上下文
      </label>
      <div className="note">
        没有统一的“相关性
        0.5”开关。Dense、BM25、融合和重排分数含义不同，不能当作可信度概率。
      </div>
    </>
  );
}
