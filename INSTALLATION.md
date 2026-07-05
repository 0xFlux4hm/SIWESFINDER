# SIWES Hunter NG - Installation Guide

## Prerequisites

- Python 3.9 or higher
- Git
- Telegram account
- GitHub account (optional, for GitHub Actions automation)

## Step 1: Get Your Telegram Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/start` command
3. Send `/newbot` command
4. Follow the prompts to create a new bot
5. Copy the bot token (you'll need this)

## Step 2: Get Your Telegram IDs

1. Search for **@userinfobot** in Telegram
2. Send any message
3. The bot will reply with your user ID and chat ID
4. Save these IDs

## Installation on Linux/macOS

### 1. Clone the Repository

```bash
git clone https://github.com/0xFlux4hm/siwes-hunter-ng.git
cd siwes-hunter-ng
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create Environment File

```bash
cp .env.example .env
nano .env
```

Edit the following:
```env
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHANNEL_ID=your_channel_id
TELEGRAM_ADMIN_ID=your_user_id
```

### 5. Initialize Database

```bash
python -c "from database.manager import DatabaseManager; DatabaseManager()"
```

### 6. Run the Bot

```bash
python main.py
```

## Installation on Windows (PowerShell)

### 1. Clone the Repository

```powershell
git clone https://github.com/0xFlux4hm/siwes-hunter-ng.git
cd siwes-hunter-ng
```

### 2. Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Create Environment File

```powershell
Copy-Item .env.example -Destination .env
notepad .env
```

Edit the following:
```env
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHANNEL_ID=your_channel_id
TELEGRAM_ADMIN_ID=your_user_id
```

### 5. Initialize Database

```powershell
python -c "from database.manager import DatabaseManager; DatabaseManager()"
```

### 6. Run the Bot

```powershell
python main.py
```

## Installation on Termux (Android)

### 1. Install Required Packages

```bash
pkg update && pkg upgrade
pkg install python git clang make
```

### 2. Clone the Repository

```bash
git clone https://github.com/0xFlux4hm/siwes-hunter-ng.git
cd siwes-hunter-ng
```

### 3. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Create Environment File

```bash
cp .env.example .env
nano .env
```

Edit the following:
```env
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHANNEL_ID=your_channel_id
TELEGRAM_ADMIN_ID=your_user_id
```

### 6. Initialize Database

```bash
python -c "from database.manager import DatabaseManager; DatabaseManager()"
```

### 7. Run the Bot

```bash
python main.py
```

## Installation with Docker

### 1. Clone the Repository

```bash
git clone https://github.com/0xFlux4hm/siwes-hunter-ng.git
cd siwes-hunter-ng
```

### 2. Create .env File

```bash
cp .env.example .env
# Edit .env with your Telegram credentials
```

### 3. Build and Run

```bash
# Build image
docker build -t siwes-hunter-ng .

# Run container
docker run -d \
  --name siwes-bot \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  siwes-hunter-ng
```

### 4. Using Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f siwes-bot

# Stop services
docker-compose down
```

## Testing the Installation

### 1. Check Database

```bash
python -c "from database.manager import DatabaseManager; db = DatabaseManager(); print(f'Database: {db.db_path}')"
```

### 2. Test Bot Connection

```bash
python -c "from config.settings import settings; print(f'Bot Token: {settings.TELEGRAM_BOT_TOKEN[:10]}...')"
```

### 3. Manual Scrape Test

```bash
python -c "from scraper.runner import ScraperRunner; sr = ScraperRunner(); total, new = sr.run(); print(f'Scraped {total} jobs, {new} are new')"
```

## Troubleshooting

### 1. ModuleNotFoundError

**Solution:** Ensure you're in the virtual environment
```bash
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\Activate.ps1  # Windows
```

### 2. TELEGRAM_BOT_TOKEN not found

**Solution:** Create .env file and add your token
```bash
cp .env.example .env
# Edit .env file
```

### 3. Database Error

**Solution:** Delete and reinitialize database
```bash
rm data/siwes_hunter.db
python -c "from database.manager import DatabaseManager; DatabaseManager()"
```

### 4. Timeout Errors

**Solution:** Increase timeout in .env
```env
SCRAPER_TIMEOUT=60
REQUEST_TIMEOUT=60
```

## Next Steps

1. **Customize Scraper:** Edit `scraper/` files to add more job sources
2. **Improve Ranking:** Adjust weights in `config/constants.py`
3. **Add Features:** Extend bot commands in `bot/handlers.py`
4. **Monitor Logs:** Check `logs/bot.log` for debugging

## Support

If you encounter issues:

1. Check `logs/bot.log` for error messages
2. Review the troubleshooting section above
3. Create a GitHub issue with error details
4. Include your environment details (OS, Python version, etc.)

---

**Made with ❤️ for Nigerian students**
