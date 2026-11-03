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
    job,
  };
}
export type DocumentFeature = ReturnType<typeof useDocuments>;
