"""
SIWES Hunter NG — Main entry point
Usage:
  python main.py             # runs bot (default)
  python main.py --mode bot  # runs Telegram bot (polling)
  python main.py --mode scrape  # runs one scrape + alert cycle
"""
import asyncio
import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from bot.main import TelegramBot


def setup_logging():
    Path(settings.LOGS_DIR).mkdir(exist_ok=True)
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(settings.LOG_FILE),
        ],
    )


async def run_bot():
    """Run Telegram bot in polling mode."""
    bot = TelegramBot()
    await bot.run()


async def run_scrape():
    """Run one scrape + rank + alert cycle."""
    from scraper.runner import ScraperRunner
    from database.manager import DatabaseManager

    db = DatabaseManager()
    runner = ScraperRunner(db_manager=db)
    total, new = runner.run()
    logging.getLogger(__name__).info(
        "Scrape complete: %d total, %d new", total, new
    )


async def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="SIWES Hunter NG")
    parser.add_argument(
        "--mode",
        choices=["bot", "scrape"],
        default="bot",
        help="bot = polling mode | scrape = one-shot pipeline",
    )
    args = parser.parse_args()

    try:
        settings.validate()
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)

    logger.info("Starting SIWES Hunter NG in [%s] mode...", args.mode)

    if args.mode == "scrape":
        await run_scrape()
    else:
        await run_bot()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Stopped by user.")
    except Exception as e:
        logging.error("Fatal error: %s", e)
        sys.exit(1)
