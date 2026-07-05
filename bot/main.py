"""
Main Telegram bot implementation
"""
import logging
import asyncio
from telegram.request import HTTPXRequest
from telegram.ext import Application, CommandHandler
from bot.handlers import CommandHandlers
from config.settings import settings

logger = logging.getLogger(__name__)


class TelegramBot:

    def __init__(self):
        request = HTTPXRequest(
            connect_timeout=30.0,
            read_timeout=30.0,
            write_timeout=30.0,
            pool_timeout=30.0,
        )
        self.app = (
            Application.builder()
            .token(settings.TELEGRAM_BOT_TOKEN)
            .request(request)
            .build()
        )
        self.handlers = CommandHandlers()
        self._setup_handlers()

    def _setup_handlers(self):
        self.app.add_handler(CommandHandler('start', self.handlers.start))
        self.app.add_handler(CommandHandler('help', self.handlers.help))
        self.app.add_handler(CommandHandler('today', self.handlers.today))
        self.app.add_handler(CommandHandler('top', self.handlers.top))
        self.app.add_handler(CommandHandler('abuja', self.handlers.abuja))
        self.app.add_handler(CommandHandler('lagos', self.handlers.lagos))
        self.app.add_handler(CommandHandler('kaduna', self.handlers.kaduna))
        self.app.add_handler(CommandHandler('kano', self.handlers.kano))
        self.app.add_handler(CommandHandler('cyber', self.handlers.cyber))
        self.app.add_handler(CommandHandler('software', self.handlers.software))
        self.app.add_handler(CommandHandler('remote', self.handlers.remote))
        self.app.add_handler(CommandHandler('stipend', self.handlers.stipend))
        logger.info("Command handlers setup complete")

    async def run(self):
        try:
            logger.info("Starting Telegram bot...")
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling(
                drop_pending_updates=True,
                allowed_updates=["message", "callback_query"],
            )
            logger.info("Bot is running.")
            await asyncio.Event().wait()
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            raise
        finally:
            await self.stop()

    async def stop(self):
        try:
            if self.app.updater.running:
                await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()
            logger.info("Telegram bot stopped")
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
