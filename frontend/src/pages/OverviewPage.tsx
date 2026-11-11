import type { ConsoleContext } from "../useConsoleController";
import { Json, short, stamp, type Data } from "../shared";
type Props = Pick<
  ConsoleContext,
  | "act"
  | "admin"
  | "api"
  | "bases"
  | "busy"
  | "current"
  | "docs"
  | "filter"
  | "job"
  | "kb"
  | "reload"
  | "setKb"
  | "status"
>;
export default function OverviewPage({
  act,
  admin,
  api,
  bases,
  busy,
  current,
  docs,
  filter,
  job,
  kb,
  reload,
  setKb,
  status,
}: Props) {
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
          {bases.map((b) => (
            <button
              className={"base-card " + (b.id === kb ? "chosen" : "")}
              key={b.id}
              onClick={() => setKb(b.id)}
            >
              <span className="base-icon">▤</span>
              <div>
                <strong>{b.name}</strong>
                <p>{b.description || "尚未添加描述"}</p>
                <small>
                  {short(b.id)} · 配置 v{b.revision}
                </small>
              </div>
              <span>↗</span>
            </button>
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
              <button>＋ 创建</button>
            </form>
          )}
        </section>
        <section className="panel">
          <div className="section-label">PUBLICATION</div>
          <h2>当前服务状态</h2>
          <dl>
            <dt>生效索引</dt>
            <dd>{short(status.current?.generation)}</dd>
            <dt>生效 Embedding</dt>
            <dd>{status.active_embedding || "尚未发布"}</dd>
            <dt>期望 Embedding</dt>
            <dd>{current?.build.embedding_id}</dd>
            <dt>配置状态</dt>
            <dd>{status.configuration_pending ? "待构建 / 发布" : "已生效"}</dd>
            <dt>Multi-View 查询</dt>
            <dd>
              {current?.profile.multi_view_enabled ? "允许明确补检" : "关闭"}
            </dd>
          </dl>
          <div className="note">
            RAG 返回原始证据，不判断业务证据是否充分，也不自动生成答案。
          </div>
          {admin && (
            <button
              className="primary"
              disabled={busy || !kb}
              onClick={() => void act(() => job())}
            >
              构建并发布 →
            </button>
          )}
        </section>
      </div>
    </>
  );
}
