"""
天气查询工具 — 和风天气 API / 无 API Key 时返回友好提示
"""
from __future__ import annotations
from typing import Any, Dict
import httpx
from app.tools.base import BaseTool
from app.config.settings import settings


# 热门城市 -> 和风天气 Location ID
CITY_IDS: Dict[str, str] = {
    "北京": "101010100", "上海": "101020100", "广州": "101280101",
    "深圳": "101280601", "杭州": "101210101", "成都": "101270101",
    "武汉": "101200101", "南京": "101190101", "西安": "101110101",
    "重庆": "101040100", "天津": "101030100", "长沙": "101250101",
    "苏州": "101190401", "郑州": "101180101", "东莞": "101281601",
    "青岛": "101120201", "沈阳": "101070101", "大连": "101070201",
    "厦门": "101230201", "济南": "101120101",
}


class WeatherTool(BaseTool):
    """天气查询工具"""
    name = "weather_tool"
    description = "天气查询 — 查询实时天气和未来预报，提供穿衣建议"
    input_schema = {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "城市名称"},
            "action": {"type": "string", "enum": ["current", "forecast"], "description": "查询类型"},
        },
        "required": ["city"],
    }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        city = kwargs.get("city", "北京")
        action = kwargs.get("action", "current")
        api_key = settings.QWEATHER_API_KEY

        if not api_key:
            return self._mock_weather(city, action)

        location = CITY_IDS.get(city)
        if not location:
            # 尝试用城市名直接查询
            location = city

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                if action == "forecast":
                    return await self._real_forecast(client, api_key, location, city)
                else:
                    return await self._real_current(client, api_key, location, city)
        except Exception as e:
            return {"success": False, "message": f"天气查询失败: {str(e)}"}

    async def _real_current(self, client, api_key, location, city):
        resp = await client.get(
            "https://devapi.qweather.com/v7/weather/now",
            params={"key": api_key, "location": location},
        )
        data = resp.json()
        if data.get("code") != "200":
            return {"success": False, "message": f"查询失败，请检查城市名称「{city}」"}
        now = data["now"]
        temp = int(now["temp"])
        advice = self._clothing_advice(temp)
        return {
            "success": True,
            "message": f"☀️ {city}当前天气: {now['text']}\n🌡️ 温度: {now['temp']}℃ (体感{now['feelsLike']}℃)\n💨 风力: {now['windDir']}{now['windScale']}级\n💧 湿度: {now['humidity']}%\n👔 {advice}",
        }

    async def _real_forecast(self, client, api_key, location, city):
        resp = await client.get(
            "https://devapi.qweather.com/v7/weather/3d",
            params={"key": api_key, "location": location},
        )
        data = resp.json()
        if data.get("code") != "200":
            return {"success": False, "message": f"查询失败，请检查城市名称「{city}」"}
        days = data["daily"]
        lines = [f"☀️ {city}未来3天天气:"]
        for d in days:
            lines.append(f"  {d['fxDate']}: {d['textDay']} {d['tempMin']}-{d['tempMax']}℃")
        avg_temp = sum(int(d["tempMax"]) for d in days) // len(days)
        lines.append(f"👔 {self._clothing_advice(avg_temp)}")
        return {"success": True, "message": "\n".join(lines)}

    def _clothing_advice(self, temp: int) -> str:
        if temp >= 30: return "穿衣建议: 短袖短裤，注意防晒 ☀️"
        if temp >= 22: return "穿衣建议: 薄外套或长袖即可 🌤️"
        if temp >= 15: return "穿衣建议: 卫衣或薄毛衣 🍂"
        if temp >= 5: return "穿衣建议: 厚外套或羽绒服 🧥"
        return "穿衣建议: 注意保暖，多穿衣物 🥶"

    def _mock_weather(self, city: str, action: str) -> Dict[str, Any]:
        """无 API Key 时返回模拟数据"""
        if action == "forecast":
            return {
                "success": True,
                "message": f"☀️ {city}未来3天天气（模拟数据）:\n  明天: 晴 15-25℃\n  后天: 多云 14-23℃\n  大后天: 小雨 12-20℃\n💡 建议: 明天适合出行~\n⚠️ 提示: 配置和风天气 API Key 可获取实时天气",
            }
        return {
            "success": True,
            "message": f"☀️ {city}当前天气（模拟数据）:\n🌡️ 温度: 22℃\n💨 风力: 微风\n💧 湿度: 45%\n👔 穿衣建议: 适合穿薄外套\n⚠️ 提示: 在设置中配置和风天气 API Key 可获取实时天气",
        }
