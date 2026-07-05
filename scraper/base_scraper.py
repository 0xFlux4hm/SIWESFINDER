"""
Base scraper class
"""
import logging
import hashlib
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from database.models import Job
from config.settings import settings

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Abstract base class for all scrapers
    """
    
    def __init__(self, name: str):
        """
        Initialize scraper
        
        Args:
            name: Scraper name
        """
        self.name = name
        self.timeout = settings.SCRAPER_TIMEOUT
        self.retry_attempts = settings.SCRAPER_RETRY_ATTEMPTS
        self.user_agent = settings.SCRAPER_USER_AGENT
    
    @abstractmethod
    def scrape(self) -> List[Job]:
        """
        Scrape opportunities (to be implemented by subclasses)
        
        Returns:
            List of Job objects
        """
        pass
    
    def generate_hash(self, title: str, company: str, location: str = None) -> str:
        """
        Generate unique hash for job
        
        Args:
            title: Job title
            company: Company name
            location: Job location
        
        Returns:
            Hash string
        """
        content = f"{title.lower()}{company.lower()}{location.lower() if location else ''}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def log_scrape(self, status: str, jobs_found: int, jobs_new: int, error: str = None, duration: float = 0):
        """
        Log scraping activity
        
        Args:
            status: Scraping status (success, failed, error)
            jobs_found: Total jobs found
            jobs_new: New jobs found
            error: Error message if any
            duration: Duration in seconds
        """
        log_msg = f"{self.name}: {status} | Found: {jobs_found} | New: {jobs_new} | Duration: {duration:.2f}s"
        if error:
            log_msg += f" | Error: {error}"
            logger.error(log_msg)
        else:
            logger.info(log_msg)
