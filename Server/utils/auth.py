from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from models import User
from utils.redis_client import get_user_id_by_token, refresh_token
from utils.database import SessionLocal


def get_identity_token_from_request(request: Request) -> str:
    """从请求中获取 identityToken，支持 Bearer 前缀"""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    # 支持 "Bearer <token>" 和直接传 token 两种格式
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return auth_header


def get_current_user(request: Request, db: Session = None) -> User:
    """根据 identityToken 获取当前用户，未登录返回 None"""
    identity_token = get_identity_token_from_request(request)
    if not identity_token:
        return None

    # 从 Redis 获取 user_id
    user_id = get_user_id_by_token(identity_token)
    if not user_id:
        return None

    # 仅在 Token 剩余时间不足 5 分钟时刷新，减少 Redis 写入
    from utils.redis_client import redis_client
    ttl = redis_client.ttl(f"token:{identity_token}")
    if ttl is not None and 0 < ttl < 300:
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
    """获取当前用户，未登录则抛出 401 异常"""
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录"
        )
    return user