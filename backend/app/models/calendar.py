from __future__ import annotations
"""
日程事件模型
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.config.database import Base


class CalendarEvent(Base):
    """日程事件表"""
    __tablename__ = "calendar_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default="")
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, default="")
    is_all_day: Mapped[bool] = mapped_column(Boolean, default=False)
    repeat_type: Mapped[str] = mapped_column(String(20), default="none")  # none/daily/weekly/monthly
    remind_before: Mapped[int] = mapped_column(Integer, default=15)  # 提前提醒分钟数
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
