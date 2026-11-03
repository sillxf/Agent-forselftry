import { useDashboard } from "./useDashboard";
import { Json, short, stamp, type Data } from "../../shared/ui";

export default function OverviewPage() {
  const {
    act,
    admin,
    api,
    bases,
    busy,
    current,
    docs,
    deleteBase,
    job,
    kb,
    reload,
    setKb,
    status,
  } = useDashboard();

  return (
    <>
      <div className="stats">
        {[
          ["知识库", bases.length, "授权范围内的知识空间"],
          [
            "文档",
            docs.filter((d) => !d.purged_at).length,
            "当前知识库的受管文档",
          ],
          ["已发布切块", status.counts?.children ?? "—", "来自当前生效快照"],
          [
            "待更新",
            docs.filter((d) => d.needs_build).length,
            "需构建后检索新内容",
          ],
        ].map(([name, value, note]) => (
          <section className="stat" key={name}>
            <span>{name}</span>
            <strong>{value}</strong>
            <small>{note}</small>
          </section>
        ))}
      </div>
      <div className="two-col">
        <section className="panel">
          <div className="section-label">KNOWLEDGE SPACES</div>
          <h2>你的知识库</h2>
          {!bases.length && (
            <div className="empty">暂无知识库，请创建一个知识库开始使用。</div>
          )}
          {bases.map((b) => (
            <div className="base-entry" key={b.id}>
              <button
                className={"base-card " + (b.id === kb ? "chosen" : "")}
                onClick={() => setKb(b.id)}
                disabled={busy}
              >
                <span className="base-icon">▤</span>
                <div>
                  <strong>{b.name}</strong>
                  <p>
                    {b.deleting
                      ? "删除未完成，已停止服务；请重试删除。"
                      : b.description || "尚未添加描述"}
                  </p>
                  <small>
                    {short(b.id)} · 配置 v{b.revision}
                  </small>
                </div>
                <span>↗</span>
              </button>
              {admin && (
                <button
                  className="danger"
                  disabled={busy}
                  aria-label={
                    (b.deleting ? "重试删除知识库 " : "删除知识库 ") + b.name
                  }
                  onClick={() => deleteBase(b)}
                >
                  {b.deleting ? "重试删除" : "删除知识库"}
                </button>
              )}
            </div>
          ))}
          {admin && (
            <form
              className="inline"
              onSubmit={(e) => {
                e.preventDefault();
                const form = e.currentTarget;
                const name = new FormData(form).get("name");
                void act(async () => {
                  const b = await api("/knowledge-bases", {
                    method: "POST",
                    body: JSON.stringify({ name }),
                  });
                  await reload(b.id);
                  form.reset();
                });
              }}
            >
              <input
                name="name"
                aria-label="新知识库名称"
                placeholder="新知识库名称"
                required
                maxLength={120}
              />
              <button disabled={busy}>＋ 创建</button>
            </form>
          )}
        </section>
        <section className="panel">
          <div className="section-label">PUBLICATION</div>
          <h2>当前服务状态</h2>
          {!current || current.deleting ? (
            <div className="empty">
              {current?.deleting
                ? "该知识库删除未完成，已停止服务；请在左侧重试删除。"
                : "创建或选择知识库后，可查看当前服务状态。"}
            </div>
          ) : (
            <>
              <dl>
                <dt>生效索引</dt>
                <dd>{short(status.current?.generation)}</dd>
                <dt>生效 Embedding</dt>
                <dd>{status.active_embedding || "尚未发布"}</dd>
                <dt>期望 Embedding</dt>
                <dd>{current?.build.embedding_id}</dd>
                <dt>配置状态</dt>
                <dd>
                  {status.configuration_pending ? "待构建 / 发布" : "已生效"}
                </dd>
                <dt>Multi-View 查询</dt>
                <dd>
                  {current?.profile.multi_view_enabled
                    ? "允许明确补检"
                    : "关闭"}
                </dd>
              </dl>
              <div className="note">
                RAG 返回原始证据，不判断业务证据是否充分，也不自动生成答案。
              </div>
              {admin && (
                <button
                  className="primary"
                  disabled={busy || !kb || current?.deleting}
                  onClick={() => void act(() => job())}
                >
                  构建并发布 →
                </button>
              )}
            </>
          )}
        </section>
      </div>
    </>
  );
}
