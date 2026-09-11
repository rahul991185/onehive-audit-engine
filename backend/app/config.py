import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"
STORAGE_DIR = BASE_DIR / "storage"

# Centralized artifact directories
ARTIFACTS_DIR = STORAGE_DIR / "artifacts"
REPORTS_DIR = ARTIFACTS_DIR / "reports"
PREVIEWS_DIR = ARTIFACTS_DIR / "previews"
QUICKWINS_DIR = ARTIFACTS_DIR / "quickwins"
SALESPACKS_DIR = ARTIFACTS_DIR / "salespacks"
IMAGEPACKS_DIR = ARTIFACTS_DIR / "imagepacks"
VISUAL_QA_DIR = ARTIFACTS_DIR / "visual_qa"

for d in [REPORTS_DIR, PREVIEWS_DIR, QUICKWINS_DIR, SALESPACKS_DIR, IMAGEPACKS_DIR, VISUAL_QA_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Templates & Static assets
TEMPLATES_DIR = APP_DIR / "templates"
STATIC_DIR = APP_DIR / "static"
ASSETS_DIR = STATIC_DIR / "assets"
ONEHIVE_LOGO_PATH = ASSETS_DIR / "onehive_logo.png"
DEMO_FIXTURE_PATH = APP_DIR / "fixtures" / "demo_business.json"


# App & Network
APP_ENV = os.getenv("APP_ENV", "development")
PORT = int(os.getenv("PORT", 8050))
HOST = os.getenv("HOST", "127.0.0.1")
BASE_URL = os.getenv("BASE_URL", f"http://{HOST}:{PORT}")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{STORAGE_DIR}/onehive.db")

# AI Settings
AI_PROVIDER = os.getenv("AI_PROVIDER", "deterministic") # ollama | gemini | openai | deterministic
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Google Maps API (optional)
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

# Centralized OneHive Organization Details
ONEHIVE_COMPANY_NAME = "OneHive Technologies"
ONEHIVE_TAGLINE = "Build. Automate. Grow."
ONEHIVE_SECONDARY_TAGLINE = "Better Presence. Bigger Possibilities."
ONEHIVE_WEBSITE = os.getenv("ONEHIVE_WEBSITE", "www.onehivetech.com")
ONEHIVE_EMAIL = os.getenv("ONEHIVE_EMAIL", "growth@onehivetech.com")
ONEHIVE_PHONE = os.getenv("ONEHIVE_PHONE", "+91 98450 12345")
ONEHIVE_ADDRESS = os.getenv("ONEHIVE_ADDRESS", "Bengaluru, India")
ONEHIVE_QR_URL = os.getenv("ONEHIVE_QR_URL", "")
