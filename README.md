# 头条新闻项目

基于 FastAPI + Vue 3 的新闻资讯项目，包含新闻浏览、用户登录注册、收藏、浏览历史、Redis 缓存和 AI 问答功能。

## 技术栈

- 后端：FastAPI、SQLAlchemy Async、MySQL、Redis、Pydantic、Passlib/bcrypt
- 前端：Vue 3、Vite、Pinia、Vue Router、Vant、Axios
- AI：兼容 OpenAI Chat Completions 格式的大模型接口，例如阿里云 DashScope

## 主要功能

- 新闻分类、新闻列表、新闻详情、相关推荐
- 用户注册、登录、获取用户信息、修改资料、修改密码
- 新闻收藏、取消收藏、收藏列表、清空收藏
- 浏览历史添加、分页列表、删除单条历史、清空历史
- Redis 缓存新闻分类、新闻列表、新闻详情、相关新闻
- AI 问答，支持会话列表和多轮上下文记忆
- 管理后台，支持数据概览、新闻管理、分类管理、用户列表

## 目录结构

```text
toutiao_project
├── toutiao_backend     # FastAPI 后端
├── toutiao_frontend    # Vue 前端
└── README.md
```

## 环境准备

需要提前安装：

- Python 3.10+
- Node.js 18+
- MySQL 8+
- Redis，可选但推荐启动

Redis 当前用于缓存新闻数据。如果 Redis 服务未启动，项目会回退查询 MySQL，功能仍可用，但控制台会打印缓存连接失败日志。

## 后端启动

进入后端目录：

```bash
cd toutiao_backend
```

安装依赖，按你的环境选择执行：

```bash
pip install fastapi uvicorn sqlalchemy aiomysql pydantic passlib bcrypt redis httpx
```

初始化数据库：

```sql
source sql/database.sql;
```

或在 Navicat 中执行 `toutiao_backend/sql/database.sql`。

配置数据库连接：

```python
# toutiao_backend/config/db_conf.py
DATABASE_URL = "mysql+aiomysql://用户名:密码@localhost:3306/news_app?charset=utf8mb4"
```

配置 Redis：

```python
# toutiao_backend/config/cache_conf.py
host = "你的Redis地址"
port = 6379
password = "你的Redis密码"
```

配置 AI 环境变量，在 `toutiao_backend/.env` 中填写：

```env
AI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
AI_API_KEY=你的API_KEY
AI_MODEL=qwen3-max-preview
```

启动后端：

```bash
python main.py
```

后端默认地址：

```text
http://127.0.0.1:8000
```

## 前端启动

进入前端目录：

```bash
cd toutiao_frontend
```

安装依赖：

```bash
npm install
```

启动开发服务器：

```bash
npm run dev
```

前端默认请求后端地址：

```js
// toutiao_frontend/src/config/api.js
baseURL: 'http://127.0.0.1:8000'
```

如果后端地址变化，需要同步修改这里。

## 常用接口

用户：

```text
POST /api/user/register
POST /api/user/login
GET  /api/user/info
PUT  /api/user/update
PUT  /api/user/password
```

管理后台：

```text
GET    /api/admin/dashboard
GET    /api/admin/news/list
POST   /api/admin/news/add
PUT    /api/admin/news/update/{news_id}
DELETE /api/admin/news/delete/{news_id}
GET    /api/admin/category/list
POST   /api/admin/category/add
PUT    /api/admin/category/update/{category_id}
DELETE /api/admin/category/delete/{category_id}
GET    /api/admin/users/list
```

新闻：

```text
GET /api/news/categories
GET /api/news/list
GET /api/news/detail
```

收藏：

```text
GET    /api/favorite/check
POST   /api/favorite/add
DELETE /api/favorite/remove
GET    /api/favorite/list
DELETE /api/favorite/clear
```

浏览历史：

```text
POST   /api/history/add
GET    /api/history/list
DELETE /api/history/delete/{history_id}
DELETE /api/history/clear
```

AI 问答：

```text
POST /api/ai/chat
GET  /api/ai/sessions
GET  /api/ai/sessions/{session_id}/messages
```

登录后的接口需要请求头：

```text
Authorization: Bearer 登录后返回的token
```

管理后台页面：

```text
http://localhost:5173/admin
```

访问后台需要登录管理员账号。`user` 表通过 `role` 字段区分权限：

```text
admin  管理员
user   普通用户
```

## AI 记忆说明

AI 问答使用两张表保存上下文：

```text
ai_chat_session   # 会话表
ai_chat_message   # 消息表
```

前端第一次提问时后端创建会话，并返回 `X-Session-Id`。后续同一会话继续提问时，后端会查询该会话下的历史消息，一起发送给大模型，从而实现多轮记忆。

## 常见问题

### 1. AI 提示 API_KEY 未配置

检查 `toutiao_backend/.env` 是否存在，并重启后端。

### 2. AI 提示数据库操作失败

检查数据库是否已经创建 `ai_chat_session` 和 `ai_chat_message` 两张表，并确认字段和 `sql/database.sql` 一致。

### 3. Redis 没启动项目能不能运行

可以运行。Redis 连接失败时会返回 `None`，新闻接口会继续查 MySQL，只是不会使用缓存。

### 4. 前端请求不到后端

检查：

- 后端是否运行在 `http://127.0.0.1:8000`
- 前端 `src/config/api.js` 中的 `baseURL` 是否正确
- 后端 CORS 配置是否允许当前前端地址

## 注意事项

- 不要把真实 `.env`、数据库密码、Redis 密码、AI API Key 上传到 GitHub。
- `.gitignore` 已忽略 `.env`、`__pycache__/`、`*.pyc` 和 `dist/`。
- 生产环境建议将数据库、Redis、AI 配置改为环境变量管理。
