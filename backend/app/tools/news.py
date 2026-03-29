"""
新闻摘要工具 — 聚合热点新闻
"""
from __future__ import annotations
from typing import Any, Dict
import httpx
from app.tools.base import BaseTool


class NewsTool(BaseTool):
    """新闻摘要工具"""
    name = "news_tool"
    description = "新闻摘要 — 获取今日热点新闻，支持分类筛选"
    input_schema = {
        "type": "object",
        "properties": {
            "category": {"type": "string", "enum": ["all", "tech", "finance", "sports", "entertainment"], "description": "新闻分类"},
        },
    }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """使用免费新闻API或返回模拟数据"""
        category = kwargs.get("category", "all")

        # 尝试从免费API获取（如 NewsAPI.org 免费版）
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # 使用 NewsData.io 免费API（需要注册获取key）
                # 这里先返回模拟数据，用户可以自行配置API key
                return self._mock_news(category)
        except Exception:
            return self._mock_news(category)

    def _mock_news(self, category: str) -> Dict[str, Any]:
        """返回模拟新闻数据"""
        news_by_category = {
            "all": [
                {"title": "AI技术取得新突破", "summary": "最新研究显示AI在多模态理解方面取得重大进展"},
                {"title": "全球经济稳步复苏", "summary": "多国经济数据显示复苏势头良好"},
                {"title": "科技公司发布新产品", "summary": "多家科技巨头发布创新产品"},
            ],
            "tech": [
                {"title": "AI大模型性能提升50%", "summary": "新一代模型在多项基准测试中表现优异"},
                {"title": "量子计算取得突破", "summary": "科学家实现更稳定的量子比特"},
            ],
            "finance": [
                {"title": "股市创新高", "summary": "主要指数突破历史高点"},
                {"title": "央行调整利率", "summary": "货币政策保持稳健"},
            ],
            "sports": [
                {"title": "国足取得胜利", "summary": "世预赛关键战役获胜"},
                {"title": "奥运会筹备进展顺利", "summary": "各项准备工作按计划推进"},
            ],
            "entertainment": [
                {"title": "新电影票房破纪录", "summary": "春节档电影表现亮眼"},
                {"title": "音乐节即将开幕", "summary": "多位知名艺人确认参加"},
            ],
        }

        news_list = news_by_category.get(category, news_by_category["all"])
        lines = ["📰 今日热点:"]
        for i, n in enumerate(news_list, 1):
            lines.append(f"{i}. {n['title']}")

        lines.append("\n💡 提示: 这是模拟数据，可配置 NewsAPI Key 获取实时新闻")

        return {
            "success": True,
            "message": "\n".join(lines),
            "news": news_list,
        }
