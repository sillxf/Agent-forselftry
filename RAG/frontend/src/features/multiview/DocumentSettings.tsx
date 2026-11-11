import type { DocumentFeature } from "../documents/useDocuments";
type Props = Pick<
  DocumentFeature,
  "docs" | "docId" | "act" | "patchDoc" | "busy"
>;
export function DocumentViewSettings({
  docs,
  docId,
  act,
  patchDoc,
  busy,
}: Props) {
  return (
    <>
      <h3>文档级 View 生成配置</h3>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          const f = new FormData(e.currentTarget);
          const d = docs.find((x) => x.document_id === docId)!;
          void act(() =>
            patchDoc(d, {
              view_config: {
                ...d.view_config,
                enabled: f.get("enabled") === "on",
                model: f.get("model") || null,
                batch_size: Number(f.get("batch_size")),
                max_requests: Number(f.get("max_requests")),
                timeout_seconds: Number(f.get("timeout_seconds")),
                max_completion_tokens: Number(f.get("max_completion_tokens")),
                failure_policy: f.get("failure_policy"),
              },
            }),
          );
        }}
      >
        <label className="check">
          <input
            type="checkbox"
            name="enabled"
            defaultChecked={
              docs.find((d) => d.document_id === docId)?.view_config.enabled
            }
          />
          启用离线生成（构建时可能收费）
        </label>
        <div className="form-grid">
          <label>
            生成模型
            <input
              name="model"
              defaultValue={
                docs.find((d) => d.document_id === docId)?.view_config.model ||
                ""
              }
              placeholder="留空继承服务环境配置"
            />
          </label>
          {[
            ["batch_size", "每批 Chunk 数", 8],
            ["max_requests", "每文档请求上限", 8],
            ["timeout_seconds", "请求超时（秒）", 90],
            ["max_completion_tokens", "单次输出 Token 上限", 2048],
          ].map(([name, label, fallback]) => (
            <label key={String(name)}>
              {label}
              <input
                type="number"
                name={String(name)}
                defaultValue={
                  docs.find((d) => d.document_id === docId)?.view_config[
                    String(name)
                  ] ?? fallback
                }
              />
            </label>
          ))}
          <label>
            生成失败策略
            <select
              name="failure_policy"
              defaultValue={
                docs.find((d) => d.document_id === docId)?.view_config
                  .failure_policy || "publish_without_views"
              }
            >
              <option value="publish_without_views">
                保留原文索引，不带 View 发布
              </option>
              <option value="fail_build">整个构建失败，保留旧发布</option>
            </select>
          </label>
        </div>
        <button disabled={busy}>保存文档生成配置</button>
      </form>
    </>
  );
}
