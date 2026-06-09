import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from schemas import AppleLoginRequest, TokenVerifyRequest
from utils.apple_auth import verify_apple_identity_token, get_or_create_user_by_apple_payload
from utils.redis_client import set_token, get_user_id_by_token, delete_token
from models import User
from utils.database import get_db

router = APIRouter(prefix="/api", tags=["认证"])


class LogoutRequest(BaseModel):
    token: str


@router.get("/test")
def test():
    """测试接口"""
    return {"status": "ok", "message": "后端正常"}


@router.post("/apple/login")
def apple_login(data: AppleLoginRequest, db: Session = Depends(get_db)):
    """
    苹果登录 API
    仅接收 identityToken，服务端自行向 Apple 验证 JWT 签名并解析用户信息。
    """
    identity_token = data.identity_token
    if not identity_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="缺少 identityToken")

    # 向 Apple 验证 JWT 签名并解析 payload
    try:
        payload = verify_apple_identity_token(identity_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Apple Token 验证失败: {str(e)}"
        )

    apple_user_id = payload.get("sub")
    if not apple_user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无法从 Apple Token 解析用户标识")

    # 查找或创建用户（基于 JWT 解析出的信息）
    user = get_or_create_user_by_apple_payload(payload, db)

    # 若首次登录且 iOS 提供了 full_name，则更新
    if data.full_name and not user.full_name:
        user.full_name = data.full_name
        # 同时用 full_name 作为默认昵称（若尚未设置）
        if not user.nickname or user.nickname.startswith("用户"):
            user.nickname = data.full_name
        db.commit()
        db.refresh(user)

    # 将 identityToken -> user_id 存入 Redis（30分钟过期）
    set_token(identity_token, user.id)

    return {
        "message": "登录成功",
        "user": user.to_dict(),
        "token": identity_token  # 返回给客户端作为会话凭证
    }


@router.post("/apple/verify")
def apple_verify(data: TokenVerifyRequest, db: Session = Depends(get_db)):
    """验证登录状态（根据后端 Redis 中的 Token）"""
    if not data.token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="缺少 token")

    user_id = get_user_id_by_token(data.token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token 已过期或无效")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    return {
        "verified": True,
        "user": user.to_dict()
    }


@router.post("/logout")
def logout(data: LogoutRequest):
    """登出"""
    if not data.token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="缺少 token")
    delete_token(data.token)
    return {"message": "登出成功"}