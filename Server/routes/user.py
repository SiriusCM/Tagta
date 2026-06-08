from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models import User, Follow, Post, Like
from schemas import ProfileUpdate
from utils.database import get_db
from utils.auth import get_current_user_from_request, get_token_from_request, get_current_user

router = APIRouter(prefix="/api", tags=["用户"])


@router.post("/profile")
def update_profile(data: ProfileUpdate, request, db: Session = Depends(get_db)):
    """更新用户资料"""
    current_user = get_current_user_from_request(request, db)

    if not current_user:
        return {"success": False, "message": "未登录"}

    if data.nickname is not None:
        current_user.nickname = data.nickname
    if data.bio is not None:
        current_user.bio = data.bio
    if data.avatar is not None:
        current_user.avatar = data.avatar

    db.commit()

    return {"success": True, "message": "更新成功", "user": current_user.to_dict()}


@router.post("/users/{user_id}")
def get_user(user_id: int, request=None, db: Session = Depends(get_db)):
    """获取用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "message": "用户不存在"}

    current_user = None
    if request:
        token = get_token_from_request(request)
        current_user = get_current_user(token, db)

    is_following = False
    if current_user:
        is_following = db.query(Follow).filter_by(
            follower_id=current_user.id,
            following_id=user_id
        ).first() is not None

    return {
        "success": True,
        "user": user.to_dict(),
        "follower_count": db.query(Follow).filter(Follow.following_id == user_id).count(),
        "following_count": db.query(Follow).filter(Follow.follower_id == user_id).count(),
        "post_count": db.query(Post).filter(Post.user_id == user_id).count(),
        "is_following": is_following
    }


@router.post("/users/{user_id}/posts")
def get_user_posts(user_id: int, request=None, db: Session = Depends(get_db)):
    """获取用户发布的帖子"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "message": "用户不存在"}

    posts = db.query(Post).filter(Post.user_id == user_id).order_by(Post.created_at.desc()).all()

    liked_post_ids = set()
    if request:
        token = get_token_from_request(request)
        current_user = get_current_user(token, db)
        if current_user:
            liked_post_ids = {like.post_id for like in db.query(Like).filter(Like.user_id == current_user.id).all()}

    return {"success": True, "posts": [post.to_dict(is_liked=post.id in liked_post_ids) for post in posts]}


@router.post("/search")
def search_users(keyword: str = "", db: Session = Depends(get_db)):
    """搜索用户"""
    if not keyword:
        return {"success": True, "users": []}

    users = db.query(User).filter(
        (User.username.like(f"%{keyword}%")) |
        (User.nickname.like(f"%{keyword}%"))
    ).limit(20).all()

    return {"success": True, "users": [user.to_dict() for user in users]}


