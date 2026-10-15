class LLMConfigurationError(RuntimeError):
    """LLM 配置缺失或无效。"""


class LLMRequestError(RuntimeError):
    """向 LLM 服务发送请求失败。"""


class LLMResponseError(RuntimeError):
    """LLM 服务返回了不可用的响应。"""