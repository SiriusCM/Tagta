import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from schemas import AppleLoginRequest
from utils.auth import create_access_token, get_password_hash
from models import User
from utils.database import get_db

router = APIRouter(prefix="/api", tags=["认证"])


@router.post("/apple/login")
def apple_login(data: AppleLoginRequest, db: Session = Depends(get_db)):
    """
    苹果登录API
    用于iOS App的苹果登录验证
    """
    apple_user_id = data.apple_user_id

    if not apple_user_id:
        return {"success": False, "message": "缺少Apple用户ID"}

    # 查找是否已存在该Apple用户
    user = db.query(User).filter(User.apple_user_id == apple_user_id).first()

    if not user:
        # 新用户，自动注册
        random_id = str(uuid.uuid4())[:8]
        username = f"user_{random_id}"
        email = f"{random_id}@apple.user"

        from utils.auth import get_password_hash

        user = User(
            username=username,
            email=email,
            password=get_password_hash(str(uuid.uuid4())),
            nickname=f"用户{random_id[:4]}",
            apple_user_id=apple_user_id
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 创建访问令牌
    token = create_access_token(user.id)

    return {
        "success": True,
        "message": "登录成功",
        "user": user.to_dict(),
        "token": token
    }


@router.post("/apple/verify")
def apple_verify(data: AppleLoginRequest, db: Session = Depends(get_db)):
    """验证苹果登录状态"""
    user = db.query(User).filter(User.apple_user_id == data.apple_user_id).first()
    if not user:
        return {"success": False, "message": "用户不存在", "verified": False}

    return {
        "success": True,
        "verified": True,
        "user": user.to_dict()
    }


