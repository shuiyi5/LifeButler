from __future__ import annotations
"""
财务交易模型
"""
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.config.database import Base


class Transaction(Base):
    """财务交易表"""
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # income/expense
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="其他")
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, default="")
    encrypted_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # AES-256 加密的敏感备注
    date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
