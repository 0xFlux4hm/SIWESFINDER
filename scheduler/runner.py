"""
Scheduler runner - manages scheduled tasks
"""
import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from .jobs import ScheduledJobs
from config.settings import settings

logger = logging.getLogger(__name__)


class SchedulerRunner:
    """
    Manages scheduled tasks
    """
    
    def __init__(self):
        """
        Initialize scheduler
        """
        self.scheduler = AsyncIOScheduler(timezone=settings.SCHEDULER_TIMEZONE)
        self.jobs = ScheduledJobs()
    
    def add_scrape_jobs(self):
        """
        Add scraping jobs to scheduler
        """
        if not settings.SCHEDULER_ENABLED:
            logger.warning("Scheduler is disabled")
            return
        
        # Parse times
        morning_parts = settings.SCHEDULER_MORNING_TIME.split(':')
        afternoon_parts = settings.SCHEDULER_AFTERNOON_TIME.split(':')
        evening_parts = settings.SCHEDULER_EVENING_TIME.split(':')
        
        # Morning job (8 AM)
        self.scheduler.add_job(
            self.jobs.scrape_and_rank,
            CronTrigger(hour=int(morning_parts[0]), minute=int(morning_parts[1])),
            id='morning_scrape',
            name='Morning Scrape and Rank'
        )
        
        # Afternoon job (2 PM)
        self.scheduler.add_job(
            self.jobs.scrape_and_rank,
            CronTrigger(hour=int(afternoon_parts[0]), minute=int(afternoon_parts[1])),
            id='afternoon_scrape',
            name='Afternoon Scrape and Rank'
        )
        
        # Evening job (8 PM)
        self.scheduler.add_job(
            self.jobs.scrape_and_rank,
            CronTrigger(hour=int(evening_parts[0]), minute=int(evening_parts[1])),
            id='evening_scrape',
            name='Evening Scrape and Rank'
        )
        
        logger.info("Scraping jobs added to scheduler")
    
    def start(self):
        """
        Start the scheduler
        """
        try:
            self.add_scrape_jobs()
            
            logger.info("Starting scheduler...")
            
            # Create event loop and run
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            self.scheduler.start()
            logger.info("Scheduler started successfully")
            
            # Keep scheduler running
            try:
                loop.run_forever()
            except KeyboardInterrupt:
                logger.info("Scheduler interrupted")
        
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
    
    def stop(self):
        """
        Stop the scheduler
        """
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
