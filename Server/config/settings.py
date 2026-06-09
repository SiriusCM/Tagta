import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class Settings:
    """应用配置类"""

    # 数据库配置
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "tagta")

    @property
    def DATABASE_URL(self) -> str:
        """生成 PostgreSQL 数据库连接 URL"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Redis 配置
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))

    @property
    def REDIS_URL(self) -> str:
        """生成 Redis 连接 URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # Token 过期时间（秒）
    TOKEN_EXPIRE_SECONDS = int(os.getenv("TOKEN_EXPIRE_SECONDS", "1800"))  # 30分钟

    # 服务器配置
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8080"))

    # 上传配置
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB

    # 京东OSS配置
    JD_OSS_BUCKET = os.getenv("JD_OSS_BUCKET", "")
    JD_OSS_ENDPOINT = os.getenv("JD_OSS_ENDPOINT", "")
    JD_OSS_ACCESS_KEY = os.getenv("JD_OSS_ACCESS_KEY", "")
    JD_OSS_SECRET_KEY = os.getenv("JD_OSS_SECRET_KEY", "")
    JD_OSS_PREFIX = os.getenv("JD_OSS_PREFIX", "")

    # 允许的图片格式
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

    # 允许的视频格式
    ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.webm'}

    # Apple 登录配置
    APPLE_CLIENT_ID = os.getenv("APPLE_CLIENT_ID", "com.sirius.tagta")
    APPLE_ISSUER = "https://appleid.apple.com"
    APPLE_JWKS_URL = "https://appleid.apple.com/auth/keys"


# 创建配置实例
settings = Settings()