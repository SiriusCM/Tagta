from fastapi import APIRouter, Depends, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from typing import Optional

from models import User, Follow, Post, Like
from schemas import ProfileUpdate
from utils.database import get_db
from utils.auth import get_current_user_from_request, get_token_from_request, get_current_user
from utils.oss_uploader import upload_media

router = APIRouter(prefix="/api", tags=["用户"])


@router.post("/profile")
async def update_profile(
    request: Request,
    nickname: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    avatar_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """更新用户资料，支持 multipart 上传头像"""
    current_user = get_current_user_from_request(request, db)

    if not current_user:
        return {"success": False, "message": "未登录"}

    if nickname is not None:
        current_user.nickname = nickname
    if bio is not None:
        current_user.bio = bio

    if avatar_file:
        file_content = await avatar_file.read()
        if len(file_content) > 10 * 1024 * 1024:
            return {"success": False, "message": "头像大小不能超过10MB"}
        success, url, error = upload_media(file_content, avatar_file.filename, 'image')
        if not success:
            return {"success": False, "message": f"头像上传失败: {error}"}
        current_user.avatar = url

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


