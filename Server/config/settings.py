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

    # JWT 配置
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

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


# 创建配置实例
settings = Settings()