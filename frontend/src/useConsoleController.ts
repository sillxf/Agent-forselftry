import { useEffect, useState, useRef } from "react";
import { short, type Data } from "./shared";
export function useConsoleController() {
  const [token, setToken] = useState(""),
    [connected, setConnected] = useState(false),
    [admin, setAdmin] = useState(false),
    [page, setPage] = useState(0);
  const [bases, setBases] = useState<Data[]>([]),
    [kb, setKb] = useState(""),
    [docs, setDocs] = useState<Data[]>([]),
    [models, setModels] = useState<Data[]>([]),
    [jobs, setJobs] = useState<Data[]>([]),
    [keys, setKeys] = useState<Data[]>([]),
    [audit, setAudit] = useState<Data[]>([]);
  const [status, setStatus] = useState<Data>({}),
    [history, setHistory] = useState<Data>({}),
    [detail, setDetail] = useState<Data | null>(null),
    [docId, setDocId] = useState("");
  const [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false),
    [query, setQuery] = useState(""),
    [supplement, setSupplement] = useState(false),
    [filter, setFilter] = useState(""),
    [asOf, setAsOf] = useState(""),
    [k, setK] = useState(5),
    [result, setResult] = useState<Data | null>(null),
    [comparison, setComparison] = useState<Data[]>([]),
    [newKey, setNewKey] = useState(""),
    [docFilter, setDocFilter] = useState("");
  const current = bases.find((b) => b.id === kb);
  const latest = useRef(0),
    selection = useRef(kb);
  selection.current = kb;
  async function api(path: string, options: RequestInit = {}) {
    const r = await fetch("/api/v1" + path, {
      ...options,
      headers: {
        Authorization: "Bearer " + token,
        ...(typeof options.body === "string"
          ? { "Content-Type": "application/json" }
          : {}),
        ...options.headers,
      },
    });
    if (!r.ok) {
      let d;
      try {
        d = await r.json();
      } catch {
        d = { detail: r.statusText };
      }
      throw Error(
        typeof d.detail === "string" ? d.detail : JSON.stringify(d.detail),
      );
    }
    return r.headers.get("content-type")?.includes("json")
      ? r.json()
      : r.blob();
  }
  async function act(fn: () => Promise<void>) {
    setBusy(true);
    setMessage("");
    try {
      await fn();
    } catch (e) {
      setMessage("操作未完成：" + String(e));
    } finally {
      setBusy(false);
    }
  }
  async function reload(id = kb) {
    const epoch = ++latest.current;
    const rows = await api("/knowledge-bases");
    const next = id || rows[0]?.id || "";
    const documents = next
      ? await api("/knowledge-bases/" + next + "/documents")
      : [];
    const info =
      admin && next ? await api("/knowledge-bases/" + next + "/status") : {};
    const publications =
      admin && next
        ? await api("/knowledge-bases/" + next + "/generations")
        : {};
    const modelRows = admin ? await api("/models") : [];
    const jobRows = admin ? await api("/jobs") : [];
    const keyRows = admin ? await api("/keys") : [];
    const auditRows = admin ? await api("/audit") : [];
    if (epoch !== latest.current) return;
    setBases(rows);
    setKb(next);
    setDocs(documents);
    setStatus(info);
    setHistory(publications);
    setModels(modelRows);
    setJobs(jobRows);
    setKeys(keyRows);
    setAudit(auditRows);
  }

  useEffect(() => {
    if (connected) void act(() => reload(kb));
  }, [connected, kb, admin]);
  useEffect(() => {
    setDetail(null);
    setResult(null);
    setComparison([]);
  }, [kb]);
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
  function filters() {
    const out: Data = {};
    for (const item of filter.split(",").filter(Boolean)) {
      const i = item.indexOf("=");
      if (i < 1) throw Error("过滤格式：file_type=pdf,metadata.domain=研发");
      out[item.slice(0, i).trim()] = item.slice(i + 1).trim();
    }
    return out;
  }
  async function runSearch(compare = false) {
    const body = {
      query,
      knowledge_base_ids: [kb],
      top_k: k,
      filters: filters(),
      include_trace: true,
      as_of: asOf || null,
    };
    if (compare) {
      const rows = [];
      for (const x of [false, true])
        rows.push(
          await api("/search", {
            method: "POST",
            body: JSON.stringify({ ...body, supplement: x }),
          }),
        );
      if (selection.current !== kb) return;
      setComparison(rows);
      setResult(rows[1]);
    } else {
      const row = await api("/search", {
        method: "POST",
        body: JSON.stringify({ ...body, supplement }),
      });
      if (selection.current !== kb) return;
      setComparison([]);
      setResult(row);
    }
  }
  async function saveConfig(form: HTMLFormElement) {
    if (!current) return;
    const f = new FormData(form);
    const body = {
      name: f.get("name"),
      description: f.get("description"),
      build: {
        ...current.build,
        embedding_id: f.get("embedding_id"),
        parent_tokens: Number(f.get("parent_tokens")),
        child_tokens: Number(f.get("child_tokens")),
        overlap_tokens: Number(f.get("overlap_tokens")),
        ocr_enabled: f.get("ocr") === "on",
      },
      profile: {
        ...current.profile,
        default_strategy: f.get("strategy"),
        reranker_id: f.get("reranker_id"),
        candidate_k: Number(f.get("candidate_k")),
        supplement_candidate_k: Number(f.get("supplement_candidate_k")),
        reranker_timeout_seconds: Number(f.get("reranker_timeout_seconds")),
        max_top_k: Number(f.get("max_top_k")),
        max_context_chars: Number(f.get("max_context_chars")),
        multi_view_enabled: f.get("multi_view") === "on",
        parent_context: f.get("parent_context") === "on",
      },
    };
    await api("/knowledge-bases/" + kb + "?revision=" + current.revision, {
      method: "PUT",
      body: JSON.stringify(body),
    });
    await reload();
    setMessage("配置已保存。构建配置需发布新索引；检索策略对新请求生效。");
  }
  function logout() {
    latest.current++;
    setConnected(false);
    setToken("");
    setNewKey("");
    setBases([]);
    setKb("");
    setDocs([]);
    setModels([]);
    setJobs([]);
    setKeys([]);
    setAudit([]);
    setStatus({});
    setHistory({});
    setDetail(null);
    setResult(null);
    setComparison([]);
  }

  return {
    act,
    admin,
    api,
    asOf,
    audit,
    bases,
    busy,
    comparison,
    connected,
    current,
    detail,
    docFilter,
    docId,
    docs,
    download,
    filter,
    history,
    inspect,
    job,
    jobs,
    k,
    kb,
    keys,
    logout,
    message,
    models,
    newKey,
    page,
    patchDoc,
    query,
    reload,
    result,
    runSearch,
    saveConfig,
    setAdmin,
    setAsOf,
    setConnected,
    setDetail,
    setDocFilter,
    setFilter,
    setK,
    setKb,
    setMessage,
    setNewKey,
    setPage,
    setQuery,
    setSupplement,
    setToken,
    status,
    supplement,
    token,
    upload,
  };
}
export type ConsoleContext = ReturnType<typeof useConsoleController>;
