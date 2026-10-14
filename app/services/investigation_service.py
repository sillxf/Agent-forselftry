from app.services.risk_analyzer import (
    analyze_alert
)

from app.rag.retriever import (
    KnowledgeRetriever
)

from app.prompts.security_analysis import (
    SECURITY_ANALYSIS_PROMPT
)

from app.llm.client import MockLLM


class InvestigationService:

    def __init__(
        self,
        retriever
    ):

        self.retriever=retriever

        self.llm=MockLLM()




class InvestigationService:

    def __init__(
        self,
        retriever,
        llm
    ):

        self.retriever = retriever

        self.llm = llm

    def investigate(
        self,
        alert
    ):

        risk = analyze_alert(
            alert
        )


        query = self.build_query(
            alert
        )


        knowledge = (
            self.retriever.search(
                query=query,
                k=3
            )
        )

        analysis_context = (
            self.build_analysis_context(
                alert,
                risk,
                knowledge
            )
        )

        analysis = self.llm.generate(
           analysis_context
        )
        
        return {
            "alert": alert,
            "risk": risk,
            "knowledge": knowledge,
            "analysis": analysis
        }



    def build_query(
        self,
        alert
    ):

        return (
            f"{alert.title} "
            f"{alert.description}"
        )



    def generate_context(
        self,
        alert,
        knowledge
    ):

        if len(knowledge)==0:

            return (
                "No related knowledge found"
            )


        return (
            f"Alert {alert.title} "
            "may require investigation "
            "based on related security knowledge."
        )

    def build_analysis_context(
        self,
        alert,
        risk,
        knowledge
    ):

        knowledge_text = "\n".join(
            [
                item["content"]
                for item in knowledge
            ]
        )

        prompt = SECURITY_ANALYSIS_PROMPT.format(
            alert=alert.description,
            risk=risk,
            knowledge=knowledge_text
        )

        return prompt

