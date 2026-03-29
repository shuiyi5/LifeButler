"""
面板相关 API 路由 — 今日概览 + 财务/习惯统计
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import date, timedelta
from app.config.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.finance import Transaction
from app.models.habit import Habit, HabitCheckIn
from app.agent.proactive import generate_daily_overview

router = APIRouter()


@router.get("/overview")
async def get_overview(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取今日概览"""
    overview = await generate_daily_overview(user.id, db)
    return overview


@router.get("/finance")
async def get_finance_stats(
    period: str = Query("month", regex="^(week|month)$"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取财务统计"""
    today = date.today()
    start_date = today - timedelta(days=7) if period == "week" else today.replace(day=1)

    result = await db.execute(
        select(Transaction).where(and_(
            Transaction.user_id == user.id,
            Transaction.date >= start_date,
        ))
    )
    txns = result.scalars().all()

    income = sum(t.amount for t in txns if t.type == "income")
    expense = sum(t.amount for t in txns if t.type == "expense")

    categories = {}
    for t in txns:
        if t.type == "expense":
            categories[t.category] = categories.get(t.category, 0) + t.amount

    cat_list = [{"name": k, "amount": v} for k, v in sorted(categories.items(), key=lambda x: -x[1])]

    return {"income": income, "expense": expense, "categories": cat_list[:5]}


@router.get("/habits")
async def get_habit_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取习惯统计"""
    result = await db.execute(select(Habit).where(Habit.user_id == user.id))
    habits = result.scalars().all()

    stats = []
    for h in habits[:3]:
        result = await db.execute(
            select(HabitCheckIn).where(HabitCheckIn.habit_id == h.id).order_by(HabitCheckIn.check_in_date.desc())
        )
        checkins = result.scalars().all()
        streak = 0
        for ci in checkins:
            if (date.today() - ci.check_in_date).days == streak:
                streak += 1
            else:
                break
        stats.append({"id": h.id, "name": h.name, "streak": streak, "total": len(checkins)})

    return {"habits": stats}


@router.get("/habits/{habit_id}/calendar")
async def get_habit_calendar(
    habit_id: int,
    year: int = Query(date.today().year),
    month: int = Query(date.today().month),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取习惯打卡日历"""
    start = date(year, month, 1)
    end = date(year, month + 1, 1) if month < 12 else date(year + 1, 1, 1)

    result = await db.execute(
        select(HabitCheckIn).where(and_(
            HabitCheckIn.habit_id == habit_id,
            HabitCheckIn.check_in_date >= start,
            HabitCheckIn.check_in_date < end,
        ))
    )
    checkins = result.scalars().all()
    days = [ci.check_in_date.day for ci in checkins]

    return {"checked_days": days}
