from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi_sso.sso.github import GithubSSO 
from .service import AuthService, get_auth_service
import os
from dotenv import load_dotenv
load_dotenv()

github_router = APIRouter()

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

sso = GithubSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri="http://localhost:8000/auth/github/callback",
    allow_insecure_http=True,
)


@github_router.get("/")
async def auth_init():
    async with sso:
        return await sso.get_login_redirect()


@github_router.get("/callback")
async def auth_callback(request: Request,
                        service: AuthService = Depends(get_auth_service)):
    try:
        async with sso:
            github_user = await sso.verify_and_process(request)
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    return await service.github_auth(github_user, request)