# 功能开发任务清单

## Phase 1: 初始化
- [Done] T-000: 创建项目目录结构（backend + frontend）
- [Done] T-001: 初始化 Python 虚拟环境 + 安装后端依赖（FastAPI, LangChain, SQLAlchemy, etc.）
- [Done] T-002: 初始化 React 前端 + 安装前端依赖（React, TailwindCSS, Zustand, etc.）
- [Done] T-003: 配置环境变量文件（.env.example）+ .gitignore
- [Done] T-004: 配置 PostgreSQL 数据库连接 + Alembic 迁移工具
- [Done] T-005: 配置 Redis 连接
- [Done] T-006: 初始化 Git 仓库并首次提交
- [Done] T-007: 创建 TODO.md / DEV_LOG.md / FAILURES.md
- [Done] T-008: 配置测试框架（pytest + jest + playwright）
- [Done] T-009: 创建 UI_DESIGN_GUIDE.md

## Phase 2: 基础架构（P0 — 必须先完成）
- [Done] T-100: 实现用户注册 API（邮箱+密码，bcrypt 哈希，数据库存储）
- [Done] T-101: 实现用户登录 API（验证密码，生成 JWT Token）
- [Done] T-102: 实现 JWT 认证中间件（Token 校验、用户身份注入）
- [Done] T-103: 实现 AI 模型适配器（CustomAnthropicProvider，支持 claude-sonnet-4-6）
- [Done] T-104: 实现 WebSocket 对话端点（JWT 认证 + 流式响应）
- [Done] T-105: 实现前端登录/注册页面（遵循 UI_DESIGN_GUIDE.md 温暖治愈风格）
- [Done] T-106: 实现前端对话界面（聊天气泡、消息输入框、流式显示）
- [Done] T-107: 实现 LangGraph Agent 核心编排（ReAct 模式，工具路由）
- [Done] T-108: 实现数据加密服务（AES-256 加密/解密 + 密钥管理）
- [Done] T-109: 创建数据库模型（User, ChatHistory 表 + Alembic 迁移）

## Phase 2: 核心功能 — 日程与待办（P0）
- [Done] T-110: 创建数据库模型（CalendarEvent, Todo 表 + 迁移）
- [Done] T-111: 实现日程管理工具（创建/查询/修改/删除日程，重复事件，冲突检测）
- [Done] T-112: 实现待办管理工具（CRUD + 优先级 + 截止日期 + 分类标签）
- [Done] T-113: 将日程/待办工具注册到 Agent，测试自然语言调用

## Phase 2: 核心功能 — 记账理财（P0）
- [Done] T-114: 创建数据库模型（Transaction 表 + 迁移）
- [Done] T-115: 实现记账工具（收支记录、自然语言解析金额/分类/日期）
- [Done] T-116: 实现财务统计（日/周/月统计、分类饼图数据、预算预警）
- [Done] T-117: 财务数据加密存储集成

## Phase 2: 核心功能 — 主动关怀引擎（P0）
- [Done] T-118: 实现主动关怀引擎后端（登录触发、并行查询各模块、AI 组织汇总）
- [Done] T-119: 实现前端今日概览卡片（管家问候 + 分区块展示天气/日程/待办/提醒）
- [Done] T-120: 实现前端底部导航栏 + 页面路由（首页/对话/面板/设置）

## Phase 2: 重要功能（P1）
- [Done] T-121: 创建数据库模型（MealRecord, Habit, HabitCheckIn 表 + 迁移）
- [Done] T-122: 实现天气查询工具（和风天气 API 接入、实时天气+7日预报+穿衣建议）
- [Done] T-123: 实现饮食健康工具（饮食记录 + 简单营养估算 + 饮水提醒）
- [Done] T-124: 实现习惯打卡工具（创建习惯、打卡、连续天数统计、断签提醒）
- [Done] T-125: 创建数据库模型（ShoppingItem 表 + 迁移）
- [Done] T-126: 实现购物清单工具（添加/分类/勾选已购/清空已购）
- [Done] T-127: 实现邮件管理工具（QQ 邮箱 IMAP 收件 + SMTP 发件 + AI 摘要）
- [Done] T-128: 实现出行规划工具（高德地图路线规划 + POI 搜索）
- [Done] T-129: 创建数据库模型（Note 表 + 迁移）
- [Done] T-130: 实现备忘笔记工具（本地 CRUD + Notion API 同步 + 失败降级）
- [Done] T-131: 将所有 P1 工具注册到 Agent，测试自然语言调用

## Phase 2: 辅助功能（P2）
- [Done] T-132: 实现新闻摘要工具（RSS 聚合 + AI 摘要生成）
- [Done] T-133: 创建数据库模型（ReadingPlan 表 + 迁移）
- [Done] T-134: 实现读书学习工具（计划创建 + 进度追踪 + 落后提醒）
- [Done] T-135: 实现智能家居工具（通用适配器接口 + Mock 设备测试）

## Phase 2: 前端完善
- [Todo] T-136: 实现数据面板页（记账图表、打卡日历、习惯统计）
- [Todo] T-137: 实现设置页（个人信息、API 配置、默认城市、常用地址）
- [Todo] T-138: 实现侧边栏（桌面端展开、移动端隐藏，功能分组导航）
- [Todo] T-139: 响应式布局适配（mobile / tablet / desktop 三断点）
- [Done] T-140: 暗色模式支持（跟随系统 + 手动切换）

## Phase 2: 部署与收尾
- [Todo] T-141: 编写 Dockerfile（backend + frontend）
- [Todo] T-142: 编写 docker-compose.yml（含 PostgreSQL + Redis）
- [Todo] T-143: 端到端集成测试（完整用户流程：注册→登录→对话→各功能）
- [Todo] T-144: 性能优化（API 响应、前端首屏加载、数据库查询）
- [Todo] T-145: 安全审查（SQL 注入、XSS、CSRF、敏感数据泄露检查）

## 状态说明
- [Todo]        待开发
- [In Progress] 开发中
- [Done]        已完成
- [Failed]      开发失败（详见 FAILURES.md）
