"""
中間件配置
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging

from .config import settings

logger = logging.getLogger(__name__)


def setup_middleware(app: FastAPI):
    """
    設置應用中間件
    
    Args:
        app: FastAPI 應用實例
    """
    
    # CORS 中間件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    )
    
    # 可信主機中間件
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.TRUSTED_HOSTS
    )
    
    logger.info("中間件配置完成")
