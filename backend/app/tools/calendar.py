"""
日程管理工具 — 创建/查询/修改/删除日程事件 + 冲突检测
"""
from __future__ import annotations
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, delete
from app.tools.base import BaseTool
from app.models.calendar import CalendarEvent


class CalendarTool(BaseTool):
    """日程管理工具"""
    name = "calendar_tool"
    description = "日程管理 — 创建/查询/修改/删除日程事件，支持重复事件和冲突检测"
    input_schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["create", "list", "update", "delete"], "description": "操作类型"},
            "title": {"type": "string", "description": "日程标题"},
            "description": {"type": "string", "description": "日程描述"},
            "start_time": {"type": "string", "description": "开始时间 (YYYY-MM-DD HH:MM)"},
            "end_time": {"type": "string", "description": "结束时间 (YYYY-MM-DD HH:MM)"},
            "location": {"type": "string", "description": "地点"},
            "event_id": {"type": "integer", "description": "日程ID（修改/删除时用）"},
            "date": {"type": "string", "description": "查询日期 (YYYY-MM-DD)"},
        },
        "required": ["action"],
    }

    async def execute(self, db: AsyncSession = None, user_id: int = None, **kwargs) -> Dict[str, Any]:
        action = kwargs.get("action", "list")
        if action == "create":
            return await self._create(db, user_id, **kwargs)
        elif action == "list":
            return await self._list(db, user_id, **kwargs)
        elif action == "update":
            return await self._update(db, user_id, **kwargs)
        elif action == "delete":
            return await self._delete(db, user_id, **kwargs)
        return {"success": False, "message": f"未知操作: {action}"}

    async def _create(self, db: AsyncSession, user_id: int, **kwargs) -> Dict[str, Any]:
        try:
            start = datetime.strptime(kwargs["start_time"], "%Y-%m-%d %H:%M")
            end = datetime.strptime(kwargs.get("end_time", ""), "%Y-%m-%d %H:%M") if kwargs.get("end_time") else start + timedelta(hours=1)
        except (ValueError, KeyError):
            return {"success": False, "message": "请提供正确的时间格式 (YYYY-MM-DD HH:MM)"}

        # 冲突检测
        conflicts = await self._check_conflicts(db, user_id, start, end)
        event = CalendarEvent(
            user_id=user_id, title=kwargs.get("title", "新日程"),
            description=kwargs.get("description", ""), start_time=start, end_time=end,
            location=kwargs.get("location", ""), repeat_type=kwargs.get("repeat_type", "none"),
        )
        db.add(event)
        await db.flush()
        msg = f"日程「{event.title}」已创建 ✅"
        if conflicts:
            msg += f"\n⚠️ 注意：与 {len(conflicts)} 个日程存在时间冲突"
        return {"success": True, "message": msg, "event_id": event.id, "conflicts": len(conflicts)}

    async def _list(self, db: AsyncSession, user_id: int, **kwargs) -> Dict[str, Any]:
        query = select(CalendarEvent).where(CalendarEvent.user_id == user_id)
        if kwargs.get("date"):
            try:
                d = datetime.strptime(kwargs["date"], "%Y-%m-%d")
                query = query.where(and_(
                    CalendarEvent.start_time >= d,
                    CalendarEvent.start_time < d + timedelta(days=1),
                ))
            except ValueError:
                pass
        query = query.order_by(CalendarEvent.start_time)
        result = await db.execute(query)
        events = result.scalars().all()
        return {
            "success": True, "count": len(events),
            "events": [{"id": e.id, "title": e.title, "start": str(e.start_time), "end": str(e.end_time), "location": e.location or ""} for e in events],
        }

    async def _update(self, db: AsyncSession, user_id: int, **kwargs) -> Dict[str, Any]:
        eid = kwargs.get("event_id")
        if not eid:
            return {"success": False, "message": "请提供日程 ID"}
        result = await db.execute(select(CalendarEvent).where(and_(CalendarEvent.id == eid, CalendarEvent.user_id == user_id)))
        event = result.scalar_one_or_none()
        if not event:
            return {"success": False, "message": "日程不存在"}
        for field in ["title", "description", "location"]:
            if kwargs.get(field):
                setattr(event, field, kwargs[field])
        if kwargs.get("start_time"):
            event.start_time = datetime.strptime(kwargs["start_time"], "%Y-%m-%d %H:%M")
        if kwargs.get("end_time"):
            event.end_time = datetime.strptime(kwargs["end_time"], "%Y-%m-%d %H:%M")
        await db.flush()
        return {"success": True, "message": f"日程「{event.title}」已更新 ✅"}

    async def _delete(self, db: AsyncSession, user_id: int, **kwargs) -> Dict[str, Any]:
        eid = kwargs.get("event_id")
        if not eid:
            return {"success": False, "message": "请提供日程 ID"}
        result = await db.execute(select(CalendarEvent).where(and_(CalendarEvent.id == eid, CalendarEvent.user_id == user_id)))
        event = result.scalar_one_or_none()
        if not event:
            return {"success": False, "message": "日程不存在"}
        title = event.title
        await db.delete(event)
        await db.flush()
        return {"success": True, "message": f"日程「{title}」已删除 🗑️"}

    async def _check_conflicts(self, db: AsyncSession, user_id: int, start: datetime, end: datetime, exclude_id: int = None) -> list:
        query = select(CalendarEvent).where(and_(
            CalendarEvent.user_id == user_id,
            CalendarEvent.start_time < end,
            CalendarEvent.end_time > start,
        ))
        if exclude_id:
            query = query.where(CalendarEvent.id != exclude_id)
        result = await db.execute(query)
        return result.scalars().all()
