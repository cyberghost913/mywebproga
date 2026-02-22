import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
from app.users.models import User

            
@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def test_user():
    user = MagicMock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.is_active = True
    return user

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}

@pytest.fixture(autouse=True)
def auto_mock_oauth(test_user):
    """Автоматически мокает get_oauth_user для всех тестов"""
    with patch('app.news.urls.get_oauth_user', return_value=test_user):
        yield

@pytest_asyncio.fixture
async def mock_redis():
    redis_mock = AsyncMock()
    redis_mock.get.return_value = None
    redis_mock.setex.return_value = AsyncMock()
    redis_mock.delete.return_value = 1
    with patch('app.add_redis.get_redis', return_value=redis_mock):
        yield redis_mock

@pytest_asyncio.fixture
async def mock_db_session():
    db_mock = AsyncMock()
    with patch('app.database.get_db_session', return_value=db_mock):
        yield db_mock


@pytest.fixture
def mock_check_user_permission():
    """Мокаем check_user_permission"""
    with patch('app.auth.depends.check_user_permission') as mock:
        mock.return_value = None
        yield mock