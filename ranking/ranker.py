"""
Job ranking engine
"""
import logging
from typing import List
from database.models import Job
from database.manager import DatabaseManager
from config.constants import (
    RANKING_WEIGHTS,
    CYBERSECURITY_KEYWORDS,
    SOFTWARE_ENGINEERING_KEYWORDS,
    DATA_ANALYSIS_KEYWORDS,
)

logger = logging.getLogger(__name__)


class Ranker:
    """
    Ranks job opportunities based on relevance and other factors
    """
    
    def __init__(self, db_manager: DatabaseManager = None):
        """
        Initialize ranker
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager or DatabaseManager()
    
    def rank_job(self, job: Job) -> float:
        """
        Calculate rank score for a job
        
        Args:
            job: Job object
        
        Returns:
            Rank score (0-100)
        """
        score = 0.0
        
        # Cybersecurity relevance (20%)
        if self._check_keywords(job, CYBERSECURITY_KEYWORDS):
            score += 20
        
        # Software engineering relevance (20%)
        if self._check_keywords(job, SOFTWARE_ENGINEERING_KEYWORDS):
            score += 20
        
        # Computer science relevance (15%)
        if self._check_relevance(job):
            score += 15
        
        # Stipend amount (20%)
        stipend_score = self._score_stipend(job.stipend)
        score += stipend_score * 0.2
        
        # Company reputation (15%)
        reputation_score = self._score_company(job.company)
        score += reputation_score * 0.15
        
        # Remote availability (5%)
        if job.remote:
            score += 5
        
        # Location preference (5%)
        if job.location:
            score += 5
        
        return min(score, 100.0)
    
    def _check_keywords(self, job: Job, keywords: List[str]) -> bool:
        """
        Check if job matches keywords
        
        Args:
            job: Job object
            keywords: List of keywords
        
        Returns:
            True if job matches any keyword
        """
        text = f"{job.title} {job.description or ''}".
        text_lower = text.lower()
        
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return True
        
        return False
    
    def _check_relevance(self, job: Job) -> bool:
        """
        Check if job is relevant to computer science
        
        Args:
            job: Job object
        
        Returns:
            True if relevant
        """
        cs_keywords = [
            'software', 'developer', 'engineer', 'programming',
            'technology', 'it', 'computer', 'data', 'cloud',
        ]
        
        text = f"{job.title} {job.job_type or ''}".lower()
        
        for keyword in cs_keywords:
            if keyword in text:
                return True
        
        return False
    
    def _score_stipend(self, stipend: str) -> float:
        """
        Score job based on stipend amount
        
        Args:
            stipend: Stipend information
        
        Returns:
            Score (0-100)
        """
        if not stipend:
            return 0.0
        
        # Extract numeric value from stipend
        import re
        matches = re.findall(r'\d+(?:,\d+)?', stipend.replace(',', ''))
        
        if matches:
            try:
                amount = int(matches[0])
                # Score based on amount
                if amount >= 100000:  # ₦100,000+
                    return 100.0
                elif amount >= 50000:  # ₦50,000+
                    return 80.0
                elif amount >= 20000:  # ₦20,000+
                    return 60.0
                else:
                    return 30.0
            except ValueError:
                return 0.0
        
        return 0.0
    
    def _score_company(self, company: str) -> float:
        """
        Score job based on company reputation
        
        Args:
            company: Company name
        
        Returns:
            Score (0-100)
        """
        # List of top companies
        top_companies = [
            'google', 'microsoft', 'facebook', 'amazon', 'apple',
            'ibm', 'intel', 'cisco', 'oracle', 'vmware',
            'bank', 'fintech', 'telecom', 'nigerian',
        ]
        
        company_lower = company.lower()
        
        for top_company in top_companies:
            if top_company in company_lower:
                return 80.0
        
        return 50.0
    
    def rank_all_jobs(self, jobs: List[Job] = None) -> List[Job]:
        """
        Rank all jobs in database
        
        Args:
            jobs: Optional list of jobs to rank
        
        Returns:
            List of ranked jobs sorted by score
        """
        if jobs is None:
            jobs = self.db_manager.get_jobs(limit=1000)
        
        for job in jobs:
            score = self.rank_job(job)
            job.rank_score = score
            self.db_manager.update_job_rank(job.id, score)
        
        # Sort by rank score
        jobs.sort(key=lambda x: x.rank_score, reverse=True)
        
        logger.info(f"Ranked {len(jobs)} jobs")
        
        return jobs
