"""
FastAPI 云帆・企业级权限管理平台。
启动：uv run uvicorn main:app --reload
文档：/docs  或  /redoc
"""
from fastapi import FastAPI

from app.api.v1.router import api_router
from app.utils.response import ApiResponse, ok

app = FastAPI(
    title="云帆・企业级权限管理平台",
    description="用户 / 角色 / 权限 RBAC 管理，含 JWT 认证、Redis 缓存、消息队列日志",
    version="1.0.0",
)

app.include_router(api_router)


@app.get("/", response_model=ApiResponse, summary="健康检查")
def root():
    return ok({"msg": "FastAPI 管理后台运行中"})
