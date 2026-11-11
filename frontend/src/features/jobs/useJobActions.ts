import { useWorkspace } from "../../app/context";
import { short, type Data } from "../../shared/ui";
export function useJobActions() {
  const { api, kb, reload, setMessage } = useWorkspace();
  async function job(operation = "build", extra: Data = {}) {
    const j = await api("/knowledge-bases/" + kb + "/jobs", {
      method: "POST",
      headers: { "Idempotency-Key": crypto.randomUUID() },
      body: JSON.stringify({ operation, ...extra }),
    });
    await reload();
    setMessage(
      "已提交后台处理，任务编号 " +
        short(j.id) +
        "。请在“任务与发布”查看进度；成功前本次操作尚未完成。",
    );
  }
  async function control(id: string, action: "pause" | "resume" | "cancel") {
    const updated = await api("/jobs/" + id + "/control", {
      method: "POST",
      body: JSON.stringify({ action }),
    });
    await reload();
    setMessage(
      action === "pause"
        ? "已请求暂停；当前解析或模型调用会先到达安全检查点。"
        : action === "resume"
          ? "任务已恢复/重新排队。"
          : updated.status === "cancelled"
            ? "排队任务已取消。"
            : "已请求取消；任务会在安全检查点停止，当前发布版本保持不变。",
    );
  }
  return Object.assign(job, { control });
}
