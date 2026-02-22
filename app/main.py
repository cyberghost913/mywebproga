import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .users.urls import router as users_router
from .news.urls import router as news_router
from .comments.urls import router as comments_router
from .auth.urls import router as auth_router

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000",
                   "http://127.0.0.1:8000",
                   "http://localhost:5173",
                   "http://127.0.0.1:5173"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(users_router, prefix="/users")
app.include_router(news_router, prefix="/news")
app.include_router(comments_router, prefix="/comments")
app.include_router(auth_router, prefix="/auth")