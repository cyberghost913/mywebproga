from fastapi import Depends
from sqlalchemy import select, delete
from .models import User
from ..database import get_db_session
from ..auth.depends import check_user_permission

class UsersService:
    def __init__(self, db = Depends(get_db_session)):
        self.db = db

    async def get_users(self):
        users = await self.db.execute(select(User))
        return users.scalars().all()

    async def get_user(self, user_id, current_user):
        await check_user_permission(user_id, current_user)
        user = await self.db.execute(select(User).where(User.id == user_id))
        return user.scalar_one()

    async def edit_user(self, user_id, user_data, current_user):
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            return user
        await check_user_permission(user_id, current_user)
        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        await self.db.commit()
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one()

    async def remove_user(self, user_id, current_user):
        await check_user_permission(user_id, current_user)
        await self.db.execute(delete(User).where(User.id == user_id))
        await self.db.commit()
        return {"message": f"user with id:{user_id} was deleted"}

async def get_users_service(service: UsersService = Depends()):
    return service