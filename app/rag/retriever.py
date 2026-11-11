from app.rag.loader import load_documents
from app.rag.chunker import split_text
from app.rag.embedder import embed_texts
from app.rag.vector_store import VectorStore

class KnowledgeRetriever:

    def __init__(
        self,
        build=True
    ):

        self.store=None

        if build:
            self.build_index()


    def build_index(self):

        documents = load_documents()

        chunks = []

        for doc in documents:

            doc_chunks = split_text(
                doc["content"]
            )

            for chunk in doc_chunks:

                chunks.append(
                    {
                        "source": doc["filename"],
                        "content": chunk
                    }
                )


        texts = [
            c["content"]
            for c in chunks
        ]


        vectors = embed_texts(texts)


        dimension = vectors.shape[1]


        self.store = VectorStore(
            dimension
        )


        self.store.add(
            vectors,
            chunks
        )


    def search(
        self,
        query: str,
        k: int = 2
    ):
        if self.store is None:
            self.build_index()

        query_vector = embed_texts(
            [query]
        )


        results = self.store.search(
            query_vector[0],
            k
        )


        return results