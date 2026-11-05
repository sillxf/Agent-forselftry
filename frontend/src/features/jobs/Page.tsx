import { useJobs } from "./useJobs";
import { Json, short, stamp, type Data } from "../../shared/ui";

const statusNames: Record<string, string> = {
  queued: "排队中",
  running: "执行中",
  paused: "已暂停",
  succeeded: "已完成",
  failed: "失败",
  interrupted: "已中断",
  cancelled: "已取消",
};
const stageNames: Record<string, string> = {
  queued: "等待执行",
  paused_queued: "暂停排队",
  starting: "启动中",
  freezing_inputs: "读取构建输入",
  parsing_and_chunking: "解析与切分文档",
  embedding_and_indexing: "编码并构建索引",
  optional_view_generation: "整理检索视图",
  pause_requested: "等待安全暂停点",
  paused: "暂停中",
  ready_to_publish: "准备发布",
  publishing: "切换发布中",
  cancelling: "等待安全取消点",
  completed: "已完成",
  failed: "失败",
  interrupted: "已中断",
  cancelled: "已取消",
};

export default function JobsPage() {
  const { act, admin, api, busy, history, job, jobs, reload } = useJobs();

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
          增量构建会复用未变化文档的解析与向量，只处理新增或变更内容，并移除已删除内容；兼容条件不满足时会自动全量重建。新索引准备完成后才切换发布，构建期间旧版本继续服务。
        </p>
        <p>
          排队任务可立即暂停或取消。运行中的任务会在安全检查点响应；正在进行的单个解析/模型调用需先结束。进入“发布切换”后不再接受暂停或取消。暂停期间会占用后台执行位，若此时关闭程序，任务会标记为中断。
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
                  <span className="badge">
                    {j.awaiting_confirmation ? "待确认执行" : statusNames[j.status] || j.status}
                  </span>
                  <small>{stageNames[j.stage] || j.stage}</small>
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
                  {["build", "rollback"].includes(j.operation) && (
                    <div className="inline">
                      {j.status === "queued" && (
                        <>
                          <button onClick={() => void act(() => job.control(j.id, "pause"))}>
                            暂停
                          </button>
                          <button onClick={() => {
                            if (confirm("取消这个排队任务？"))
                              void act(() => job.control(j.id, "cancel"));
                          }}>
                            取消
                          </button>
                        </>
                      )}
                      {j.status === "running" && !["publishing", "cancelling"].includes(j.stage) && (
                        <>
                          {j.stage === "pause_requested" ? (
                            <button onClick={() => void act(() => job.control(j.id, "resume"))}>
                              撤销暂停
                            </button>
                          ) : (
                            <button onClick={() => void act(() => job.control(j.id, "pause"))}>
                              暂停
                            </button>
                          )}
                          <button onClick={() => {
                            if (confirm("请求取消任务？会等当前解析/模型调用结束后停止，不发布本次构建。"))
                              void act(() => job.control(j.id, "cancel"));
                          }}>
                            取消
                          </button>
                        </>
                      )}
                      {j.status === "running" && j.stage === "publishing" && (
                        <small>正在切换发布，不可中断</small>
                      )}
                      {j.status === "paused" && (
                        <>
                          <button onClick={() => void act(() => job.control(j.id, "resume"))}>
                            继续
                          </button>
                          <button onClick={() => {
                            if (confirm("取消已暂停的任务？本次构建不会发布。"))
                              void act(() => job.control(j.id, "cancel"));
                          }}>
                            取消
                          </button>
                        </>
                      )}
                      {j.status === "running" && j.stage === "cancelling" && (
                        <small>正在等待安全检查点</small>
                      )}
                    </div>
                  )}
                  {j.operation === "purge" &&
                    ["failed", "interrupted"].includes(j.status) && (
                      <small>
                        该历史删除未完成。请到“文档与内容”核对并直接删除。
                      </small>
                    )}
                  {(["failed", "interrupted", "cancelled"].includes(j.status) ||
                    j.awaiting_confirmation) &&
                    j.operation !== "purge" && (
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
                        {j.awaiting_confirmation ? "确认执行" : j.status === "cancelled" ? "重新提交" : "明确重试"}
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
