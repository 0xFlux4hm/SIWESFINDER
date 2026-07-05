# SIWES Hunter NG 🚀

A completely free Telegram bot that automatically finds SIWES, Industrial Training, Internship, and Graduate Trainee opportunities for Nigerian students.

## 🎯 Objective

Build a powerful automation system that:
- Searches the internet daily for opportunities
- Removes duplicates automatically
- Ranks opportunities by relevance
- Sends Telegram alerts to users
- Works completely free (no paid services)

## 👥 Target User

Computer Science students from ATBU preparing for SIWES and looking for the best opportunities with stipends in:
- Lagos
- Abuja
- Kaduna
- Kano

## 📋 Features

### Telegram Bot Commands
- `/start` - Initialize the bot
- `/help` - Get help information
- `/today` - Today's opportunities
- `/top` - Top-ranked opportunities
- `/abuja` - Opportunities in Abuja
- `/lagos` - Opportunities in Lagos
- `/kaduna` - Opportunities in Kaduna
- `/kano` - Opportunities in Kano
- `/cyber` - Cybersecurity opportunities
- `/software` - Software engineering opportunities
- `/remote` - Remote opportunities
- `/stipend` - Opportunities with stipends

### Opportunities Tracked
- SIWES (Students' Industrial Work Experience Scheme)
- Industrial Training
- Internships
- Graduate Trainee Programs
- Software Engineering Roles
- Cybersecurity Roles
- Networking Roles
- IT Support Roles
- Data Analysis Roles
- AI/Machine Learning Roles

### Data Sources
- LinkedIn public opportunities
- Job boards (LinkedIn, Indeed, Glassdoor)
- Company career pages
- Nigerian banks
- Fintech companies
- Telecom companies
- Government ICT agencies
- Technology startups
- Software companies

### Ranking Engine
Opportunities are scored based on:
- Cybersecurity relevance (20%)
- Software engineering relevance (20%)
- Computer science relevance (15%)
- Stipend amount (20%)
- Company reputation (15%)
- Remote availability (5%)
- Location preference (5%)

## 🛠️ Tech Stack

- **Python 3.9+** - Core language
- **python-telegram-bot** - Telegram bot framework
- **SQLite** - Database
- **BeautifulSoup4** - HTML parsing
- **Requests** - HTTP library
- **Playwright** - Browser automation
- **APScheduler** - Task scheduling
- **GitHub Actions** - Automation pipeline
- **Docker** (optional) - Containerization

## 📁 Project Structure

```
siwes-hunter-ng/
├── bot/
│   ├── __init__.py
│   ├── main.py              # Main bot entry point
│   ├── handlers.py          # Command handlers
│   ├── callbacks.py         # Button callbacks
│   └── keyboards.py         # Keyboard layouts
├── scraper/
│   ├── __init__.py
│   ├── base_scraper.py      # Base scraper class
│   ├── linkedin_scraper.py  # LinkedIn scraper
│   ├── job_board_scraper.py # Job board scraper
│   ├── company_scraper.py   # Company page scraper
│   └── runner.py            # Scraper orchestration
├── ranking/
│   ├── __init__.py
│   ├── ranker.py            # Ranking engine
│   ├── scorer.py            # Scoring logic
│   └── filters.py           # Filter logic
├── database/
│   ├── __init__.py
│   ├── models.py            # Database models
│   ├── manager.py           # Database manager
│   └── schema.sql           # SQLite schema
├── scheduler/
│   ├── __init__.py
│   ├── jobs.py              # Scheduled jobs
│   └── runner.py            # Scheduler runner
├── config/
│   ├── __init__.py
│   ├── settings.py          # Configuration
│   └── constants.py         # Constants
├── github_actions/
│   └── workflows/
│       ├── scraper.yml      # Daily scraper workflow
│       └── alerts.yml       # Alert workflow
├── tests/
│   ├── __init__.py
│   ├── test_scraper.py
│   ├── test_ranker.py
│   └── test_database.py
├── logs/                    # Logs directory
├── data/                    # Database directory
├── requirements.txt
├── .env.example
├── .gitignore
├── main.py                  # Application entry point
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Git
- GitHub account
- Telegram account

### Installation

#### On Linux/macOS

```bash
# Clone the repository
git clone https://github.com/0xFlux4hm/siwes-hunter-ng.git
cd siwes-hunter-ng

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env with your credentials
nano .env

# Initialize database
python database/manager.py --init

# Run the bot
python main.py
```

#### On Windows (PowerShell)

```powershell
# Clone the repository
git clone https://github.com/0xFlux4hm/siwes-hunter-ng.git
cd siwes-hunter-ng

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create environment file
Copy-Item .env.example -Destination .env

# Edit .env with your credentials
noteepad .env

# Initialize database
python database/manager.py --init

# Run the bot
python main.py
```

#### On Termux (Android)

```bash
# Install Python and required tools
pkg install python git clang make

# Clone the repository
git clone https://github.com/0xFlux4hm/siwes-hunter-ng.git
cd siwes-hunter-ng

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env
nano .env

# Initialize database
python database/manager.py --init

# Run the bot
python main.py
```

## 🔐 Environment Setup

Create a `.env` file based on `.env.example`:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=your_channel_id_here
TELEGRAM_ADMIN_ID=your_admin_id_here

# Database
DATABASE_PATH=./data/siwes_hunter.db

# Scraper Settings
SCRAPER_TIMEOUT=30
SCRAPER_RETRY_ATTEMPTS=3
LINKEDIN_SEARCH_LIMIT=50

# Scheduler
SCHEDULER_ENABLED=True
SCHEDULER_TIMEZONE=Africa/Lagos

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/bot.log

# Scraper Sources
ENABLE_LINKEDIN=True
ENABLE_INDEED=True
ENABLE_GLASSDOOR=True
ENABLE_COMPANY_PAGES=True
```

## 📊 Database Schema

The bot uses SQLite with the following tables:

### jobs
- id (INTEGER PRIMARY KEY)
- title (TEXT)
- company (TEXT)
- location (TEXT)
- stipend (TEXT)
- deadline (DATETIME)
- application_link (TEXT)
- source (TEXT)
- description (TEXT)
- requirements (TEXT)
- job_type (TEXT)
- remote (BOOLEAN)
- rank_score (FLOAT)
- created_at (DATETIME)
- updated_at (DATETIME)
- hash (TEXT UNIQUE) - For duplicate detection

### users
- id (INTEGER PRIMARY KEY)
- telegram_id (INTEGER UNIQUE)
- username (TEXT)
- first_name (TEXT)
- last_name (TEXT)
- location (TEXT)
- interests (TEXT) - JSON
- subscribed (BOOLEAN)
- created_at (DATETIME)

### alerts
- id (INTEGER PRIMARY KEY)
- user_id (INTEGER)
- job_id (INTEGER)
- sent_at (DATETIME)
- read (BOOLEAN)

### settings
- id (INTEGER PRIMARY KEY)
- user_id (INTEGER)
- notification_frequency (TEXT)
- preferred_locations (TEXT) - JSON
- preferred_roles (TEXT) - JSON
- min_stipend (INTEGER)

## 🔄 Automation Schedule

The bot runs scrapers and sends alerts:
- **8:00 AM** - Morning scrape and alert
- **2:00 PM** - Afternoon scrape and alert
- **8:00 PM** - Evening scrape and alert

## 🐳 Docker Deployment

```bash
# Build image
docker build -t siwes-hunter-ng .

# Run container
docker run -d \
  --name siwes-bot \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  siwes-hunter-ng
```

## 📈 GitHub Actions Automation

The project includes automated workflows:

1. **scraper.yml** - Runs scraper on schedule
2. **alerts.yml** - Sends alerts to Telegram

These workflows run on the schedule defined in the YAML files and handle all automation without any manual intervention.

## 🔍 Key Features

### Duplicate Detection
- Uses content hashing to detect duplicates
- Checks title, company, and location
- Prevents duplicate alerts

### Smart Ranking
- AI-powered relevance scoring
- Considers multiple factors
- Prioritizes high-paying opportunities
- Factors in company reputation

### User Management
- Subscription management
- Location preferences
- Role preferences
- Notification frequency settings

### Error Handling
- Comprehensive logging
- Retry mechanisms
- Graceful error recovery
- Detailed error messages

## 📝 Logging

All logs are saved to `./logs/bot.log` with rotation:
- INFO level for general information
- WARNING level for warnings
- ERROR level for errors
- DEBUG level for debugging

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 💡 Tips

- Test the bot locally before deployment
- Monitor logs regularly
- Update scraper selectors if websites change
- Run tests before pushing to production

## 🆘 Support

For issues and questions:
1. Check existing GitHub issues
2. Review the logs
3. Create a new GitHub issue with details

## 🎓 Educational Purpose

This bot is designed to help Nigerian students find quality internship and training opportunities. Use it responsibly and in accordance with website terms of service.

---

**Made with ❤️ for Nigerian students**
