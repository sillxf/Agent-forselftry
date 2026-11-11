import { useWorkspace } from "../../app/context";
import { useResource } from "../../shared/useResource";
import { short, type Data } from "../../shared/ui";
import { useEffect, useRef, useState } from "react";
export function useKnowledgeSettings() {
  const workspace = useWorkspace();
  const { api, kb, current, reload, setMessage, admin } = workspace;
  const models = useResource<Data[]>(admin ? "/models" : null, []);
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
        max_context_tokens: Number(f.get("max_context_tokens")),
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
  return { ...workspace, models, saveConfig };
}
