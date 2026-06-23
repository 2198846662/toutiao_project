# 头条新闻项目

基于 **FastAPI + Vue 3** 的新闻资讯项目，包含新闻浏览、用户系统、收藏、浏览历史、AI 问答、多轮会话记忆、Redis 可选缓存和管理员后台。

## 技术栈

- 后端：FastAPI、SQLAlchemy Async、MySQL、Pydantic、Passlib/bcrypt、Redis、HTTPX
- 前端：Vue 3、Vite、Pinia、Vue Router、Vant、Axios
- AI：兼容 OpenAI Chat Completions 格式的大模型接口，例如阿里云 DashScope
- 数据库：MySQL 8+
- 缓存：Redis，可选启用

## 已实现功能

- 新闻分类、新闻列表、新闻详情、相关推荐
- 用户注册、登录、获取用户信息、修改资料、修改密码
- 新闻收藏、取消收藏、收藏状态检查、收藏列表、清空收藏
- 浏览历史添加、分页列表、删除单条历史、清空历史
- AI 问答，支持流式回复、会话列表、历史消息加载和多轮上下文记忆
- AI 本地聊天状态按用户隔离，避免不同账号之间串号
- Redis 缓存新闻分类、新闻列表、新闻详情和相关新闻
- Redis 默认关闭，未启动 Redis 时项目仍会直接查询 MySQL
- 管理员后台，支持数据概览、新闻管理、分类管理、用户列表
- 管理员后台新闻支持按关键词、分类筛选，支持新增、编辑、删除
- 管理员后台采用桌面端全宽布局，前台移动端页面仍保留移动端宽度

## 目录结构

```text
toutiao_project
├── toutiao_backend       # FastAPI 后端
│   ├── cache             # 缓存封装
│   ├── config            # 数据库、Redis、AI 配置
│   ├── crud              # 数据库操作
│   ├── models            # SQLAlchemy 模型
│   ├── routers           # API 路由
│   ├── schemas           # Pydantic 数据模型
│   ├── sql               # 数据库初始化 SQL
│   ├── tests             # 后端契约测试
│   └── main.py
├── toutiao_frontend      # Vue 前端
│   ├── src
│   │   ├── api           # API 封装
│   │   ├── components
│   │   ├── config
│   │   ├── router
│   │   ├── store
│   │   └── views
│   └── package.json
└── README.md
```

## 环境准备

需要提前安装：

- Python 3.10+
- Node.js 18+
- MySQL 8+
- Redis，可选

## 后端启动

进入后端目录：

```bash
cd toutiao_backend
```

安装依赖：

```bash
pip install fastapi uvicorn sqlalchemy aiomysql pydantic passlib bcrypt redis httpx python-multipart
```

如果你使用的是本项目开发环境，也可以直接使用已有 Conda 环境：

```powershell
D:\miniconda3\envs\fastapi-learning\python.exe main.py
```

初始化数据库：

```sql
source sql/news_app.sql;
```

也可以在 Navicat 中执行：

```text
toutiao_backend/sql/news_app.sql
```

数据库连接配置位于：

```text
toutiao_backend/config/db_conf.py
```

默认配置：

```python
DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/news_app?charset=utf8mb4"
```

如果你的 MySQL 用户名、密码或端口不同，需要修改这里。

启动后端：

```bash
python main.py
```

后端默认地址：

```text
http://127.0.0.1:8000
```

接口文档：

```text
http://127.0.0.1:8000/docs
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

前端默认地址：

```text
http://localhost:5173
```

前端默认请求后端地址：

```js
// toutiao_frontend/src/config/api.js
baseURL: 'http://127.0.0.1:8000'
```

如果后端地址变化，需要同步修改这里。

## 环境变量

后端会读取：

```text
toutiao_backend/.env
```

可以参考：

```text
toutiao_backend/.env.example
```

AI 配置示例：

```env
AI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
AI_API_KEY=your-api-key
AI_MODEL=qwen3-max-preview
```

注意：如果 `AI_BASE_URL` 填成完整的 `/chat/completions` 地址，后端会自动裁剪成基础地址再拼接。

Redis 默认关闭，不配置也可以正常运行。如果需要启用 Redis 缓存，再添加：

```env
REDIS_ENABLED=true
REDIS_HOST=192.168.152.128
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=xcl123456
REDIS_TIMEOUT=1
```

如果后续想关闭 Redis：

```env
REDIS_ENABLED=false
```

或者删除 `REDIS_ENABLED` 这一行。默认就是关闭。

## 管理员后台

后台地址：

```text
http://localhost:5173/admin
```

访问后台需要登录管理员账号。权限由 `user` 表的 `role` 字段控制：

```text
admin  管理员
user   普通用户
```

如果要把某个账号设为管理员，可以在 MySQL 中执行：

```sql
UPDATE user SET role = 'admin' WHERE username = '你的用户名';
```

管理后台功能：

- 数据概览
- 新闻列表、关键词模糊查询、分类筛选
- 新闻新增、编辑、删除
- 分类新增、编辑、删除
- 用户列表查看

后台接口采用资源型路径：

```text
GET    /api/admin/dashboard
GET    /api/admin/news
POST   /api/admin/news
PUT    /api/admin/news/{news_id}
DELETE /api/admin/news/{news_id}
GET    /api/admin/categories
POST   /api/admin/categories
PUT    /api/admin/categories/{category_id}
DELETE /api/admin/categories/{category_id}
GET    /api/admin/users
```

## 常用接口

用户：

```text
POST /api/user/register
POST /api/user/login
GET  /api/user/info
PUT  /api/user/update
PUT  /api/user/password
```

新闻：

```text
GET /api/news/categories
GET /api/news/list?categoryId=1&page=1&pageSize=10
GET /api/news/detail?id=4
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
Authorization: Bearer 登录后返回的 token
```

## AI 记忆机制

AI 问答相关数据使用两张表保存：

```text
ai_chat_session   # 会话表
ai_chat_message   # 消息表
```

流程：

1. 用户第一次提问时，后端创建一个 `session_id`。
2. 后端通过响应头 `X-Session-Id` 返回会话 ID。
3. 前端保存当前会话 ID。
4. 后续同一会话继续提问时，前端带上 `session_id`。
5. 后端查询该用户、该会话下的历史消息，并一起发送给大模型。
6. 模型回复后，用户消息和 AI 回复都会写入数据库。

前端也会在本地保存当前聊天状态，但已经按用户隔离，避免 A 用户看到 B 用户的本地聊天内容。退出后再次登录同一个账号，进入 AI 页面会自动加载最近一次历史会话。

## Redis 缓存说明

Redis 只用于提升新闻相关接口性能，不是项目运行的强依赖。

缓存范围：

- 新闻分类
- 新闻列表
- 新闻详情
- 相关新闻

默认情况下：

```env
REDIS_ENABLED=false
```

此时项目不会连接 Redis，新闻接口会直接查询 MySQL。

如果启用 Redis 但 Redis 服务不可达，后端设置了短超时并会降级查询 MySQL，避免接口长时间卡住。

## 前端页面

主要页面：

```text
/home              新闻首页
/news/detail/:id   新闻详情
/category          分类页
/favorite          我的收藏
/history           浏览历史
/aichat            AI 问答
/my                我的页面
/profile           个人资料
/admin             管理员后台
```

前台页面采用移动端布局，管理员后台采用桌面端全宽布局。

## 测试

后端测试使用 Python 标准库 `unittest`。

在后端目录执行：

```bash
cd toutiao_backend
python -m unittest discover tests
```

如果你使用项目开发环境：

```powershell
cd D:\python_learning\toutiao_project\toutiao_backend
D:\miniconda3\envs\fastapi-learning\python.exe -m unittest discover tests
```

前端构建验证：

```bash
cd toutiao_frontend
npm run build
```

## 常见问题

### 1. Redis 没启动，项目能运行吗？

可以。默认 `REDIS_ENABLED=false`，项目不会连接 Redis，新闻接口直接查 MySQL。

### 2. 改了 `.env` 后为什么没有生效？

需要重启后端。`--reload` 不一定会因为 `.env` 改动而重启进程。

### 3. 新闻列表或新闻详情不显示

优先检查：

- 后端是否启动在 `http://127.0.0.1:8000`
- `/api/news/list?categoryId=1&page=1&pageSize=10` 是否能返回数据
- 前端 `src/config/api.js` 的 `baseURL` 是否正确
- 如果刚改过 Redis 配置，重启后端

### 4. AI 提示 API_KEY 未配置

检查 `toutiao_backend/.env` 中是否填写：

```env
AI_API_KEY=your-api-key
```

修改后需要重启后端。

### 5. 管理后台看不到入口

只有 `role = 'admin'` 的账号在“我的”页面能看到管理后台入口。

### 6. 管理后台显示比例不对

后台已经单独脱离前台移动端 750px 容器限制。如果仍异常，刷新页面或重启前端开发服务器。

## 注意事项

- 不要把真实 `.env`、数据库密码、Redis 密码、AI API Key 上传到 GitHub。
- `.gitignore` 已忽略 `.env`、`__pycache__/`、`*.pyc` 和 `dist/`。
- 上传 GitHub 前建议检查是否存在真实密钥或本机路径。
- 生产环境建议将数据库、Redis、AI 配置全部改为环境变量管理。
