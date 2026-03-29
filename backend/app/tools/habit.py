"""
习惯打卡工具 — 创建习惯 + 打卡 + 连续天数统计
"""
from __future__ import annotations
from typing import Any, Dict
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func as sa_func
from app.tools.base import BaseTool
from app.models.habit import Habit, HabitCheckIn


class HabitTool(BaseTool):
    """习惯打卡工具"""
    name = "habit_tool"
    description = "习惯打卡 — 创建习惯、打卡、查看连续天数和完成率"
    input_schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["create", "check_in", "list", "stats"], "description": "操作类型"},
            "name": {"type": "string", "description": "习惯名称"},
            "description": {"type": "string", "description": "习惯描述"},
            "habit_id": {"type": "integer", "description": "习惯ID"},
            "note": {"type": "string", "description": "打卡备注"},
        },
        "required": ["action"],
    }

    async def execute(self, db: AsyncSession = None, user_id: int = None, **kwargs) -> Dict[str, Any]:
        action = kwargs.get("action", "list")
        if action == "create":
            return await self._create(db, user_id, **kwargs)
        elif action == "check_in":
            return await self._check_in(db, user_id, **kwargs)
        elif action == "list":
            return await self._list(db, user_id, **kwargs)
        elif action == "stats":
            return await self._stats(db, user_id, **kwargs)
        return {"success": False, "message": f"未知操作: {action}"}

    async def _create(self, db: AsyncSession, user_id: int, **kwargs) -> Dict[str, Any]:
        habit = Habit(
            user_id=user_id, name=kwargs.get("name", "新习惯"),
            description=kwargs.get("description", ""),
            frequency=kwargs.get("frequency", "daily"),
        )
        db.add(habit)
        await db.flush()
        return {"success": True, "message": f"🌟 习惯「{habit.name}」已创建！加油坚持哦~", "habit_id": habit.id}

    async def _check_in(self, db: AsyncSession, user_id: int, **kwargs) -> Dict[str, Any]:
        habit_id = kwargs.get("habit_id")
        if not habit_id:
            # 尝试按名称查找
            name = kwargs.get("name", "")
            if name:
                result = await db.execute(select(Habit).where(and_(Habit.user_id == user_id, Habit.name == name, Habit.is_active == True)))
                habit = result.scalar_one_or_none()
                if habit:
                    habit_id = habit.id
            if not habit_id:
                return {"success": False, "message": "请提供习惯ID或名称"}
        # 检查今天是否已打卡
        today = date.today()
        result = await db.execute(select(HabitCheckIn).where(and_(
            HabitCheckIn.habit_id == habit_id, HabitCheckIn.user_id == user_id, HabitCheckIn.check_in_date == today,
        )))
        existing = result.scalar_one_or_none()
        if existing:
            return {"success": False, "message": "今天已经打过卡啦~ 明天继续加油 💪"}
        check_in = HabitCheckIn(habit_id=habit_id, user_id=user_id, check_in_date=today, note=kwargs.get("note", ""))
        db.add(check_in)
        await db.flush()
        # 计算连续天数
        streak = await self._get_streak(db, habit_id, user_id)
        result = await db.execute(select(Habit).where(Habit.id == habit_id))
        habit = result.scalar_one_or_none()
        name = habit.name if habit else "习惯"
        return {"success": True, "message": f"✅ 「{name}」打卡成功！\n🔥 已连续 {streak} 天，继续保持~", "streak": streak}

    async def _get_streak(self, db: AsyncSession, habit_id: int, user_id: int) -> int:
        """计算连续打卡天数"""
        today = date.today()
        streak = 0
        check_date = today
        while True:
            result = await db.execute(select(HabitCheckIn).where(and_(
                HabitCheckIn.habit_id == habit_id, HabitCheckIn.user_id == user_id, HabitCheckIn.check_in_date == check_date,
            )))
            if result.scalar_one_or_none():
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break
        return streak

    async def _list(self, db: AsyncSession, user_id: int, **kwargs) -> Dict[str, Any]:
        result = await db.execute(select(Habit).where(and_(Habit.user_id == user_id, Habit.is_active == True)))
        habits = result.scalars().all()
        today = date.today()
        habit_list = []
        for h in habits:
            check_result = await db.execute(select(HabitCheckIn).where(and_(
                HabitCheckIn.habit_id == h.id, HabitCheckIn.check_in_date == today,
            )))
            checked = check_result.scalar_one_or_none() is not None
            streak = await self._get_streak(db, h.id, user_id) if checked else 0
            habit_list.append({"id": h.id, "name": h.name, "checked_today": checked, "streak": streak})
        return {"success": True, "habits": habit_list, "count": len(habits)}

    async def _stats(self, db: AsyncSession, user_id: int, **kwargs) -> Dict[str, Any]:
        habit_id = kwargs.get("habit_id")
        if not habit_id:
            return await self._list(db, user_id, **kwargs)
        result = await db.execute(select(Habit).where(and_(Habit.id == habit_id, Habit.user_id == user_id)))
        habit = result.scalar_one_or_none()
        if not habit:
            return {"success": False, "message": "习惯不存在"}
        # 统计最近30天
        thirty_days_ago = date.today() - timedelta(days=30)
        result = await db.execute(select(HabitCheckIn).where(and_(
            HabitCheckIn.habit_id == habit_id, HabitCheckIn.check_in_date >= thirty_days_ago,
        )))
        check_ins = result.scalars().all()
        rate = len(check_ins) / 30 * 100
        streak = await self._get_streak(db, habit_id, user_id)
        return {
            "success": True,
            "message": f"📊 「{habit.name}」统计\n🔥 连续打卡: {streak}天\n📈 30天完成率: {rate:.1f}%\n✅ 打卡次数: {len(check_ins)}/30",
            "streak": streak, "completion_rate": rate, "total_check_ins": len(check_ins),
        }
