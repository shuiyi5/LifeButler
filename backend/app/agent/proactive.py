"""
主动关怀引擎 — 登录时生成今日概览
"""
from __future__ import annotations
from typing import Dict, Any
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.calendar import CalendarEvent
from app.models.todo import Todo
from app.models.finance import Transaction
from app.services.ai_provider import get_ai_provider


async def generate_daily_overview(user_id: int, db: AsyncSession) -> Dict[str, Any]:
    """生成今日概览"""
    today = date.today()
    now = datetime.now()

    # 获取今日日程
    result = await db.execute(
        select(CalendarEvent).where(and_(
            CalendarEvent.user_id == user_id,
            CalendarEvent.start_time >= now,
            CalendarEvent.start_time < datetime(today.year, today.month, today.day, 23, 59, 59),
        )).order_by(CalendarEvent.start_time).limit(5)
    )
    events = result.scalars().all()

    # 获取待办事项
    result = await db.execute(
        select(Todo).where(and_(
            Todo.user_id == user_id,
            Todo.status != "done",
        )).order_by(Todo.priority.desc()).limit(5)
    )
    todos = result.scalars().all()

    # 获取本月支出
    month_start = today.replace(day=1)
    result = await db.execute(
        select(Transaction).where(and_(
            Transaction.user_id == user_id,
            Transaction.date >= month_start,
            Transaction.type == "expense",
        ))
    )
    txns = result.scalars().all()
    total_expense = sum(t.amount for t in txns)

    # 组织数据
    overview = {
        "events": [{"title": e.title, "start_time": e.start_time.strftime("%H:%M")} for e in events],
        "todos": [{"title": t.title, "priority": t.priority} for t in todos],
        "expenses": {"total": total_expense, "count": len(txns)},
    }

    # 生成问候语
    hour = now.hour
    if 6 <= hour < 11:
        greeting = "早上好~今天也要元气满满哦！"
    elif 11 <= hour < 14:
        greeting = "午安~记得好好吃午饭呀"
    elif 14 <= hour < 18:
        greeting = "下午好~今天辛苦了"
    elif 18 <= hour < 22:
        greeting = "晚上好~今天过得怎么样？"
    else:
        greeting = "夜深了,早点休息哦~"

    overview["greeting"] = greeting
    return overview
