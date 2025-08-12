"""
Django settings for bot_testing project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------
# Helper: Parse boolean envs
# ------------------------
def get_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "y", "on"}

# ------------------------
# Core settings
# ------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-secret-key")
DEBUG = get_bool("DEBUG", True)

ALLOWED_HOSTS = ["*"] if DEBUG else os.getenv("ALLOWED_HOSTS", "").split()

# Add Render hostname automatically
RENDER_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if RENDER_HOSTNAME and RENDER_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_HOSTNAME)

# ------------------------
# Custos configuration
# ------------------------
CUSTOS_API_KEY = os.getenv("CUSTOS_API_KEY", "")
CUSTOS_BACKEND_URL = os.getenv("CUSTOS_BACKEND_URL", "https://custoslabs-backend.onrender.com")

# ------------------------
# Model provider configuration
# ------------------------
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "llama-3.1-8b-instant")
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "140"))

SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "")

# ------------------------
# Installed apps
# ------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "corsheaders",

    "chatbot1",  
]

# ------------------------
# Middleware
# ------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",      
    "corsheaders.middleware.CorsMiddleware",       
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",


    "custos.integrations.django.CustosCaptureMiddleware",

]

ROOT_URLCONF = "bot_testing.urls"

# ------------------------
# Templates
# ------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "bot_testing.wsgi.application"

# ------------------------
# Database (Postgres via DATABASE_URL or SQLite)
# ------------------------
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        ssl_require=False,
    )
}

# ------------------------
# Password validation
# ------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ------------------------
# Internationalization
# ------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ------------------------
# Static files
# ------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
if (BASE_DIR / "static").exists():
    STATICFILES_DIRS = [BASE_DIR / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# WhiteNoise storage for production
if not DEBUG:
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    }

# ------------------------
# Django REST Framework
# ------------------------
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
}

# ------------------------
# CORS
# ------------------------
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = False
CORS_ALLOW_METHODS = ["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"]
CORS_ALLOW_HEADERS = ["*"]
CORS_URLS_REGEX = r"^/.*$"
