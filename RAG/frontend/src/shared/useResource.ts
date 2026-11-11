import { useEffect, useRef, useState } from "react";
import { useWorkspace } from "../app/context";
/** Transport helper only. Each mounted feature owns its own returned state. */
export function useResource<T>(
  path: string | null,
  initial: T,
  pollMilliseconds = 0,
): T {
  const { api, connected, revision, setMessage } = useWorkspace();
  const initialValue = useRef(initial),
    [data, setData] = useState<T>(initial);
  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();
    setData(initialValue.current);
    if (!path || !connected) return () => controller.abort();
    async function load() {
      try {
        const value = await api(path!, { signal: controller.signal });
        if (!cancelled) setData(value);
      } catch (error) {
        if (!cancelled && !controller.signal.aborted)
          setMessage("读取失败：" + String(error));
      }
    }
    void load();
    const timer = pollMilliseconds
      ? window.setInterval(() => void load(), pollMilliseconds)
      : undefined;
    return () => {
      cancelled = true;
      controller.abort();
      if (timer !== undefined) window.clearInterval(timer);
    };
  }, [path, api, connected, revision, pollMilliseconds, setMessage]);
  return data;
}
