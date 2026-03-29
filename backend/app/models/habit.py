from __future__ import annotations
"""
习惯打卡模型
"""
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Text, Integer, Boolean, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.config.database import Base


class Habit(Base):
    """习惯表"""
    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default="")
    frequency: Mapped[str] = mapped_column(String(20), default="daily")  # daily/weekly
    target_count: Mapped[int] = mapped_column(Integer, default=1)
    color: Mapped[str] = mapped_column(String(20), default="#7BB6A4")
    icon: Mapped[str] = mapped_column(String(50), default="star")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class HabitCheckIn(Base):
    """习惯打卡记录表"""
    __tablename__ = "habit_check_ins"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    habit_id: Mapped[int] = mapped_column(Integer, ForeignKey("habits.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    check_in_date: Mapped[date] = mapped_column(Date, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
