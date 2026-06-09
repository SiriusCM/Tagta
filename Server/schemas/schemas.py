from pydantic import BaseModel
from typing import Optional


class AppleLoginRequest(BaseModel):
    """苹果登录请求：仅接收 identity_token，服务端自行验证并解析用户信息"""
    identity_token: str  # Apple 的 identityToken（JWT）
    full_name: Optional[str] = None  # 全名（仅首次登录由 iOS 提供，不在 JWT 中）


class TokenVerifyRequest(BaseModel):
    """Token 校验请求"""
    token: str


class ProfileUpdate(BaseModel):
    """更新用户资料"""
    nickname: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None


class PostCreate(BaseModel):
    """发布帖子"""
    content: str
    media_type: Optional[str] = "text"  # text/image/video
    image: Optional[str] = None
    video: Optional[str] = None