from openai import OpenAI, OpenAIError

from app.llm.error import (
    LLMConfigurationError,
    LLMRequestError,
    LLMResponseError,
)


class LLMClient:
    def __init__(
        self,
        api_key,
        base_url,
        model,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self._client = None

    def _get_client(self):
        if not self.api_key:
            raise LLMConfigurationError(
                "LLM_API_KEY is not configured."
            )

        if not self.base_url:
            raise LLMConfigurationError(
                "LLM_BASE_URL is not configured."
            )

        if not self.model:
            raise LLMConfigurationError(
                "LLM_MODEL is not configured."
            )

        if self._client is None:
            try:
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
                )
            except OpenAIError as exc:
                raise LLMConfigurationError(
                    "LLM client configuration is invalid."
                ) from exc

        return self._client

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> dict:

        request = {
            "model": self.model,
            "messages": messages,
        }

        if tools is not None:
            request["tools"] = tools
            request["tool_choice"] = "auto"

        try:
            response = (
                self._get_client()
                .chat.completions.create(**request)
            )
        except OpenAIError as exc:
            raise LLMRequestError(
                "The LLM API request failed."
            ) from exc

        if not response.choices:
            raise LLMResponseError(
                "The LLM response contains no choices."
            )

        message = response.choices[0].message

        tool_calls = []

        for call in message.tool_calls or []:
            tool_calls.append(
                {
                    "id": call.id,
                    "name": call.function.name,
                    "arguments": call.function.arguments,
                }
            )

        content = message.content

        if not tool_calls and (
            not isinstance(content, str)
            or not content.strip()
        ):
            raise LLMResponseError(
                "The LLM returned no usable content."
            )

        return {
            "content": content,
            "tool_calls": tool_calls,
            "assistant_message": (
                message.model_dump(exclude_none=True)
            ),
        }

    def generate(
        self,
        prompt: str,
    ) -> str:

        response = self.chat(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        )

        return response["content"]