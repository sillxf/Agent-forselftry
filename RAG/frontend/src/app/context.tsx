import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { request } from "../api/client";
import type { Data } from "../shared/ui";
function useWorkspaceState() {
  const [token, setToken] = useState("");
  const [connected, setConnected] = useState(false),
    [admin, setAdmin] = useState(false);
  const [bases, setBases] = useState<Data[]>([]),
    [kb, setKb] = useState("");
  const [busy, setBusy] = useState(false),
    [message, setMessage] = useState("");
  const [connecting, setConnecting] = useState(true);
  const [localConsole, setLocalConsole] = useState(false);
  const connectLocal = useCallback(async () => {
    const response = await fetch("/api/v1/console/session", {
      method: "POST",
      headers: { "X-Console-Request": "1" },
    });
    if (response.status === 404) return false;
    if (!response.ok)
      throw new Error("本地工作台连接失败，请用“启动.cmd”重新打开服务。");
    setLocalConsole(true);
    setAdmin(true);
    setConnected(true);
    return true;
  }, []);
  useEffect(() => {
    void connectLocal()
      .catch((error) => setMessage(String(error)))
      .finally(() => setConnecting(false));
  }, [connectLocal]);
  const [revision, setRevision] = useState(0);
  const selected = useRef(kb),
    latest = useRef(0);
  selected.current = kb;
  const api = useCallback(
    (path: string, options: RequestInit = {}) => request(token, path, options),
    [token],
  );
  const act = useCallback(async (fn: () => Promise<void>) => {
    setBusy(true);
    setMessage("");
    try {
      await fn();
    } catch (error) {
      setMessage(
        "操作未完成：" + (error instanceof Error ? error.message : String(error)),
      );
    } finally {
      setBusy(false);
    }
  }, []);
  const reload = useCallback(
    async (id = selected.current) => {
      const epoch = ++latest.current;
      const rows: Data[] = await api("/knowledge-bases");
      if (epoch !== latest.current) return;
      setBases(rows);
      setKb(rows.some((row) => row.id === id) ? id : rows[0]?.id || "");
      setRevision((value) => value + 1);
    },
    [api],
  );
  useEffect(() => {
    if (connected) void act(() => reload());
  }, [connected, api, act, reload]);
  async function logout() {
    if (localConsole) {
      try {
        await request("", "/console/session", { method: "DELETE" });
      } catch (error) {
        setMessage("退出失败：" + String(error));
        return;
      }
    }
    latest.current++;
    setConnected(false);
    setAdmin(false);
    setToken("");
    setBases([]);
    setKb("");
    setMessage("");
  }
  return {
    token,
    setToken,
    connecting,
    localConsole,
    connectLocal,
    connected,
    setConnected,
    admin,
    setAdmin,
    bases,
    kb,
    setKb,
    current: bases.find((row) => row.id === kb),
    busy,
    message,
    setMessage,
    api,
    act,
    reload,
    revision,
    logout,
  };
}
type WorkspaceState = ReturnType<typeof useWorkspaceState>;
const WorkspaceContext = createContext<WorkspaceState | null>(null);
export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const state = useWorkspaceState();
  return (
    <WorkspaceContext.Provider value={state}>
      {children}
    </WorkspaceContext.Provider>
  );
}
export function useWorkspace() {
  const state = useContext(WorkspaceContext);
  if (!state) throw Error("WorkspaceProvider is required");
  return state;
}
