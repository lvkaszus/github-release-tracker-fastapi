from dotenv import load_dotenv
from fastapi import FastAPI, Request
import version
from routes.api import webhook
from routes import index
from database import init_db, redis_client
from limiter import init_limiter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from logger import logger
import os


from slowapi.errors import RateLimitExceeded

load_dotenv()


app = FastAPI(
    title="FastAPI GitHub Release Tracker",
    description="A lightweight API that tracks the latest GitHub releases with webhook support and caching to optimize GitHub API usage.",
    version=version.__version__,

    # Disabling Swagger UI, ReDoc and OpenAPI because I need to create documentation for this project soon!
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)


@app.on_event("startup")
async def startup():
    await init_db()
    await init_limiter(app)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"error": "Too many requests!"})

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception! : {exc}")

    return JSONResponse(status_code=500, content={"error": "Internal Server Error!"})


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.update({
        "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Content-Security-Policy": "default-src 'self'"
    })
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


app.include_router(webhook.router)
app.include_router(index.router)
