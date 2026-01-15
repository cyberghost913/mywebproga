from fastapi import APIRouter, Depends, Request
from .schemas import User, SessionInfo
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from .github import github_router
from .schemas import AccessToken
from .depends import get_oauth_user, check_password, check_refresh_token
from .service import AuthService, get_auth_service

router = APIRouter()

router.include_router(github_router, prefix="/github")

@router.post("/login")
async def login(request: Request,
                user: Annotated[User, Depends(check_password)],
                service: AuthService = Depends(get_auth_service)) -> AccessToken:
    return await service.give_access_token(user, request)

@router.post("/refresh")
async def refresh_token(request: Request,
                        user: Annotated[User, Depends(check_refresh_token)],
                        service: AuthService = Depends(get_auth_service)) -> AccessToken:
    return await service.give_access_token(user, request)

@router.post("/logout")
async def logout(_ = Depends(check_refresh_token)):
    return {
        "detail": "Logged out"
    }

@router.post("/register")
async def register_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                        service: AuthService = Depends(get_auth_service)) -> User:
    return await service.new_user(form_data)

@router.get("/sessions", response_model=list[SessionInfo])
async def get_sessions(user: Annotated[User, Depends(get_oauth_user)],
                       service: AuthService = Depends(get_auth_service)):
    return await service.session_list(user)