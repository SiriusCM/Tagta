import os
import uuid
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from config import settings as config
from models import User

# JWT密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer Token 认证
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """哈希密码"""
    return pwd_context.hash(password)


def create_access_token(user_id: int, expires_delta: int = None) -> str:
    """创建访问令牌"""
    expire = datetime.utcnow() + timedelta(
        minutes=expires_delta or config.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = {"exp": expire, "user_id": user_id}
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)


def decode_token(token: str) -> dict:
    """解码令牌"""
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token_from_request(request: Request) -> str:
    """从请求中获取令牌"""
    # 从Header获取
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]

    # 从Cookie获取
    return request.cookies.get("token")


def get_current_user(token: str, db: Session) -> User:
    """根据令牌获取当前用户"""
    if not token:
        return None

    payload = decode_token(token)
    if not payload:
        return None

    user_id = payload.get("user_id")
    if not user_id:
        return None

    return db.query(User).filter(User.id == user_id).first()


def get_current_user_from_request(request: Request, db: Session = None) -> User:
    """从请求中获取当前用户"""
    from utils.database import SessionLocal

    token = get_token_from_request(request)
    if not token:
        return None

    # 如果没有提供db，创建一个
    if db is None:
        db = SessionLocal()
        try:
            return get_current_user(token, db)
        finally:
            db.close()

    return get_current_user(token, db)