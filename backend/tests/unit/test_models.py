"""
测试基础数据库模型 — User, ChatHistory
"""
import pytest
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config.database import Base
from app.models.user import User
from app.models.chat import ChatHistory


@pytest.fixture
async def db_session():
    """创建内存数据库测试会话"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


class TestUserModel:
    """User 模型测试"""

    @pytest.mark.asyncio
    async def test_create_user(self, db_session):
        """TC-109-1: 创建用户"""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
            nickname="测试用户"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.nickname == "测试用户"
        assert user.is_active is True
        assert user.created_at is not None

    @pytest.mark.asyncio
    async def test_user_unique_email(self, db_session):
        """用户邮箱唯一性"""
        user1 = User(email="dup@test.com", hashed_password="hash1")
        db_session.add(user1)
        await db_session.commit()

        user2 = User(email="dup@test.com", hashed_password="hash2")
        db_session.add(user2)
        with pytest.raises(Exception):
            await db_session.commit()


class TestChatHistoryModel:
    """ChatHistory 模型测试"""

    @pytest.mark.asyncio
    async def test_create_chat_history(self, db_session):
        """创建聊天记录"""
        user = User(email="chat@test.com", hashed_password="hash")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        chat = ChatHistory(
            user_id=user.id,
            role="user",
            content="你好，帮我查看今天的日程"
        )
        db_session.add(chat)
        await db_session.commit()
        await db_session.refresh(chat)

        assert chat.id is not None
        assert chat.user_id == user.id
        assert chat.role == "user"
        assert chat.content == "你好，帮我查看今天的日程"
