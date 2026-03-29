"""
备忘笔记工具 — 本地存储 + Notion 可选同步
"""
from __future__ import annotations
from typing import Any, Dict
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.tools.base import BaseTool
from app.models.note import Note


class NotionTool(BaseTool):
    """备忘笔记工具"""
    name = "notion_tool"
    description = "备忘笔记 — 创建、查询、更新、删除笔记，自然语言快速记录想法"
    input_schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["create", "list", "update", "delete", "search"]},
            "title": {"type": "string", "description": "笔记标题"},
            "content": {"type": "string", "description": "笔记内容"},
            "note_id": {"type": "integer", "description": "笔记ID"},
            "keyword": {"type": "string", "description": "搜索关键词"},
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
        elif action == "search":
            return await self._search(db, user_id, **kwargs)
        return {"success": False, "message": f"未知操作: {action}"}

    async def _create(self, db, user_id, **kwargs):
        title = kwargs.get("title") or kwargs.get("content", "")[:20] or "新笔记"
        note = Note(
            user_id=user_id,
            title=title,
            content=kwargs.get("content", ""),
        )
        db.add(note)
        await db.flush()
        return {"success": True, "message": f"📝 笔记「{note.title}」已保存 ✅", "note_id": note.id}

    async def _list(self, db, user_id, **kwargs):
        result = await db.execute(
            select(Note).where(Note.user_id == user_id).order_by(Note.updated_at.desc()).limit(10)
        )
        notes = result.scalars().all()
        if not notes:
            return {"success": True, "message": "暂无笔记，说「记一下：...」即可创建"}
        items = [f"[{n.id}] {n.title}" for n in notes]
        return {"success": True, "message": "📒 最近笔记:\n" + "\n".join(items), "notes": [{"id": n.id, "title": n.title, "preview": n.content[:80]} for n in notes]}

    async def _update(self, db, user_id, **kwargs):
        nid = kwargs.get("note_id")
        if not nid:
            return {"success": False, "message": "请提供笔记ID"}
        result = await db.execute(select(Note).where(and_(Note.id == nid, Note.user_id == user_id)))
        note = result.scalar_one_or_none()
        if not note:
            return {"success": False, "message": "笔记不存在"}
        if kwargs.get("title"):
            note.title = kwargs["title"]
        if kwargs.get("content"):
            note.content = kwargs["content"]
        note.updated_at = datetime.now()
        await db.flush()
        return {"success": True, "message": f"📝 笔记「{note.title}」已更新 ✅"}

    async def _delete(self, db, user_id, **kwargs):
        nid = kwargs.get("note_id")
        if not nid:
            return {"success": False, "message": "请提供笔记ID"}
        result = await db.execute(select(Note).where(and_(Note.id == nid, Note.user_id == user_id)))
        note = result.scalar_one_or_none()
        if not note:
            return {"success": False, "message": "笔记不存在"}
        await db.delete(note)
        await db.flush()
        return {"success": True, "message": "🗑️ 笔记已删除"}

    async def _search(self, db, user_id, **kwargs):
        kw = kwargs.get("keyword", "")
        result = await db.execute(select(Note).where(Note.user_id == user_id))
        notes = result.scalars().all()
        matched = [n for n in notes if kw.lower() in n.title.lower() or kw.lower() in n.content.lower()]
        if not matched:
            return {"success": True, "message": f"没有找到包含「{kw}」的笔记"}
        items = [f"[{n.id}] {n.title}: {n.content[:50]}" for n in matched[:5]]
        return {"success": True, "message": f"🔍 找到 {len(matched)} 条笔记:\n" + "\n".join(items)}
