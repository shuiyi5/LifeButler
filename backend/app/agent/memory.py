"""
对话记忆管理 — Redis 短期缓存 + PostgreSQL 长期存储
"""
from __future__ import annotations

from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.chat import ChatHistory
import json


class ConversationMemory:
    """对话记忆管理器"""

    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self._cache: Dict[int, List[Dict]] = {}  # user_id -> messages（内存兜底缓存）

    async def get_history(self, user_id: int, db: AsyncSession) -> List[Dict[str, str]]:
        """获取用户的对话历史"""
        # 先检查内存缓存
        if user_id in self._cache:
            return self._cache[user_id][-self.max_history:]

        # 从数据库加载
        result = await db.execute(
            select(ChatHistory)
            .where(ChatHistory.user_id == user_id)
            .order_by(desc(ChatHistory.created_at))
            .limit(self.max_history)
        )
        records = result.scalars().all()
        records.reverse()  # 按时间正序

        messages = [
            {"role": record.role, "content": record.content}
            for record in records
        ]
        self._cache[user_id] = messages
        return messages

    async def add_message(
        self,
        user_id: int,
        role: str,
        content: str,
        db: AsyncSession,
        tool_calls: Optional[str] = None,
    ):
        """添加一条消息到记忆"""
        # 保存到数据库
        record = ChatHistory(
            user_id=user_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
        )
        db.add(record)
        await db.commit()

        # 更新缓存
        if user_id not in self._cache:
            self._cache[user_id] = []
        self._cache[user_id].append({"role": role, "content": content})

        # 限制缓存大小
        if len(self._cache[user_id]) > self.max_history:
            self._cache[user_id] = self._cache[user_id][-self.max_history:]

    def clear_cache(self, user_id: int):
        """清除用户的内存缓存"""
        self._cache.pop(user_id, None)


# 全局单例
_memory: Optional[ConversationMemory] = None


def get_memory() -> ConversationMemory:
    """获取对话记忆管理器单例"""
    global _memory
    if _memory is None:
        _memory = ConversationMemory()
    return _memory
