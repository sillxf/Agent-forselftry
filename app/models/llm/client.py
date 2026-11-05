from openai import OpenAI, OpenAIError

from app.models.llm.error import (
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
        *,
        timeout=None,
        max_retries=None,
        max_completion_tokens=None,
    ):
        # .env files saved on Windows can leave "\r" on values, which made the base
        # URL invalid. Surrounding whitespace is never meaningful in these settings.
        self.api_key = api_key.strip() if isinstance(api_key, str) else api_key
        self.base_url = base_url.strip() if isinstance(base_url, str) else base_url
        self.model = model.strip() if isinstance(model, str) else model
        self._client = None
        self.request_options = {}
        if max_completion_tokens is not None:
            if max_completion_tokens <= 0:
                raise ValueError("max_completion_tokens must be positive")
            self.request_options["max_completion_tokens"] = max_completion_tokens
        self.client_options = {}
        if timeout is not None:
            if timeout <= 0:
                raise ValueError("timeout must be positive")
            self.client_options["timeout"] = timeout
        if max_retries is not None:
            if max_retries < 0:
                raise ValueError("max_retries must be nonnegative")
            self.client_options["max_retries"] = max_retries

    def _get_client(self):
        if not self.api_key:
            raise LLMConfigurationError("LLM_API_KEY is not configured.")

        if not self.base_url:
            raise LLMConfigurationError("LLM_BASE_URL is not configured.")

        if not self.model:
            raise LLMConfigurationError("LLM_MODEL is not configured.")

        if self._client is None:
            try:
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
                    **self.client_options,
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
            **self.request_options,
        }

        if tools is not None:
            request["tools"] = tools
            request["tool_choice"] = "auto"

        try:
            response = self._get_client().chat.completions.create(**request)
        except OpenAIError as exc:
            raise LLMRequestError("The LLM API request failed.") from exc

        if not response.choices:
            raise LLMResponseError("The LLM response contains no choices.")

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

        if not tool_calls and (not isinstance(content, str) or not content.strip()):
            raise LLMResponseError("The LLM returned no usable content.")

        usage = getattr(response, "usage", None)
        return {
            "usage": usage.model_dump(mode="json") if usage is not None else None,
            "content": content,
            "tool_calls": tool_calls,
            "assistant_message": (message.model_dump(exclude_none=True)),
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
