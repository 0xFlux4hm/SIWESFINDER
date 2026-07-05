"""
Main Telegram bot implementation
"""
import logging
from telegram.ext import Application, CommandHandler
from bot.handlers import CommandHandlers
from config.settings import settings

logger = logging.getLogger(__name__)


class TelegramBot:
    """
    Main Telegram bot class
    """
    
    def __init__(self):
        """
        Initialize Telegram bot
        """
        self.app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        self.handlers = CommandHandlers()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """
        Setup command handlers
        """
        # Add command handlers
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
        """
        Run the bot
        """
        try:
            logger.info("Starting Telegram bot...")
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling()
            logger.info("Telegram bot started successfully")
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            raise
    
    async def stop(self):
        """
        Stop the bot
        """
        await self.app.stop()
        logger.info("Telegram bot stopped")
