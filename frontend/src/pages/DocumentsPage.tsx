import type { ConsoleContext } from "../useConsoleController";
import { Json, short, stamp, type Data } from "../shared";
type Props = Pick<
  ConsoleContext,
  | "act"
  | "admin"
  | "api"
  | "busy"
  | "detail"
  | "docFilter"
  | "docId"
  | "docs"
  | "download"
  | "filter"
  | "inspect"
  | "job"
  | "k"
  | "kb"
  | "patchDoc"
  | "reload"
  | "setDetail"
  | "setDocFilter"
  | "setMessage"
  | "status"
  | "upload"
>;
export default function DocumentsPage({
  act,
  admin,
  api,
  busy,
  detail,
  docFilter,
  docId,
  docs,
  download,
  filter,
  inspect,
  job,
  k,
  kb,
  patchDoc,
  reload,
  setDetail,
  setDocFilter,
  setMessage,
  status,
  upload,
}: Props) {
  return (
    <>
      <section className="panel toolbar">
        <input
          aria-label="筛选文档"
          placeholder="搜索文档名称、元数据…"
          value={docFilter}
          onChange={(e) => setDocFilter(e.target.value)}
        />
        {admin && (
          <>
            <label className="button primary">
              ＋ 上传文档
              <input
                hidden
                type="file"
                multiple
                onChange={(e) => {
                  const files = e.target.files;
                  void act(() => upload(files));
                  e.target.value = "";
                }}
              />
            </label>
            <button disabled={busy} onClick={() => void act(() => job())}>
              构建并发布
            </button>
          </>
        )}
      </section>
      <section className="panel">
        <div className="section-heading">
          <h2>
            文档 <span>{docs.length}</span>
          </h2>
          <small>上传不等于发布 · 原件和生成产物分离</small>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>文档</th>
                <th>状态</th>
                <th>版本 / 发布</th>
                <th>View</th>
                <th>更新时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {docs
                .filter((d) =>
                  JSON.stringify([d.name, d.metadata])
                    .toLowerCase()
                    .includes(docFilter.toLowerCase()),
                )
                .map((d) => (
                  <tr key={d.document_id}>
                    <td>
                      <strong>{d.name}</strong>
                      <small>
                        {short(d.document_id)} · {d.file_type}
                      </small>
                      <small>
                        {Object.entries(d.metadata || {})
                          .map(([k, v]) => k + ": " + v)
                          .join(" · ")}
                      </small>
                    </td>
                    <td>
                      <span
                        className={
                          "badge " + (d.status === "published" ? "green" : "")
                        }
                      >
                        {d.status}
                      </span>
                      {d.needs_build && (
                        <span className="badge amber">待构建</span>
                      )}
                    </td>
                    <td>
                      {d.versions.length} 个版本
                      <small>发布 {short(d.published?.version_id)}</small>
                    </td>
                    <td>
                      {d.view_count} 条
                      <small>
                        {d.view_config.enabled ? "离线生成启用" : "生成关闭"}
                      </small>
                    </td>
                    <td>{stamp(d.updated_at)}</td>
                    <td>
                      <div className="row-actions">
                        {!d.deleted_at && !d.purged_at && (
                          <>
                            <button
                              onClick={() =>
                                void act(() => inspect(d.document_id))
                              }
                            >
                              查看内容
                            </button>
                            <button onClick={() => void act(() => download(d))}>
                              原件 ↓
                            </button>
                          </>
                        )}
                        {admin && (
                          <details>
                            <summary>管理</summary>
                            <div className="action-menu">
                              {!d.purged_at && (
                                <>
                                  <label className="button">
                                    上传新版本
                                    <input
                                      hidden
                                      type="file"
                                      onChange={(e) => {
                                        const f = e.target.files;
                                        void act(() =>
                                          upload(f, d.document_id),
                                        );
                                      }}
                                    />
                                  </label>
                                  <button
                                    onClick={() => {
                                      if (
                                        !d.view_config.enabled &&
                                        !confirm(
                                          "启用后，下次构建可能调用收费 LLM。确认？",
                                        )
                                      )
                                        return;
                                      void act(() =>
                                        patchDoc(d, {
                                          view_config: {
                                            ...d.view_config,
                                            enabled: !d.view_config.enabled,
                                          },
                                        }),
                                      );
                                    }}
                                  >
                                    {d.view_config.enabled
                                      ? "停用 View（下次构建移除）"
                                      : "启用 View"}
                                  </button>
                                  <button
                                    onClick={() => {
                                      const value = prompt(
                                        "用逗号分隔 key=value",
                                        Object.entries(d.metadata || {})
                                          .map(([k, v]) => k + "=" + v)
                                          .join(","),
                                      );
                                      if (value === null) return;
                                      void act(async () => {
                                        const metadata = Object.fromEntries(
                                          value
                                            .split(",")
                                            .filter(Boolean)
                                            .map((x) => {
                                              const i = x.indexOf("=");
                                              if (i < 1)
                                                throw Error("需要 key=value");
                                              return [
                                                x.slice(0, i).trim(),
                                                x.slice(i + 1).trim(),
                                              ];
                                            }),
                                        );
                                        await patchDoc(d, {
                                          metadata,
                                        });
                                      });
                                    }}
                                  >
                                    元数据
                                  </button>
                                  <button
                                    onClick={() => {
                                      const effective_at = prompt(
                                        "生效时间 ISO8601（带时区），空表示立即",
                                        d.effective_at || "",
                                      );
                                      if (effective_at === null) return;
                                      const expires_at = prompt(
                                        "到期时间 ISO8601（带时区），空表示无到期",
                                        d.expires_at || "",
                                      );
                                      if (expires_at === null) return;
                                      void act(async () => {
                                        await api(
                                          "/knowledge-bases/" +
                                            kb +
                                            "/documents/" +
                                            d.document_id +
                                            "/validity",
                                          {
                                            method: "PUT",
                                            body: JSON.stringify({
                                              effective_at:
                                                effective_at || null,
                                              expires_at: expires_at || null,
                                            }),
                                          },
                                        );
                                        await reload();
                                      });
                                    }}
                                  >
                                    有效期
                                  </button>
                                  <button
                                    onClick={() =>
                                      void act(async () => {
                                        await api(
                                          "/knowledge-bases/" +
                                            kb +
                                            "/documents/" +
                                            d.document_id +
                                            (d.deleted_at ? "/undelete" : ""),
                                          {
                                            method: d.deleted_at
                                              ? "POST"
                                              : "DELETE",
                                          },
                                        );
                                        await reload();
                                      })
                                    }
                                  >
                                    {d.deleted_at ? "恢复文档" : "软删除"}
                                  </button>
                                </>
                              )}
                              {d.purge_state !== "completed" && (
                                <button
                                  className="danger"
                                  onClick={() => {
                                    if (
                                      confirm(
                                        "永久清理会撤销包含该文档的旧快照，可能影响其他文档的历史访问；外部备份不在范围内。确认？",
                                      )
                                    )
                                      void act(() =>
                                        job("purge", {
                                          document_id: d.document_id,
                                          confirm: true,
                                        }),
                                      );
                                  }}
                                >
                                  永久 / 继续清理
                                </button>
                              )}
                            </div>
                          </details>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
          {!docs.length && (
            <div className="empty">上传第一份知识，构建发布后即可检索。</div>
          )}
        </div>
      </section>
      {detail && (
        <section className="panel inspection">
          <div className="section-heading">
            <h2>内容检查 · {short(docId)}</h2>
            <button onClick={() => setDetail(null)}>关闭</button>
          </div>
          <div className="note">
            查看已发布版本 {short(detail.published?.version_id)}
            ，不是上传区最新内容。
          </div>
          <div className="inline">
            <button
              disabled={!detail.pagination.offset}
              onClick={() =>
                void act(() =>
                  inspect(docId, Math.max(0, detail.pagination.offset - 30)),
                )
              }
            >
              上一页
            </button>
            <span>
              偏移 {detail.pagination.offset} · Child 总数{" "}
              {detail.pagination.children}
            </span>
            <button
              disabled={
                detail.pagination.offset + 30 >=
                Math.max(
                  detail.pagination.children,
                  detail.pagination.parents,
                  detail.pagination.views,
                )
              }
              onClick={() =>
                void act(() => inspect(docId, detail.pagination.offset + 30))
              }
            >
              下一页
            </button>
          </div>
          <details open>
            <summary>
              解析 Markdown（纯文本预览）
              {detail.markdown_truncated ? " · 已截断" : ""}
            </summary>
            <pre>{detail.markdown || "尚无已发布解析内容"}</pre>
          </details>
          <details>
            <summary>目录</summary>
            <Json value={detail.outline} />
          </details>
          <details>
            <summary>Parent / Child 与来源元数据</summary>
            <Json
              value={{
                parents: detail.parents,
                children: detail.children,
              }}
            />
          </details>
          <details>
            <summary>Multi-View 问题（辅助索引，不是原文）</summary>
            <Json value={detail.views} />
          </details>
          {admin && (
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
                        max_completion_tokens: Number(
                          f.get("max_completion_tokens"),
                        ),
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
                      docs.find((d) => d.document_id === docId)?.view_config
                        .enabled
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
                        docs.find((d) => d.document_id === docId)?.view_config
                          .model || ""
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
                          docs.find((d) => d.document_id === docId)
                            ?.view_config[String(name)] ?? fallback
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
                      <option value="fail_build">
                        整个构建失败，保留旧发布
                      </option>
                    </select>
                  </label>
                </div>
                <button disabled={busy}>保存文档生成配置</button>
              </form>
              <h3>版本恢复</h3>
              {docs
                .find((d) => d.document_id === docId)
                ?.versions.map((v: Data) => (
                  <button
                    key={v.version_id}
                    onClick={() =>
                      void act(async () => {
                        await api(
                          "/knowledge-bases/" +
                            kb +
                            "/documents/" +
                            docId +
                            "/restore-version",
                          {
                            method: "POST",
                            body: JSON.stringify({
                              version_id: v.version_id,
                            }),
                          },
                        );
                        await reload();
                        setMessage("已选择历史原件，构建发布后生效。");
                      })
                    }
                  >
                    选择 v{v.version_number} · {stamp(v.created_at)}
                  </button>
                ))}
            </>
          )}
        </section>
      )}
    </>
  );
}
