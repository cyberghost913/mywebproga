from fastapi import APIRouter, Depends
from typing import Annotated
from .schemas import NewsRead, NewsBase
from ..auth.depends import get_oauth_user
from ..users.models import User
from .service import NewsService, get_news_service

router = APIRouter()

@router.post("/", response_model=NewsRead)
async def create_news(news: NewsBase,
                      current_user: User = Depends(get_oauth_user),
                      service: NewsService = Depends(get_news_service)):
    return await service.add_news(news, current_user)

@router.get("/", response_model=list[NewsRead])
async def read_news (_: Annotated[User, Depends(get_oauth_user)],
                     service: NewsService = Depends(get_news_service)):
    return await service.get_news()

@router.put("/{news_id}", response_model=NewsRead)
async def update_news(news_id: int,
                      news_data: NewsBase,
                      current_user: User = Depends(get_oauth_user),
                      service: NewsService = Depends(get_news_service)):
    return await service.edit_news(news_id, news_data, current_user)

@router.delete("/{news_id}")
async def delete_news(news_id: int,
                      current_user: User = Depends(get_oauth_user),
                      service: NewsService = Depends(get_news_service)):
    return await service.remove_news(news_id, current_user)