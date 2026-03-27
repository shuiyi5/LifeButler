"""
工具基类 — 所有 Agent 工具的抽象基类
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseTool(ABC):
    """所有工具的抽象基类"""

    name: str = ""
    description: str = ""

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """执行工具操作"""
        pass

    def to_langchain_tool(self):
        """转换为 LangChain 工具格式"""
        from langchain_core.tools import StructuredTool
        return StructuredTool.from_function(
            coroutine=self.execute,
            name=self.name,
            description=self.description,
        )
