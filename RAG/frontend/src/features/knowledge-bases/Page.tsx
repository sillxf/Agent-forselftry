import { useKnowledgeBaseDeletion } from "./useKnowledgeBaseDeletion";
import { useKnowledgeSettings } from "./useKnowledgeSettings";
import { RetrievalFields } from "../retrieval-settings/Fields";
import { Json, short, stamp, type Data } from "../../shared/ui";

export default function SettingsPage() {
  const { act, admin, busy, current, kb, models, saveConfig } =
    useKnowledgeSettings();

  const deleteBase = useKnowledgeBaseDeletion();
  if (!current) return null;
  return admin ? (
    <section className="panel" key={kb + "-" + current.revision}>
      <div className="section-label">BUILD ≠ QUERY</div>
      <div className="section-heading">
        <h2>配置版本 {current.revision}</h2>
        <button
          className="danger"
          disabled={busy}
          onClick={() => deleteBase(current)}
        >
          删除知识库
        </button>
      </div>
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
        <RetrievalFields current={current} models={models} />
        <button className="primary" disabled={busy}>
          保存配置
        </button>
      </form>
    </section>
  ) : (
    <section className="panel">只读调用方不能修改全局配置。</section>
  );
}
