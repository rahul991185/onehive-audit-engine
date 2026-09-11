import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
APP_DIR = BASE_DIR / "app"
STORAGE_DIR = BASE_DIR / "storage"
PDF_DIR = STORAGE_DIR / "generated_pdfs"
STATIC_DIR = APP_DIR / "static"
ASSETS_DIR = STATIC_DIR / "assets"
TEMPLATES_DIR = APP_DIR / "templates"

# Ensure storage directories exist
PDF_DIR.mkdir(parents=True, exist_ok=True)
(STORAGE_DIR / "generated_previews").mkdir(parents=True, exist_ok=True)
(STORAGE_DIR / "generated_quick_wins").mkdir(parents=True, exist_ok=True)
(STORAGE_DIR / "generated_packs").mkdir(parents=True, exist_ok=True)

ONEHIVE_LOGO_PATH = ASSETS_DIR / "onehive_logo.png"

# Default API URL
API_PORT = int(os.getenv("PORT", 8050))
API_HOST = os.getenv("HOST", "127.0.0.1")
BASE_URL = os.getenv("BASE_URL", f"http://{API_HOST}:{API_PORT}")
