import redis
from config import settings as config

# Redis 连接
redis_client = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    password=config.REDIS_PASSWORD if config.REDIS_PASSWORD else None,
    db=config.REDIS_DB,
    decode_responses=True
)


def set_token(token: str, user_id: int, expire_seconds: int = None) -> bool:
    """
    存储 identityToken -> user_id 到 Redis
    :param token: identityToken
    :param user_id: 用户ID
    :param expire_seconds: 过期时间（秒），默认30分钟
    :return: 是否成功
    """
    expire = expire_seconds or config.TOKEN_EXPIRE_SECONDS
    return redis_client.setex(f"token:{token}", expire, user_id)


def get_user_id_by_token(token: str) -> int:
    """
    根据 identityToken 获取用户ID
    :param token: identityToken
    :return: 用户ID，不存在返回 None
    """
    result = redis_client.get(f"token:{token}")
    return int(result) if result else None


def delete_token(token: str) -> bool:
    """
    删除 token
    :param token: identityToken
    :return: 是否成功
    """
    return redis_client.delete(f"token:{token}") > 0


def refresh_token(token: str, expire_seconds: int = None) -> bool:
    """
    刷新 token 过期时间
    :param token: identityToken
    :param expire_seconds: 新的过期时间
    :return: 是否成功
    """
    expire = expire_seconds or config.TOKEN_EXPIRE_SECONDS
    return redis_client.expire(f"token:{token}", expire)