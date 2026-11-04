import { useWorkspace } from "../../app/context";
import { useResource } from "../../shared/useResource";
import { short, type Data } from "../../shared/ui";
import { useEffect, useRef, useState } from "react";
import { useJobActions } from "../jobs/useJobActions";
export function useDocuments() {
  const workspace = useWorkspace();
  const { api, kb, reload, setMessage } = workspace;
  const docs = useResource<Data[]>(
    kb ? "/knowledge-bases/" + kb + "/documents" : null,
    [],
  );
  const [detail, setDetail] = useState<Data | null>(null),
    [docId, setDocId] = useState(""),
    [docFilter, setDocFilter] = useState("");
  const selection = useRef(kb);
  selection.current = kb;
  const job = useJobActions();
  useEffect(() => {
    setDetail(null);
    setDocId("");
  }, [kb]);
  async function inspect(id: string, offset = 0) {
    const d = await api(
      "/knowledge-bases/" +
        kb +
        "/documents/" +
        id +
        "?offset=" +
        offset +
        "&limit=30",
    );
    if (selection.current !== kb) return;
    setDocId(id);
    setDetail(d);
  }
  async function upload(files: FileList | null, id?: string) {
    if (!files) return;
    for (const f of Array.from(files))
      await api(
        "/knowledge-bases/" +
          kb +
          "/documents?filename=" +
          encodeURIComponent(f.name) +
          (id ? "&document_id=" + id : ""),
        { method: "POST", body: f },
      );
    await reload();
    setMessage("上传完成。构建并发布后，新内容才进入检索。");
  }
  async function patchDoc(d: Data, body: Data) {
    await api("/knowledge-bases/" + kb + "/documents/" + d.document_id, {
      method: "PATCH",
      body: JSON.stringify(body),
    });
    await reload();
    setMessage("已保存；影响索引的配置需构建发布后生效。");
  }
  async function deleteDocument(d: Data) {
    setMessage("正在删除“" + d.name + "”及其索引、原件和缓存…");
    let result: Data;
    try {
      result = await api(
        "/knowledge-bases/" +
          kb +
          "/documents/" +
          d.document_id +
          "?confirm=true",
        { method: "DELETE" },
      );
    } catch (error) {
      if (selection.current === kb) {
        setDetail(null);
        setDocId("");
      }
      // Partial deletion is fail-closed; refresh so its retry action is visible.
      try {
        await reload();
      } catch {
        /* Preserve the deletion error if refresh also fails. */
      }
      const message = error instanceof Error ? error.message : String(error);
      throw new Error(
        message === "Knowledge maintenance is busy"
          ? "暂时无法删除：知识库正在构建或维护，请结束后重试。没有提交后台任务。"
          : "删除未完成，请检查后重试；没有提交后台任务。" + message,
      );
    }
    if (selection.current === kb) {
      setDetail(null);
      setDocId("");
    }
    try {
      await reload();
    } catch {
      setMessage("删除已完成，但列表刷新失败，请刷新页面。");
      return;
    }
    setMessage(
      "删除完成，文档已从检索和文档列表中移除。" +
        (result.external_original_preserved ? "外部原件未删除。" : "") +
        "外部备份不在删除范围内。",
    );
  }
  async function download(d: Data) {
    const blob = await api(
      "/knowledge-bases/" +
        kb +
        "/documents/" +
        d.document_id +
        "/original/" +
        (d.selected_version_id || d.latest_version_id),
    );
    const u = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = u;
    a.download = d.name;
    a.click();
    URL.revokeObjectURL(u);
  }
  return {
    ...workspace,
    docs,
    detail,
    setDetail,
    docId,
    docFilter,
    setDocFilter,
    inspect,
    upload,
    patchDoc,
    download,
    deleteDocument,
    job,
  };
}
export type DocumentFeature = ReturnType<typeof useDocuments>;
