from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from models import User
from utils.redis_client import get_user_id_by_token, refresh_token
from utils.database import SessionLocal


def get_identity_token_from_request(request: Request) -> str:
    """从请求中获取 identityToken"""
    # 从 Header 获取
    return request.headers.get("Authorization")


def get_current_user(request: Request, db: Session = None) -> User:
    """根据 identityToken 获取当前用户"""
    identity_token = get_identity_token_from_request(request)
    if not identity_token:
        return None

    # 从 Redis 获取 user_id
    user_id = get_user_id_by_token(identity_token)
    if not user_id:
        return None

    # 刷新 token 过期时间
    refresh_token(identity_token)

    # 查询用户
    if db is None:
        db = SessionLocal()
        try:
            return db.query(User).filter(User.id == user_id).first()
        finally:
            db.close()

    return db.query(User).filter(User.id == user_id).first()


def get_current_user_required(request: Request, db: Session = None) -> User:
    """获取当前用户，未登录则抛出异常"""
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录"
        )
    return user