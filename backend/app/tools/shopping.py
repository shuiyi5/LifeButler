"""
购物清单工具 — 添加/分类/勾选已购/清空
"""
from __future__ import annotations
from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from app.tools.base import BaseTool
from app.models.shopping import ShoppingItem


class ShoppingTool(BaseTool):
    """购物清单工具"""
    name = "shopping_tool"
    description = "购物清单 — 添加商品、分类管理、勾选已购、清空已购"
    input_schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["add", "list", "mark_purchased", "clear_purchased", "delete"], "description": "操作类型"},
            "name": {"type": "string", "description": "商品名称"},
            "category": {"type": "string", "description": "分类"},
            "quantity": {"type": "integer", "description": "数量"},
            "unit": {"type": "string", "description": "单位"},
            "item_id": {"type": "integer", "description": "商品ID"},
            "items": {"type": "string", "description": "批量添加（逗号分隔）"},
        },
        "required": ["action"],
    }

    # 自动分类映射
    AUTO_CATEGORIES = {
        "蔬菜": ["白菜", "菠菜", "西红柿", "黄瓜", "茄子", "土豆", "胡萝卜", "生菜", "青椒", "洋葱"],
        "水果": ["苹果", "香蕉", "橙子", "葡萄", "草莓", "西瓜", "芒果", "桃子", "梨"],
        "肉类": ["鸡肉", "猪肉", "牛肉", "鱼", "虾", "鸡蛋", "排骨", "鸡腿", "鸡翅"],
        "饮品": ["牛奶", "酸奶", "果汁", "可乐", "咖啡", "茶", "矿泉水", "啤酒"],
        "日用": ["纸巾", "洗衣液", "沐浴露", "牙膏", "洗发水", "垃圾袋"],
    }

    def _auto_categorize(self, name: str) -> str:
        for cat, items in self.AUTO_CATEGORIES.items():
            if any(item in name for item in items):
                return cat
        return "其他"

    async def execute(self, db: AsyncSession = None, user_id: int = None, **kwargs) -> Dict[str, Any]:
        action = kwargs.get("action", "list")
        if action == "add":
            return await self._add(db, user_id, **kwargs)
        elif action == "list":
            return await self._list(db, user_id, **kwargs)
        elif action == "mark_purchased":
            return await self._mark_purchased(db, user_id, **kwargs)
        elif action == "clear_purchased":
            return await self._clear_purchased(db, user_id, **kwargs)
        elif action == "delete":
            return await self._delete_item(db, user_id, **kwargs)
        return {"success": False, "message": f"未知操作: {action}"}

    async def _add(self, db: AsyncSession, user_id: int, **kwargs) -> Dict[str, Any]:
        # 支持批量添加
        items_str = kwargs.get("items", "")
        names = [n.strip() for n in items_str.split(",") if n.strip()] if items_str else []
        if kwargs.get("name") and not names:
            names = [kwargs["name"]]
        if not names:
            return {"success": False, "message": "请告诉我要添加什么商品~"}
        added = []
        for name in names:
            cat = kwargs.get("category") or self._auto_categorize(name)
            item = ShoppingItem(
                user_id=user_id, name=name, category=cat,
                quantity=kwargs.get("quantity", 1), unit=kwargs.get("unit", "个"),
            )
            db.add(item)
            added.append(name)
        await db.flush()
        return {"success": True, "message": f"🛒 已添加 {len(added)} 件商品: {', '.join(added)}"}

    async def _list(self, db: AsyncSession, user_id: int, **kwargs) -> Dict[str, Any]:
        result = await db.execute(
            select(ShoppingItem).where(and_(ShoppingItem.user_id == user_id, ShoppingItem.is_purchased == False))
            .order_by(ShoppingItem.category)
        )
        items = result.scalars().all()
        grouped: Dict[str, list] = {}
        for item in items:
            grouped.setdefault(item.category, []).append({"id": item.id, "name": item.name, "quantity": item.quantity, "unit": item.unit})
        return {"success": True, "count": len(items), "items_by_category": grouped}

    async def _mark_purchased(self, db: AsyncSession, user_id: int, **kwargs) -> Dict[str, Any]:
        item_id = kwargs.get("item_id")
        if not item_id:
            return {"success": False, "message": "请提供商品 ID"}
        result = await db.execute(select(ShoppingItem).where(and_(ShoppingItem.id == item_id, ShoppingItem.user_id == user_id)))
        item = result.scalar_one_or_none()
        if not item:
            return {"success": False, "message": "商品不存在"}
        item.is_purchased = True
        await db.flush()
        return {"success": True, "message": f"✅ 「{item.name}」已购买"}

    async def _clear_purchased(self, db: AsyncSession, user_id: int, **kwargs) -> Dict[str, Any]:
        await db.execute(delete(ShoppingItem).where(and_(ShoppingItem.user_id == user_id, ShoppingItem.is_purchased == True)))
        await db.flush()
        return {"success": True, "message": "🧹 已清空已购商品"}

    async def _delete_item(self, db: AsyncSession, user_id: int, **kwargs) -> Dict[str, Any]:
        item_id = kwargs.get("item_id")
        if not item_id:
            return {"success": False, "message": "请提供商品 ID"}
        result = await db.execute(select(ShoppingItem).where(and_(ShoppingItem.id == item_id, ShoppingItem.user_id == user_id)))
        item = result.scalar_one_or_none()
        if not item:
            return {"success": False, "message": "商品不存在"}
        name = item.name
        await db.delete(item)
        await db.flush()
        return {"success": True, "message": f"🗑️ 已删除「{name}」"}
