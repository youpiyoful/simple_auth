"""Main entry point for the FastAPI application."""

import logging
from fastapi import FastAPI
from src.api.server import create_app

# Configuration du logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app: FastAPI = create_app()

