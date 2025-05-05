import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar .env en la raíz del proyecto
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

def get(key: str, fallback=None):
    """Lee variables desde .env (u otras del entorno)."""
    return os.getenv(key, fallback)
