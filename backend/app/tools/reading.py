"""
读书学习工具 — 创建计划、更新进度、统计分析
"""
from __future__ import annotations
from typing import Any, Dict
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.tools.base import BaseTool
from app.models.reading import ReadingPlan


class ReadingTool(BaseTool):
    """读书学习工具"""
    name = "reading_tool"
    description = "读书学习 — 创建读书计划、更新进度、查看统计"
    input_schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["create", "update_progress", "list", "stats"]},
            "book_title": {"type": "string", "description": "书名"},
            "total_pages": {"type": "integer", "description": "总页数"},
            "current_page": {"type": "integer", "description": "当前页数"},
            "plan_id": {"type": "integer", "description": "计划ID"},
        },
        "required": ["action"],
    }

    async def execute(self, db: AsyncSession = None, user_id: int = None, **kwargs) -> Dict[str, Any]:
        action = kwargs.get("action", "list")
        if action == "create":
            return await self._create(db, user_id, **kwargs)
        elif action == "update_progress":
            return await self._update_progress(db, user_id, **kwargs)
        elif action == "list":
            return await self._list(db, user_id, **kwargs)
        elif action == "stats":
            return await self._stats(db, user_id, **kwargs)
        return {"success": False, "message": f"未知操作: {action}"}

    async def _create(self, db, user_id, **kwargs):
        plan = ReadingPlan(
            user_id=user_id,
            book_title=kwargs.get("book_title", "新书"),
            total_pages=kwargs.get("total_pages", 300),
        )
        db.add(plan)
        await db.flush()
        return {"success": True, "message": f"📚 读书计划「{plan.book_title}」已创建（共{plan.total_pages}页）", "plan_id": plan.id}

    async def _update_progress(self, db, user_id, **kwargs):
        pid = kwargs.get("plan_id")
        if not pid:
            return {"success": False, "message": "请提供计划ID"}
        result = await db.execute(select(ReadingPlan).where(and_(ReadingPlan.id == pid, ReadingPlan.user_id == user_id)))
        plan = result.scalar_one_or_none()
        if not plan:
            return {"success": False, "message": "读书计划不存在"}
        plan.current_page = kwargs.get("current_page", plan.current_page)
        plan.updated_at = datetime.now()
        await db.flush()
        progress = plan.current_page / plan.total_pages * 100 if plan.total_pages > 0 else 0
        if plan.current_page >= plan.total_pages:
            return {"success": True, "message": f"🎉 恭喜！「{plan.book_title}」已读完！"}
        return {"success": True, "message": f"📖 进度已更新: {plan.current_page}/{plan.total_pages}页 ({progress:.0f}%)"}

    async def _list(self, db, user_id, **kwargs):
        result = await db.execute(select(ReadingPlan).where(ReadingPlan.user_id == user_id).order_by(ReadingPlan.updated_at.desc()))
        plans = result.scalars().all()
        if not plans:
            return {"success": True, "message": "暂无读书计划，说「开始读《原则》300页」即可创建"}
        items = []
        for p in plans:
            prog = p.current_page / p.total_pages * 100 if p.total_pages > 0 else 0
            status = "✅" if p.current_page >= p.total_pages else f"{prog:.0f}%"
            items.append(f"[{p.id}] {p.book_title}: {p.current_page}/{p.total_pages}页 ({status})")
        return {"success": True, "message": "📚 读书计划:\n" + "\n".join(items), "plans": [{"id": p.id, "title": p.book_title, "progress": f"{p.current_page}/{p.total_pages}"} for p in plans]}

    async def _stats(self, db, user_id, **kwargs):
        result = await db.execute(select(ReadingPlan).where(ReadingPlan.user_id == user_id))
        plans = result.scalars().all()
        if not plans:
            return {"success": True, "message": "暂无读书数据"}
        total_books = len(plans)
        completed = sum(1 for p in plans if p.current_page >= p.total_pages)
        in_progress = total_books - completed
        total_pages_read = sum(p.current_page for p in plans)
        return {
            "success": True,
            "message": f"📊 读书统计:\n📚 总计划: {total_books}本\n✅ 已完成: {completed}本\n📖 进行中: {in_progress}本\n📄 累计阅读: {total_pages_read}页",
            "stats": {"total": total_books, "completed": completed, "in_progress": in_progress, "pages_read": total_pages_read}
        }
