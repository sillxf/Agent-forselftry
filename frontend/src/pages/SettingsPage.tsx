import type { ConsoleContext } from "../useConsoleController";
import { Json, short, stamp, type Data } from "../shared";
type Props = Pick<
  ConsoleContext,
  | "act"
  | "admin"
  | "busy"
  | "current"
  | "filter"
  | "kb"
  | "models"
  | "saveConfig"
>;
export default function SettingsPage({
  act,
  admin,
  busy,
  current,
  filter,
  kb,
  models,
  saveConfig,
}: Props) {
  if (!current) return null;
  return admin ? (
    <section className="panel" key={kb + "-" + current.revision}>
      <div className="section-label">BUILD ≠ QUERY</div>
      <h2>配置版本 {current.revision}</h2>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          const f = e.currentTarget;
          void act(() => saveConfig(f));
        }}
      >
        <h3>知识库</h3>
        <div className="form-grid">
          <label>
            名称
            <input name="name" defaultValue={current.name} required />
          </label>
          <label>
            描述
            <input name="description" defaultValue={current.description} />
          </label>
        </div>
        <h3>
          索引构建配置 <small>修改后需要构建新快照</small>
        </h3>
        <div className="form-grid">
          <label>
            Embedding
            <select
              name="embedding_id"
              defaultValue={current.build.embedding_id}
            >
              {models
                .filter((m) => m.config.kind === "embedding" && m.enabled)
                .map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.config.model} · {short(m.id)}
                  </option>
                ))}
            </select>
          </label>
          {[
            ["parent_tokens", "Parent token 上限"],
            ["child_tokens", "Child token 上限"],
            ["overlap_tokens", "Child 重叠 token"],
          ].map(([name, label]) => (
            <label key={name}>
              {label}
              <input
                type="number"
                name={name}
                defaultValue={current.build[name]}
                required
              />
            </label>
          ))}
        </div>
        <label className="check">
          <input
            name="ocr"
            type="checkbox"
            defaultChecked={current.build.ocr_enabled}
          />
          启用 OCR
        </label>
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
            <select
              name="reranker_id"
              defaultValue={current.profile.reranker_id}
            >
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
        <label className="check">
          <input
            name="multi_view"
            type="checkbox"
            defaultChecked={current.profile.multi_view_enabled}
          />
          允许调用方明确请求 Multi-View 补检（不自动判断证据不足）
        </label>
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
        <button className="primary" disabled={busy}>
          保存配置
        </button>
      </form>
    </section>
  ) : (
    <section className="panel">只读调用方不能修改全局配置。</section>
  );
}
