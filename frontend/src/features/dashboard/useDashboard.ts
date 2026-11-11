import { useWorkspace } from "../../app/context";
import { useResource } from "../../shared/useResource";
import { short, type Data } from "../../shared/ui";
import { useEffect, useRef, useState } from "react";
import { useKnowledgeBaseDeletion } from "../knowledge-bases/useKnowledgeBaseDeletion";
import { useJobActions } from "../jobs/useJobActions";
export function useDashboard() {
  const workspace = useWorkspace();
  const { kb, admin, current } = workspace;
  const docs = useResource<Data[]>(
    kb && !current?.deleting ? "/knowledge-bases/" + kb + "/documents" : null,
    [],
  );
  const status = useResource<Data>(
    kb && admin && !current?.deleting
      ? "/knowledge-bases/" + kb + "/status"
      : null,
    {},
  );
  return {
    ...workspace,
    docs,
    status,
    job: useJobActions(),
    deleteBase: useKnowledgeBaseDeletion(),
  };
}
