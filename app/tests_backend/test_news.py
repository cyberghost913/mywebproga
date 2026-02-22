import pytest
from fastapi.testclient import TestClient
from app.news.schemas import NewsIn, NewsUpdate
from unittest.mock import AsyncMock, patch, ANY, MagicMock

@pytest.mark.asyncio
class TestNewsUrls:
    async def test_get_all_news(
        self, 
        test_client: TestClient, 
        mock_redis, 
        mock_db_session
    ):
        with patch('app.news.urls.NewsService.get_news') as mock_get_news:
            mock_get_news.return_value = [
                {
                    "id": 1,
                    "header": "Test News 1",
                    "content": {"text": "Content 1"},
                    "author_id": 1,
                    "author_name": "testuser",
                    "date": "2023-01-01T00:00:00"
                }
            ]
            response = test_client.get("/news/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["header"] == "Test News 1"
        mock_get_news.assert_called_once()

    async def test_get_one_news(
        self, 
        test_client: TestClient, 
        mock_redis, 
        mock_db_session
    ):
        with patch('app.news.urls.NewsService.get_one_news') as mock_get_one:
            mock_get_one.return_value = {
                "id": 1,
                "header": "Test News",
                "content": {"text": "Test content"},
                "author_id": 1,
                "author_name": "testuser",
                "date": "2023-01-01T00:00:00"
            }
            response = test_client.get("/news/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        mock_get_one.assert_called_once_with(1)

    async def test_get_one_news_not_found(
        self, 
        test_client: TestClient, 
        mock_redis, 
        mock_db_session
    ):
        with patch('app.news.urls.NewsService.get_one_news') as mock_get_one:
            mock_get_one.return_value = None
            response = test_client.get("/news/999")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "News not found"

    