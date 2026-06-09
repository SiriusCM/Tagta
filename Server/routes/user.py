from fastapi import APIRouter, Depends, UploadFile, File, Form, Request, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from models import User, Follow, Post, Like
from schemas import ProfileUpdate
from utils.database import get_db
from utils.auth import get_current_user
from utils.oss_uploader import upload_media


class SearchRequest(BaseModel):
    keyword: str = ""
    skip: int = 0
    limit: int = 20

router = APIRouter(prefix="/api", tags=["用户"])

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


@router.post("/profile")
async def update_profile(
    request: Request,
    nickname: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    avatar_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """更新用户资料，支持 multipart 上传头像"""
    current_user = get_current_user(request, db)

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录")

    if nickname is not None:
        current_user.nickname = nickname
    if bio is not None:
        current_user.bio = bio

    if avatar_file:
        file_content = await avatar_file.read()
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="头像大小不能超过10MB")
        success, url, error = upload_media(file_content, avatar_file.filename, 'image')
        if not success:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"头像上传失败: {error}")
        current_user.avatar = url

    db.commit()

    return {"user": current_user.to_dict()}


@router.post("/users/{user_id}")
def get_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """获取用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    current_user = get_current_user(request, db)

    is_following = False
    if current_user:
        is_following = db.query(Follow).filter_by(
            follower_id=current_user.id,
            following_id=user_id
        ).first() is not None

    return {
        "user": user.to_dict(),
        "follower_count": db.query(Follow).filter(Follow.following_id == user_id).count(),
        "following_count": db.query(Follow).filter(Follow.follower_id == user_id).count(),
        "post_count": db.query(Post).filter(Post.user_id == user_id).count(),
        "is_following": is_following
    }


@router.post("/users/{user_id}/posts")
def get_user_posts(
    user_id: int,
    request: Request,
    skip: int = 0,
    limit: int = DEFAULT_PAGE_SIZE,
    db: Session = Depends(get_db)
):
    """获取用户发布的帖子"""
    if limit > MAX_PAGE_SIZE:
        limit = MAX_PAGE_SIZE

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    posts = (
        db.query(Post)
        .filter(Post.user_id == user_id)
        .order_by(Post.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    liked_post_ids = set()
    current_user = get_current_user(request, db)
    if current_user:
        liked_post_ids = {like.post_id for like in db.query(Like).filter(Like.user_id == current_user.id).all()}

    return {"posts": [post.to_dict(is_liked=post.id in liked_post_ids) for post in posts]}


@router.post("/search")
def search_users(
    data: SearchRequest,
    db: Session = Depends(get_db)
):
    """搜索用户"""
    limit = data.limit
    if limit > MAX_PAGE_SIZE:
        limit = MAX_PAGE_SIZE

    if not data.keyword:
        return {"users": []}

    users = (
        db.query(User)
        .filter(
            (User.username.like(f"%{data.keyword}%")) |
            (User.nickname.like(f"%{data.keyword}%"))
        )
        .offset(data.skip)
        .limit(limit)
        .all()
    )

    return {"users": [user.to_dict() for user in users]}