from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models import User, Follow
from utils.auth import get_token_from_request, get_current_user
from utils.database import get_db

router = APIRouter(prefix="/api", tags=["关注"])


def get_current_user_from_request(request, db: Session):
    """从请求中获取当前用户"""
    token = get_token_from_request(request)
    return get_current_user(token, db)


@router.post("/follow/{user_id}")
def follow_user(user_id: int, request, db: Session = Depends(get_db)):
    """关注用户"""
    current_user = get_current_user_from_request(request, db)

    if not current_user:
        return {"success": False, "message": "请先登录"}

    if current_user.id == user_id:
        return {"success": False, "message": "不能关注自己"}

    if not db.query(User).filter(User.id == user_id).first():
        return {"success": False, "message": "用户不存在"}

    existing = db.query(Follow).filter_by(
        follower_id=current_user.id,
        following_id=user_id
    ).first()

    if existing:
        return {"success": False, "message": "已经关注了"}

    follow = Follow(follower_id=current_user.id, following_id=user_id)
    db.add(follow)
    db.commit()

    return {"success": True, "message": "关注成功"}


@router.post("/follow/{user_id}/unfollow")
def unfollow_user(user_id: int, request, db: Session = Depends(get_db)):
    """取消关注"""
    current_user = get_current_user_from_request(request, db)

    if not current_user:
        return {"success": False, "message": "请先登录"}

    follow = db.query(Follow).filter_by(
        follower_id=current_user.id,
        following_id=user_id
    ).first()

    if not follow:
        return {"success": False, "message": "尚未关注"}

    db.delete(follow)
    db.commit()

    return {"success": True, "message": "取消关注成功"}


@router.post("/users/{user_id}/following")
def get_following(user_id: int, db: Session = Depends(get_db)):
    """获取用户的关注列表"""
    if not db.query(User).filter(User.id == user_id).first():
        return {"success": False, "message": "用户不存在"}

    following = db.query(Follow).filter(Follow.follower_id == user_id).all()

    return {"success": True, "users": [f.following.to_dict() for f in following]}


@router.post("/users/{user_id}/followers")
def get_followers(user_id: int, db: Session = Depends(get_db)):
    """获取用户的粉丝列表"""
    if not db.query(User).filter(User.id == user_id).first():
        return {"success": False, "message": "用户不存在"}

    followers = db.query(Follow).filter(Follow.following_id == user_id).all()

    return {"success": True, "users": [f.follower.to_dict() for f in followers]}