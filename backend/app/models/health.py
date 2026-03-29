from __future__ import annotations
"""
饮食健康模型
"""
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.config.database import Base


class MealRecord(Base):
    """饮食记录表"""
    __tablename__ = "meal_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    meal_type: Mapped[str] = mapped_column(String(20), nullable=False)  # breakfast/lunch/dinner/snack
    food_items: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON 字符串
    calories_estimate: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0)
    water_ml: Mapped[int] = mapped_column(Integer, default=0)  # 饮水量(毫升)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default="")
    date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
