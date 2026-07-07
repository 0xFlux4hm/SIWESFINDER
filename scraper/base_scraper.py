"""
Base scraper class
"""
import logging
import hashlib
from abc import ABC, abstractmethod
from typing import List
from database.models import Job
from config.settings import settings

logger = logging.getLogger(__name__)


class BaseScraper(ABC):

    def __init__(self, name: str):
        self.name = name
        self.timeout = settings.SCRAPER_TIMEOUT
        self.retry_attempts = 3
        self.user_agent = settings.SCRAPER_USER_AGENT

    @abstractmethod
    def scrape(self) -> List[Job]:
        pass

    def generate_hash(self, title: str, company: str, location: str = None) -> str:
        content = (
            f"{title.lower()}"
            f"{company.lower()}"
            f"{location.lower() if location else ''}"
        )
        return hashlib.md5(content.encode()).hexdigest()

    def log_scrape(self, status: str, jobs_found: int, jobs_new: int,
                   error: str = None, duration: float = 0):
        log_msg = (
            f"{self.name}: {status} | "
            f"Found: {jobs_found} | "
            f"New: {jobs_new} | "
            f"Duration: {duration:.2f}s"
        )
        if error:
            log_msg += f" | Error: {error}"
            logger.error(log_msg)
        else:
            logger.info(log_msg)
