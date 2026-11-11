import type { Data } from "../../shared/ui";
export function MultiViewPolicyFields({ current }: { current: Data }) {
  return (
    <label className="check">
      <input
        name="multi_view"
        type="checkbox"
        defaultChecked={current.profile.multi_view_enabled}
      />
      允许调用方明确请求 Multi-View 补检（不自动判断证据不足）
    </label>
  );
}
