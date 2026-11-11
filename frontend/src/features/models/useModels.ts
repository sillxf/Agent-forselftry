import { useWorkspace } from "../../app/context";
import { useResource } from "../../shared/useResource";
import { short, type Data } from "../../shared/ui";
import { useEffect, useRef, useState } from "react";
export function useModels() {
  const workspace = useWorkspace();
  const models = useResource<Data[]>(workspace.admin ? "/models" : null, []);
  return { ...workspace, models };
}
