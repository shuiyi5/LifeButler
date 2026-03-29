"""
AI 模型适配器 — 支持多种 AI 提供商
当前实现: CustomAnthropicProvider (claude-sonnet-4-6 via 自定义端点)
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
import anthropic
from app.config.settings import settings


class AIProvider(ABC):
    """AI 提供商抽象基类"""

    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """同步对话"""
        pass

    @abstractmethod
    async def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """流式对话"""
        pass

    @abstractmethod
    async def chat_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """带工具调用的对话"""
        pass


class CustomAnthropicProvider(AIProvider):
    """自定义 Anthropic API 适配器"""

    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        model: str = None,
    ):
        self.api_key = api_key or settings.CUSTOM_API_KEY
        self.base_url = base_url or settings.AI_BASE_URL
        self.model = model or settings.AI_MODEL

        self._client = anthropic.AsyncAnthropic(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """同步对话 — 返回完整响应"""
        try:
            response = await self._client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", settings.AI_MAX_TOKENS),
                temperature=kwargs.get("temperature", settings.AI_TEMPERATURE),
                messages=messages,
            )
            # 提取文本内容
            text_parts = [
                block.text for block in response.content
                if hasattr(block, 'text')
            ]
            return "".join(text_parts)
        except anthropic.AuthenticationError:
            return "抱歉，AI 服务认证失败，请检查 API Key 配置 🔑"
        except anthropic.APIConnectionError:
            return "抱歉，AI 服务暂时不可用，请稍后再试 🔄"
        except Exception as e:
            return f"抱歉，发生了意外错误：{str(e)} 😅"

    async def chat_stream(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式对话 — 逐 chunk 返回"""
        try:
            async with self._client.messages.stream(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", settings.AI_MAX_TOKENS),
                temperature=kwargs.get("temperature", settings.AI_TEMPERATURE),
                messages=messages,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except anthropic.AuthenticationError:
            yield "抱歉，AI 服务认证失败，请检查 API Key 配置 🔑"
        except anthropic.APIConnectionError:
            yield "抱歉，AI 服务暂时不可用，请稍后再试 🔄"
        except Exception as e:
            yield f"抱歉，发生了意外错误：{str(e)} 😅"

    async def chat_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        system: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """带工具调用的对话"""
        try:
            params: Dict[str, Any] = {
                "model": self.model,
                "max_tokens": kwargs.get("max_tokens", settings.AI_MAX_TOKENS),
                "temperature": kwargs.get("temperature", settings.AI_TEMPERATURE),
                "messages": messages,
                "tools": tools,
            }
            if system:
                params["system"] = system
            response = await self._client.messages.create(**params)
            return {
                "content": response.content,
                "stop_reason": response.stop_reason,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"AI 调用失败: {str(e)}"}],
                "stop_reason": "error",
                "usage": {"input_tokens": 0, "output_tokens": 0},
            }


# 全局适配器单例
_provider = None

def get_ai_provider() -> CustomAnthropicProvider:
    """获取 AI 适配器单例"""
    global _provider
    if _provider is None:
        _provider = CustomAnthropicProvider()
    return _provider
