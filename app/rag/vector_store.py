import faiss
import numpy as np


class VectorStore:


    def __init__(self, dimension):

        self.index = faiss.IndexFlatL2(
            dimension
        )

        self.documents=[]



    def add(
        self,
        vectors,
        docs
    ):

        self.index.add(
            np.array(vectors)
        )

        self.documents.extend(
            docs
        )


    def search(
        self,
        vector,
        k=3
    ):

        distance, indices = (
            self.index.search(
                np.array([vector]),
                k
            )
        )


        return [
            self.documents[i]
            for i in indices[0]
        ]