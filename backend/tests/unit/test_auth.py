"""
测试用户认证 — 注册、登录、JWT 校验
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.config.database import Base, engine


@pytest.fixture(autouse=True)
async def setup_db():
    """每个测试前创建表，测试后删除"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    """异步测试客户端"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestRegister:
    """用户注册测试"""

    @pytest.mark.asyncio
    async def test_register_success(self, client):
        """TC-100-1: 有效邮箱注册成功"""
        response = await client.post("/api/auth/register", json={
            "email": "new@test.com",
            "password": "password123"
        })
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["email"] == "new@test.com"
        assert data["user_id"] > 0

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client):
        """TC-100-2: 重复邮箱注册失败"""
        await client.post("/api/auth/register", json={
            "email": "dup@test.com",
            "password": "password123"
        })
        response = await client.post("/api/auth/register", json={
            "email": "dup@test.com",
            "password": "password456"
        })
        assert response.status_code == 409


class TestLogin:
    """用户登录测试"""

    @pytest.mark.asyncio
    async def test_login_success(self, client):
        """TC-101-1: 正确密码登录成功"""
        await client.post("/api/auth/register", json={
            "email": "login@test.com",
            "password": "password123"
        })
        response = await client.post("/api/auth/login", json={
            "email": "login@test.com",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client):
        """TC-101-2: 错误密码登录失败"""
        await client.post("/api/auth/register", json={
            "email": "wrong@test.com",
            "password": "password123"
        })
        response = await client.post("/api/auth/login", json={
            "email": "wrong@test.com",
            "password": "wrongpass"
        })
        assert response.status_code == 401


class TestJWTAuth:
    """JWT 认证测试"""

    @pytest.mark.asyncio
    async def test_valid_token(self, client):
        """TC-102-1: 有效 Token 通过验证"""
        reg = await client.post("/api/auth/register", json={
            "email": "jwt@test.com",
            "password": "password123"
        })
        token = reg.json()["access_token"]
        response = await client.get("/api/health", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_invalid_token(self, client):
        """TC-102-2: 无效 Token 拒绝"""
        from app.services.auth import decode_token
        result = decode_token("invalid.token.here")
        assert result is None
