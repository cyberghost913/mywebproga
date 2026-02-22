from fastapi import Depends
from sqlalchemy import select, delete
import json
from datetime import datetime
from ..database import get_db_session
from .models import News
from ..users.models import User
from ..comments.models import Comment
from ..auth.depends import check_author_permission, check_user_permission
from ..add_redis import get_redis
from ..add_logs import news_log
from ..background.tasks import send_news_notification

class NewsService:
    def __init__(self, db=Depends(get_db_session), redis=Depends(get_redis)):
        self.db = db
        self.redis = redis

    async def get_emails(self):
        result = await self.db.execute(select(User.email).where(User.is_active == True))
        return result.scalars().all()

    async def serialize_news_obj(self, news_obj):
        if isinstance(news_obj, dict):
            data = news_obj
        else:
            data = {
                "id": news_obj.id,
                "header": news_obj.header,
                "content": news_obj.content,
                "author_id": news_obj.author_id,
                "date": news_obj.date if getattr(news_obj, "date", None) else datetime.utcnow()
            }

        if isinstance(data.get("date"), str):
            try:
                data["date"] = datetime.fromisoformat(data["date"])
            except Exception:
                try:
                    data["date"] = datetime.strptime(data["date"], "%Y-%m-%d %H:%M:%S.%f")
                except Exception:
                    data["date"] = datetime.utcnow()

        if not data.get("author_name"):
            author = await self.db.execute(select(User.username).where(User.id == data["author_id"]))
            data["author_name"] = author.scalar_one_or_none() or "—"

        return data

    async def add_news(self, news, current_user):
        await check_author_permission(current_user)

        if hasattr(news, "model_dump"):
            news_data = news.model_dump()
        else:
            news_data = dict(news)

        news_data["author_id"] = current_user.id

        new_news = News(
            header=news_data.get("header"),
            content=news_data.get("content"),
            author_id=news_data["author_id"]
        )

        self.db.add(new_news)
        await self.db.commit()
        await self.db.refresh(new_news)

        resp = await self.serialize_news_obj(new_news)

        await self.redis.setex(f"news:{resp['id']}", 300, json.dumps({
            **resp,
            "date": resp["date"].isoformat()
        }))

        await self.redis.delete("all:news")

        try:
            email_list = await self.get_emails()
            news_data_for_email = {
                'id': new_news.id,
                'header': new_news.header,
                'content': new_news.content
            }
            send_news_notification.delay(email_list, news_data_for_email)
        except Exception:
            pass

        return resp

    async def add_news_to_cache(self, news):
        data = await self.serialize_news_obj(news)
        payload = {
            "id": data["id"],
            "header": data["header"],
            "content": data["content"],
            "cover": None,
            "author_id": data["author_id"],
            "author_name": data.get("author_name"),
            "date": data["date"].isoformat()
        }
        news_log(data["id"], from_cache=False)
        await self.redis.setex(f"news:{data['id']}", 300, json.dumps(payload))

    async def get_news(self):
        in_cache = await self.redis.get("all:news")
        if in_cache == "True":
            news = []
            async for key in self.redis.scan_iter("news:*"):
                one_news = json.loads(await self.redis.get(key))
                news_log(one_news['id'], from_cache=True)
                try:
                    one_news["date"] = datetime.fromisoformat(one_news["date"])
                except Exception:
                    one_news["date"] = datetime.utcnow()
                news.append(one_news)
            return news

        result = await self.db.execute(select(News))
        news_objs = result.scalars().all()
        res = []
        for obj in news_objs:
            data = await self.serialize_news_obj(obj)
            res.append(data)
            await self.add_news_to_cache(data)
        await self.redis.setex("all:news", 300, "True")
        return res

    async def get_one_news(self, news_id):
        cached_news = await self.redis.get(f"news:{news_id}")
        if cached_news:
            news_log(news_id, from_cache=True)
            data = json.loads(cached_news)
            try:
                data["date"] = datetime.fromisoformat(data["date"])
            except Exception:
                data["date"] = datetime.utcnow()
            return data

        result = await self.db.execute(select(News).where(News.id == news_id))
        news = result.scalar_one_or_none()
        if not news:
            return None
        data = await self.serialize_news_obj(news)
        await self.add_news_to_cache(data)
        return data

    async def edit_news(self, news_id, news_data, current_user):
        result = await self.db.execute(select(News).where(News.id == news_id))
        news = result.scalar_one_or_none()
        if news is None:
            return None
        await check_user_permission(news.author_id, current_user)

        if hasattr(news_data, "model_dump"):
            nd = news_data.model_dump(exclude_unset=True)
        else:
            nd = {k: v for k, v in dict(news_data).items() if v is not None}

        if "header" in nd:
            news.header = nd["header"]
        if "content" in nd:
            news.content = nd["content"]

        await self.db.commit()
        await self.db.refresh(news)

        data = await self.serialize_news_obj(news)

        await self.add_news_to_cache(data)
        await self.redis.delete("all:news")

        return data

    async def remove_news(self, news_id, current_user):
        result = await self.db.execute(select(News.author_id).where(News.id == news_id))
        author_id = result.scalar_one_or_none()
        if author_id is None:
            return None
        await check_user_permission(author_id, current_user)
        await self.db.execute(delete(Comment).where(Comment.news_id == news_id))
        await self.db.execute(delete(News).where(News.id == news_id))
        await self.db.commit()
        await self.redis.delete(f"news:{news_id}")
        await self.redis.delete("all:news")
        return {"message": f"News with id:{news_id} was deleted"}

async def get_news_service(service: NewsService = Depends()):
    return service