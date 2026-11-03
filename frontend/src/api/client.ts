export async function request(
  token: string,
  path: string,
  options: RequestInit = {},
) {
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
  return r.headers.get("content-type")?.includes("json") ? r.json() : r.blob();
}
