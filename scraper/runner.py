"""
Scraper runner - orchestrates all scrapers and sends Telegram alerts
"""
import logging
import asyncio
import time
from database.models import Job
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

        if new_job_objects and settings.TELEGRAM_CHANNEL_ID:
            try:
                asyncio.run(self._send_alerts(new_job_objects))
            except Exception as e:
                logger.error(f"Alert sending failed: {e}")
        else:
            logger.info("No new jobs to alert or channel ID not set")

        return total_jobs, new_jobs

    async def _send_alerts(self, jobs):
        from telegram import Bot
        from telegram.constants import ParseMode
        from telegram.request import HTTPXRequest

        token = settings.TELEGRAM_BOT_TOKEN
        channel = settings.TELEGRAM_CHANNEL_ID
        max_alerts = settings.MAX_ALERTS_PER_RUN

        if not token or not channel:
            logger.warning("Token or channel missing")
            return

        request = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0)
        bot = Bot(token=token, request=request)

        try:
            await bot.send_message(
                chat_id=channel,
                text=(
                    f"🚨 <b>SIWES Hunter NG — {len(jobs)} New Opportunities!</b>\n\n"
                    f"🤖 Auto-scraped and ranked by AI\n"
                    f"📅 Fresh opportunities just found\n\n"
                    f"👇 Scroll down for details"
                ),
                parse_mode=ParseMode.HTML,
            )
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Header failed: {e}")

        sent = 0
        for i, job in enumerate(jobs[:max_alerts], 1):
            try:
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

                await bot.send_message(
                    chat_id=channel,
                    text=text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
                sent += 1
                await asyncio.sleep(1.5)

            except Exception as e:
                logger.error(f"Failed to send job {i}: {e}")

        logger.info(f"Alerts sent: {sent}/{len(jobs)}")
