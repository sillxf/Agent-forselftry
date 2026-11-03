import { useWorkspace } from "../../app/context";
import { useResource } from "../../shared/useResource";
import { short, type Data } from "../../shared/ui";
import { useEffect, useRef, useState } from "react";
import { useJobActions } from "../jobs/useJobActions";
export function useDashboard() {
  const workspace = useWorkspace();
  const { kb, admin } = workspace;
  const docs = useResource<Data[]>(
    kb ? "/knowledge-bases/" + kb + "/documents" : null,
    [],
  );
  const status = useResource<Data>(
    kb && admin ? "/knowledge-bases/" + kb + "/status" : null,
    {},
  );
  return { ...workspace, docs, status, job: useJobActions() };
}
