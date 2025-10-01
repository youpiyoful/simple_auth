#!/usr/bin/env python3
"""
Script de démarrage pour l'API Simple Auth
"""
import os
import sys
import uvicorn

# Ajouter le répertoire src au path Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        app_dir="src"
    )
