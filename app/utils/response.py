"""
统一响应格式。所有接口返回：
{
  "code": 0,        # 0 成功，非0 失败
  "message": "success",
  "data": {...}     # 业务数据
}
"""
from typing import Any, Optional

from pydantic import BaseModel


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None


def ok(data: Any = None, message: str = "success") -> ApiResponse:
    """成功响应"""
    return ApiResponse(code=0, message=message, data=data)


def fail(code: int, message: str, data: Any = None) -> ApiResponse:
    """失败响应，code 非 0 表示错误类型"""
    return ApiResponse(code=code, message=message, data=data)
