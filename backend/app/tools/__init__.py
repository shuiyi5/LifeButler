"""
工具注册 — 导入并注册所有工具到Agent
"""
from app.tools.calendar import CalendarTool
from app.tools.todo import TodoTool
from app.tools.finance import FinanceTool
from app.tools.health import HealthTool
from app.tools.habit import HabitTool
from app.tools.shopping import ShoppingTool
from app.tools.weather import WeatherTool
from app.tools.news import NewsTool
from app.tools.email_tool import EmailTool
from app.tools.travel import TravelTool
from app.tools.notion import NotionTool
from app.tools.reading import ReadingTool
from app.tools.smarthome import SmartHomeTool


def get_all_tools():
    """获取所有工具实例"""
    return [
        CalendarTool(),
        TodoTool(),
        FinanceTool(),
        HealthTool(),
        HabitTool(),
        ShoppingTool(),
        WeatherTool(),
        NewsTool(),
        EmailTool(),
        TravelTool(),
        NotionTool(),
        ReadingTool(),
        SmartHomeTool(),
    ]
