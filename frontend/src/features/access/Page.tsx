import { useAccess } from "./useAccess";
import { Json, short, stamp, type Data } from "../../shared/ui";

export default function AccessPage() {
  const {
    act,
    admin,
    api,
    audit,
    bases,
    busy,
    keys,
    newKey,
    reload,
    setNewKey,
  } = useAccess();

  return admin ? (
    <>
      <section className="panel">
        <h2>调用方 API Key</h2>
        <p>只读 Key 绑定知识库，不能修改模型、构建索引或删除文档。</p>
        {newKey && (
          <div className="key-display">
            <strong>仅显示一次，请立即保存</strong>
            <code>{newKey}</code>
            <button onClick={() => setNewKey("")}>隐藏</button>
          </div>
        )}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const form = e.currentTarget;
            const f = new FormData(form);
            void act(async () => {
              const d = await api("/keys", {
                method: "POST",
                body: JSON.stringify({
                  name: f.get("name"),
                  knowledge_base_ids: f.getAll("kb"),
                  requests_per_minute: Number(f.get("rpm")),
                }),
              });
              setNewKey(d.token);
              await reload();
              form.reset();
            });
          }}
        >
          <div className="form-grid">
            <label>
              调用方名称
              <input name="name" required placeholder="Operations Agent" />
            </label>
            <label>
              每分钟请求上限
              <input
                name="rpm"
                type="number"
                defaultValue={60}
                min={1}
                max={10000}
              />
            </label>
          </div>
          <div className="inline">
            {bases.map((b) => (
              <label className="check" key={b.id}>
                <input type="checkbox" name="kb" value={b.id} />
                {b.name}
              </label>
            ))}
          </div>
          <button className="primary" disabled={busy}>
            创建受限 Key
          </button>
        </form>
        {keys.map((x) => (
          <div className="model-row" key={x.id}>
            <div>
              <strong>{x.name}</strong>
              <small>
                {x.knowledge_base_ids.map(short).join(", ")} ·{" "}
                {x.requests_per_minute}/min
              </small>
            </div>
            <span className="badge">{x.revoked ? "已撤销" : "有效"}</span>
            <button
              disabled={busy || x.revoked}
              onClick={() =>
                void act(async () => {
                  await api("/keys/" + x.id, {
                    method: "DELETE",
                  });
                  await reload();
                })
              }
            >
              撤销
            </button>
          </div>
        ))}
      </section>
      <section className="panel">
        <h2>最近操作记录</h2>
        <p>保留 30 天，不保存查询正文或密钥。</p>
        <table>
          <thead>
            <tr>
              <th>时间</th>
              <th>调用方</th>
              <th>操作</th>
              <th>详情</th>
            </tr>
          </thead>
          <tbody>
            {audit.map((a) => (
              <tr key={a.id}>
                <td>{stamp(a.at)}</td>
                <td>{short(a.actor)}</td>
                <td>{a.action}</td>
                <td>
                  <details>
                    <summary>统计与引用</summary>
                    <Json value={JSON.parse(a.details)} />
                  </details>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </>
  ) : (
    <section className="panel">访问管理仅对管理员开放。</section>
  );
}
