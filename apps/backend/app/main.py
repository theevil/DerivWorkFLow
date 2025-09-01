from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.routers import health, auth, deriv, trading, websocket, market, automation_simple as automation
from app.routers import settings as settings_router
# from app.routers import ai  # Temporarily commented out due to pandas issue

app = FastAPI(title=settings.app_name)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(deriv.router, prefix="/api/v1/deriv", tags=["deriv"])
app.include_router(trading.router, prefix="/api/v1/trading", tags=["trading"])
app.include_router(market.router, prefix="/api/v1/market", tags=["market"])
# app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"])  # Temporarily commented out
app.include_router(automation.router, prefix="/api/v1/automation", tags=["automation"])
app.include_router(settings_router.router, prefix="/api/v1/settings", tags=["settings"])
app.include_router(websocket.router, prefix="/api/v1", tags=["websocket"])

@app.get("/")
async def root() -> dict:
    return {"message": "Deriv Workflow API", "env": settings.environment}

# Startup/Shutdown hooks
@app.on_event("startup")
async def on_startup() -> None:
    logger.info("Starting up {}", settings.app_name)
    await connect_to_mongo()

@app.on_event("shutdown")
async def on_shutdown() -> None:
    logger.info("Shutting down {}", settings.app_name)
    await close_mongo_connection()