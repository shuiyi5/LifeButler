"""通用工具函数"""
from datetime import datetime, date
from typing import Optional

def format_date(d: Optional[date]) -> str:
    """格式化日期为字符串"""
    return d.isoformat() if d else ""

def format_datetime(dt: Optional[datetime]) -> str:
    """格式化日期时间为字符串"""
    return dt.isoformat() if dt else ""

def safe_int(value: any, default: int = 0) -> int:
    """安全转换为整数"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
