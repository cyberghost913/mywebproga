from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from ..users.models import User as DBUser
from .schemas import User, RefreshTokenRequest
from .models import Session as DBSession
from datetime import datetime, timezone
from .security import TOKEN_SECRET, TOKEN_ALGORITHM, validate_credentials
from ..database import SessionDep
from typing import Annotated
from sqlalchemy import select
import jwt

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
        token_request: RefreshTokenRequest):
    db_session = await db.execute(select(DBSession).where(DBSession.token == token_request.refresh_token))
    db_session = db_session.scalar_one_or_none()
    if not db_session or db_session.expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = await db.execute(select(DBUser).where(DBUser.id == db_session.user_id))
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    await db.delete(db_session)
    return user

async def get_oauth_user(
    token: Annotated[str, Depends(oauth)],
    session: SessionDep
) -> User | None:
    try:
        payload = jwt.decode(token, TOKEN_SECRET, algorithms=[TOKEN_ALGORITHM])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    result = await session.execute(select(DBUser).where(DBUser.username == payload["username"]))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    
    return User(
        id=db_user.id,
        username=db_user.username,
        is_active=db_user.is_active,
        is_admin=db_user.is_admin,
        is_author=db_user.is_author
    )

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