from fastapi import Depends, HTTPException, status
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from ..database import get_db_session
from .models import Session as DBSession
from ..users.models import User as DBUser
from .schemas import AccessToken
from .utils import create_access_token, create_refresh_token, hash_password


class AuthService:
    def __init__(self, db = Depends(get_db_session)):
        self.db = db 

    async def give_access_token(self, user, request):
        token = create_access_token(username=user.username, is_admin=user.is_admin, is_active=user.is_active, id=user.id)
        refresh_token = create_refresh_token()
        user_agent = request.headers.get('user-agent')
        client_ip = request.client.host
        db_session = DBSession(user_id=user.id, user_agent=user_agent, ip_address=client_ip, token=refresh_token, expires_at=(datetime.now(timezone.utc) + timedelta(days=30)).replace(tzinfo=None))
        self.db.add(db_session)
        await self.db.commit()
        await self.db.refresh(db_session)
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
        result = await self.db.execute(select(DBSession).where(DBSession.user_id == user.id))
        return result.scalars().all()
    
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