# LifeButler — 个人生活管家agent

> 一个主动关怀型 AI 生活管家，通过自然语言对话管理你的日程、财务、健康、出行等 15 大生活场景，像贴心管家一样主动提醒和照顾你。

## 功能特性

- 📅 **日程管理**：创建、查询、修改日程事件，智能冲突检测
- ✅ **待办管理**：任务增删、优先级排序、完成追踪、截止日期提醒
- 🔔 **智能提醒**：登录时主动推送待处理事项、纪念日、账单提醒
- 🌤️ **天气查询**：每日天气播报、穿衣建议、极端天气预警
- 📰 **新闻摘要**：每日热点资讯简报、个性化推荐
- 💰 **记账理财**：收支记录、分类统计、月度报表、预算预警
- 🍽️ **饮食健康**：饮食记录、营养分析、饮水提醒、健康建议
- 🏃 **习惯打卡**：习惯追踪、连续打卡统计、成就系统
- 🛒 **购物清单**：商品添加、分类管理、购买勾选、清单分享
- 📚 **读书学习**：阅读计划、进度追踪、学习提醒、笔记记录
- 🏠 **智能家居**：通用设备控制接口（预留，支持未来接入米家/HomeKit等）
- 📧 **邮件管理**：QQ 邮箱收件摘要、智能分类、快捷回复
- 🗺️ **出行规划**：路线推荐、实时交通、打车比价、周边搜索
- 💬 **自然语言对话**：用日常聊天方式操作所有功能
- 📝 **备忘笔记**：快速记录想法，自动同步到 Notion

## 技术栈

| 类别 | 技术 |
|------|------|
| 语言 | Python 3.11+ / TypeScript |
| 后端框架 | FastAPI |
| 前端框架 | React 18 + TailwindCSS |
| AI 框架 | LangChain / LangGraph |
| 数据库 | PostgreSQL + Redis |
| 测试 | pytest + Jest + Playwright |

## 快速启动

### 环境要求
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose（推荐）

### 安装步骤
```bash
# 1. 克隆项目
git clone <repo-url>
cd LifeButler

# 2. 安装后端依赖
cd backend
pip install -r requirements.txt

# 3. 安装前端依赖
cd ../frontend
npm install

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key

# 5. 初始化数据库
cd ../backend
alembic upgrade head

# 6. 启动项目
# 后端
uvicorn app.main:app --reload --port 8000
# 前端（新终端）
cd frontend && npm run dev
```

### Docker 一键启动（推荐）
```bash
docker-compose up -d
```

## 项目结构

```
LifeButler/
├── backend/                  # Python 后端
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── agent/           # Agent 核心逻辑
│   │   │   ├── core.py      # LangChain Agent 编排
│   │   │   ├── memory.py    # 对话记忆管理
│   │   │   └── proactive.py # 主动关怀引擎
│   │   ├── tools/           # Agent 工具集
│   │   │   ├── calendar.py  # 日程管理
│   │   │   ├── todo.py      # 待办管理
│   │   │   ├── weather.py   # 天气查询
│   │   │   ├── news.py      # 新闻摘要
│   │   │   ├── finance.py   # 记账理财
│   │   │   ├── health.py    # 饮食健康
│   │   │   ├── habit.py     # 习惯打卡
│   │   │   ├── shopping.py  # 购物清单
│   │   │   ├── reading.py   # 读书学习
│   │   │   ├── smarthome.py # 智能家居
│   │   │   ├── email.py     # 邮件管理
│   │   │   ├── travel.py    # 出行规划
│   │   │   └── notion.py    # Notion 同步
│   │   ├── api/             # API 路由
│   │   │   ├── auth.py      # 认证接口
│   │   │   ├── chat.py      # 对话接口
│   │   │   └── dashboard.py # 数据面板接口
│   │   ├── models/          # 数据库模型
│   │   ├── schemas/         # Pydantic 模型
│   │   ├── services/        # 业务逻辑层
│   │   ├── config/          # 配置管理
│   │   └── utils/           # 工具函数
│   ├── tests/               # 测试文件
│   ├── alembic/             # 数据库迁移
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 # React 前端
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/      # 通用组件
│   │   ├── pages/           # 页面
│   │   ├── hooks/           # 自定义 Hooks
│   │   ├── stores/          # 状态管理
│   │   ├── services/        # API 调用
│   │   ├── styles/          # 全局样式
│   │   └── utils/           # 工具函数
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── TODO.md
├── DEV_LOG.md
└── FAILURES.md
```

## 变更历史

| 版本 | 日期 | 描述 |
|------|------|------|
| v1.0 | 2025-01-01 | 初始版本 — 15 大功能模块 |
