"""Server configuration for the FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.errors_handler import add_error_handlers
from src.api.routes import user_routes


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Create the FastAPI instance
    app = FastAPI(
        title="Simple Auth API",
        description="API d'authentification simple avec FastAPI",
        version="1.0.0",
    )

    # Include the routers
    app.include_router(router=user_routes.router)

    # Configuration CORS
    app.add_middleware(
        middleware_class=CORSMiddleware,
        allow_origins=["*"],  # In production, specify allowed domains
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Setup exception handlers
    add_error_handlers(app)

    return app
