import { useConsoleController } from "./useConsoleController";
import { pages, type Data } from "./shared";
import OverviewPage from "./pages/OverviewPage";
import DocumentsPage from "./pages/DocumentsPage";
import SettingsPage from "./pages/SettingsPage";
import ModelsPage from "./pages/ModelsPage";
import PlaygroundPage from "./pages/PlaygroundPage";
import JobsPage from "./pages/JobsPage";
import AccessPage from "./pages/AccessPage";
export default function App() {
  const context = useConsoleController();
  const {
    act,
    admin,
    api,
    bases,
    busy,
    connected,
    current,
    kb,
    logout,
    message,
    page,
    reload,
    setAdmin,
    setConnected,
    setDetail,
    setKb,
    setMessage,
    setPage,
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
                setDetail(null);
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
            <button onClick={logout}>退出</button>
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
          {!connected ? (
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
          ) : (
            <>
              {page === 0 && <OverviewPage {...context} />}
              {page === 1 && <DocumentsPage {...context} />}
              {page === 2 && current && <SettingsPage {...context} />}
              {page === 3 && <ModelsPage {...context} />}
              {page === 4 && <PlaygroundPage {...context} />}
              {page === 5 && <JobsPage {...context} />}
              {page === 6 && <AccessPage {...context} />}
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
            知序 RAG · 原始证据，而非自动结论<span>REST / MCP · v1.0</span>
          </footer>
        </div>
      </main>
    </div>
  );
}
