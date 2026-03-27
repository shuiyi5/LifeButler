"""
API 依赖注入
"""
from fastapi import Depends
from app.config.database import get_db
