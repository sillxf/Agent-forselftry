import { useWorkspace } from "../../app/context";
import { useResource } from "../../shared/useResource";
import { short, type Data } from "../../shared/ui";
import { useEffect, useRef, useState } from "react";
export function usePlayground() {
  const workspace = useWorkspace();
  const { api, kb } = workspace;
  const [query, setQuery] = useState(""),
    [extraQueries, setExtraQueries] = useState(""),
    [supplement, setSupplement] = useState(false),
    [filter, setFilter] = useState(""),
    [minScore, setMinScore] = useState(""),
    [asOf, setAsOf] = useState("");
  const [k, setK] = useState(5),
    [result, setResult] = useState<Data | null>(null),
    [comparison, setComparison] = useState<Data[]>([]);
  const selection = useRef(kb);
  selection.current = kb;
  useEffect(() => {
    setResult(null);
    setComparison([]);
  }, [kb]);
  function filters() {
    const text = filter.trim();
    if (text.startsWith("{")) {
      try {
        return JSON.parse(text);
      } catch {
        throw Error("过滤条件不是有效的 JSON");
      }
    }
    const out: Data = {};
    for (const item of text.split(",").filter(Boolean)) {
      const i = item.indexOf("=");
      if (i < 1) throw Error("过滤格式：file_type=pdf,metadata.domain=研发，或 JSON 对象");
      out[item.slice(0, i).trim()] = item.slice(i + 1).trim();
    }
    return out;
  }
  async function runSearch(compare = false) {
    const body = {
      query,
      queries: extraQueries
        .split("\n")
        .map((x) => x.trim())
        .filter(Boolean)
        .slice(0, 4),
      knowledge_base_ids: [kb],
      top_k: k,
      filters: filters(),
      include_trace: true,
      as_of: asOf || null,
      min_score: minScore === "" ? null : Number(minScore),
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
  return {
    ...workspace,
    query,
    setQuery,
    extraQueries,
    setExtraQueries,
    supplement,
    setSupplement,
    filter,
    setFilter,
    minScore,
    setMinScore,
    asOf,
    setAsOf,
    k,
    setK,
    result,
    comparison,
    runSearch,
  };
}
