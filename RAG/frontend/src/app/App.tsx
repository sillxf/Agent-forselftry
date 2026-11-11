import { useWorkspace, WorkspaceProvider } from "./context";
import { useState } from "react";
import { pages, type Data } from "../shared/ui";
import OverviewPage from "../features/dashboard/Page";
import DocumentsPage from "../features/documents/Page";
import SettingsPage from "../features/knowledge-bases/Page";
import ModelsPage from "../features/models/Page";
import PlaygroundPage from "../features/playground/Page";
import JobsPage from "../features/jobs/Page";
import AccessPage from "../features/access/Page";
function Shell() {
  const context = useWorkspace();
  const [page, setPage] = useState(0);
  const {
    act,
    admin,
    api,
    bases,
    busy,
    connected,
    connecting,
    localConsole,
    connectLocal,
    current,
    kb,
    logout,
    message,

    reload,
    setAdmin,
    setConnected,

    setKb,
    setMessage,

    setToken,
    token,
  } = context;
  return (
    <div className="shell">
      <aside>
        <a className="brand" href="/">
          <span className="mark">知</span>
          <span>
            知序<small>KNOWLEDGE SERVICE</small>
          </span>
        </a>
        <div className="eyebrow">WORKSPACE / 知识工作台</div>
        <nav>
          {pages.map((s, i) => (
            <button
              key={s}
              className={page === i ? "active" : ""}
              onClick={() => {
                setPage(i);
              }}
            >
              <span>{["◈", "▤", "⚙", "⬡", "⌕", "↗", "⌘"][i]}</span>
              {s}
            </button>
          ))}
        </nav>
        <div className="aside-bottom">
          <span className="dot" /> 独立 RAG 服务
          <small>证据优先 · 配置可控 · 全生命周期</small>
        </div>
      </aside>
      <main>
        <header>
          <div>
            工作空间 <span>/</span> {pages[page]}
          </div>
          <div className="header-actions">
            <span className={"connection " + (connected ? "online" : "")}>
              {connected ? (admin ? "管理员已连接" : "只读调用方") : "尚未连接"}
            </span>
            {connected && (
              <button disabled={busy} onClick={() => void act(() => reload())}>
                刷新
              </button>
            )}
            <button disabled={busy || connecting} onClick={() => void logout()}>
              退出
            </button>
          </div>
        </header>
        <div className="workspace">
          <div className="title-row">
            <div>
              <div className="eyebrow">RETRIEVAL INFRASTRUCTURE</div>
              <h1>{pages[page]}</h1>
              <p>让知识成为可管理、可追溯、可被不同 Agent 使用的证据。</p>
            </div>
            {connected && (
              <select
                aria-label="当前知识库"
                value={kb}
                onChange={(e) => setKb(e.target.value)}
              >
                {bases.map((b) => (
                  <option key={b.id} value={b.id}>
                    {b.name}
                  </option>
                ))}
              </select>
            )}
          </div>
          {connecting ? (
            <section className="panel">
              <h2>正在打开工作台…</h2>
            </section>
          ) : !connected && localConsole ? (
            <section className="panel">
              <h2>本地工作台已断开</h2>
              <button
                className="primary"
                disabled={busy}
                onClick={() =>
                  void act(async () => {
                    await connectLocal();
                  })
                }
              >
                重新打开工作台
              </button>
            </section>
          ) : !connected ? (
            <section className="panel login">
              <div className="section-label">CONNECT YOUR WORKSPACE</div>
              <h2>连接你的知识服务</h2>
              <p>令牌仅保存在当前页面内存，不写入浏览器本地存储。</p>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  void act(async () => {
                    const me = await api("/me");
                    setAdmin(me.admin);
                    setConnected(true);
                  });
                }}
              >
                <input
                  type="password"
                  aria-label="访问令牌"
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  placeholder="管理员令牌 / Agent API Key"
                  required
                />
                <button className="primary" disabled={busy}>
                  连接服务 →
                </button>
              </form>
              <small>
                首次使用：运行 rag-service init，从数据目录 admin.token
                读取管理员令牌。
              </small>
            </section>
          ) : [1, 2, 4, 5].includes(page) && (!kb || current?.deleting) ? (
            <section className="panel">
              <h2>{current?.deleting ? "知识库删除未完成" : "暂无知识库"}</h2>
              <p>
                {current?.deleting
                  ? "该库已停止服务，请到知识总览重试删除。"
                  : "请先到知识总览创建知识库。"}
              </p>
              <button onClick={() => setPage(0)}>前往知识总览</button>
            </section>
          ) : (
            <>
              {page === 0 && <OverviewPage />}
              {page === 1 && <DocumentsPage />}
              {page === 2 && current && <SettingsPage />}
              {page === 3 && <ModelsPage />}
              {page === 4 && <PlaygroundPage />}
              {page === 5 && <JobsPage />}
              {page === 6 && <AccessPage />}
            </>
          )}
          {message && (
            <div role="status" className="notice">
              <span>{message}</span>
              <button onClick={() => setMessage("")}>×</button>
            </div>
          )}
          {busy && <div className="working">正在处理…</div>}
          <footer>
            知序 RAG · 原始证据，而非自动结论<span>REST / MCP · v1.3.0</span>
          </footer>
        </div>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <WorkspaceProvider>
      <Shell />
    </WorkspaceProvider>
  );
}
