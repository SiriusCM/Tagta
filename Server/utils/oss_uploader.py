#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
京东OSS文件上传工具
用于上传图片和视频到京东OSS
"""

import os
import uuid
from datetime import datetime
from typing import Optional, Tuple
import boto3
from botocore.config import Config
from config import settings as config


class JDOssUploader:
    """京东OSS文件上传器类"""

    def __init__(self):
        """初始化上传器，从配置读取京东OSS配置"""
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f"https://{config.JD_OSS_ENDPOINT}",
            aws_access_key_id=config.JD_OSS_ACCESS_KEY,
            aws_secret_access_key=config.JD_OSS_SECRET_KEY,
            config=Config(
                s3={'payload_signing_enabled': False},
                parameter_validation=False
            )
        )
        self.bucket_name = config.JD_OSS_BUCKET

    def _get_file_extension(self, filename: str) -> str:
        """获取文件扩展名"""
        return os.path.splitext(filename)[1].lower() if filename else ''

    def _validate_extension(self, filename: str, media_type: str) -> None:
        """校验文件扩展名是否合法，不合法则抛出 ValueError"""
        ext = self._get_file_extension(filename)
        if media_type == 'image':
            allowed = config.ALLOWED_IMAGE_EXTENSIONS
        elif media_type == 'video':
            allowed = config.ALLOWED_VIDEO_EXTENSIONS
        else:
            return  # 其他类型不校验
        if not ext or ext not in allowed:
            raise ValueError(f"不支持的文件格式 {ext}，允许的格式: {', '.join(sorted(allowed))}")

    def _generate_s3_key(self, filename: str, media_type: str) -> str:
        """
        生成OSS存储路径

        Args:
            filename: 原始文件名
            media_type: 媒体类型 (image/video)

        Returns:
            OSS存储路径
        """
        ext = self._get_file_extension(filename)

        unique_id = uuid.uuid4().hex
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        new_filename = f"{timestamp}_{unique_id}{ext}"

        subdir = 'images' if media_type == 'image' else 'videos'

        return f"{config.JD_OSS_PREFIX}medias/{subdir}/{new_filename}"

    def _get_content_type(self, filename: str) -> str:
        """根据文件扩展名获取Content-Type"""
        import mimetypes
        content_type, _ = mimetypes.guess_type(filename)

        type_mapping = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.mp4': 'video/mp4',
            '.mov': 'video/quicktime',
            '.avi': 'video/x-msvideo',
            '.webm': 'video/webm',
        }

        ext = self._get_file_extension(filename)
        return type_mapping.get(ext, content_type or 'application/octet-stream')

    def upload_file(self, file_content: bytes, filename: str, media_type: str = 'image') -> Tuple[bool, str, str]:
        """
        上传文件到OSS

        Args:
            file_content: 文件内容(字节)
            filename: 原始文件名
            media_type: 媒体类型 (image/video)

        Returns:
            (是否成功, 文件URL, 错误信息)
        """
        try:
            # 校验文件扩展名
            self._validate_extension(filename, media_type)

            s3_key = self._generate_s3_key(filename, media_type)
            content_type = self._get_content_type(filename)

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type
            )

            file_url = f"https://{self.bucket_name}.{config.JD_OSS_ENDPOINT}/{s3_key}"

            return True, file_url, ""

        except Exception as e:
            return False, "", str(e)

    def upload_image(self, file_content: bytes, filename: str) -> Tuple[bool, str, str]:
        """上传图片"""
        return self.upload_file(file_content, filename, 'image')

    def upload_video(self, file_content: bytes, filename: str) -> Tuple[bool, str, str]:
        """上传视频"""
        return self.upload_file(file_content, filename, 'video')


# 创建单例上传器实例
oss_uploader = JDOssUploader()


def upload_media(file_content: bytes, filename: str, media_type: str = 'image') -> Tuple[bool, str, str]:
    """上传媒体文件的便捷函数"""
    return oss_uploader.upload_file(file_content, filename, media_type)
    def upload_video(self, file_content: bytes, filename: str) -> Tuple[bool, str, str]:
        """上传视频"""
        return self.upload_file(file_content, filename, 'video')


# 创建单例上传器实例
oss_uploader = JDOssUploader()


def upload_media(file_content: bytes, filename: str, media_type: str = 'image') -> Tuple[bool, str, str]:
    """上传媒体文件的便捷函数"""
    return oss_uploader.upload_file(file_content, filename, media_type)