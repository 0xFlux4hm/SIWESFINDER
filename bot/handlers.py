"""
Telegram bot command handlers
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from database.manager import DatabaseManager
from database.models import User
from config.constants import EMOJIS

logger = logging.getLogger(__name__)


class CommandHandlers:
    """
    Telegram bot command handlers
    """
    
    def __init__(self):
        """
        Initialize handlers
        """
        self.db = DatabaseManager()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /start command
        """
        user = update.effective_user
        
        # Add user to database
        db_user = User(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        existing_user = self.db.get_user(user.id)
        if not existing_user:
            self.db.add_user(db_user)
        
        message = f"""
{EMOJIS['info']} Welcome to SIWES Hunter NG!

I help you find the best SIWES, Internship, and Graduate Trainee opportunities in Nigeria.

Use /help to see available commands.
"""
        
        await update.message.reply_text(message)
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /help command
        """
        message = """
{EMOJIS['info']} Available Commands:

/today - View today's opportunities
/top - View top-ranked opportunities

📍 By Location:
/abuja - Opportunities in Abuja
/lagos - Opportunities in Lagos
/kaduna - Opportunities in Kaduna
/kano - Opportunities in Kano

💼 By Role:
/cyber - Cybersecurity opportunities
/software - Software engineering opportunities
/remote - Remote opportunities
/stipend - Opportunities with stipends

/help - Show this help message
""".format(EMOJIS=EMOJIS)
        
        await update.message.reply_text(message)
    
    async def today(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /today command - show today's opportunities
        """
        jobs = self.db.get_top_jobs(limit=5)
        
        if not jobs:
            await update.message.reply_text(
                f"{EMOJIS['info']} No opportunities found today. Check back later!"
            )
            return
        
        for job in jobs:
            await update.message.reply_text(job.telegram_message())
    
    async def top(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /top command - show top opportunities
        """
        jobs = self.db.get_top_jobs(limit=10)
        
        if not jobs:
            await update.message.reply_text(
                f"{EMOJIS['info']} No opportunities found. Check back later!"
            )
            return
        
        message = f"{EMOJIS['star']} Top 10 Opportunities:\n\n"
        for i, job in enumerate(jobs, 1):
            message += f"{i}. {job.title} at {job.company} - Score: {job.rank_score:.1f}\n"
        
        await update.message.reply_text(message)
    
    async def abuja(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /abuja command - show Abuja opportunities
        """
        jobs = self.db.get_jobs_by_location('Abuja', limit=5)
        
        if not jobs:
            await update.message.reply_text(
                f"{EMOJIS['location']} No opportunities in Abuja at the moment."
            )
            return
        
        for job in jobs:
            await update.message.reply_text(job.telegram_message())
    
    async def lagos(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /lagos command - show Lagos opportunities
        """
        jobs = self.db.get_jobs_by_location('Lagos', limit=5)
        
        if not jobs:
            await update.message.reply_text(
                f"{EMOJIS['location']} No opportunities in Lagos at the moment."
            )
            return
        
        for job in jobs:
            await update.message.reply_text(job.telegram_message())
    
    async def kaduna(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /kaduna command - show Kaduna opportunities
        """
        jobs = self.db.get_jobs_by_location('Kaduna', limit=5)
        
        if not jobs:
            await update.message.reply_text(
                f"{EMOJIS['location']} No opportunities in Kaduna at the moment."
            )
            return
        
        for job in jobs:
            await update.message.reply_text(job.telegram_message())
    
    async def kano(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /kano command - show Kano opportunities
        """
        jobs = self.db.get_jobs_by_location('Kano', limit=5)
        
        if not jobs:
            await update.message.reply_text(
                f"{EMOJIS['location']} No opportunities in Kano at the moment."
            )
            return
        
        for job in jobs:
            await update.message.reply_text(job.telegram_message())
    
    async def cyber(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /cyber command - show cybersecurity opportunities
        """
        jobs = self.db.get_jobs_by_role('Cybersecurity', limit=5)
        
        if not jobs:
            await update.message.reply_text(
                f"{EMOJIS['info']} No cybersecurity opportunities at the moment."
            )
            return
        
        for job in jobs:
            await update.message.reply_text(job.telegram_message())
    
    async def software(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /software command - show software engineering opportunities
        """
        jobs = self.db.get_jobs_by_role('Software Engineering', limit=5)
        
        if not jobs:
            await update.message.reply_text(
                f"{EMOJIS['info']} No software engineering opportunities at the moment."
            )
            return
        
        for job in jobs:
            await update.message.reply_text(job.telegram_message())
    
    async def remote(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /remote command - show remote opportunities
        """
        jobs = self.db.get_remote_jobs(limit=5)
        
        if not jobs:
            await update.message.reply_text(
                f"{EMOJIS['location']} No remote opportunities at the moment."
            )
            return
        
        for job in jobs:
            await update.message.reply_text(job.telegram_message())
    
    async def stipend(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /stipend command - show opportunities with stipends
        """
        jobs = self.db.get_jobs(limit=5)
        stipend_jobs = [job for job in jobs if job.stipend]
        
        if not stipend_jobs:
            await update.message.reply_text(
                f"{EMOJIS['money']} No opportunities with stipends at the moment."
            )
            return
        
        for job in stipend_jobs:
            await update.message.reply_text(job.telegram_message())
