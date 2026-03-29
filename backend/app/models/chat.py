from __future__ import annotations
"""
聊天记录模型
"""
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.config.database import Base


class ChatHistory(Base):
    """聊天记录表"""
    __tablename__ = "chat_histories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # "user" | "assistant"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tool_calls: Mapped[str] = mapped_column(Text, nullable=True)  # JSON 字符串
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
