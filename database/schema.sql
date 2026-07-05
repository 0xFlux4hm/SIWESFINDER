-- SIWES Hunter NG Database Schema

-- Jobs Table
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    stipend TEXT,
    deadline DATETIME,
    application_link TEXT,
    source TEXT,
    description TEXT,
    requirements TEXT,
    job_type TEXT,
    remote BOOLEAN DEFAULT 0,
    rank_score REAL DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    hash TEXT UNIQUE NOT NULL,
    sent_to_channel BOOLEAN DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_jobs_hash ON jobs(hash);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_jobs_rank_score ON jobs(rank_score DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);
CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source);

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    location TEXT,
    interests TEXT,
    subscribed BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_subscribed ON users(subscribed);

-- Alerts Table
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    read BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_alerts_job_id ON alerts(job_id);
CREATE INDEX IF NOT EXISTS idx_alerts_sent_at ON alerts(sent_at);

-- Settings Table
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    notification_frequency TEXT DEFAULT 'all',
    preferred_locations TEXT,
    preferred_roles TEXT,
    min_stipend INTEGER DEFAULT 0,
    email_notifications BOOLEAN DEFAULT 1,
    telegram_notifications BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_settings_user_id ON settings(user_id);

-- Scraper Logs Table
CREATE TABLE IF NOT EXISTS scraper_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    status TEXT,
    jobs_found INTEGER DEFAULT 0,
    jobs_new INTEGER DEFAULT 0,
    error_message TEXT,
    executed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    duration_seconds REAL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_scraper_logs_source ON scraper_logs(source);
CREATE INDEX IF NOT EXISTS idx_scraper_logs_executed_at ON scraper_logs(executed_at);

-- Statistics Table
CREATE TABLE IF NOT EXISTS statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    total_jobs INTEGER DEFAULT 0,
    total_users INTEGER DEFAULT 0,
    total_alerts_sent INTEGER DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
