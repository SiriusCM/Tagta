from pydantic import BaseModel
from typing import Optional

class AppleLoginRequest(BaseModel):
    """苹果登录请求"""
    apple_user_id: str
    authorization_code: Optional[str] = None
    identity_token: Optional[str] = None

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