export type Data = Record<string, any>;
export const pages = [
  "知识总览",
  "文档与内容",
  "构建与检索配置",
  "模型管理",
  "检索调试台",
  "任务与发布",
  "访问与审计",
];
export const short = (v: any) => String(v || "—").slice(0, 12);
export const stamp = (v: any) =>
  v
    ? (typeof v === "number" ? new Date(v * 1000) : new Date(v)).toLocaleString(
        "zh-CN",
      )
    : "—";
export const Json = ({ value }: { value: any }) => (
  <pre>{JSON.stringify(value, null, 2)}</pre>
);
