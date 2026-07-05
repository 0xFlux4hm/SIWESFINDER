"""
SIWES Hunter NG - Real Multi-Source Scraper
"""
import logging
import time
import hashlib
import requests
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime
from database.models import Job
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}

def _get(url, timeout=20):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        logger.warning("GET failed %s - %s", url, e)
        return None

def _clean(text):
    return " ".join(text.split()).strip() if text else ""

def _fingerprint(title, company, location):
    raw = f"{title.lower()}{company.lower()}{location.lower()}"
    return hashlib.md5(raw.encode()).hexdigest()


class LinkedInScraper(BaseScraper):

    def __init__(self):
        super().__init__('MultiSource')

    def scrape(self):
        jobs = []
        start_time = time.time()
        seen = set()

        for fn in [
            self._jobberman,
            self._myjobmag,
            self._ngcareers,
            self._graduatejobs,
            self._hotnigerianjobs,
        ]:
            try:
                for job in fn():
                    if job.hash not in seen:
                        seen.add(job.hash)
                        jobs.append(job)
                time.sleep(2)
            except Exception as e:
                logger.error("%s failed: %s", fn.__name__, e)

        duration = time.time() - start_time
        self.log_scrape('success', len(jobs), len(jobs), duration=duration)
        return jobs

    def _jobberman(self):
        jobs = []
        for q in ["internship", "industrial-training", "graduate-trainee", "SIWES"]:
            url = f"https://www.jobberman.com/jobs?q={q}&l=nigeria"
            soup = _get(url)
            if not soup:
                continue
            for card in soup.select("article, .job-card, li.job")[:10]:
                title_el = card.select_one("h3 a, h2 a, .job-title a")
                company_el = card.select_one(".company-name, [class*='company']")
                location_el = card.select_one(".location, [class*='location']")
                link_el = card.select_one("a[href]")
                title = _clean(title_el.text) if title_el else ""
                company = _clean(company_el.text) if company_el else "N/A"
                location = _clean(location_el.text) if location_el else "Nigeria"
                link = link_el.get("href", "") if link_el else ""
                if link.startswith("/"):
                    link = "https://www.jobberman.com" + link
                if not title:
                    continue
                jobs.append(Job(
                    title=title, company=company, location=location,
                    stipend="See listing", application_link=link or url,
                    source="Jobberman", job_type="Internship", remote=False,
                    hash=_fingerprint(title, company, location),
                ))
            time.sleep(1.5)
        logger.info("Jobberman: %d jobs", len(jobs))
        return jobs

    def _myjobmag(self):
        jobs = []
        for q in ["internship", "industrial-training", "SIWES"]:
            url = f"https://www.myjobmag.com/jobs-by-title/{q}"
            soup = _get(url)
            if not soup:
                continue
            for card in soup.select(".job-list-item, article.job, li.job-listing")[:10]:
                title_el = card.select_one("h2 a, h3 a, .job-title a")
                company_el = card.select_one(".company-name, .employer")
                location_el = card.select_one(".location, .job-location")
                link_el = card.select_one("a[href]")
                title = _clean(title_el.text) if title_el else ""
                company = _clean(company_el.text) if company_el else "N/A"
                location = _clean(location_el.text) if location_el else "Nigeria"
                link = link_el.get("href", "") if link_el else ""
                if link.startswith("/"):
                    link = "https://www.myjobmag.com" + link
                if not title:
                    continue
                jobs.append(Job(
                    title=title, company=company, location=location,
                    stipend="See listing", application_link=link or url,
                    source="MyJobMag", job_type="Internship", remote=False,
                    hash=_fingerprint(title, company, location),
                ))
            time.sleep(1.5)
        logger.info("MyJobMag: %d jobs", len(jobs))
        return jobs

    def _ngcareers(self):
        jobs = []
        url = "https://ngcareers.com/jobs/?s=internship+SIWES"
        soup = _get(url)
        if not soup:
            return jobs
        for card in soup.select("article, .job-listing")[:15]:
            title_el = card.select_one("h2 a, h3 a")
            company_el = card.select_one(".company, .employer")
            location_el = card.select_one(".location")
            title = _clean(title_el.text) if title_el else ""
            company = _clean(company_el.text) if company_el else "N/A"
            location = _clean(location_el.text) if location_el else "Nigeria"
            link = title_el.get("href", url) if title_el else url
            if not title:
                continue
            jobs.append(Job(
                title=title, company=company, location=location,
                stipend="See listing", application_link=link,
                source="NGCareers", job_type="Internship", remote=False,
                hash=_fingerprint(title, company, location),
            ))
        logger.info("NGCareers: %d jobs", len(jobs))
        return jobs

    def _graduatejobs(self):
        jobs = []
        for url in [
            "https://graduatejobsng.com/category/internship/",
            "https://graduatejobsng.com/category/graduate-trainee/",
        ]:
            soup = _get(url)
            if not soup:
                continue
            for card in soup.select("article, .post")[:10]:
                title_el = card.select_one("h2 a, h3 a, .entry-title a")
                title = _clean(title_el.text) if title_el else ""
                link = title_el.get("href", url) if title_el else url
                if not title:
                    continue
                jobs.append(Job(
                    title=title, company="See listing", location="Nigeria",
                    stipend="See listing", application_link=link,
                    source="GraduateJobsNG", job_type="Internship", remote=False,
                    hash=_fingerprint(title, "graduatejobsng", url),
                ))
            time.sleep(1)
        logger.info("GraduateJobsNG: %d jobs", len(jobs))
        return jobs

    def _hotnigerianjobs(self):
        jobs = []
        url = "https://www.hotnigerianjobs.com/hotjobs/internship/"
        soup = _get(url)
        if not soup:
            return jobs
        for card in soup.select("article, .job-item, .post")[:10]:
            title_el = card.select_one("h2 a, h3 a")
            company_el = card.select_one(".company, .employer")
            title = _clean(title_el.text) if title_el else ""
            company = _clean(company_el.text) if company_el else "N/A"
            link = title_el.get("href", url) if title_el else url
            if not title:
                continue
            jobs.append(Job(
                title=title, company=company, location="Nigeria",
                stipend="See listing", application_link=link,
                source="HotNigerianJobs", job_type="Internship", remote=False,
                hash=_fingerprint(title, company, "nigeria"),
            ))
        logger.info("HotNigerianJobs: %d jobs", len(jobs))
        return jobs
