from app.rag.retriever import KnowledgeRetriever

def test_knowledge_search():

    retriever = KnowledgeRetriever(
        build=True
    )

    results = retriever.search(
        "failed login attempts",
        k=3
    )


    sources = [
        item["source"]
        for item in results
    ]


    assert len(sources) > 0

    assert any(
        source.endswith(".md")
        for source in sources
    )