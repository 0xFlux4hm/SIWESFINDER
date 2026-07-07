import logging
import time
import requests
from datetime import datetime
from database.manager import DatabaseManager
from .linkedin_scraper import LinkedInScraper
from .gemini_scraper import scrape_gemini
from config.settings import settings

logger = logging.getLogger(__name__)


def clean(text):
    if not text:
        return "N/A"
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .strip())


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
        new_job_objects = []  # Only NEW jobs get alerted

        # Run web scrapers
        for scraper in self.scrapers:
            try:
                jobs = scraper.scrape()
                total_jobs += len(jobs)
                for job in jobs:
                    if not self.db_manager.job_exists(job.hash):
                        self.db_manager.add_job(job)
                        new_jobs += 1
                        new_job_objects.append(job)
            except Exception as e:
                logger.error(f"Scraper error: {e}")

        # Run Gemini AI scraper
        try:
            gemini_jobs = scrape_gemini()
            total_jobs += len(gemini_jobs)
            for job in gemini_jobs:
                if not self.db_manager.job_exists(job.hash):
                    self.db_manager.add_job(job)
                    new_jobs += 1
                    new_job_objects.append(job)
            logger.info(f"Gemini added {len(gemini_jobs)} jobs")
        except Exception as e:
            logger.error(f"Gemini error: {e}")

        logger.info(f"Total: {total_jobs} found, {new_jobs} new")

        if new_job_objects:
            self._send_digest(new_job_objects[:10])
        else:
            # Send heartbeat so you know bot is alive
            self._send_heartbeat(total_jobs)

        return total_jobs, new_jobs

    def _send_heartbeat(self, total):
        token = settings.TELEGRAM_BOT_TOKEN
        channel = settings.TELEGRAM_CHANNEL_ID
        if not token or not channel:
            return
        now = datetime.utcnow().strftime("%d %b %Y • %H:%M UTC")
        base = "https://api.telegram.org/bot" + token + "/sendMessage"
        try:
            requests.post(base, json={
                "chat_id": channel,
                "text": (
                    f"🔍 <b>SIWES Finder NG — Scan Complete</b>\n\n"
                    f"📅 {now}\n"
                    f"📊 {total} opportunities in database\n"
                    f"✅ No new opportunities this round\n\n"
                    f"🔔 Will scan again soon!"
                ),
                "parse_mode": "HTML",
            }, timeout=30)
        except Exception as e:
            logger.error(f"Heartbeat failed: {e}")

    def _send_digest(self, jobs):
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

        now = datetime.utcnow().strftime("%d %b %Y • %H:%M UTC")

        # Header
        post(
            f"🇳🇬 <b>SIWES FINDER NG — New Opportunities!</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📅 {now}\n"
            f"🆕 {len(jobs)} NEW opportunities found\n"
            f"🤖 Powered by AI + Web Scraping\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"👇 Scroll down for details"
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
            job_type = clean(getattr(job, 'job_type', 'Internship'))

            # Fix bad stipend values
            if stipend in ['N/A', 'N1', 'N2', 'N3', 'N4', 'N5']:
                stipend = "See listing"

            remote_badge = "🌐 REMOTE" if remote else "🏢 ON-SITE"

            # Pick emoji
            if 'Gemini' in source:
                emoji = "🤖"
            elif 'Cyber' in source or 'Security' in title:
                emoji = "🔐"
            elif 'Software' in source or 'Engineer' in title:
                emoji = "💻"
            elif 'Data' in source or 'AI' in source:
                emoji = "📊"
            elif 'Bank' in company or 'Finance' in title:
                emoji = "🏦"
            elif 'Oil' in title or 'Gas' in title or 'Energy' in company:
                emoji = "🛢"
            else:
                emoji = "🎯"

            # Fix empty apply links
            if not link or link.strip() == "":
                link = "Check source for application link"

            text = (
                f"{emoji} <b>NEW OPPORTUNITY #{i}</b> — {remote_badge}\n"
                f"━━━━━━━━━━━━━━\n"
                f"🏢 <b>Company:</b> {company}\n"
                f"💼 <b>Role:</b> {title}\n"
                f"📍 <b>Location:</b> {location}\n"
                f"💰 <b>Stipend:</b> {stipend}\n"
                f"🏷 <b>Type:</b> {job_type}\n"
                f"📡 <b>Source:</b> {source}\n"
                f"🔗 <b>Apply:</b> {link}\n"
                f"━━━━━━━━━━━━━━"
            )

            if post(text):
                sent += 1
            time.sleep(2)

        # Footer
        post(
            f"✅ <b>{sent} new opportunities delivered!</b>\n\n"
            f"🔔 Next scan in a few hours\n"
            f"📢 Share channel: @techdroidkey\n"
            f"🤖 Use bot: @Siwesalartbot\n\n"
            f"💡 <b>Bot Commands:</b>\n"
            f"/today — Today's jobs\n"
            f"/cyber — Cybersecurity roles\n"
            f"/software — Software roles\n"
            f"/lagos — Lagos opportunities\n"
            f"/stipend — Paid roles only\n"
            f"/remote — Remote jobs\n\n"
            f"<i>Built for Nigerian CS students 🇳🇬</i>"
        )

        logger.info(f"✅ Sent {sent} alerts to channel")
