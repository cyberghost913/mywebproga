from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from ..users.models import User as DBUser
from .schemas import User, RefreshTokenRequest
from .security import TOKEN_SECRET, TOKEN_ALGORITHM, validate_credentials
from ..database import SessionDep
from ..add_redis import get_redis
from ..add_logs import user_log
from typing import Annotated
from sqlalchemy import select
import jwt
import json

oauth = OAuth2PasswordBearer(tokenUrl="login")

async def check_password(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: SessionDep):
    result = await db.execute(select(DBUser).where(DBUser.username == form_data.username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    if not validate_credentials(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    return user

async def check_refresh_token(
        db:SessionDep,
        token_request: RefreshTokenRequest,
        redis = Depends(get_redis)):
    session_id = await redis.get(f"token_to_session:{token_request.refresh_token}")
    if not session_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    session_exists = await redis.exists(f"session:{session_id}")
    if not session_exists:
        await redis.delete(f"token_to_session:{token_request.refresh_token}")
        raise HTTPException(status_code=401, detail="Refresh token expired")

    session_data = await redis.hgetall(f"session:{session_id}")
    
    user_id = int(session_data["user_id"])
    result = await db.execute(select(DBUser).where(DBUser.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        await redis.srem(f"user_sessions:{session_data['user_id']}", session_id)
        await redis.delete(f"token_to_session:{token_request.refresh_token}")
        await redis.delete(f"session:{session_id}")
        raise HTTPException(status_code=401, detail="User not found")
    
    await redis.srem(f"user_sessions:{session_data['user_id']}", session_id)
    await redis.delete(f"token_to_session:{token_request.refresh_token}")
    await redis.delete(f"session:{session_id}")
    
    return user

async def get_oauth_user(
    token: Annotated[str, Depends(oauth)],
    session: SessionDep,
    redis = Depends(get_redis)
) -> User | None:
    try:
        payload = jwt.decode(token, TOKEN_SECRET, algorithms=[TOKEN_ALGORITHM])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    cached_user = await redis.get(f'user:{payload["username"]}')
    if cached_user:
        user = User(**json.loads(cached_user))
        user_log(user.username, from_cache=True)
        return user
    result = await session.execute(select(DBUser).where(DBUser.username == payload["username"]))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    user_dict = {
        "id": db_user.id,
        "username": db_user.username,
        "is_author": db_user.is_author,
        "is_admin": db_user.is_admin,
        "is_author": db_user.is_author
    }
    await redis.setex(f'user:{payload["username"]}', 3600, json.dumps(user_dict))
    user_log(db_user.username, from_cache=False)
    return User(**user_dict)

async def get_oauth_admin(
    user: Annotated[User, Depends(get_oauth_user)]
) -> User | None:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user

async def check_user_permission(
    user_id: int,
    current_user: User = Depends(get_oauth_user)
) -> User:
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def check_author_permission(
    current_user: User = Depends(get_oauth_user)
) -> User:
    if not current_user.is_author and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create news"
        )
    return current_user