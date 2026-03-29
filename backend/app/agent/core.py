"""
LifeButler LangGraph Agent 核心 — ReAct 模式
支持工具调用、流式响应、对话记忆
"""
from __future__ import annotations

import json
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator, Union

from app.services.ai_provider import AIProvider, get_ai_provider
from app.agent.prompts import SYSTEM_PROMPT
from app.tools.base import BaseTool

logger = logging.getLogger(__name__)

# 最大工具调用迭代次数，防止无限循环
MAX_TOOL_ITERATIONS = 5


class LifeButlerAgent:
    """
    LifeButler 智能体
    采用 ReAct 模式：Reason → Act → Observe，循环直到生成最终回复
    """

    def __init__(
        self,
        provider: Optional[AIProvider] = None,
        tools: Optional[List[BaseTool]] = None,
    ):
        # AI 提供商（默认使用全局单例）
        self._provider = provider or get_ai_provider()
        # 已注册的工具 name -> tool
        self._tools: Dict[str, BaseTool] = {}
        # 初始化时批量注册工具
        if tools:
            for tool in tools:
                self.register_tool(tool)

    # ─── 工具管理 ──────────────────────────────────────────────

    def register_tool(self, tool: BaseTool) -> None:
        """注册一个工具到 Agent"""
        self._tools[tool.name] = tool
        logger.info("已注册工具: %s", tool.name)

    def _get_tool_definitions(self) -> List[Dict[str, Any]]:
        """将已注册工具转换为 Anthropic tool-use 格式"""
        definitions: List[Dict[str, Any]] = []
        for tool in self._tools.values():
            # 使用 BaseTool 自带的 schema 信息
            tool_def: Dict[str, Any] = {
                "name": tool.name,
                "description": tool.description,
                "input_schema": getattr(tool, "input_schema", {
                    "type": "object",
                    "properties": {},
                }),
            }
            definitions.append(tool_def)
        return definitions

    # ─── 消息构建 ──────────────────────────────────────────────

    @staticmethod
    def _build_messages(
        user_message: str,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        构建发送给 AI 的消息列表
        history 格式: [{"role": "user"/"assistant", "content": "..."}]
        """
        messages: List[Dict[str, Any]] = []
        # 加入历史对话
        if history:
            for msg in history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"],
                })
        # 加入当前用户消息
        messages.append({"role": "user", "content": user_message})
        return messages

    # ─── 工具执行 ──────────────────────────────────────────────

    async def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any], user_id: int = None, db = None) -> str:
        """执行指定工具并返回结果字符串"""
        tool = self._tools.get(tool_name)
        if tool is None:
            return json.dumps({"error": f"未找到工具: {tool_name}"}, ensure_ascii=False)
        try:
            # 传递db和user_id给需要的工具
            result = await tool.execute(**tool_input, user_id=user_id, db=db)
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as exc:
            logger.exception("工具 %s 执行失败", tool_name)
            return json.dumps(
                {"error": f"工具执行失败: {str(exc)}"},
                ensure_ascii=False,
            )

    # ─── 核心调用（同步返回完整回复） ──────────────────────────

    async def invoke(
        self,
        user_message: str,
        user_id: int,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        处理用户消息并返回完整回复
        实现 ReAct 循环：调用 AI → 如果需要工具则执行 → 将结果送回 AI → 重复
        """
        messages = self._build_messages(user_message, history)
        tool_defs = self._get_tool_definitions()

        for iteration in range(MAX_TOOL_ITERATIONS):
            # 调用 AI（带工具定义或不带）
            if tool_defs:
                response = await self._provider.chat_with_tools(
                    messages=messages,
                    tools=tool_defs,
                    system=SYSTEM_PROMPT,
                )
            else:
                # 没有注册工具时走普通对话
                full_messages = [{"role": "user", "content": SYSTEM_PROMPT + "\n\n请根据以上设定回复用户。"}] + messages[1:] if not history else messages
                # 在没有工具时把 system prompt 放到首条消息
                sys_messages = [{"role": "user", "content": SYSTEM_PROMPT}]
                sys_messages.append({"role": "assistant", "content": "好的，我会按照 LifeButler 的设定来回复。"})
                sys_messages.extend(messages)
                text = await self._provider.chat(messages=sys_messages)
                return text

            # 检查是否出错
            if response.get("stop_reason") == "error":
                content_blocks = response.get("content", [])
                if content_blocks:
                    block = content_blocks[0]
                    if isinstance(block, dict):
                        return block.get("text", "抱歉，发生了错误 😅")
                    elif hasattr(block, "text"):
                        return block.text
                return "抱歉，AI 服务暂时不可用 🔄"

            # 解析响应内容
            content_blocks = response.get("content", [])
            stop_reason = response.get("stop_reason", "end_turn")

            # 提取文本和工具调用
            text_parts: List[str] = []
            tool_use_blocks: List[Any] = []

            for block in content_blocks:
                if isinstance(block, dict):
                    if block.get("type") == "text":
                        text_parts.append(block["text"])
                    elif block.get("type") == "tool_use":
                        tool_use_blocks.append(block)
                else:
                    # Anthropic SDK 返回的对象
                    if hasattr(block, "type"):
                        if block.type == "text":
                            text_parts.append(block.text)
                        elif block.type == "tool_use":
                            tool_use_blocks.append(block)

            # 如果没有工具调用，返回文本
            if not tool_use_blocks:
                return "".join(text_parts) or "我在呢，请问有什么需要帮忙的吗？😊"

            # 有工具调用 → 执行工具 → 组装 tool_result → 继续循环
            # 先把 assistant 的完整回复加到 messages
            assistant_content: List[Dict[str, Any]] = []
            for block in content_blocks:
                if isinstance(block, dict):
                    assistant_content.append(block)
                else:
                    # 将 SDK 对象转为 dict
                    if hasattr(block, "type"):
                        if block.type == "text":
                            assistant_content.append({"type": "text", "text": block.text})
                        elif block.type == "tool_use":
                            assistant_content.append({
                                "type": "tool_use",
                                "id": block.id,
                                "name": block.name,
                                "input": block.input,
                            })

            messages.append({"role": "assistant", "content": assistant_content})

            # 执行每个工具并收集结果
            tool_results: List[Dict[str, Any]] = []
            for tool_block in tool_use_blocks:
                if isinstance(tool_block, dict):
                    t_id = tool_block["id"]
                    t_name = tool_block["name"]
                    t_input = tool_block.get("input", {})
                else:
                    t_id = tool_block.id
                    t_name = tool_block.name
                    t_input = tool_block.input

                logger.info("执行工具: %s, 参数: %s", t_name, t_input)
                result_str = await self._execute_tool(t_name, t_input)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": t_id,
                    "content": result_str,
                })

            # 把工具结果加到 messages
            messages.append({"role": "user", "content": tool_results})

        # 超过最大迭代次数
        return "抱歉，处理过程有些复杂，请换个方式描述你的需求~ 😊"

    # ─── 流式调用（逐 chunk 返回） ─────────────────────────────

    async def stream(
        self,
        user_message: str,
        user_id: int,
        history: Optional[List[Dict[str, str]]] = None,
        db = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式处理用户消息，返回包含类型的事件
        yield {"type": "thinking"} - AI正在思考
        yield {"type": "tool_call", "tool": "...", "input": {...}}
        yield {"type": "tool_result", "tool": "...", "result": "..."}
        yield {"type": "text", "content": "..."}
        """
        messages = self._build_messages(user_message, history)
        tool_defs = self._get_tool_definitions()

        if not tool_defs:
            yield {"type": "thinking"}
            sys_messages = [{"role": "user", "content": SYSTEM_PROMPT}]
            sys_messages.append({"role": "assistant", "content": "好的，我会按照 LifeButler 的设定来回复。"})
            sys_messages.extend(messages)
            async for chunk in self._provider.chat_stream(messages=sys_messages):
                yield {"type": "text", "content": chunk}
            return

        # 执行ReAct循环并发送事件
        for iteration in range(MAX_TOOL_ITERATIONS):
            yield {"type": "thinking"}
            response = await self._provider.chat_with_tools(
                messages=messages,
                tools=tool_defs,
                system=SYSTEM_PROMPT,
            )

            content_blocks = response.get("content", [])
            tool_use_blocks = []
            text_parts = []

            for block in content_blocks:
                if isinstance(block, dict):
                    if block.get("type") == "text":
                        text_parts.append(block["text"])
                    elif block.get("type") == "tool_use":
                        tool_use_blocks.append(block)
                else:
                    if hasattr(block, "type"):
                        if block.type == "text":
                            text_parts.append(block.text)
                        elif block.type == "tool_use":
                            tool_use_blocks.append(block)

            if not tool_use_blocks:
                # 没有工具调用，流式返回文本
                full_text = "".join(text_parts)
                for i, char in enumerate(full_text):
                    yield {"type": "text", "content": char}
                return

            # 有工具调用，发送工具调用事件
            assistant_content = []
            for block in content_blocks:
                if isinstance(block, dict):
                    assistant_content.append(block)
                else:
                    if hasattr(block, "type"):
                        if block.type == "text":
                            assistant_content.append({"type": "text", "text": block.text})
                        elif block.type == "tool_use":
                            assistant_content.append({
                                "type": "tool_use",
                                "id": block.id,
                                "name": block.name,
                                "input": block.input,
                            })

            messages.append({"role": "assistant", "content": assistant_content})

            # 执行工具并发送事件
            tool_results = []
            for tool_block in tool_use_blocks:
                if isinstance(tool_block, dict):
                    t_id = tool_block["id"]
                    t_name = tool_block["name"]
                    t_input = tool_block.get("input", {})
                else:
                    t_id = tool_block.id
                    t_name = tool_block.name
                    t_input = tool_block.input

                yield {"type": "tool_call", "tool": t_name, "input": t_input}
                result_str = await self._execute_tool(t_name, t_input, user_id=user_id, db=db)
                yield {"type": "tool_result", "tool": t_name, "result": result_str}

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": t_id,
                    "content": result_str,
                })

            messages.append({"role": "user", "content": tool_results})

        # 超时返回
        msg = "抱歉，处理过程有些复杂，请换个方式描述你的需求~ 😊"
        for char in msg:
            yield {"type": "text", "content": char}


# ─── 全局 Agent 单例 ──────────────────────────────────────────

_agent: Optional[LifeButlerAgent] = None


def get_agent() -> LifeButlerAgent:
    """获取 LifeButler Agent 全局单例"""
    global _agent
    if _agent is None:
        _agent = LifeButlerAgent()
    return _agent
