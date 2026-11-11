from app.knowledge.versioning import parse_time
from app.core.exceptions import NotPublished


class HistoricalQuery:
    def __init__(self, owner, snapshot, publication, at):
        self.orchestrator = owner.orchestrator
        self.pipeline = owner.factory.create(
            snapshot, publication["signature"]["model"], owner.workspace.registry
        )
        self.pipeline.generation_id = publication["generation"]
        moment = parse_time(at)
        documents = snapshot.documents
        if any(d.lifecycle_state is None for d in documents):
            raise NotPublished("This generation predates historical lifecycle recording")

        def live(state):
            return not state.get("deleted_at") and (
                not state.get("effective_at")
                or parse_time(state["effective_at"]) <= moment
            )

        states = {d.document_id: d.lifecycle_state for d in documents}

        def eligible():
            # Read the authoritative registry, fail closed if it is unavailable.
            owner.workspace.registry.eligible_ids(d.document_id for d in documents)
            purged = owner.workspace.registry.purged_ids()
            return {
                d.document_id
                for d in documents
                if d.document_id not in purged
                and live(d.lifecycle_state)
                and (
                    not d.lifecycle_state.get("expires_at")
                    or moment < parse_time(d.lifecycle_state["expires_at"])
                )
                # Replacement as recorded in this publication, same rule as live search.
                and not (
                    d.lifecycle_state.get("superseded_by") in states
                    and d.lifecycle_state["superseded_by"] not in purged
                    and live(states[d.lifecycle_state["superseded_by"]])
                )
            }

        self.pipeline.eligibility = eligible
