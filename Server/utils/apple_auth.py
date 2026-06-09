import jwt
from jwt import PyJWKClient
from sqlalchemy.orm import Session
from config import settings as config
from models import User

# Apple JWKS 客户端（自动缓存公钥）
_jwks_client = None


def _get_jwks_client():
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = PyJWKClient(config.APPLE_JWKS_URL, cache_keys=True)
    return _jwks_client


def verify_apple_identity_token(identity_token: str) -> dict:
    """
    验证 Apple identityToken 的 JWT 签名并返回 Payload。

    :param identity_token: Apple 登录返回的 identityToken
    :return: 解析后的 JWT payload（包含 sub, email, email_verified 等）
    :raises: jwt.InvalidTokenError 及其子类（签名验证失败、过期、audience 不匹配等）
    """
    jwks_client = _get_jwks_client()
    signing_key = jwks_client.get_signing_key_from_jwt(identity_token)

    payload = jwt.decode(
        identity_token,
        signing_key.key,
        algorithms=["RS256"],
        audience=config.APPLE_CLIENT_ID,
        issuer=config.APPLE_ISSUER,
    )
    return payload


def get_or_create_user_by_apple_payload(payload: dict, db: Session) -> User:
    """
    根据 Apple JWT Payload 查找或创建用户。

    :param payload: verify_apple_identity_token 返回的 payload
    :param db: 数据库会话
    :return: User 对象
    """
    apple_user_id = payload.get("sub")
    if not apple_user_id:
        raise ValueError("Apple JWT 中缺少 sub（apple_user_id）")

    email = payload.get("email")
    email_verified = payload.get("email_verified", False)

    user = db.query(User).filter(User.apple_user_id == apple_user_id).first()

    if not user:
        import uuid
        random_id = str(uuid.uuid4())[:8]
        username = f"user_{random_id}"

        nickname = email.split("@")[0] if email else f"用户{random_id[:4]}"

        user = User(
            username=username,
            email=email if email_verified else None,
            nickname=nickname,
            apple_user_id=apple_user_id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # 若邮箱更新且已验证，同步更新
        if email and email_verified and user.email != email:
            existing = db.query(User).filter(User.email == email, User.id != user.id).first()
            if not existing:
                user.email = email
                db.commit()
                db.refresh(user)

    return user