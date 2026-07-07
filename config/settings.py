"""
Settings and configuration management
All secrets loaded from environment variables ONLY.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Settings:

    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"

    DATA_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)

    # Telegram
    TELEGRAM_BOT_TOKEN   = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHANNEL_ID  = os.getenv("TELEGRAM_CHANNEL_ID", "")
    TELEGRAM_ADMIN_ID    = os.getenv("TELEGRAM_ADMIN_ID", "")

    # Database
    DATABASE_PATH        = os.getenv("DATABASE_PATH",
                              str(DATA_DIR / "siwes_hunter.db"))

    # Scraper
    SCRAPER_TIMEOUT          = int(os.getenv("SCRAPER_TIMEOUT", 30))
    SCRAPER_USER_AGENT       = os.getenv(
        "SCRAPER_USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    MAX_ALERTS_PER_RUN       = int(os.getenv("MAX_ALERTS_PER_RUN", 10))

    # Scheduler
    SCHEDULER_TIMEZONE       = os.getenv("SCHEDULER_TIMEZONE", "Africa/Lagos")

    # Logging
    LOG_LEVEL        = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE         = os.getenv("LOG_FILE", str(LOGS_DIR / "bot.log"))

    # Feature flags
    ENABLE_LINKEDIN      = os.getenv("ENABLE_LINKEDIN", "True").lower() == "true"
    ENABLE_NAIRALAND     = os.getenv("ENABLE_NAIRALAND", "True").lower() == "true"
    ENABLE_COMPANY_PAGES = os.getenv("ENABLE_COMPANY_PAGES", "True").lower() == "true"
    ENABLE_GEMINI        = os.getenv("ENABLE_GEMINI", "True").lower() == "true"

    # Gemini AI
    GEMINI_API_KEY       = os.getenv("GEMINI_API_KEY", "")

    # Ranking
    MIN_RANK_SCORE = float(os.getenv("MIN_RANK_SCORE", 0.5))

    # Misc
    DEBUG   = os.getenv("DEBUG", "False").lower() == "true"
    DRY_RUN = os.getenv("DRY_RUN", "False").lower() == "true"

    @classmethod
    def validate(cls) -> bool:
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is not set.")
        if not cls.TELEGRAM_CHANNEL_ID:
            raise ValueError("TELEGRAM_CHANNEL_ID is not set.")
        return True


settings = Settings()
