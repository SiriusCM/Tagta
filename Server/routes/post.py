from fastapi import APIRouter, Depends, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from typing import Optional

from models import User, Post, Follow, Like
from schemas import PostCreate
from utils.auth import get_token_from_request, get_current_user
from utils.oss_uploader import upload_media
from utils.database import get_db

router = APIRouter(prefix="/api", tags=["帖子"])


def get_current_user_from_request(request, db: Session):
    """从请求中获取当前用户"""
    token = get_token_from_request(request)
    return get_current_user(token, db)


@router.post("/feed")
def get_feed(request=None, db: Session = Depends(get_db)):
    """获取关注的人的动态"""
    current_user = None
    if request:
        token = get_token_from_request(request)
        current_user = get_current_user(token, db)

    user_id = current_user.id if current_user else None

    if user_id:
        following_ids = [f.following_id for f in db.query(Follow).filter(Follow.follower_id == user_id).all()]
        following_ids.append(user_id)
        posts = db.query(Post).filter(Post.user_id.in_(following_ids)).order_by(Post.created_at.desc()).limit(20).all()
    else:
        posts = db.query(Post).order_by(Post.created_at.desc()).limit(20).all()

    liked_post_ids = set()
    if current_user:
        liked_post_ids = {like.post_id for like in db.query(Like).filter(Like.user_id == current_user.id).all()}

    return {"success": True, "posts": [post.to_dict(is_liked=post.id in liked_post_ids) for post in posts]}


@router.post("/discover")
def get_discover(request=None, db: Session = Depends(get_db)):
    """发现页推荐"""
    current_user = None
    if request:
        token = get_token_from_request(request)
        current_user = get_current_user(token, db)

    # 获取热门帖子
    posts = db.query(Post).order_by(Post.created_at.desc()).limit(20).all()

    liked_post_ids = set()
    if current_user:
        liked_post_ids = {like.post_id for like in db.query(Like).filter(Like.user_id == current_user.id).all()}

    # 获取推荐用户
    from models import User
    query = db.query(User)
    if current_user:
        following_ids = [f.following_id for f in db.query(Follow).filter(Follow.follower_id == current_user.id).all()]
        following_ids.append(current_user.id)
        query = query.filter(~User.id.in_(following_ids))

    suggested_users = query.order_by(User.created_at.desc()).limit(10).all()

    return {
        "success": True,
        "posts": [post.to_dict(is_liked=post.id in liked_post_ids) for post in posts],
        "suggested_users": [user.to_dict() for user in suggested_users]
    }


@router.post("/posts")
async def create_post(
    request: Request,
    content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    data: Optional[PostCreate] = None,
    db: Session = Depends(get_db)
):
    """发布新帖，支持同时上传图片或视频
    
    支持两种格式:
    1. multipart/form-data: content (Form) + file (File)
    2. application/json: {content, media_type?, image?, video?}
    """
    current_user = get_current_user_from_request(request, db)

    if not current_user:
        return {"success": False, "message": "请先登录"}

    # 处理 JSON 格式请求
    if data is not None:
        content_text = data.content.strip() if data.content else ""
        if not content_text:
            return {"success": False, "message": "内容不能为空"}

        if len(content_text) > 500:
            return {"success": False, "message": "内容不能超过500字"}

        post = Post(
            user_id=current_user.id,
            content=content_text,
            media_type=data.media_type or "text",
            image=data.image,
            video=data.video
        )
        db.add(post)
        db.commit()
        db.refresh(post)

        return {"success": True, "message": "发布成功", "post": post.to_dict()}

    # 处理 multipart/form-data 格式
    if content is None:
        return {"success": False, "message": "内容不能为空"}

    content_text = content.strip()
    if not content_text:
        return {"success": False, "message": "内容不能为空"}

    if len(content_text) > 500:
        return {"success": False, "message": "内容不能超过500字"}

    # 处理文件和媒体类型
    image_url = None
    video_url = None
    media_type = "text"

    if file:
        # 根据文件类型判断是图片还是视频
        content_type = file.content_type or ""

        if content_type.startswith('image/'):
            media_type = "image"
            file_content = await file.read()

            # 检查文件大小 (最大10MB)
            if len(file_content) > 10 * 1024 * 1024:
                return {"success": False, "message": "图片大小不能超过10MB"}

            # 上传到OSS
            success, image_url, error = upload_media(file_content, file.filename, 'image')
            if not success:
                return {"success": False, "message": f"图片上传失败: {error}"}

        elif content_type.startswith('video/'):
            media_type = "video"
            file_content = await file.read()

            # 检查文件大小 (最大100MB)
            if len(file_content) > 100 * 1024 * 1024:
                return {"success": False, "message": "视频大小不能超过100MB"}

            # 上传到OSS
            success, video_url, error = upload_media(file_content, file.filename, 'video')
            if not success:
                return {"success": False, "message": f"视频上传失败: {error}"}
        else:
            return {"success": False, "message": "不支持的文件类型"}

    # 创建帖子
    post = Post(
        user_id=current_user.id,
        content=content_text,
        media_type=media_type,
        image=image_url,
        video=video_url
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    return {"success": True, "message": "发布成功", "post": post.to_dict()}


@router.post("/posts/{post_id}/delete")
def delete_post(post_id: int, request, db: Session = Depends(get_db)):
    """删除帖子"""
    current_user = get_current_user_from_request(request, db)

    if not current_user:
        return {"success": False, "message": "请先登录"}

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return {"success": False, "message": "帖子不存在"}

    if post.user_id != current_user.id:
        return {"success": False, "message": "无权删除"}

    db.delete(post)
    db.commit()

    return {"success": True, "message": "删除成功"}


@router.post("/posts/{post_id}/like")
def like_post(post_id: int, request, db: Session = Depends(get_db)):
    """点赞/取消点赞"""
    current_user = get_current_user_from_request(request, db)

    if not current_user:
        return {"success": False, "message": "请先登录"}

    if not db.query(Post).filter(Post.id == post_id).first():
        return {"success": False, "message": "帖子不存在"}

    existing = db.query(Like).filter_by(user_id=current_user.id, post_id=post_id).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {"success": True, "message": "已取消点赞"}

    like = Like(user_id=current_user.id, post_id=post_id)
    db.add(like)
    db.commit()

    return {"success": True, "message": "点赞成功"}