"""
记账理财工具 — 收支记录 + 分类统计 + 预算预警
"""
from __future__ import annotations
from typing import Any, Dict
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func as sa_func
from app.tools.base import BaseTool
from app.models.finance import Transaction
from app.services.encryption import get_encryption_service


class FinanceTool(BaseTool):
    """记账理财工具"""
    name = "finance_tool"
    description = "记账理财 — 记录收支、查看统计、分类汇总、预算预警"
    input_schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["record", "statistics", "category_breakdown"], "description": "操作类型"},
            "type": {"type": "string", "enum": ["income", "expense"], "description": "收/支"},
            "amount": {"type": "number", "description": "金额"},
            "category": {"type": "string", "description": "分类（如餐饮、交通、工资）"},
            "description": {"type": "string", "description": "描述"},
            "note": {"type": "string", "description": "敏感备注（会加密存储）"},
            "date": {"type": "string", "description": "日期 (YYYY-MM-DD)"},
            "period": {"type": "string", "enum": ["day", "week", "month"], "description": "统计周期"},
        },
        "required": ["action"],
    }

    # 常见支出分类
    EXPENSE_CATEGORIES = {"餐饮": "🍽️", "交通": "🚗", "购物": "🛒", "住房": "🏠", "娱乐": "🎮", "医疗": "💊", "教育": "📚", "其他": "📦"}
    INCOME_CATEGORIES = {"工资": "💰", "奖金": "🎁", "投资": "📈", "兼职": "💼", "其他": "📦"}

    async def execute(self, db: AsyncSession = None, user_id: int = None, **kwargs) -> Dict[str, Any]:
        action = kwargs.get("action", "statistics")
        if action == "record":
            return await self._record(db, user_id, **kwargs)
        elif action == "statistics":
            return await self._statistics(db, user_id, **kwargs)
        elif action == "category_breakdown":
            return await self._category_breakdown(db, user_id, **kwargs)
        return {"success": False, "message": f"未知操作: {action}"}

    async def _record(self, db: AsyncSession, user_id: int, **kwargs) -> Dict[str, Any]:
        t_type = kwargs.get("type", "expense")
        amount = kwargs.get("amount")
        if not amount or amount <= 0:
            return {"success": False, "message": "请提供有效金额"}
        try:
            t_date = datetime.strptime(kwargs.get("date", ""), "%Y-%m-%d").date() if kwargs.get("date") else date.today()
        except ValueError:
            t_date = date.today()
        category = kwargs.get("category", "其他")
        encrypted_note = None
        if kwargs.get("note"):
            enc = get_encryption_service()
            encrypted_note = enc.encrypt(kwargs["note"])
        txn = Transaction(
            user_id=user_id, type=t_type, amount=amount, category=category,
            description=kwargs.get("description", ""), encrypted_note=encrypted_note, date=t_date,
        )
        db.add(txn)
        await db.flush()
        emoji = "💰" if t_type == "income" else "💸"
        return {"success": True, "message": f"{emoji} 已记录{('收入' if t_type == 'income' else '支出')} ¥{amount:.2f}（{category}）"}

    async def _statistics(self, db: AsyncSession, user_id: int, **kwargs) -> Dict[str, Any]:
        period = kwargs.get("period", "month")
        today = date.today()
        if period == "day":
            start_date = today
        elif period == "week":
            start_date = today - timedelta(days=today.weekday())
        else:
            start_date = today.replace(day=1)

        result = await db.execute(
            select(Transaction).where(and_(
                Transaction.user_id == user_id, Transaction.date >= start_date,
            ))
        )
        txns = result.scalars().all()
        total_income = sum(t.amount for t in txns if t.type == "income")
        total_expense = sum(t.amount for t in txns if t.type == "expense")
        period_name = {"day": "今日", "week": "本周", "month": "本月"}.get(period, "本月")
        return {
            "success": True,
            "message": f"📊 {period_name}财务概览：\n💰 收入: ¥{total_income:.2f}\n💸 支出: ¥{total_expense:.2f}\n💎 结余: ¥{(total_income - total_expense):.2f}",
            "income": total_income, "expense": total_expense, "balance": total_income - total_expense,
        }

    async def _category_breakdown(self, db: AsyncSession, user_id: int, **kwargs) -> Dict[str, Any]:
        today = date.today()
        start_date = today.replace(day=1)
        result = await db.execute(
            select(Transaction).where(and_(
                Transaction.user_id == user_id, Transaction.date >= start_date, Transaction.type == "expense",
            ))
        )
        txns = result.scalars().all()
        categories: Dict[str, float] = {}
        for t in txns:
            categories[t.category] = categories.get(t.category, 0) + t.amount
        breakdown = [{"category": k, "amount": v, "emoji": self.EXPENSE_CATEGORIES.get(k, "📦")} for k, v in sorted(categories.items(), key=lambda x: -x[1])]
        return {"success": True, "breakdown": breakdown, "total": sum(categories.values())}
