#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tagta API 入口文件
"""

import re
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routes import auth_router, user_router, post_router, follow_router
from config import settings as config
from models import Base
from utils.database import engine

# 创建数据库表
Base.metadata.create_all(bind=engine)

# FastAPI应用
app = FastAPI(title="Tagta API")

# 上传目录
UPLOAD_DIR = config.UPLOAD_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)

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


# 注册路由
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(post_router)
app.include_router(follow_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)