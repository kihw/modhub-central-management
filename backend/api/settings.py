import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# API settings
API_V1_STR = "/api/v1"
PROJECT_NAME = "DeviceControlHub"

# CORS settings
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8668",
    "http://localhost:5173",
    "electron://localhost"
]

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/data/database.sqlite")

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_change_in_production")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24))  # 1 day

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.path.join(BASE_DIR, "data", "logs", "app.log")

# Mod settings
MODS_DIRECTORY = os.path.join(BASE_DIR, "data", "mods")
RULES_DIRECTORY = os.path.join(BASE_DIR, "data", "rules")

# Configuration file
CONFIG_FILE = os.path.join(BASE_DIR, "data", "config.json")