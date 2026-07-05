"""
Scraper runner - orchestrates all scrapers
"""
import logging
import time
from typing import List
from datetime import datetime
from database.models import Job
from database.manager import DatabaseManager
from .linkedin_scraper import LinkedInScraper
from config.settings import settings

logger = logging.getLogger(__name__)


class ScraperRunner:
    """
    Orchestrates all scrapers and manages job discovery
    """
    
    def __init__(self, db_manager: DatabaseManager = None):
        """
        Initialize scraper runner
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager or DatabaseManager()
        self.scrapers = []
        self._initialize_scrapers()
    
    def _initialize_scrapers(self):
        """
        Initialize all enabled scrapers
        """
        if settings.ENABLE_LINKEDIN:
            self.scrapers.append(LinkedInScraper())
        
        logger.info(f"Initialized {len(self.scrapers)} scrapers")
    
    def run(self) -> tuple[int, int]:
        """
        Run all scrapers
        
        Returns:
            Tuple of (total_jobs_found, new_jobs_added)
        """
        total_jobs = 0
        new_jobs = 0
        
        logger.info("Starting scraper run...")
        
        for scraper in self.scrapers:
            try:
                jobs = scraper.scrape()
                total_jobs += len(jobs)
                
                # Add jobs to database
                for job in jobs:
                    if not self.db_manager.job_exists(job.hash):
                        job_id = self.db_manager.add_job(job)
                        if job_id:
                            new_jobs += 1
                
            except Exception as e:
                logger.error(f"Error running {scraper.name}: {e}")
        
        logger.info(f"Scraper run complete: {total_jobs} jobs found, {new_jobs} new jobs added")
        return total_jobs, new_jobs
