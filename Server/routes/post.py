from fastapi import APIRouter, Depends, UploadFile, File, Form, Request, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from models import User, Post, Follow, Like
from utils.auth import get_current_user, get_current_user_required
from utils.oss_uploader import upload_media
from utils.database import get_db

router = APIRouter(prefix="/api", tags=["帖子"])

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


@router.post("/feed")
def get_feed(
    request: Request,
    skip: int = 0,
    limit: int = DEFAULT_PAGE_SIZE,
    db: Session = Depends(get_db)
):
    """获取关注的人的动态"""
    if limit > MAX_PAGE_SIZE:
        limit = MAX_PAGE_SIZE

    current_user = get_current_user(request, db)

    user_id = current_user.id if current_user else None

    if user_id:
        following_ids = [f.following_id for f in db.query(Follow).filter(Follow.follower_id == user_id).all()]
        following_ids.append(user_id)
        posts = (
            db.query(Post)
            .filter(Post.user_id.in_(following_ids))
            .order_by(Post.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    else:
        posts = (
            db.query(Post)
            .order_by(Post.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    liked_post_ids = set()
    if current_user:
        liked_post_ids = {like.post_id for like in db.query(Like).filter(Like.user_id == current_user.id).all()}

    return {"posts": [post.to_dict(is_liked=post.id in liked_post_ids) for post in posts]}


@router.post("/discover")
def get_discover(
    request: Request,
    skip: int = 0,
    limit: int = DEFAULT_PAGE_SIZE,
    db: Session = Depends(get_db)
):
    """发现页推荐"""
    if limit > MAX_PAGE_SIZE:
        limit = MAX_PAGE_SIZE

    current_user = get_current_user(request, db)

    posts = (
        db.query(Post)
        .order_by(Post.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    liked_post_ids = set()
    if current_user:
        liked_post_ids = {like.post_id for like in db.query(Like).filter(Like.user_id == current_user.id).all()}

    # 获取推荐用户
    from models import User as UserModel
    query = db.query(UserModel)
    if current_user:
        following_ids = [f.following_id for f in db.query(Follow).filter(Follow.follower_id == current_user.id).all()]
        following_ids.append(current_user.id)
        query = query.filter(~UserModel.id.in_(following_ids))

    suggested_users = query.order_by(UserModel.created_at.desc()).limit(10).all()

    return {
        "posts": [post.to_dict(is_liked=post.id in liked_post_ids) for post in posts],
        "suggested_users": [user.to_dict() for user in suggested_users]
    }


@router.post("/posts")
async def create_post(
    request: Request,
    content: Optional[str] = Form(None),
    media_type: Optional[str] = Form("text"),
    image: Optional[str] = Form(None),
    video: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """发布新帖，支持同时上传图片或视频

    支持两种格式:
    1. multipart/form-data: content (Form) + file (File)
    2. application/x-www-form-urlencoded: content + media_type + image + video
    """
    current_user = get_current_user_required(request, db)

    if content is None or not content.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="内容不能为空")

    content_text = content.strip()
    if len(content_text) > 500:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="内容不能超过500字")

    # 处理文件和媒体类型
    image_url = image
    video_url = video
    final_media_type = media_type or "text"

    if file:
        content_type = file.content_type or ""

        if content_type.startswith('image/'):
            final_media_type = "image"
            file_content = await file.read()

            if len(file_content) > 10 * 1024 * 1024:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="图片大小不能超过10MB")

            success, image_url, error = upload_media(file_content, file.filename, 'image')
            if not success:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"图片上传失败: {error}")

        elif content_type.startswith('video/'):
            final_media_type = "video"
            file_content = await file.read()

            if len(file_content) > 100 * 1024 * 1024:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="视频大小不能超过100MB")

            success, video_url, error = upload_media(file_content, file.filename, 'video')
            if not success:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"视频上传失败: {error}")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的文件类型")

    post = Post(
        user_id=current_user.id,
        content=content_text,
        media_type=final_media_type,
        image=image_url,
        video=video_url
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    return {"message": "发布成功", "post": post.to_dict()}


@router.post("/posts/{post_id}/delete")
def delete_post(post_id: int, request: Request, db: Session = Depends(get_db)):
    """删除帖子"""
    current_user = get_current_user_required(request, db)

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")

    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除")

    db.delete(post)
    db.commit()

    return {"message": "删除成功"}


@router.post("/posts/{post_id}/like")
def like_post(post_id: int, request: Request, db: Session = Depends(get_db)):
    """点赞/取消点赞"""
    current_user = get_current_user_required(request, db)

    if not db.query(Post).filter(Post.id == post_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")

    existing = db.query(Like).filter_by(user_id=current_user.id, post_id=post_id).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {"message": "已取消点赞"}

    like = Like(user_id=current_user.id, post_id=post_id)
    db.add(like)
    db.commit()

    return {"message": "点赞成功"}