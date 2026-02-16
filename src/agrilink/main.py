"""FastAPI application entry point."""

from dotenv import load_dotenv
load_dotenv()

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from agrilink.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager."""
    settings = get_settings()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    
    # Initialize services on startup
    from agrilink.events.bus import get_event_bus
    from agrilink.events.handlers import setup_event_handlers
    from agrilink.realtime.websocket import router as ws_router, broadcast_event_to_clients
    
    # Initialize event bus
    bus = await get_event_bus()
    logger.info("Event bus initialized")
    
    # Set up event handlers
    await setup_event_handlers()
    
    # Subscribe WebSocket broadcaster to all events
    await bus.subscribe_all(broadcast_event_to_clients)
    logger.info("Real-time event broadcasting configured")
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down AgriLink")
    await bus.disconnect()


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Real-time, sensor-less agricultural intelligence platform",
        lifespan=lifespan,
        debug=settings.debug,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return JSONResponse(
            content={
                "status": "healthy",
                "service": settings.app_name,
                "version": settings.app_version,
                "environment": settings.environment,
            }
        )
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return JSONResponse(
            content={
                "service": settings.app_name,
                "version": settings.app_version,
                "description": "Real-time agricultural intelligence platform",
                "docs": "/docs",
                "health": "/health",
            }
        )
    
    # Register API routes
    from agrilink.api.routes import router as api_router
    app.include_router(api_router)
    
    # Register WebSocket endpoint
    from agrilink.realtime.websocket import router as ws_router
    app.include_router(ws_router)
    
    # Global exception handler for debugging
    from fastapi import Request
    from fastapi.responses import JSONResponse
    import traceback
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": str(exc),
                "traceback": traceback.format_exc()
            },
        )
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "agrilink.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower(),
    )
