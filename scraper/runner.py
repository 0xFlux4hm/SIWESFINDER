                    
"""
Scraper runner - orchestrates all scrapers and sends Telegram alerts
"""
import logging
import time
import requests
from database.manager import DatabaseManager
from .linkedin_scraper import LinkedInScraper
from config.settings import settings

logger = logging.getLogger(__name__)


class ScraperRunner:

    def __init__(self, db_manager=None):
        self.db_manager = db_manager or DatabaseManager()
        self.scrapers = []
        self._initialize_scrapers()

    def _initialize_scrapers(self):
        if settings.ENABLE_LINKEDIN:
            self.scrapers.append(LinkedInScraper())
        logger.info(f"Initialized {len(self.scrapers)} scrapers")

    def run(self):
        total_jobs = 0
        new_jobs = 0
        new_job_objects = []

        logger.info("Starting scraper run...")

        for scraper in self.scrapers:
            try:
                jobs = scraper.scrape()
                total_jobs += len(jobs)
                for job in jobs:
                    if not self.db_manager.job_exists(job.hash):
                        job_id = self.db_manager.add_job(job)
                        if job_id:
                            new_jobs += 1
                            new_job_objects.append(job)
            except Exception as e:
                logger.error(f"Error running {scraper.name}: {e}")

        logger.info(f"Scraper run complete: {total_jobs} jobs found, {new_jobs} new jobs added")

        if new_job_objects and settings.TELEGRAM_CHANNEL_ID and settings.TELEGRAM_BOT_TOKEN:
            self._send_alerts_sync(new_job_objects)
        else:
            logger.info("No new jobs to alert or credentials not set")

        return total_jobs, new_jobs

    def _send_alerts_sync(self, jobs):
        token = settings.TELEGRAM_BOT_TOKEN
        channel = settings.TELEGRAM_CHANNEL_ID
        max_alerts = settings.MAX_ALERTS_PER_RUN
        base_url = f"https://api.telegram.org/bot{token}/sendMessage"

        def send(text):
            try:
                resp = requests.post(base_url, json={
                    "chat_id": channel,
                    "text": text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                }, timeout=30)
                if not resp.ok:
                    logger.error(f"Telegram error: {resp.text}")
                return resp.ok
            except Exception as e:
                logger.error(f"Send failed: {e}")
                return False

        send(
            f"🚨 <b>SIWES Hunter NG — {len(jobs)} New Opportunities!</b>\n\n"
            f"🤖 Auto-scraped and AI ranked\n"
            f"📅 Fresh opportunities just found\n\n"
            f"👇 Scroll down for details"
        )
        time.sleep(1)

        sent = 0
        for i, job in enumerate(jobs[:max_alerts], 1):
            stipend = getattr(job, 'stipend', 'See listing') or 'See listing'
            location = getattr(job, 'location', 'Nigeria') or 'Nigeria'
            remote_tag = "🌐 Remote" if getattr(job, 'remote', False) else ""
            source = getattr(job, 'source', 'Job Board') or 'Job Board'
            link = getattr(job, 'application_link', '') or ''

            text = (
                f"🚨 <b>OPPORTUNITY #{i}</b>\n"
                f"━━━━━━━━━━━━━━\n"
                f"🏢 <b>Company:</b> {job.company}\n"
                f"💼 <b>Position:</b> {job.title}\n"
                f"📍 <b>Location:</b> {location} {remote_tag}\n"
                f"💰 <b>Stipend:</b> {stipend}\n"
                f"📡 <b>Source:</b> {source}\n"
                f"🔗 <b>Apply:</b> {link}\n"
                f"━━━━━━━━━━━━━━"
            )

            if send(text):
                sent += 1
            time.sleep(1.5)

        logger.info(f"Alerts sent: {sent}/{min(len(jobs), max_alerts)}")
