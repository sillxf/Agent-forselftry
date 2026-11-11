import { useWorkspace } from "../../app/context";
import type { Data } from "../../shared/ui";

export function useKnowledgeBaseDeletion() {
  const { act, api, reload, setMessage } = useWorkspace();
  return function deleteBase(base: Data) {
    if (
      !confirm(
        "删除知识库“" +
          base.name +
          "”？将立即删除库内所有文档、版本、索引、缓存和任务记录，不可恢复。关联 API Key 将移除该库的授权。外部原件、备份和共用模型不会删除。",
      )
    )
      return;
    void act(async () => {
      setMessage("正在删除知识库“" + base.name + "”…");
      try {
        await api("/knowledge-bases/" + base.id + "?confirm=true", {
          method: "DELETE",
        });
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        // A partially deleted base stays listed with a retry action, but cannot serve reads/writes.
        try {
          await reload();
        } catch {
          /* Keep the deletion error visible. */
        }
        throw new Error(
          message === "Knowledge maintenance is busy"
            ? "知识库正在构建或维护，暂时无法删除；请结束后重试。没有提交后台任务。"
            : "知识库删除未完成，请重试删除。" + message,
        );
      }
      try {
        await reload();
      } catch {
        setMessage("知识库已删除，但列表刷新失败，请刷新页面。");
        return;
      }
      setMessage(
        "知识库“" + base.name + "”已删除。外部原件、备份和共用模型未删除。",
      );
    });
  };
}
