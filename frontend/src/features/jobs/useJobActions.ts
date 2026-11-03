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
      "任务已排队 " + short(j.id) + "，由 Worker 执行；旧发布仍然服务。",
    );
  }
  return job;
}
