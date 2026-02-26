import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .users.urls import router as users_router
from .news.urls import router as news_router
from .comments.urls import router as comments_router
from .auth.urls import router as auth_router
from prometheus_fastapi_instrumentator import Instrumentator
from . import metrics
import structlog
import logging
import time
from hawk_python_sdk.modules.fastapi import HawkFastapi

load_dotenv()

HAWK_TOKEN = os.getenv("HAWK_TOKEN")

os.makedirs("logs", exist_ok=True)

logging.basicConfig(level=logging.INFO, filename="logs/app.log", filemode="a",
                    format="%(message)s")

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.EventRenamer("message"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

log = structlog.get_logger().bind(service="orders-api", env="local")

app = FastAPI()

hawk = HawkFastapi({
    'app_instance': app,
    'token': HAWK_TOKEN
})

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
        duration = (time.time() - start) * 1000

        status_code=response.status_code

        if 400 <= status_code < 500:
            log_func = log.warning
            message = "client_error"
        else:
            log_func = log.info
            message = "request_ok"

        log_func(
            message,
            path=request.url.path,
            method=request.method,
            status_code=status_code,
            duration_ms=round(duration, 2),
        )
        return response
    
    except HTTPException as httpe:
        duration = (time.time() - start) * 1000
        log.warning(
            "http_error",
            path=request.url.path,
            method=request.method,
            status_code=httpe.status_code,
            error_detail=httpe.detail,
            duration_ms=round(duration, 2),
        )
        raise

    except Exception as e:
        duration = (time.time() - start) * 1000
        log.error(
            "server_error",
            path=request.url.path,
            method=request.method,
            status_code=500,
            error_type=type(e).__name__,
            error_message=str(e),
            duration_ms=round(duration, 2),
        )
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )

instrumentator = Instrumentator()
instrumentator.instrument(app)
instrumentator.expose(app)

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
app.include_router(metrics.router, prefix='/metrics')