import { useModels } from "./useModels";
import { Json, short, stamp, type Data } from "../../shared/ui";

export default function ModelsPage() {
  const { act, admin, api, busy, models, reload, setMessage } = useModels();

  return admin ? (
    <>
      <section className="panel">
        <h2>模型版本</h2>
        <p>
          模型配置不可原地修改。新增版本，再选择、构建与发布。停用禁止新配置/构建，不破坏已发布历史的读取。
        </p>
        {models.map((m) => (
          <div className="model-row" key={m.id}>
            <div>
              <strong>{m.config.model}</strong>
              <small>
                {m.config.kind} · {m.config.provider} · 修订 {m.config.revision}{" "}
                · {short(m.id)}
              </small>
            </div>
            <span className="badge">
              {m.enabled ? "可用于新构建" : "已停用"}
            </span>
            <button
              onClick={() => {
                if (
                  confirm(
                    "测试可能下载/加载本地模型，或发起一次收费远程请求，确认？",
                  )
                )
                  void act(async () => {
                    const r = await api(
                      "/models/" + m.id + "/probe?confirm=true",
                      { method: "POST" },
                    );
                    setMessage(JSON.stringify(r));
                  });
              }}
            >
              测试推理
            </button>
            <button
              onClick={() =>
                void act(async () => {
                  await api("/models/" + m.id + "/enabled", {
                    method: "PUT",
                    body: JSON.stringify({ enabled: !m.enabled }),
                  });
                  await reload();
                })
              }
            >
              {m.enabled ? "停用" : "启用"}
            </button>
          </div>
        ))}
      </section>
      <section className="panel">
        <h2>添加模型版本</h2>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const form = e.currentTarget;
            const f = new FormData(form);
            void act(async () => {
              const provider = String(f.get("provider"));
              const body = {
                kind: provider === "cross_encoder" ? "reranker" : "embedding",
                provider,
                model: f.get("model"),
                revision: f.get("revision") || "default",
                dimension: f.get("dimension")
                  ? Number(f.get("dimension"))
                  : null,
                tokenizer: f.get("tokenizer") || null,
                base_url: f.get("base_url") || null,
                secret_env: f.get("secret_env") || null,
                encoding: f.get("encoding"),
                query_prefix: f.get("query_prefix"),
                document_prefix: f.get("document_prefix"),
              };
              await api("/models", {
                method: "POST",
                body: JSON.stringify(body),
              });
              await reload();
              form.reset();
            });
          }}
        >
          <div className="form-grid">
            <label>
              Provider
              <select name="provider">
                <option value="sentence_transformers">
                  本地 Sentence Transformers Embedding
                </option>
                <option value="openai_compatible">兼容 HTTP Embedding</option>
                <option value="cross_encoder">
                  本地 Cross Encoder Reranker
                </option>
              </select>
            </label>
            <label>
              模型名称
              <input name="model" required placeholder="BAAI/bge-m3" />
            </label>
            <label>
              模型修订
              <input
                name="revision"
                placeholder="建议填不可变 commit / 服务版本"
              />
            </label>
            <label>
              预期维度
              <input
                name="dimension"
                type="number"
                placeholder="远程模型必填"
              />
            </label>
            <label>
              Tokenizer
              <input
                name="tokenizer"
                placeholder="远程模型需指定本地 tokenizer"
              />
            </label>
            <label>
              编码方式
              <select name="encoding">
                <option value="encode">通用 encode（兼容旧索引）</option>
                <option value="query_document">
                  独立 query / document 编码
                </option>
              </select>
            </label>
            <label>
              远程 Base URL
              <input
                name="base_url"
                placeholder="https://provider.example/v1"
              />
            </label>
            <label>
              凭据环境变量名
              <input
                name="secret_env"
                placeholder="RAG_EMBEDDING_API_KEY（不是密钥）"
              />
            </label>
            <label>
              查询前缀
              <input name="query_prefix" defaultValue="" />
            </label>
            <label>
              文档前缀
              <input name="document_prefix" defaultValue="" />
            </label>
          </div>
          <div className="note">
            远程 Provider
            会接收文档/查询文本。只有管理员能配置端点；密钥保留在服务运行环境，不通过页面保存。
          </div>
          <button className="primary" disabled={busy}>
            添加不可变版本
          </button>
        </form>
      </section>
    </>
  ) : (
    <section className="panel">模型配置仅对管理员开放。</section>
  );
}
