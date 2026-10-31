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


class ToolCallLimitError(RuntimeError):
    """The model exceeded the allowed tool-call rounds."""

class InvestigationService:

    MAX_TOOL_ROUNDS = 3    

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

        llm_context = self.build_analysis_context(
            alert,
            risk,
            knowledge,
        )

        analysis = self._run_tool_loop(
            prompt=llm_context,
            alerts=alerts,
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
    ):
        messages = [
            {
                "role": "user",
                "content": prompt,
            }
        ]

        for round_index in range(
            self.MAX_TOOL_ROUNDS + 1
        ):
            response = self.llm.chat(
                messages=messages,
                tools=ALERT_TOOL_DEFINITIONS,
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
                tool_call_id = tool_call["id"]

                try:
                    arguments = json.loads(
                        tool_call["arguments"]
                    )

                    result = execute_alert_tool(
                        tool_name=tool_call["name"],
                        arguments=arguments,
                        alerts=alerts,
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
                    "source", "document_id", "parent_id", "chunk_id",
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

