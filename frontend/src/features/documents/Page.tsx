import { useDocuments } from "./useDocuments";
import { DocumentViewSettings } from "../multiview/DocumentSettings";
import { Json, short, stamp, type Data } from "../../shared/ui";

const documentStatusLabels: Record<string, string> = {
  published: "已发布",
  uploaded: "已上传",
  deleted: "回收站",
  purge_incomplete: "删除未完成",
};

export default function DocumentsPage() {
  const {
    act,
    admin,
    api,
    busy,
    detail,
    docFilter,
    docId,
    docs,
    download,
    deleteDocument,
    inspect,
    job,
    kb,
    patchDoc,
    reload,
    setDetail,
    setDocFilter,
    setMessage,
    upload,
  } = useDocuments();

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
          <small>上传后需构建 · 删除立即执行，不需要后台任务</small>
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
                        {documentStatusLabels[d.status] || d.status}
                      </span>
                      {d.needs_build && (
                        <span className="badge amber">待构建</span>
                      )}
                      {d.hidden_reason && (
                        <span className="badge amber">
                          {d.hidden_reason === "superseded"
                            ? "已被取代，不参与检索"
                            : "不在有效期，不参与检索"}
                        </span>
                      )}
                      {d.review_due && (
                        <span className="badge amber">到期待复核</span>
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
                                    onClick={() => {
                                      const review_after = prompt(
                                        "复核日期 ISO8601（带时区），空表示不提醒。只做提醒，不影响检索",
                                        d.review_after || "",
                                      );
                                      if (review_after === null) return;
                                      void act(async () => {
                                        await api(
                                          "/knowledge-bases/" +
                                            kb +
                                            "/documents/" +
                                            d.document_id +
                                            "/review",
                                          {
                                            method: "PUT",
                                            body: JSON.stringify({
                                              review_after:
                                                review_after || null,
                                            }),
                                          },
                                        );
                                        await reload();
                                      });
                                    }}
                                  >
                                    复核日期
                                  </button>
                                  <button
                                    onClick={() => {
                                      const others = docs.filter(
                                        (x) =>
                                          x.document_id !== d.document_id &&
                                          !x.purged_at,
                                      );
                                      const choice = prompt(
                                        "输入取代本文档的新文档序号，空表示取消取代关系：\n" +
                                          others
                                            .map(
                                              (x, i) => i + 1 + ". " + x.name,
                                            )
                                            .join("\n"),
                                        "",
                                      );
                                      if (choice === null) return;
                                      const target = choice.trim()
                                        ? others[Number(choice) - 1]
                                        : null;
                                      if (choice.trim() && !target) {
                                        setMessage("序号无效，未修改。");
                                        return;
                                      }
                                      void act(async () => {
                                        await api(
                                          "/knowledge-bases/" +
                                            kb +
                                            "/documents/" +
                                            d.document_id +
                                            "/superseded-by",
                                          {
                                            method: "PUT",
                                            body: JSON.stringify({
                                              superseded_by:
                                                target?.document_id || null,
                                            }),
                                          },
                                        );
                                        await reload();
                                        setMessage(
                                          target
                                            ? "已设为被“" +
                                                target.name +
                                                "”取代，立即停止检索本文档。"
                                            : "已取消取代关系。",
                                        );
                                      });
                                    }}
                                  >
                                    被新文档取代
                                  </button>
                                  <button
                                    disabled={busy}
                                    onClick={() =>
                                      void act(async () => {
                                        await api(
                                          "/knowledge-bases/" +
                                            kb +
                                            "/documents/" +
                                            d.document_id +
                                            (d.deleted_at
                                              ? "/undelete"
                                              : "/trash"),
                                          { method: "POST" },
                                        );
                                        setDetail(null);
                                        await reload();
                                        setMessage(
                                          d.deleted_at
                                            ? "文档已恢复。"
                                            : "已移入回收站，立即停止检索；可以恢复。",
                                        );
                                      })
                                    }
                                  >
                                    {d.deleted_at
                                      ? "从回收站恢复"
                                      : "移入回收站（可恢复）"}
                                  </button>
                                </>
                              )}
                            </div>
                          </details>
                        )}
                        {admin && (
                          <button
                            className="danger"
                            disabled={busy}
                            onClick={() => {
                              if (
                                confirm(
                                  "删除“" +
                                    d.name +
                                    "”？将立即删除本服务中的原件、版本、索引和缓存，不可恢复。包含它的旧快照也会移除，可能影响其他文档的历史访问。外部原件和备份不在范围内。",
                                )
                              )
                                void act(() => deleteDocument(d));
                            }}
                          >
                            {d.status === "purge_incomplete"
                              ? "重试删除"
                              : "删除"}
                          </button>
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
              <DocumentViewSettings
                docs={docs}
                docId={docId}
                act={act}
                patchDoc={patchDoc}
                busy={busy}
              />
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
