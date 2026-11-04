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
  return job;
}
