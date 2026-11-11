import { useWorkspace } from "../../app/context";
import { useResource } from "../../shared/useResource";
import { short, type Data } from "../../shared/ui";
import { useEffect, useRef, useState } from "react";
import { useJobActions } from "./useJobActions";
export function useJobs() {
  const workspace = useWorkspace();
  const { admin, kb } = workspace;
  const jobs = useResource<Data[]>(admin ? "/jobs" : null, [], 3000);
  const history = useResource<Data>(
    admin && kb ? "/knowledge-bases/" + kb + "/generations" : null,
    {},
    3000,
  );
  return { ...workspace, jobs, history, job: useJobActions() };
}
