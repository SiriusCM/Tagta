from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session

from models import User, Follow
from utils.auth import get_current_user
from utils.database import get_db

router = APIRouter(prefix="/api", tags=["关注"])

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def get_current_user_from_request(request: Request, db: Session):
    """从请求中获取当前用户"""
    return get_current_user(request, db)


@router.post("/follow/{user_id}")
def follow_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    """关注用户"""
    current_user = get_current_user_from_request(request, db)

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")

    if current_user.id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能关注自己")

    if not db.query(User).filter(User.id == user_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    existing = db.query(Follow).filter_by(
        follower_id=current_user.id,
        following_id=user_id
    ).first()

    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="已经关注了")

    follow = Follow(follower_id=current_user.id, following_id=user_id)
    db.add(follow)
    db.commit()

    return {"message": "关注成功"}


@router.post("/follow/{user_id}/unfollow")
def unfollow_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    """取消关注"""
    current_user = get_current_user_from_request(request, db)

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")

    follow = db.query(Follow).filter_by(
        follower_id=current_user.id,
        following_id=user_id
    ).first()

    if not follow:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="尚未关注")

    db.delete(follow)
    db.commit()

    return {"message": "取消关注成功"}


@router.post("/users/{user_id}/following")
def get_following(
    user_id: int,
    skip: int = 0,
    limit: int = DEFAULT_PAGE_SIZE,
    db: Session = Depends(get_db)
):
    """获取用户的关注列表"""
    if limit > MAX_PAGE_SIZE:
        limit = MAX_PAGE_SIZE

    if not db.query(User).filter(User.id == user_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    following = (
        db.query(Follow)
        .filter(Follow.follower_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {"users": [f.following.to_dict() for f in following]}


@router.post("/users/{user_id}/followers")
def get_followers(
    user_id: int,
    skip: int = 0,
    limit: int = DEFAULT_PAGE_SIZE,
    db: Session = Depends(get_db)
):
    """获取用户的粉丝列表"""
    if limit > MAX_PAGE_SIZE:
        limit = MAX_PAGE_SIZE

    if not db.query(User).filter(User.id == user_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    followers = (
        db.query(Follow)
        .filter(Follow.following_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {"users": [f.follower.to_dict() for f in followers]}