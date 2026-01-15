import os
from dotenv import load_dotenv
from fastapi import FastAPI
from .users.urls import router as users_router
from .news.urls import router as news_router
from .comments.urls import router as comments_router
from .auth.urls import router as auth_router

load_dotenv()

app = FastAPI()

app.include_router(users_router, prefix="/users")
app.include_router(news_router, prefix="/news")
app.include_router(comments_router, prefix="/comments")
app.include_router(auth_router, prefix="/auth")