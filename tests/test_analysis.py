from app.schemas.analysis import SecurityAnalysis
from app.services.investigation_service import InvestigationService
from app.rag.retriever import KnowledgeRetriever
from app.llm.client import MockLLM
from app.main import load_alerts


def test_investigation():

    # 1. 创建RAG检索器
    retriever = KnowledgeRetriever()


    # 2. 创建LLM
    llm = MockLLM()


    # 3. 注入依赖
    service = InvestigationService(
        retriever=retriever,
        llm=llm
    )


    # 4. 获取测试告警
    alerts = load_alerts()

    alert = alerts[0]


    # 5. 执行调查
    result = service.investigate(
        alert
    )


    # 6. 验证结果
    assert result["knowledge"]

    analysis = result["analysis"]

    assert isinstance(analysis, SecurityAnalysis)
    assert analysis.attack_type == "mock_analysis"
    assert analysis.confidence == 0.0
