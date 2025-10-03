#!/usr/bin/env python3
"""
Script de démarrage pour l'API Simple Auth
"""
import os
import sys

import uvicorn

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Check if virtual environment is activated
if not hasattr(sys, "real_prefix") and not (
    hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
):
    print(
        "Erreur: Environnement virtuel non activé. Veuillez activer votre environnement virtuel avant d'exécuter ce script."
    )
    sys.exit(1)

# Install production dependencies
os.system("pip install -r requirements.txt")

# Install development dependencies
os.system("pip install -r requirements-dev.txt")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info", app_dir="src")
