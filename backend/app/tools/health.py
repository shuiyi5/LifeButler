"""
饮食健康工具 — 饮食记录 + 营养估算 + 饮水提醒
"""
from __future__ import annotations
from typing import Any, Dict
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.tools.base import BaseTool
from app.models.health import MealRecord
import json


# 扩展的食物热量估算表（千卡/100g）
CALORIE_TABLE = {
    # 主食类
    "米饭": 116, "面条": 110, "馒头": 221, "面包": 260, "包子": 227,
    "饺子": 198, "粥": 46, "油条": 388, "烧饼": 326, "煎饼": 336,
    "意面": 158, "披萨": 266, "汉堡": 295, "三明治": 250,
    # 蛋白质
    "鸡蛋": 144, "鸡胸肉": 133, "猪肉": 143, "牛肉": 125, "羊肉": 203,
    "鱼": 104, "虾": 93, "螃蟹": 95, "豆腐": 81, "豆浆": 31,
    "牛奶": 54, "酸奶": 72, "奶酪": 328, "火腿": 330, "香肠": 508,
    # 蔬菜类
    "青菜": 15, "白菜": 17, "菠菜": 24, "西红柿": 19, "黄瓜": 15,
    "土豆": 77, "红薯": 86, "南瓜": 22, "胡萝卜": 41, "茄子": 21,
    "西兰花": 34, "花菜": 24, "芹菜": 14, "洋葱": 39, "蘑菇": 22,
    # 水果类
    "苹果": 52, "香蕉": 89, "橙子": 47, "葡萄": 69, "西瓜": 30,
    "草莓": 32, "芒果": 60, "梨": 44, "桃子": 42, "樱桃": 63,
    "猕猴桃": 61, "柚子": 42, "荔枝": 66, "龙眼": 71,
    # 饮品零食
    "咖啡": 1, "可乐": 43, "奶茶": 120, "啤酒": 43, "红酒": 83,
    "薯片": 548, "饼干": 433, "巧克力": 546, "冰淇淋": 207,
    "蛋糕": 347, "糖果": 400, "坚果": 600, "瓜子": 615,
}


class HealthTool(BaseTool):
    """饮食健康工具"""
    name = "health_tool"
    description = "饮食健康 — 记录饮食、估算营养、记录饮水量"
    input_schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["record_meal", "record_water", "daily_summary"], "description": "操作类型"},
            "meal_type": {"type": "string", "enum": ["breakfast", "lunch", "dinner", "snack"], "description": "餐次"},
            "food_items": {"type": "string", "description": "食物列表（逗号分隔）"},
            "water_ml": {"type": "integer", "description": "饮水量(毫升)"},
            "date": {"type": "string", "description": "日期 (YYYY-MM-DD)"},
        },
        "required": ["action"],
    }

    async def execute(self, db: AsyncSession = None, user_id: int = None, **kwargs) -> Dict[str, Any]:
        action = kwargs.get("action", "daily_summary")
        if action == "record_meal":
            return await self._record_meal(db, user_id, **kwargs)
        elif action == "record_water":
            return await self._record_water(db, user_id, **kwargs)
        elif action == "daily_summary":
            return await self._daily_summary(db, user_id, **kwargs)
        return {"success": False, "message": f"未知操作: {action}"}

    async def _record_meal(self, db: AsyncSession, user_id: int, **kwargs) -> Dict[str, Any]:
        meal_type = kwargs.get("meal_type", "snack")
        foods = kwargs.get("food_items", "")
        food_list = [f.strip() for f in foods.split(",") if f.strip()] if foods else []
        calories = sum(CALORIE_TABLE.get(f, 200) for f in food_list)
        t_date = date.today()
        if kwargs.get("date"):
            try:
                t_date = datetime.strptime(kwargs["date"], "%Y-%m-%d").date()
            except ValueError:
                pass
        meal_names = {"breakfast": "早餐", "lunch": "午餐", "dinner": "晚餐", "snack": "加餐"}
        record = MealRecord(
            user_id=user_id, meal_type=meal_type,
            food_items=json.dumps(food_list, ensure_ascii=False),
            calories_estimate=calories, date=t_date,
        )
        db.add(record)
        await db.flush()
        return {"success": True, "message": f"🍽️ {meal_names.get(meal_type, '餐食')}已记录！\n食物: {', '.join(food_list)}\n预估热量: ~{calories}千卡"}

    async def _record_water(self, db: AsyncSession, user_id: int, **kwargs) -> Dict[str, Any]:
        water = kwargs.get("water_ml", 250)
        today = date.today()
        record = MealRecord(
            user_id=user_id, meal_type="water", water_ml=water,
            food_items="[]", date=today,
        )
        db.add(record)
        await db.flush()
        # 查询今日总饮水量
        result = await db.execute(
            select(MealRecord).where(and_(MealRecord.user_id == user_id, MealRecord.date == today))
        )
        records = result.scalars().all()
        total_water = sum(r.water_ml for r in records)
        target = 2000
        progress = min(total_water / target * 100, 100)
        return {"success": True, "message": f"💧 已记录 {water}ml 饮水\n今日总量: {total_water}ml / {target}ml ({progress:.0f}%)"}

    async def _daily_summary(self, db: AsyncSession, user_id: int, **kwargs) -> Dict[str, Any]:
        today = date.today()
        result = await db.execute(
            select(MealRecord).where(and_(MealRecord.user_id == user_id, MealRecord.date == today))
        )
        records = result.scalars().all()
        total_cal = sum(r.calories_estimate or 0 for r in records if r.meal_type != "water")
        total_water = sum(r.water_ml for r in records)
        meals = [r for r in records if r.meal_type != "water"]
        return {
            "success": True,
            "message": f"📊 今日饮食概览\n🔥 总热量: ~{total_cal:.0f}千卡\n💧 饮水量: {total_water}ml\n🍽️ 共记录 {len(meals)} 餐",
            "calories": total_cal, "water_ml": total_water, "meal_count": len(meals),
        }
