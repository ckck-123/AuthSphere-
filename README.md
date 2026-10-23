# #云帆・企业级权限管理平台

基于 **FastAPI + MySQL + SQLAlchemy 2.0** 的通用管理系统后端，实现了完整的**用户 / 角色 / 权限（RBAC）**管理，并集成了 **JWT 认证、Redis 缓存、消息队列**。

## 技术栈

- Web 框架：FastAPI + Uvicorn
- ORM：SQLAlchemy 2.0 + PyMySQL
- 数据库：MySQL
- 认证：JWT（python-jose）+ 密码哈希（bcrypt）
- 缓存：Redis（用户列表缓存、登录 token 黑名单）
- 消息队列：基于 Redis List 的轻量队列（操作日志异步落库）

## 目录结构

```
backend/
├─ main.py                 # 应用入口
├─ .env / .env.example     # 配置文件
├─ requirements.txt
└─ app/
   ├─ core/                # 配置、安全、依赖注入、Redis
   ├─ db/                  # 引擎、会话、建表与种子
   ├─ models/              # User / Role / Permission / OperationLog
   ├─ schemas/             # Pydantic 校验模型
   ├─ services/            # 业务逻辑层
   ├─ api/v1/              # 路由（认证/用户/角色/权限）
   ├─ tasks/               # 消息队列（生产者/消费者）
   └─ utils/               # 统一响应
```

## 快速启动

### 1. 准备数据库

在 MySQL 里建库（如果还没有）：

```sql
CREATE DATABASE IF NOT EXISTS fastapi_admin DEFAULT CHARACTER SET utf8mb4;
```

### 2. 改配置

编辑 `backend/.env`，把数据库账号、Redis 地址改成你本机的：

```
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的密码
DB_NAME=fastapi_admin

REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=          # 没设密码就留空
```

### 3. 装依赖（在 backend 目录）

```bash
pip install -r requirements.txt
# 或用 uv:
# uv add -r requirements.txt
```

### 4. 初始化数据库（建表 + 初始账号）

```bash
python -m app.db.init_db
```

> 初始账号：`admin / admin123`（超级管理员）

### 5. 启动消息队列消费者（可选，用于操作日志落库）

```bash
python -m app.tasks.consumer
```

> 不启动也没关系，接口照常工作，只是操作日志暂时不写库。

### 6. 启动服务

```bash
uvicorn main:app --reload
# 用 uv：uv run uvicorn main:app --reload
```

### 7. 打开文档

- Swagger 调试：http://127.0.0.1:8000/docs
- ReDoc 阅读：http://127.0.0.1:8000/redoc

## 接口清单

| 模块  | 方法                  | 路径                     | 权限           | 说明          |
| --- | ------------------- | ---------------------- | ------------ | ----------- |
| 认证  | POST                | /api/v1/auth/login     | 公开           | 登录，返回 token |
| 认证  | POST                | /api/v1/auth/logout    | 登录           | 登出，token 拉黑 |
| 认证  | GET                 | /api/v1/auth/me        | 登录           | 当前用户信息      |
| 用户  | GET                 | /api/v1/users          | user:read    | 分页列表（带缓存）   |
| 用户  | POST                | /api/v1/users          | user:create  | 新增用户        |
| 用户  | GET                 | /api/v1/users/{id}     | user:read    | 用户详情        |
| 用户  | PUT                 | /api/v1/users/{id}     | user:update  | 修改用户/角色     |
| 用户  | DELETE              | /api/v1/users/{id}     | user:delete  | 删除用户        |
| 角色  | GET/POST/PUT/DELETE | /api/v1/roles...       | role:*       | 角色管理        |
| 权限  | GET/POST/DELETE     | /api/v1/permissions... | permission:* | 权限管理        |

## 权限（RBAC）机制

- 用户 多对多 角色，角色 多对多 权限。
- 每个接口通过 `Depends(require_permission("user:create"))` 做鉴权。
- `admin` 是超级管理员，**绕过所有权限校验**。
- 非超管用户是否放行，取决于他所有角色合并起来的权限集合。

## 本项目的三个亮点（学习重点）

### 1. JWT 登录 + 登出黑名单

- 登录签发 JWT，token 里带 `user_id`。
- 登出时把 token 存进 Redis 黑名单，`get_current_user` 每次先查黑名单，实现"立即失效"。

### 2. Redis 缓存

- 用户列表接口先查 Redis，命中直接返回，30 秒过期。
- 增删改用户时主动清空相关缓存，避免脏数据。

### 3. 消息队列解耦

- 登录、增删改用户/角色/权限时，生产者只往 Redis 队列塞一条"操作日志"消息。
- 消费者进程（`app/tasks/consumer.py`）异步读取并写入 MySQL，接口不用等落库。

## 常见问题

- **连接 MySQL 失败**：检查 `.env` 账号密码、库是否存在、MySQL 服务是否启动。
- **登录报"无权限"**：确认当前用户挂的角色拥有对应权限编码，或用超管账号。
- **Redis 没启动**：接口仍可用（已做降级），但缓存、黑名单、日志队列不生效。
