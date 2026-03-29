"""
智能家居工具 — Mock模式
"""
from __future__ import annotations
from typing import Any, Dict
from app.tools.base import BaseTool


class SmartHomeTool(BaseTool):
    """智能家居工具(Mock)"""
    name = "smarthome_tool"
    description = "智能家居 — 控制智能设备(Mock模式)"
    input_schema = {
        "type": "object",
        "properties": {
            "device": {"type": "string", "description": "设备名称"},
            "action": {"type": "string", "enum": ["turn_on", "turn_off", "set_temperature"]},
            "value": {"type": "integer"},
        },
        "required": ["device", "action"],
    }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        device = kwargs.get("device", "设备")
        action = kwargs.get("action", "turn_on")
        actions = {"turn_on": "已打开", "turn_off": "已关闭", "set_temperature": f"温度已设为{kwargs.get('value', 26)}℃"}
        return {"success": True, "message": f"🏠 {device}{actions.get(action, '操作完成')}"}
