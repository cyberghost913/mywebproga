from fastapi import Depends
from sqlalchemy import select, delete
import json
from ..database import get_db_session
from .models import News
from ..comments.models import Comment
from ..auth.depends import check_author_permission, check_user_permission
from ..add_redis import get_redis
from ..add_logs import news_log

class NewsService:
    def __init__(self, db = Depends(get_db_session), redis = Depends(get_redis)):
        self.db = db
        self.redis = redis

    async def add_news(self, news, current_user):
        await check_author_permission(current_user) 
        news_data = news.model_dump()
        news_data["author_id"] = current_user.id
        new_news = News(**news_data) 
        self.db.add(new_news)
        await self.db.commit()
        await self.db.refresh(new_news)
        return new_news
    
    async def add_news_to_cache(self, news):
        news_dict = {
            "id": news.id,
            "header": news.header,
            "content": news.content,
            "cover": news.cover,
            "author_id": news.author_id
        }
        news_log(news.id, from_cache=False)
        await self.redis.setex(f"news:{news.id}", 300, json.dumps(news_dict))  # ttl = 5 min

    async def get_news(self):
        in_cache = await self.redis.get("all:news")
        if in_cache == "True":
            news = []
            async for key in self.redis.scan_iter("news:*"):
                one_news = json.loads(await self.redis.get(key))
                news_log(one_news['id'], from_cache=True)
                news.append(one_news)
            return news
        news = await self.db.execute(select(News))
        news = news.scalars().all()
        for i in news:
            await self.add_news_to_cache(i)
        await self.redis.setex("all:news", 300, "True")
        return news
    
    async def get_one_news(self, news_id):
        cached_news = await self.redis.get(f"news:{news_id}")
        if cached_news:
            news_log(news_id, from_cache=True)
            return json.loads(cached_news)
        result = await self.db.execute(select(News).where(News.id == news_id))
        news = result.scalar_one_or_none()
        if not news:
            return None
        await self.add_news_to_cache(news)
        return news

    async def edit_news(self, news_id, news_data, current_user):
        result = await self.db.execute(select(News).where(News.id == news_id))
        news = result.scalar_one_or_none()
        if news is None:
            return None
        await check_user_permission(news.author_id, current_user) 
        for field, value in news_data.model_dump(exclude_unset=True).items():
            setattr(news, field, value)
        await self.db.commit()
        result = await self.db.execute(select(News).where(News.id == news_id))
        return result.scalar_one()
    
    async def remove_news(self, news_id, current_user):
        result = await self.db.execute(select(News.author_id).where(News.id == news_id))
        author_id = result.scalar_one_or_none()
        if author_id is None:
            return None
        await check_user_permission(author_id, current_user)
        await self.db.execute(delete(Comment).where(Comment.news_id == news_id))
        await self.db.execute(delete(News).where(News.id == news_id))
        await self.db.commit()
        return {"message": f"News with id:{news_id} was deleted"}
    
async def get_news_service(service: NewsService = Depends()):
    return service