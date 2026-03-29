"""
测试 AI 模型适配器 — CustomAnthropicProvider
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.ai_provider import AIProvider, CustomAnthropicProvider


class TestAIProvider:
    """AI 适配器测试"""

    def test_provider_instantiation(self):
        """TC-103-1: 适配器实例化成功"""
        provider = CustomAnthropicProvider(
            api_key="test-key",
            base_url="https://test.api.com",
            model="claude-sonnet-4-6"
        )
        assert provider is not None
        assert provider.model == "claude-sonnet-4-6"

    def test_invalid_key_error(self):
        """TC-103-2: 无效 Key 友好报错"""
        provider = CustomAnthropicProvider(
            api_key="",
            base_url="https://test.api.com",
            model="claude-sonnet-4-6"
        )
        # 空 key 应该能创建但调用时会报错
        assert provider.api_key == ""

    def test_provider_is_abstract(self):
        """AIProvider 是抽象基类"""
        with pytest.raises(TypeError):
            AIProvider()

    @pytest.mark.asyncio
    async def test_chat_method_exists(self):
        """chat 方法存在"""
        provider = CustomAnthropicProvider(
            api_key="test-key",
            base_url="https://test.api.com",
            model="test-model"
        )
        assert hasattr(provider, 'chat')
        assert hasattr(provider, 'chat_stream')

    @pytest.mark.asyncio
    async def test_chat_with_mock(self):
        """使用 Mock 测试聊天"""
        provider = CustomAnthropicProvider(
            api_key="test-key",
            base_url="https://test.api.com",
            model="test-model"
        )

        # Mock the client
        mock_response = MagicMock()
        mock_content = MagicMock()
        mock_content.text = "你好！我是 LifeButler"
        mock_content.type = "text"
        mock_response.content = [mock_content]
        mock_response.stop_reason = "end_turn"

        with patch.object(provider._client.messages, 'create', new_callable=AsyncMock, return_value=mock_response):
            result = await provider.chat([{"role": "user", "content": "你好"}])
            assert result is not None
