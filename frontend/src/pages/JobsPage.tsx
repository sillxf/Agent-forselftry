import type { ConsoleContext } from "../useConsoleController";
import { Json, short, stamp, type Data } from "../shared";
type Props = Pick<
  ConsoleContext,
  | "act"
  | "admin"
  | "api"
  | "busy"
  | "history"
  | "job"
  | "jobs"
  | "reload"
  | "result"
  | "status"
>;
export default function JobsPage({
  act,
  admin,
  api,
  busy,
  history,
  job,
  jobs,
  reload,
  result,
  status,
}: Props) {
  return admin ? (
    <>
      <section className="panel">
        <div className="section-heading">
          <h2>任务队列</h2>
          <button onClick={() => void act(() => reload())}>刷新状态</button>
        </div>
        <div className="inline">
          <button
            className="primary"
            disabled={busy}
            onClick={() => void act(() => job())}
          >
            增量构建并发布
          </button>
          <button
            disabled={busy}
            onClick={() => {
              if (confirm("全量构建会重新处理/编码，可能消耗较多资源，确认？"))
                void act(() => job("build", { full: true }));
            }}
          >
            全量构建
          </button>
          <button
            disabled={busy}
            onClick={() => {
              if (confirm("清理超过保留期的旧索引和无引用缓存，确认？"))
                void act(() => job("gc"));
            }}
          >
            清理旧产物
          </button>
        </div>
        <p>
          需要单独运行 Worker。中断不会自动重复付费生成；核对发布状态后再重试。
        </p>
        <table>
          <thead>
            <tr>
              <th>任务</th>
              <th>状态 / 阶段</th>
              <th>创建时间</th>
              <th>详情</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((j) => (
              <tr key={j.id}>
                <td>
                  {j.operation}
                  <small>
                    {short(j.id)} · 库 {short(j.kb_id)}
                  </small>
                </td>
                <td>
                  <span className="badge">{j.status}</span>
                  <small>{j.stage}</small>
                </td>
                <td>{stamp(j.created)}</td>
                <td>
                  <details>
                    <summary>结果与错误</summary>
                    <Json
                      value={{
                        error: j.error,
                        result: j.result ? JSON.parse(j.result) : null,
                      }}
                    />
                  </details>
                  {["failed", "interrupted"].includes(j.status) && (
                    <button
                      onClick={() =>
                        void act(async () => {
                          await api("/jobs/" + j.id + "/retry", {
                            method: "POST",
                          });
                          await reload();
                        })
                      }
                    >
                      明确重试
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      <section className="panel">
        <h2>发布历史</h2>
        <p>回滚是新的发布事件。已经永久清理或回收的快照不可恢复。</p>
        {history.publications?.map((h: Data) => (
          <div className="model-row" key={h.publication_id}>
            <div>
              <strong>{short(h.generation)}</strong>
              <small>
                {stamp(h.published_at)} · {h.rollback ? "回滚发布" : "构建发布"}
              </small>
            </div>
            <span className="badge">{h.available ? "快照保留" : "不可用"}</span>
            <button
              disabled={busy || !h.available}
              onClick={() => {
                if (confirm("确认回滚到这个快照？"))
                  void act(() =>
                    job("rollback", {
                      generation_id: h.generation,
                    }),
                  );
              }}
            >
              回滚到此版本
            </button>
          </div>
        ))}
      </section>
    </>
  ) : (
    <section className="panel">任务与发布仅对管理员开放。</section>
  );
}
