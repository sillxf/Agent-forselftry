import { useWorkspace } from "../../app/context";
import { useResource } from "../../shared/useResource";
import { short, type Data } from "../../shared/ui";
import { useEffect, useRef, useState } from "react";
export function useAccess() {
  const workspace = useWorkspace();
  const keys = useResource<Data[]>(workspace.admin ? "/keys" : null, []),
    audit = useResource<Data[]>(workspace.admin ? "/audit" : null, []);
  const [newKey, setNewKey] = useState("");
  return { ...workspace, keys, audit, newKey, setNewKey };
}
