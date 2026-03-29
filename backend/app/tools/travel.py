"""
出行规划工具 — Mock模式
"""
from __future__ import annotations
from typing import Any, Dict
from app.tools.base import BaseTool


class TravelTool(BaseTool):
    """出行规划工具(Mock)"""
    name = "travel_tool"
    description = "出行规划 — 路线规划和POI搜索(Mock模式)"
    input_schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["route", "search_poi"]},
            "origin": {"type": "string"},
            "destination": {"type": "string"},
            "keyword": {"type": "string"},
        },
        "required": ["action"],
    }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        action = kwargs.get("action", "route")
        if action == "route":
            origin = kwargs.get("origin", "起点")
            dest = kwargs.get("destination", "终点")
            return {
                "success": True,
                "message": f"🚗 {origin} → {dest}\n距离: 约15公里\n驾车: 约30分钟\n公交: 约50分钟\n建议: 驾车出行",
            }
        return {"success": True, "message": f"🔍 找到3个{kwargs.get('keyword', '地点')}: 附近咖啡馆、餐厅、商场"}
