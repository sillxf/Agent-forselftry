from app.services.output_parser import parse_analysis
from app.services.risk_analyzer import (
    analyze_alert
)
from app.prompts.security_analysis import (
    SECURITY_ANALYSIS_PROMPT
)
from app.rag.retriever import (
    KnowledgeRetriever
)

from app.prompts.security_analysis import (
    SECURITY_ANALYSIS_PROMPT
)


class InvestigationService:

    def __init__(
        self,
        retriever,
        llm
    ):

        self.retriever = retriever

        self.llm = llm

    def build_analysis_context(
        self,
        alert,
        risk,
        knowledge
    ):

        knowledge_text = "\n\n".join(
            [
                item["content"]
                for item in knowledge
            ]
        )


        return SECURITY_ANALYSIS_PROMPT.format(
            alert=alert.description,
            risk=risk,
            knowledge=knowledge_text
        )
    
    def investigate(self, alert):


        risk = analyze_alert(alert)


        knowledge = self.retriever.search(
            query=self.build_query(alert),
            k=2
        )


        llm_context = self.build_analysis_context(
            alert,
            risk,
            knowledge
        )


        raw_analysis = self.llm.generate(
            llm_context
        )

        try:
            analysis=parse_analysis(
                raw_analysis
            )   

        except Exception:

            analysis={
                "error":
                "LLM response invalid"
            }


        return {

            "alert":alert,

            "risk":risk,

            "knowledge":knowledge,

            "analysis":analysis
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

