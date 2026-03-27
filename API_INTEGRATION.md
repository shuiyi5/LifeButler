# API 集成规范

## 1. AI 模型适配层设计

### 通用接口
所有模型调用通过统一适配器，支持零代码切换模型。

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator

class AIProvider(ABC):
    """AI 模型通用适配器接口"""

    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = True
    ) -> AsyncIterator[str]:
        """流式对话"""
        ...

    @abstractmethod
    async def chat_sync(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> dict:
        """同步对话（用于工具调用等需要完整响应的场景）"""
        ...
```

### 已配置模型
| 提供商 | 模型 | 环境变量 | 用途 |
|--------|------|----------|------|
| 自定义端点（兼容 Anthropic） | claude-sonnet-4-6 | `CUSTOM_API_KEY` | 主模型 — 对话、意图识别、工具调用 |

### 配置方式
```bash
# .env 文件
CUSTOM_API_KEY=your-api-key-here
AI_MODEL=claude-sonnet-4-6
AI_BASE_URL=https://cursor.scihub.edu.kg/api
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=4096
```

### 适配器实现策略
```python
class CustomAnthropicProvider(AIProvider):
    """自定义端点的 Anthropic 兼容适配器"""

    def __init__(self):
        self.client = AsyncAnthropic(
            api_key=settings.CUSTOM_API_KEY,
            base_url=settings.AI_BASE_URL
        )
        self.model = settings.AI_MODEL
```

### 切换模型
只需修改 `.env` 中的配置，无需改动任何代码：
```bash
# 切换到 OpenAI
AI_PROVIDER=openai
AI_MODEL=gpt-4o
OPENAI_API_KEY=your-key
AI_BASE_URL=https://api.openai.com/v1

# 切换到 DeepSeek
AI_PROVIDER=deepseek
AI_MODEL=deepseek-chat
DEEPSEEK_API_KEY=your-key
AI_BASE_URL=https://api.deepseek.com/v1
```

## 2. 请求规范

### 对话请求格式
```json
{
  "messages": [
    {"role": "system", "content": "你是 LifeButler 生活管家..."},
    {"role": "user", "content": "帮我记一笔午饭35元"}
  ],
  "tools": [...],
  "temperature": 0.7,
  "max_tokens": 4096,
  "stream": true
}
```

### WebSocket 对话协议
```json
// 客户端发送
{"type": "message", "content": "今天天气怎么样"}

// 服务端流式返回
{"type": "stream", "content": "今", "done": false}
{"type": "stream", "content": "天", "done": false}
{"type": "stream", "content": "...", "done": false}
{"type": "stream", "content": "", "done": true}

// 工具调用时
{"type": "tool_call", "tool": "weather", "status": "calling"}
{"type": "tool_result", "tool": "weather", "data": {...}}
{"type": "stream", "content": "今天北京天气...", "done": false}
```

## 3. 错误处理
| 错误码 | 含义 | 处理方式 |
|--------|------|----------|
| 401 | API Key 无效 | 提示用户检查 .env 配置 |
| 429 | 速率限制 | 指数退避重试，最多 3 次（1s → 2s → 4s） |
| 500 | 服务端错误 | 重试 1 次，失败则返回友好提示"管家开小差了，请再试一次~" |
| timeout | 超时（30s） | 重试 1 次，失败则返回"管家正在忙，请稍后再试~" |
| 网络错误 | 无法连接 | 返回"网络似乎不太好，检查一下连接？" |

## 4. 速率限制策略
- 请求间隔：最小 200ms
- 并发限制：每用户 2 个同时请求
- 日限额：暂不设限（根据 API 预算动态调整）
- 预算监控：每月 API 调用费 ≤ ¥30，接近上限时管家主动提醒

## 5. 工具调用规范

### 5.1 天气查询（和风天气）
- **用途**：实时天气 + 7日预报 + 生活指数
- **调用方式**：HTTP GET
- **API 文档**：https://dev.qweather.com/
- **输入格式**：`{"city": "北京"}` 或 `{"location": "116.41,39.92"}`
- **输出格式**：`{"temp": "25°C", "text": "晴", "suggestion": "适合外出"}`
- **环境变量**：`QWEATHER_API_KEY`
- **错误处理**：API 失败时返回缓存的上次查询结果或友好提示

### 5.2 出行规划（高德地图）
- **用途**：路线规划 + 实时交通 + POI 搜索
- **调用方式**：HTTP GET
- **API 文档**：https://lbs.amap.com/api/webservice/summary
- **输入格式**：`{"origin": "起点坐标", "destination": "终点坐标", "mode": "driving"}`
- **输出格式**：`{"routes": [...], "duration": "35min", "distance": "12km"}`
- **环境变量**：`AMAP_API_KEY`
- **错误处理**：地址解析失败时提示用户确认地址

### 5.3 邮件管理（QQ 邮箱 IMAP/SMTP）
- **用途**：读取未读邮件 + 发送回复
- **调用方式**：IMAP（收件） + SMTP（发件）
- **输入格式**：`{"action": "fetch_unread", "limit": 10}` 或 `{"action": "send", "to": "...", "subject": "...", "body": "..."}`
- **输出格式**：`{"emails": [{"from": "...", "subject": "...", "summary": "AI生成摘要"}]}`
- **环境变量**：`QQ_EMAIL_ADDRESS` + `QQ_EMAIL_AUTH_CODE`
- **错误处理**：认证失败提示检查授权码，网络失败重试 1 次
- **安全**：授权码加密存储，邮件内容加密存储

### 5.4 Notion 同步
- **用途**：备忘笔记同步到 Notion 数据库
- **调用方式**：HTTP POST (Notion API v1)
- **API 文档**：https://developers.notion.com/
- **输入格式**：`{"title": "笔记标题", "content": "笔记内容", "tags": ["标签"]}`
- **输出格式**：`{"notion_page_id": "xxx", "url": "https://notion.so/xxx"}`
- **环境变量**：`NOTION_API_KEY` + `NOTION_DATABASE_ID`
- **错误处理**：Notion 同步失败时本地保留笔记，下次登录时重试同步

### 5.5 新闻摘要（RSS + NewsAPI）
- **用途**：多源新闻聚合 + AI 摘要生成
- **调用方式**：HTTP GET (RSS解析) + NewsAPI
- **输入格式**：`{"category": "technology", "limit": 10}`
- **输出格式**：`{"articles": [{"title": "...", "summary": "AI生成摘要", "source": "..."}]}`
- **错误处理**：单个源失败不影响其他源

### 5.6 智能家居（预留接口）
- **用途**：通用设备控制
- **调用方式**：通过适配器接口，预留给未来具体平台实现
- **输入格式**：`{"device": "客厅灯", "action": "turn_on", "params": {}}`
- **输出格式**：`{"success": true, "device_status": "on"}`
- **当前实现**：Mock 模式，模拟设备响应用于测试

### 5.7 内部数据工具（日程/待办/记账/健康/习惯/购物/读书）
- **用途**：内部数据 CRUD
- **调用方式**：直接操作 PostgreSQL（通过 SQLAlchemy ORM）
- **输入格式**：LangChain Tool 标准参数格式
- **输出格式**：操作结果 JSON
- **错误处理**：数据库操作失败回滚事务，返回友好提示

## 6. 环境变量完整清单

```bash
# ─── AI 模型 ───
CUSTOM_API_KEY=your-api-key
AI_MODEL=claude-sonnet-4-6
AI_BASE_URL=https://cursor.scihub.edu.kg/api
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=4096

# ─── 数据库 ───
DATABASE_URL=postgresql://user:password@localhost:5432/lifebutler
REDIS_URL=redis://localhost:6379/0

# ─── 加密 ───
SECRET_KEY=your-jwt-secret-key
ENCRYPTION_KEY=your-aes-256-key

# ─── 外部 API ───
QWEATHER_API_KEY=your-qweather-key
AMAP_API_KEY=your-amap-key
QQ_EMAIL_ADDRESS=your-qq-email@qq.com
QQ_EMAIL_AUTH_CODE=your-auth-code
NOTION_API_KEY=your-notion-key
NOTION_DATABASE_ID=your-notion-db-id
```
