"""
FastAPI application entry point, lifecycle event handlers, middleware, and router inclusion.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
import logging
from backend.app.config import settings
from backend.app.database import init_db, AsyncSessionLocal
from backend.app.websocket_manager import ws_manager
from backend.app.rbac.service import RBACService
from backend.app.auth.router import router as auth_router
from backend.app.rbac.router import router as rbac_router
from backend.app.devices.router import router as device_router, site_router
from backend.app.discovery.router import router as discovery_router
from backend.app.topology.router import router as topology_router

logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger("netops.nexus")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle management."""
    logger.info("Initializing NetOps Nexus Enterprise Platform...")
    # Initialize database tables
    await init_db()
    
    # Initialize default roles and permissions
    async with AsyncSessionLocal() as session:
        await RBACService.initialize_roles_and_permissions(session)
    
    logger.info("Database and RBAC initialized successfully.")
    yield
    logger.info("Shutting down NetOps Nexus...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Carrier-Grade Enterprise Network Intelligence, Automation & Observability Platform",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception caught in API gateway", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please contact the network operations administrator."},
    )


# Health check endpoint
@app.get("/healthz", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "lab_mode": settings.LAB_MODE,
    }


# WebSocket Gateway
@app.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket, channel: str = "all"):
    """Multiplexed real-time WebSocket connection for live telemetry, alerts, and topology events."""
    await ws_manager.connect(websocket, channel=channel)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket error: {e}")
        await ws_manager.disconnect(websocket)


# Register Core Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(rbac_router, prefix=settings.API_V1_STR)
app.include_router(device_router, prefix=settings.API_V1_STR)
app.include_router(site_router, prefix=settings.API_V1_STR)
app.include_router(discovery_router, prefix=settings.API_V1_STR)
app.include_router(topology_router, prefix=settings.API_V1_STR)
