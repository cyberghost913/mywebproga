from fastapi import Depends, HTTPException
from sqlalchemy import select, delete 
from ..database import get_db_session
from .models import News
from ..comments.models import Comment
from ..auth.depends import check_author_permission, check_user_permission

class NewsService:
    def __init__(self, db = Depends(get_db_session)):
        self.db = db

    async def add_news(self, news, current_user):
        await check_author_permission(current_user) 
        news_data = news.model_dump()
        news_data["author_id"] = current_user.id
        new_news = News(**news_data) 
        self.db.add(new_news)
        await self.db.commit()
        await self.db.refresh(new_news)
        return new_news

    async def get_news(self):
        news = await self.db.execute(select(News))
        return news.scalars().all()

    async def edit_news(self, news_id, news_data, current_user):
        result = await self.db.execute(select(News).where(News.id == news_id))
        news = result.scalar_one_or_none()
        if news is None:
            raise HTTPException(status_code=404, detail="News not found")
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
            raise HTTPException(status_code=404, detail="News not found")
        await check_user_permission(author_id, current_user)
        await self.db.execute(delete(Comment).where(Comment.news_id == news_id))
        await self.db.execute(delete(News).where(News.id == news_id))
        await self.db.commit()
        return {"message": f"News with id:{news_id} was deleted"}
    
async def get_news_service(service: NewsService = Depends()):
    return service