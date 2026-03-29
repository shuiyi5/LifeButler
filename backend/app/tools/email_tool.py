"""
邮件管理工具 — Mock模式
"""
from __future__ import annotations
from typing import Any, Dict
from app.tools.base import BaseTool


class EmailTool(BaseTool):
    """邮件管理工具(Mock)"""
    name = "email_tool"
    description = "邮件管理 — 查看和发送邮件(Mock模式)"
    input_schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["list_unread", "send"]},
            "to": {"type": "string"},
            "subject": {"type": "string"},
            "body": {"type": "string"},
        },
        "required": ["action"],
    }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        action = kwargs.get("action", "list_unread")
        if action == "send":
            return {"success": True, "message": f"📧 邮件已发送至 {kwargs.get('to', '收件人')}"}
        return {
            "success": True,
            "message": "📬 未读邮件(3封):\n1. 工作通知\n2. 账单提醒\n3. 活动邀请",
            "unread_count": 3,
        }
