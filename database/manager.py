"""
Database manager for SIWES Hunter NG
"""
import sqlite3
import logging
import hashlib
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from .models import Job, User, Alert, Setting
from config.settings import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    SQLite database manager
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path or settings.DATABASE_PATH
        self.connection = None
        self.cursor = None
        self._initialize_db()
    
    def _initialize_db(self):
        """
        Initialize database connection and schema
        """
        try:
            # Create database directory if it doesn't exist
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Connect to database
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            
            # Create tables
            self._create_tables()
            logger.info(f"Database initialized: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _create_tables(self):
        """
        Create database tables
        """
        schema_path = Path(__file__).parent / 'schema.sql'
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        # Execute schema
        for statement in schema.split(';'):
            if statement.strip():
                self.cursor.execute(statement)
        
        self.connection.commit()
    
    def close(self):
        """
        Close database connection
        """
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    # ==================== Job Methods ====================
    
    def add_job(self, job: Job) -> int:
        """
        Add a new job
        
        Args:
            job: Job object
        
        Returns:
            Job ID
        """
        try:
            self.cursor.execute("""
                INSERT INTO jobs 
                (title, company, location, stipend, deadline, application_link,
                 source, description, requirements, job_type, remote, rank_score, hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.title, job.company, job.location, job.stipend, job.deadline,
                job.application_link, job.source, job.description, job.requirements,
                job.job_type, job.remote, job.rank_score, job.hash
            ))
            self.connection.commit()
            logger.info(f"Job added: {job.title} at {job.company}")
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"Job already exists (hash: {job.hash})")
            return None
        except Exception as e:
            logger.error(f"Failed to add job: {e}")
            return None
    
    def job_exists(self, job_hash: str) -> bool:
        """
        Check if job exists
        
        Args:
            job_hash: Hash of job
        
        Returns:
            True if job exists
        """
        try:
            self.cursor.execute("SELECT id FROM jobs WHERE hash = ?", (job_hash,))
            return self.cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Failed to check if job exists: {e}")
            return False
    
    def get_job(self, job_id: int) -> Optional[Job]:
        """
        Get job by ID
        
        Args:
            job_id: Job ID
        
        Returns:
            Job object or None
        """
        try:
            self.cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
            row = self.cursor.fetchone()
            if row:
                return self._row_to_job(row)
            return None
        except Exception as e:
            logger.error(f"Failed to get job: {e}")
            return None
    
    def get_jobs(self, limit: int = 50, offset: int = 0) -> List[Job]:
        """
        Get jobs with pagination
        
        Args:
            limit: Number of jobs to return
            offset: Number of jobs to skip
        
        Returns:
            List of Job objects
        """
        try:
            self.cursor.execute(
                "SELECT * FROM jobs ORDER BY rank_score DESC LIMIT ? OFFSET ?",
                (limit, offset)
            )
            rows = self.cursor.fetchall()
            return [self._row_to_job(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get jobs: {e}")
            return []
    
    def get_jobs_by_location(self, location: str, limit: int = 50) -> List[Job]:
        """
        Get jobs by location
        
        Args:
            location: Location name
            limit: Number of jobs to return
        
        Returns:
            List of Job objects
        """
        try:
            self.cursor.execute(
                "SELECT * FROM jobs WHERE location = ? ORDER BY rank_score DESC LIMIT ?",
                (location, limit)
            )
            rows = self.cursor.fetchall()
            return [self._row_to_job(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get jobs by location: {e}")
            return []
    
    def get_jobs_by_role(self, job_type: str, limit: int = 50) -> List[Job]:
        """
        Get jobs by role type
        
        Args:
            job_type: Job type/role
            limit: Number of jobs to return
        
        Returns:
            List of Job objects
        """
        try:
            self.cursor.execute(
                "SELECT * FROM jobs WHERE job_type LIKE ? ORDER BY rank_score DESC LIMIT ?",
                (f"%{job_type}%", limit)
            )
            rows = self.cursor.fetchall()
            return [self._row_to_job(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get jobs by role: {e}")
            return []
    
    def get_remote_jobs(self, limit: int = 50) -> List[Job]:
        """
        Get remote jobs
        
        Args:
            limit: Number of jobs to return
        
        Returns:
            List of Job objects
        """
        try:
            self.cursor.execute(
                "SELECT * FROM jobs WHERE remote = 1 ORDER BY rank_score DESC LIMIT ?",
                (limit,)
            )
            rows = self.cursor.fetchall()
            return [self._row_to_job(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get remote jobs: {e}")
            return []
    
    def get_top_jobs(self, limit: int = 10) -> List[Job]:
        """
        Get top-ranked jobs
        
        Args:
            limit: Number of jobs to return
        
        Returns:
            List of Job objects
        """
        try:
            self.cursor.execute(
                "SELECT * FROM jobs ORDER BY rank_score DESC, created_at DESC LIMIT ?",
                (limit,)
            )
            rows = self.cursor.fetchall()
            return [self._row_to_job(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get top jobs: {e}")
            return []
    
    def update_job_rank(self, job_id: int, rank_score: float) -> bool:
        """
        Update job rank score
        
        Args:
            job_id: Job ID
            rank_score: New rank score
        
        Returns:
            True if successful
        """
        try:
            self.cursor.execute(
                "UPDATE jobs SET rank_score = ?, updated_at = ? WHERE id = ?",
                (rank_score, datetime.now(), job_id)
            )
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update job rank: {e}")
            return False
    
    def mark_job_sent(self, job_id: int) -> bool:
        """
        Mark job as sent to channel
        
        Args:
            job_id: Job ID
        
        Returns:
            True if successful
        """
        try:
            self.cursor.execute(
                "UPDATE jobs SET sent_to_channel = 1 WHERE id = ?",
                (job_id,)
            )
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to mark job as sent: {e}")
            return False
    
    def _row_to_job(self, row: sqlite3.Row) -> Job:
        """
        Convert database row to Job object
        """
        return Job(
            id=row['id'],
            title=row['title'],
            company=row['company'],
            location=row['location'],
            stipend=row['stipend'],
            deadline=datetime.fromisoformat(row['deadline']) if row['deadline'] else None,
            application_link=row['application_link'],
            source=row['source'],
            description=row['description'],
            requirements=row['requirements'],
            job_type=row['job_type'],
            remote=bool(row['remote']),
            rank_score=row['rank_score'],
            hash=row['hash'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
            sent_to_channel=bool(row['sent_to_channel'])
        )
    
    # ==================== User Methods ====================
    
    def add_user(self, user: User) -> Optional[int]:
        """
        Add a new user
        
        Args:
            user: User object
        
        Returns:
            User ID or None
        """
        try:
            self.cursor.execute("""
                INSERT INTO users (telegram_id, username, first_name, last_name, location, interests, subscribed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user.telegram_id, user.username, user.first_name, user.last_name,
                user.location, user.interests, user.subscribed
            ))
            self.connection.commit()
            logger.info(f"User added: {user.telegram_id}")
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"User already exists: {user.telegram_id}")
            return None
        except Exception as e:
            logger.error(f"Failed to add user: {e}")
            return None
    
    def get_user(self, telegram_id: int) -> Optional[User]:
        """
        Get user by telegram ID
        
        Args:
            telegram_id: Telegram user ID
        
        Returns:
            User object or None
        """
        try:
            self.cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
            row = self.cursor.fetchone()
            if row:
                return self._row_to_user(row)
            return None
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None
    
    def get_all_users(self, subscribed_only: bool = True) -> List[User]:
        """
        Get all users
        
        Args:
            subscribed_only: Only return subscribed users
        
        Returns:
            List of User objects
        """
        try:
            if subscribed_only:
                self.cursor.execute("SELECT * FROM users WHERE subscribed = 1")
            else:
                self.cursor.execute("SELECT * FROM users")
            rows = self.cursor.fetchall()
            return [self._row_to_user(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            return []
    
    def update_user(self, user: User) -> bool:
        """
        Update user
        
        Args:
            user: User object
        
        Returns:
            True if successful
        """
        try:
            self.cursor.execute("""
                UPDATE users SET username = ?, first_name = ?, last_name = ?,
                location = ?, interests = ?, subscribed = ?, updated_at = ?
                WHERE telegram_id = ?
            """, (
                user.username, user.first_name, user.last_name, user.location,
                user.interests, user.subscribed, datetime.now(), user.telegram_id
            ))
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            return False
    
    def _row_to_user(self, row: sqlite3.Row) -> User:
        """
        Convert database row to User object
        """
        return User(
            id=row['id'],
            telegram_id=row['telegram_id'],
            username=row['username'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            location=row['location'],
            interests=row['interests'],
            subscribed=bool(row['subscribed']),
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
        )
    
    # ==================== Alert Methods ====================
    
    def add_alert(self, alert: Alert) -> Optional[int]:
        """
        Add a new alert
        
        Args:
            alert: Alert object
        
        Returns:
            Alert ID or None
        """
        try:
            self.cursor.execute("""
                INSERT INTO alerts (user_id, job_id, read)
                VALUES (?, ?, ?)
            """, (alert.user_id, alert.job_id, alert.read))
            self.connection.commit()
            return self.cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to add alert: {e}")
            return None
    
    # ==================== Statistics Methods ====================
    
    def get_total_jobs(self) -> int:
        """
        Get total number of jobs
        
        Returns:
            Total jobs count
        """
        try:
            self.cursor.execute("SELECT COUNT(*) as count FROM jobs")
            row = self.cursor.fetchone()
            return row['count'] if row else 0
        except Exception as e:
            logger.error(f"Failed to get total jobs: {e}")
            return 0
    
    def get_total_users(self) -> int:
        """
        Get total number of users
        
        Returns:
            Total users count
        """
        try:
            self.cursor.execute("SELECT COUNT(*) as count FROM users")
            row = self.cursor.fetchone()
            return row['count'] if row else 0
        except Exception as e:
            logger.error(f"Failed to get total users: {e}")
            return 0
