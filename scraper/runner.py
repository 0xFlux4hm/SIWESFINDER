import logging
import time
import requests
from database.manager import DatabaseManager
from .linkedin_scraper import LinkedInScraper
from config.settings import settings

logger = logging.getLogger(__name__)


def clean(text):
    if not text:
        return "N/A"
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").strip()


class ScraperRunner:

    def __init__(self, db_manager=None):
        self.db_manager = db_manager or DatabaseManager()
        self.scrapers = []
        if settings.ENABLE_LINKEDIN:
            self.scrapers.append(LinkedInScraper())
        logger.info(f"Initialized {len(self.scrapers)} scrapers")

    def run(self):
        total_jobs = 0
        new_jobs = 0
        all_jobs = []

        for scraper in self.scrapers:
            try:
                jobs = scraper.scrape()
                total_jobs += len(jobs)
                for job in jobs:
                    all_jobs.append(job)
                    if not self.db_manager.job_exists(job.hash):
                        self.db_manager.add_job(job)
                        new_jobs += 1
            except Exception as e:
                logger.error(f"Scraper error: {e}")

        logger.info(f"Total: {total_jobs} found, {new_jobs} new")

        if all_jobs:
            self._send(all_jobs[:8])
        else:
            logger.info("No jobs to send")

        return total_jobs, new_jobs

    def _send(self, jobs):
        token = settings.TELEGRAM_BOT_TOKEN
        channel = settings.TELEGRAM_CHANNEL_ID

        if not token or not channel:
            logger.error("TOKEN or CHANNEL missing!")
            return

        base = "https://api.telegram.org/bot" + token + "/sendMessage"

        def post(text):
            try:
                r = requests.post(base, json={
                    "chat_id": channel,
                    "text": text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True
                }, timeout=30)
                logger.info(f"Telegram: {r.status_code}")
                if not r.ok:
                    logger.error(f"Error: {r.text[:200]}")
                return r.ok
            except Exception as e:
                logger.error(f"Post failed: {e}")
                return False

        post(
            f"🚨 <b>SIWES Hunter NG</b>\n\n"
            f"📡 {len(jobs)} opportunities found!\n"
            f"🤖 AI ranked and verified\n"
            f"👇 Details below"
        )
        time.sleep(1)

        sent = 0
        for i, job in enumerate(jobs, 1):
            title = clean(getattr(job, 'title', 'N/A'))
            company = clean(getattr(job, 'company', 'N/A'))
            location = clean(getattr(job, 'location', 'Nigeria'))
            stipend = clean(getattr(job, 'stipend', 'See listing'))
            source = clean(getattr(job, 'source', 'Job Board'))
            link = str(getattr(job, 'application_link', '') or '')
            remote = getattr(job, 'remote', False)
            remote_tag = "🌐 Remote" if remote else ""

            text = (
                f"🚨 <b>OPPORTUNITY #{i}</b>\n"
                f"━━━━━━━━━━━━━━\n"
                f"🏢 <b>Company:</b> {company}\n"
                f"💼 <b>Position:</b> {title}\n"
                f"📍 <b>Location:</b> {location} {remote_tag}\n"
                f"💰 <b>Stipend:</b> {stipend}\n"
                f"📡 <b>Source:</b> {source}\n"
                f"🔗 <b>Apply:</b> {link}\n"
                f"━━━━━━━━━━━━━━"
            )

            if post(text):
                sent += 1
            time.sleep(2)

        logger.info(f"✅ Sent {sent} alerts to channel")
