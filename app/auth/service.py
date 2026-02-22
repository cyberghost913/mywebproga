from fastapi import Depends, HTTPException, status
import uuid
from sqlalchemy import select
from ..database import get_db_session
from .models import Session as DBSession  # don't delete
from ..users.models import User as DBUser
from .schemas import AccessToken
from .utils import create_access_token, create_refresh_token, hash_password
from ..add_redis import get_redis


class AuthService:
    def __init__(self, db = Depends(get_db_session), redis = Depends(get_redis)):
        self.db = db 
        self.redis = redis

    async def give_access_token(self, user, request):
        token = create_access_token(username=user.username, is_admin=user.is_admin, is_active=user.is_active, id=user.id)
        refresh_token = create_refresh_token()
        user_agent = request.headers.get('user-agent')
        client_ip = request.client.host
        session_id = str(uuid.uuid4())
        expire_seconds = 30 * 24 * 60 * 60  # 30 days

        await self.redis.hset(f"session:{session_id}", mapping={
            "user_id": user.id,
            "token": refresh_token,
            "user_agent": user_agent,
            "ip_address": client_ip
        })

        await self.redis.sadd(f"user_sessions:{user.id}", session_id)
        await self.redis.set(f"token_to_session:{refresh_token}", session_id)
        await self.redis.expire(f"session:{session_id}", expire_seconds)
        await self.redis.expire(f"user_sessions:{user.id}", expire_seconds) 
        await self.redis.expire(f"token_to_session:{refresh_token}", expire_seconds)

        return AccessToken(value=token, refresh_token=refresh_token)
    
    async def new_user(self, form_data):
        existing_user = await self.db.execute(select(DBUser).where(DBUser.username == form_data.username))
        existing_user = existing_user.scalar_one_or_none()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

        db_user = DBUser(
            username=form_data.username, 
            password=hash_password(form_data.password)
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user
    
    async def session_list(self, user):
        session_ids = await self.redis.smembers(f"user_sessions:{user.id}")
        
        sessions = []
        for session_id in session_ids:
            session_data = await self.redis.hgetall(f"session:{session_id}")
            if session_data:
                sessions.append({
                    "session_id": session_id,
                    **session_data
                })
        
        return sessions
    
    async def github_auth(self, github_user, request):
        user = await self.db.execute(select(DBUser).where(DBUser.github_id == github_user.id))
        user = user.scalar_one_or_none()

        if user:
            return await self.give_access_token(user, request)
        
        db_user = DBUser(
            username = github_user.display_name,
            github_id = github_user.id
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return await self.give_access_token(db_user, request)
        

async def get_auth_service(service: AuthService = Depends()):
    return service