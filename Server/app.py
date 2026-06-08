import os
import re
import uuid

from fastapi import FastAPI, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from auth import create_access_token, get_token_from_request, get_current_user, get_current_user_from_request, \
    get_password_hash
from database import get_db
from models import User, Post, Follow, Like
from schemas import ProfileUpdate, PostCreate, AppleLoginRequest

# 上传目录
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# FastAPI应用
app = FastAPI(title="Tagta API")

# 挂载静态文件目录
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# 仅兼容重复斜杠
@app.middleware("http")
async def normalize_request_path(request: Request, call_next):
    path = request.scope.get("path", "")
    normalized_path = re.sub(r"/+", "/", path)

    if normalized_path != path:
        request.scope["path"] = normalized_path

    return await call_next(request)

# 配置跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 苹果登录 API ============

@app.post("/api/apple/login")
def apple_login(data: AppleLoginRequest, response: Response, db=Depends(get_db)):
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
    
    # 写入Cookie
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        max_age=60 * 60 * 24 * 7,
        samesite="lax"
    )
    
    return {
        "success": True,
        "message": "登录成功",
        "user": user.to_dict(),
        "token": token
    }


@app.post("/api/apple/verify")
def apple_verify(data: AppleLoginRequest, db=Depends(get_db)):
    """
    验证苹果登录状态
    """
    user = db.query(User).filter(User.apple_user_id == data.apple_user_id).first()
    if not user:
        return {"success": False, "message": "用户不存在", "verified": False}
    
    return {
        "success": True,
        "verified": True,
        "user": user.to_dict()
    }


@app.post("/api/logout", response_model=dict)
def logout(response: Response):
    """退出登录"""
    response.delete_cookie(key="token")
    return {"success": True, "message": "已退出登录"}


@app.post("/api/me")
def get_me(current_user: User = Depends(get_current_user_from_request)):
    """获取当前用户信息"""
    if not current_user:
        return {"success": False, "message": "未登录"}

    return {"success": True, "user": current_user.to_dict()}


# ============ 用户资料 ============

@app.post("/api/profile")
def update_profile(data: ProfileUpdate, current_user: User = Depends(get_current_user_from_request), db=Depends(get_db)):
    """更新用户资料"""
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


@app.post("/api/users/{user_id}")
def get_user(user_id: int, db=Depends(get_db), request: Request = None):
    """获取用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "message": "用户不存在"}

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


@app.post("/api/users/{user_id}/posts")
def get_user_posts(user_id: int, db=Depends(get_db), request: Request = None):
    """获取用户发布的帖子"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "message": "用户不存在"}

    posts = db.query(Post).filter(Post.user_id == user_id).order_by(Post.created_at.desc()).all()

    liked_post_ids = set()
    token = get_token_from_request(request)
    current_user = get_current_user(token, db)
    if current_user:
        liked_post_ids = {like.post_id for like in db.query(Like).filter(Like.user_id == current_user.id).all()}

    return {"success": True, "posts": [post.to_dict(is_liked=post.id in liked_post_ids) for post in posts]}


# ============ 动态 ============

@app.post("/api/feed")
def get_feed(db=Depends(get_db), request: Request = None):
    """获取关注的人的动态"""
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


@app.post("/api/discover")
def get_discover(db=Depends(get_db), request: Request = None):
    """发现页推荐"""
    token = get_token_from_request(request)
    current_user = get_current_user(token, db)

    # 获取热门帖子
    posts = db.query(Post).order_by(Post.created_at.desc()).limit(20).all()
    
    liked_post_ids = set()
    if current_user:
        liked_post_ids = {like.post_id for like in db.query(Like).filter(Like.user_id == current_user.id).all()}
    
    # 获取推荐用户
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


# ============ 发帖 ============

@app.post("/api/posts")
def create_post(data: PostCreate, current_user: User = Depends(get_current_user_from_request), db=Depends(get_db)):
    """发布新帖"""
    if not current_user:
        return {"success": False, "message": "请先登录"}

    content = data.content.strip() if data.content else ""
    if not content:
        return {"success": False, "message": "内容不能为空"}

    if len(content) > 500:
        return {"success": False, "message": "内容不能超过500字"}

    post = Post(
        user_id=current_user.id,
        content=content,
        media_type=data.media_type or "text",
        image=data.image,
        video=data.video
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    return {"success": True, "message": "发布成功", "post": post.to_dict()}


@app.post("/api/posts/{post_id}/delete")
def delete_post(post_id: int, current_user: User = Depends(get_current_user_from_request), db=Depends(get_db)):
    """删除帖子"""
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


# ============ 关注 ============

@app.post("/api/follow/{user_id}")
def follow_user(user_id: int, current_user: User = Depends(get_current_user_from_request), db=Depends(get_db)):
    """关注用户"""
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


@app.post("/api/follow/{user_id}/unfollow")
def unfollow_user(user_id: int, current_user: User = Depends(get_current_user_from_request), db=Depends(get_db)):
    """取消关注"""
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


@app.post("/api/users/{user_id}/following")
def get_following(user_id: int, db=Depends(get_db)):
    """获取用户的关注列表"""
    if not db.query(User).filter(User.id == user_id).first():
        return {"success": False, "message": "用户不存在"}

    following = db.query(Follow).filter(Follow.follower_id == user_id).all()

    return {"success": True, "users": [f.following.to_dict() for f in following]}


@app.post("/api/users/{user_id}/followers")
def get_followers(user_id: int, db=Depends(get_db)):
    """获取用户的粉丝列表"""
    if not db.query(User).filter(User.id == user_id).first():
        return {"success": False, "message": "用户不存在"}

    followers = db.query(Follow).filter(Follow.following_id == user_id).all()

    return {"success": True, "users": [f.follower.to_dict() for f in followers]}


# ============ 点赞 ============

@app.post("/api/posts/{post_id}/like")
def like_post(post_id: int, current_user: User = Depends(get_current_user_from_request), db=Depends(get_db)):
    """点赞/取消点赞"""
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


# ============ 搜索和推荐 ============

@app.post("/api/search")
def search_users(keyword: str = "", db=Depends(get_db)):
    """搜索用户"""
    if not keyword:
        return {"success": True, "users": []}

    users = db.query(User).filter(
        (User.username.like(f"%{keyword}%")) |
        (User.nickname.like(f"%{keyword}%"))
    ).limit(20).all()

    return {"success": True, "users": [user.to_dict() for user in users]}


@app.post("/api/suggestions")
def get_suggestions(db=Depends(get_db), request: Request = None):
    """获取推荐用户"""
    token = get_token_from_request(request)
    current_user = get_current_user(token, db)

    query = db.query(User)
    if current_user:
        following_ids = [f.following_id for f in db.query(Follow).filter(Follow.follower_id == current_user.id).all()]
        following_ids.append(current_user.id)
        query = query.filter(~User.id.in_(following_ids))

    users = query.order_by(User.created_at.desc()).limit(10).all()

    return {"success": True, "users": [user.to_dict() for user in users]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)