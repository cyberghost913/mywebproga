from fastapi import Depends
from sqlalchemy import select, delete
from .models import Comment
from ..database import get_db_session
from ..news.models import News
from ..auth.depends import check_user_permission

class CommentService:
    def __init__(self, db = Depends(get_db_session)):
        self.db = db
    
    async def add_comment(self, comment, user_id):
        result = await self.db.execute(select(News).where(News.id == comment.news_id))
        news = result.scalar_one_or_none()
        if not news:
            return None
        comment_data = comment.model_dump()
        comment_data["author_id"] = user_id
        new_comment = Comment(**comment_data)
        self.db.add(new_comment)
        await self.db.commit()
        await self.db.refresh(new_comment)
        return new_comment
    
    async def get_comments(self):
        comments = await self.db.execute(select(Comment))
        return comments.scalars().all()
    
    async def edit_comment(self, comment_id, comment_data, current_user):
        result = await self.db.execute(select(Comment).where(Comment.id == comment_id))
        comment = result.scalar_one_or_none()
        if comment is None:
            return None
        await check_user_permission(comment.author_id, current_user) 
        for field, value in comment_data.model_dump(exclude_unset=True).items():
            setattr(comment, field, value)
        await self.db.commit()
        result = await self.db.execute(select(Comment).where(Comment.id == comment_id))
        return result.scalar_one()
    
    async def remove_comment(self, comment_id, current_user):
        result = await self.db.execute(select(Comment.author_id).where(Comment.id == comment_id))
        author_id = result.scalar_one_or_none()
        if author_id is None:
            return None
        await check_user_permission(author_id, current_user) 
        await self.db.execute(delete(Comment).where(Comment.id == comment_id))
        await self.db.commit()
        return {"message": f"Comment with id:{comment_id} was deleted"}

async def get_comment_service(service: CommentService = Depends()):
    return service