# SIWES Hunter NG - Contributing Guide

## Getting Started

### Prerequisites
- Python 3.9+
- Git
- Basic understanding of Python, Telegram bots, and web scraping

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/siwes-hunter-ng.git
cd siwes-hunter-ng

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 on Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your credentials
```

## Project Structure

```
siwes-hunter-ng/
├── bot/              # Telegram bot implementation
├── scraper/          # Web scraping modules
├── ranking/          # Job ranking engine
├── database/         # Database management
├── scheduler/        # Task scheduling
├── config/           # Configuration files
├── tests/            # Test files
├── main.py           # Entry point
└── requirements.txt  # Dependencies
```

## Development Guidelines

### Code Style

- Use **PEP 8** style guide
- Use **type hints** for function parameters
- Write **docstrings** for all functions and classes
- Use meaningful variable names

### Example:

```python
from typing import List, Optional
from database.models import Job

def filter_jobs(jobs: List[Job], min_score: float = 0.5) -> List[Job]:
    """
    Filter jobs by minimum score
    
    Args:
        jobs: List of Job objects
        min_score: Minimum rank score (0-100)
    
    Returns:
        Filtered list of Job objects
    """
    return [job for job in jobs if job.rank_score >= min_score]
```

## Adding a New Job Source

1. **Create scraper class** in `scraper/`:

```python
from scraper.base_scraper import BaseScraper
from database.models import Job
from typing import List

class NewSourceScraper(BaseScraper):
    def __init__(self):
        super().__init__('New Source')
    
    def scrape(self) -> List[Job]:
        # Implementation here
        jobs = []
        # ... scraping logic ...
        return jobs
```

2. **Register in scraper runner** (`scraper/runner.py`):

```python
def _initialize_scrapers(self):
    # Add this line
    self.scrapers.append(NewSourceScraper())
```

3. **Add feature flag** in `.env.example`:

```env
ENABLE_NEW_SOURCE=True
```

4. **Test the scraper**:

```bash
python -c "from scraper.runner import ScraperRunner; ScraperRunner().run()"
```

## Adding a New Bot Command

1. **Add handler method** in `bot/handlers.py`:

```python
async def newcommand(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /newcommand - Description
    """
    # Implementation here
    await update.message.reply_text("Response")
```

2. **Register in bot** (`bot/main.py`):

```python
def _setup_handlers(self):
    # Add this line
    self.app.add_handler(CommandHandler('newcommand', self.handlers.newcommand))
```

3. **Test locally**:

```bash
python main.py
```

## Writing Tests

Place tests in `tests/` directory:

```python
import pytest
from database.manager import DatabaseManager
from database.models import Job

def test_add_job():
    """Test adding a job to database"""
    db = DatabaseManager(':memory:')
    
    job = Job(
        title="Test Job",
        company="Test Company",
        hash="testhash123"
    )
    
    job_id = db.add_job(job)
    assert job_id is not None
```

Run tests:

```bash
pytest tests/
```

## Pull Request Process

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Follow code style guidelines
- Write clear commit messages
- Update documentation if needed

### 3. Commit and Push

```bash
git add .
git commit -m "Add: Description of changes"
git push origin feature/your-feature-name
```

### 4. Create Pull Request

- Go to GitHub repository
- Click "New Pull Request"
- Fill in the PR template
- Wait for review

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Performance improvement

## How Has This Been Tested?
Describe tests performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for clarity
- [ ] Documentation updated
- [ ] Tests added/updated
```

## Commit Message Guidelines

Use conventional commits:

```
type(scope): subject

body (optional)
footer (optional)
```

### Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Maintenance

### Examples:

```
feat(scraper): add Indeed job scraper
fix(bot): handle missing job description
docs(install): update installation steps
```

## Areas for Contribution

### 🔴 High Priority
- [ ] Add more job scrapers (Glassdoor, Indeed, etc.)
- [ ] Improve ranking algorithm
- [ ] Add user preferences/filtering
- [ ] Database optimization

### 🟠 Medium Priority
- [ ] Add more Telegram commands
- [ ] Improve error handling
- [ ] Add caching
- [ ] Performance optimization

### 🟢 Low Priority
- [ ] Documentation improvements
- [ ] Code cleanup
- [ ] Tests
- [ ] UI improvements

## Code Review Checklist

When reviewing code:

- [ ] Code follows style guidelines
- [ ] Changes are well-documented
- [ ] No hardcoded values
- [ ] Error handling is present
- [ ] Logging is appropriate
- [ ] Tests are included
- [ ] No breaking changes
- [ ] Performance implications considered

## Questions?

- Open an issue for discussion
- Ask in pull request comments
- Check existing documentation

## Code of Conduct

- Be respectful to all contributors
- Provide constructive feedback
- Help new contributors
- Report issues responsibly

---

**Thank you for contributing to SIWES Hunter NG! 🎉**
