"""
认证相关的 Pydantic 模型
"""
from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    """注册请求"""
    email: str = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, max_length=128, description="密码")


class LoginRequest(BaseModel):
    """登录请求"""
    email: str = Field(..., description="邮箱地址")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    nickname: str = ""


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    email: str
    nickname: str = ""
    is_active: bool = True
