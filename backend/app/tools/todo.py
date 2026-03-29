"""
待办管理工具 — CRUD + 优先级 + 截止日期 + 分类
"""
from __future__ import annotations
from typing import Any, Dict
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.tools.base import BaseTool
from app.models.todo import Todo


class TodoTool(BaseTool):
    """待办管理工具"""
    name = "todo_tool"
    description = "待办管理 — 创建/查询/修改/删除待办事项，支持优先级、截止日期和分类"
    input_schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["create", "list", "update", "delete", "complete"], "description": "操作类型"},
            "title": {"type": "string", "description": "待办标题"},
            "description": {"type": "string", "description": "待办描述"},
            "priority": {"type": "string", "enum": ["high", "medium", "low"], "description": "优先级"},
            "category": {"type": "string", "description": "分类"},
            "due_date": {"type": "string", "description": "截止日期 (YYYY-MM-DD)"},
            "todo_id": {"type": "integer", "description": "待办ID"},
            "status": {"type": "string", "enum": ["pending", "in_progress", "done"], "description": "状态"},
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
        elif action == "complete":
            kwargs["status"] = "done"
            return await self._update(db, user_id, **kwargs)
        return {"success": False, "message": f"未知操作: {action}"}

    async def _create(self, db: AsyncSession, user_id: int, **kwargs) -> Dict[str, Any]:
        due = None
        if kwargs.get("due_date"):
            try:
                due = datetime.strptime(kwargs["due_date"], "%Y-%m-%d").date()
            except ValueError:
                return {"success": False, "message": "截止日期格式错误 (YYYY-MM-DD)"}
        todo = Todo(
            user_id=user_id, title=kwargs.get("title", "新待办"),
            description=kwargs.get("description", ""),
            priority=kwargs.get("priority", "medium"),
            category=kwargs.get("category", ""), due_date=due,
        )
        db.add(todo)
        await db.flush()
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(todo.priority, "🟡")
        return {"success": True, "message": f"{priority_emoji} 待办「{todo.title}」已创建 ✅", "todo_id": todo.id}

    async def _list(self, db: AsyncSession, user_id: int, **kwargs) -> Dict[str, Any]:
        query = select(Todo).where(Todo.user_id == user_id)
        if kwargs.get("priority"):
            query = query.where(Todo.priority == kwargs["priority"])
        if kwargs.get("status"):
            query = query.where(Todo.status == kwargs["status"])
        else:
            query = query.where(Todo.status != "done")
        if kwargs.get("category"):
            query = query.where(Todo.category == kwargs["category"])
        query = query.order_by(Todo.created_at.desc())
        result = await db.execute(query)
        todos = result.scalars().all()
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        return {
            "success": True, "count": len(todos),
            "todos": [{
                "id": t.id, "title": t.title, "priority": t.priority,
                "status": t.status, "category": t.category or "",
                "due_date": str(t.due_date) if t.due_date else None,
                "emoji": priority_emoji.get(t.priority, "🟡"),
            } for t in todos],
        }

    async def _update(self, db: AsyncSession, user_id: int, **kwargs) -> Dict[str, Any]:
        tid = kwargs.get("todo_id")
        if not tid:
            return {"success": False, "message": "请提供待办 ID"}
        result = await db.execute(select(Todo).where(and_(Todo.id == tid, Todo.user_id == user_id)))
        todo = result.scalar_one_or_none()
        if not todo:
            return {"success": False, "message": "待办不存在"}
        for field in ["title", "description", "priority", "category", "status"]:
            if kwargs.get(field):
                setattr(todo, field, kwargs[field])
        if kwargs.get("due_date"):
            todo.due_date = datetime.strptime(kwargs["due_date"], "%Y-%m-%d").date()
        await db.flush()
        if todo.status == "done":
            return {"success": True, "message": f"✅ 太棒了！「{todo.title}」已完成！"}
        return {"success": True, "message": f"待办「{todo.title}」已更新 ✅"}

    async def _delete(self, db: AsyncSession, user_id: int, **kwargs) -> Dict[str, Any]:
        tid = kwargs.get("todo_id")
        if not tid:
            return {"success": False, "message": "请提供待办 ID"}
        result = await db.execute(select(Todo).where(and_(Todo.id == tid, Todo.user_id == user_id)))
        todo = result.scalar_one_or_none()
        if not todo:
            return {"success": False, "message": "待办不存在"}
        title = todo.title
        await db.delete(todo)
        await db.flush()
        return {"success": True, "message": f"待办「{title}」已删除 🗑️"}
