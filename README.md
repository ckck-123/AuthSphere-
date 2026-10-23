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