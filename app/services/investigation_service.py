from app.services.output_parser import parse_analysis
from app.services.risk_analyzer import (
    analyze_alert
)
from app.prompts.security_analysis import (
    SECURITY_ANALYSIS_PROMPT
)
import json

from pydantic import ValidationError

from app.services.output_parser import parse_analysis

from app.tools.alert_tools import (
    ALERT_TOOL_DEFINITIONS,
    execute_alert_tool,
    ToolExecutionError,
)


from app.tools.knowledge_tools import knowledge_tool_definition, execute_knowledge_tool


class ToolCallLimitError(RuntimeError):
    """The model exceeded the allowed tool-call rounds."""

class InvestigationService:

    MAX_TOOL_ROUNDS = 3
    MAX_KNOWLEDGE_SEARCHES = 3
    MAX_TOTAL_TOOL_CALLS = 12
    MAX_EVIDENCE_CHARS = 24000

    def __init__(
        self,
        retriever,
        llm
    ):

        self.retriever = retriever

        self.llm = llm

    
    def investigate(
        self,
        alert,
        alert_pool=None,
    ):
        alerts = (
            [alert]
            if alert_pool is None
            else alert_pool
        )

        risk = analyze_alert(alert)

        knowledge = self.retriever.search(
            query=self.build_query(alert),
            k=2,
        )

        bounded, used = [], 0
        for item in knowledge:
            if used + len(item["content"]) <= self.MAX_EVIDENCE_CHARS:
                bounded.append(item)
                used += len(item["content"])
        knowledge = bounded
        llm_context = self.build_analysis_context(
            alert,
            risk,
            knowledge,
        )

        analysis = self._run_tool_loop(
            prompt=llm_context,
            alerts=alerts,
            knowledge=knowledge,
        )

        return {
            "alert": alert,
            "risk": risk,
            "knowledge": knowledge,
            "analysis": analysis,
        }

    def _run_tool_loop(
        self,
        prompt: str,
        alerts: list,
        knowledge: list,
    ):
        messages = [
            {
                "role": "user",
                "content": prompt,
            }
        ]

        tools = [*ALERT_TOOL_DEFINITIONS, knowledge_tool_definition()]

        knowledge_searches = 1  # Includes the initial investigate() retrieval.
        tool_count = 0
        evidence_chars = sum(len(item["content"]) for item in knowledge)
        for round_index in range(
            self.MAX_TOOL_ROUNDS + 1
        ):
            response = self.llm.chat(
                messages=messages,
                tools=tools,
            )

            tool_calls = response["tool_calls"]

            if not tool_calls:
                return parse_analysis(
                    response["content"]
                )

            if round_index == self.MAX_TOOL_ROUNDS:
                raise ToolCallLimitError(
                    "Maximum tool-call rounds exceeded."
                )

            messages.append(
                response["assistant_message"]
            )

            for tool_call in tool_calls:
                tool_count += 1
                if tool_count > self.MAX_TOTAL_TOOL_CALLS:
                    raise ToolCallLimitError("Total tool-call budget exceeded")
                tool_call_id = tool_call["id"]

                try:
                    arguments = json.loads(
                        tool_call["arguments"]
                    )

                    if tool_call["name"] == "knowledge_search":
                        if knowledge_searches >= self.MAX_KNOWLEDGE_SEARCHES:
                            raise ToolExecutionError("Knowledge search budget exhausted")
                        knowledge_searches += 1
                        result = execute_knowledge_tool(arguments, self.retriever)
                        bounded = []
                        for item in result["results"]:
                            if evidence_chars + len(item["content"]) <= self.MAX_EVIDENCE_CHARS:
                                bounded.append(item)
                                evidence_chars += len(item["content"])
                        result["context_budget_exhausted"] = len(bounded) != len(result["results"])
                        result["results"] = bounded
                        seen = {item["parent_id"] for item in knowledge}
                        knowledge.extend(item for item in result["results"] if item["parent_id"] not in seen)
                    else:
                        result = execute_alert_tool(
                            tool_name=tool_call["name"], arguments=arguments, alerts=alerts,
                        )

                    tool_output = {
                        "ok": True,
                        "result": result,
                    }

                except (
                    json.JSONDecodeError,
                    TypeError,
                ):
                    tool_output = {
                        "ok": False,
                        "error": (
                            "Tool arguments are not valid JSON."
                        ),
                    }

                except ValidationError as exc:
                    tool_output = {
                        "ok": False,
                        "error": (
                            "Tool arguments failed validation."
                        ),
                        "details": exc.errors(),
                    }

                except ToolExecutionError as exc:
                    tool_output = {
                        "ok": False,
                        "error": str(exc),
                    }

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": json.dumps(
                            tool_output,
                            ensure_ascii=False,
                        ),
                    }
                )

        raise ToolCallLimitError(
            "Maximum tool-call rounds exceeded."
        )

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

        # Preserve evidence identities without copying duplicate retrieval-only fields.
        knowledge_text = json.dumps(
            [
                {key: item[key] for key in (
                    "source", "document_id", "version_id", "artifact_id", "parent_id", "chunk_id",
                    "page_start", "page_end", "content",
                ) if key in item}
                for item in knowledge
            ],
            ensure_ascii=False,
        )

        prompt = SECURITY_ANALYSIS_PROMPT.format(
            alert=alert.description,
            risk=risk,
            knowledge=knowledge_text
        )

        return prompt

