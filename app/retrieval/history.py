from app.knowledge.versioning import parse_time


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
            raise ValueError("This generation predates historical lifecycle recording")

        def eligible():
            # Read the authoritative registry, fail closed if it is unavailable.
            owner.workspace.registry.eligible_ids(d.document_id for d in documents)
            purged = owner.workspace.registry.purged_ids()
            return {
                d.document_id
                for d in documents
                if d.document_id not in purged
                and not d.lifecycle_state.get("deleted_at")
                and (
                    not d.lifecycle_state.get("effective_at")
                    or parse_time(d.lifecycle_state["effective_at"]) <= moment
                )
                and (
                    not d.lifecycle_state.get("expires_at")
                    or moment < parse_time(d.lifecycle_state["expires_at"])
                )
            }

        self.pipeline.eligibility = eligible
