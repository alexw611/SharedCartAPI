import logging
import sys
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from API.config import settings
from API.rate_limiter import limiter
from API.routers.auth import router as auth_router
from API.routers.users import router as users_router
from API.routers.groups import router as groups_router
from API.routers.shopping_lists import router as shopping_lists_router
from API.routers.shopping_items import router as shopping_items_router
from API.routers.snapshot import router as snapshot_router

class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
            if "GET /snapshot" in message and " 200" in message:
                return False
        except Exception:
            pass
        return True


log_formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

file_handler = logging.FileHandler("api.log")
file_handler.setFormatter(log_formatter)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)

logger = logging.getLogger("sharedcart")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

for log_name in ["uvicorn.access", "uvicorn.error"]:
    uv_logger = logging.getLogger(log_name)
    uv_logger.addHandler(file_handler)

logging.getLogger("uvicorn.access").addFilter(EndpointFilter())


app = FastAPI(
    title=settings.app_name,
    description="Backend API for SharedCart",
    version="1.0.0"
)

# Globaler Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"CRITICAL ERROR: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error - Please try again later."}
    )

# Rate Limiter Setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Register routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(groups_router)
app.include_router(shopping_lists_router)
app.include_router(shopping_items_router)
app.include_router(snapshot_router)


@app.on_event("startup")
async def startup_event():
    logger.info("SharedCart API started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("SharedCart API is shutting down")

@app.get("/")
@limiter.limit("10/minute")
def root(request: Request):
    return {"message": "SharedCart API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
