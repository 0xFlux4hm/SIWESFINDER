"""
SIWES Hunter NG - Global-Access Scraper
Uses job sources accessible from GitHub Actions (US servers).
"""
import logging
import time
import hashlib
import requests
from bs4 import BeautifulSoup
from typing import List
from database.models import Job
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html, */*",
}

def _get_html(url, timeout=20):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        logger.warning("HTML GET failed %s - %s", url, e)
        return None

def _get_json(url, timeout=20):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.warning("JSON GET failed %s - %s", url, e)
        return None

def _clean(text):
    return " ".join(text.split()).strip() if text else ""

def _fp(title, company, location=""):
    raw = f"{title.lower()}{company.lower()}{location.lower()}"
    return hashlib.md5(raw.encode()).hexdigest()

NIGERIA_KW = ["nigeria","lagos","abuja","kaduna","kano","ibadan","port harcourt","nigerian"]
INTERN_KW = ["intern","siwes","industrial training","trainee","attachment","graduate trainee","nysc"]

def _is_nigeria(text):
    t = text.lower()
    return any(k in t for k in NIGERIA_KW)

def _is_intern(text):
    t = text.lower()
    return any(k in t for k in INTERN_KW)


class LinkedInScraper(BaseScraper):

    def __init__(self):
        super().__init__('MultiSource')

    def scrape(self):
        jobs = []
        start_time = time.time()
        seen = set()

        sources = [
            self._arbeitnow,
            self._remotive,
            self._greenhouse_paystack,
            self._greenhouse_flutterwave,
            self._lever_andela,
            self._google_jobs_rss,
        ]

        for fn in sources:
            try:
                results = fn()
                for job in results:
                    if job.hash not in seen:
                        seen.add(job.hash)
                        jobs.append(job)
                time.sleep(1)
            except Exception as e:
                logger.error("%s failed: %s", fn.__name__, e)

        duration = time.time() - start_time
        self.log_scrape('success', len(jobs), len(jobs), duration=duration)
        return jobs

    def _arbeitnow(self):
        jobs = []
        searches = [
            "https://www.arbeitnow.com/api/job-board-api?search=intern+nigeria",
            "https://www.arbeitnow.com/api/job-board-api?search=internship+nigeria",
            "https://www.arbeitnow.com/api/job-board-api?search=SIWES",
        ]
        for url in searches:
            data = _get_json(url)
            if not data or "data" not in data:
                continue
            for item in data["data"][:10]:
                title = _clean(item.get("title", ""))
                company = _clean(item.get("company_name", "N/A"))
                location = _clean(item.get("location", "Remote"))
                link = item.get("url", "")
                tags = " ".join(item.get("tags", []))
                desc = item.get("description", "")
                if not title:
                    continue
                if not (_is_nigeria(f"{title} {company} {location} {tags} {desc}") or
                        _is_intern(f"{title} {tags}")):
                    continue
                jobs.append(Job(
                    title=title, company=company, location=location,
                    stipend="See listing", application_link=link,
                    source="Arbeitnow", job_type="Internship",
                    remote="remote" in location.lower(),
                    hash=_fp(title, company, location),
                ))
            time.sleep(1)
        logger.info("Arbeitnow: %d jobs", len(jobs))
        return jobs

    def _remotive(self):
        jobs = []
        searches = [
            "https://remotive.com/api/remote-jobs?search=intern+nigeria&limit=20",
            "https://remotive.com/api/remote-jobs?category=software-dev&search=intern&limit=20",
            "https://remotive.com/api/remote-jobs?category=cybersecurity&limit=20",
        ]
        for url in searches:
            data = _get_json(url)
            if not data or "jobs" not in data:
                continue
            for item in data["jobs"][:10]:
                title = _clean(item.get("title", ""))
                company = _clean(item.get("company_name", "N/A"))
                location = _clean(item.get("candidate_required_location", "Remote"))
                link = item.get("url", "")
                desc = item.get("description", "")
                if not title:
                    continue
                if not _is_intern(f"{title} {desc}"):
                    continue
                jobs.append(Job(
                    title=title, company=company,
                    location=f"{location} (Remote)",
                    stipend="See listing", application_link=link,
                    source="Remotive", job_type="Internship", remote=True,
                    hash=_fp(title, company, location),
                ))
            time.sleep(1)
        logger.info("Remotive: %d jobs", len(jobs))
        return jobs

    def _greenhouse_paystack(self):
        return self._greenhouse("paystack", "Paystack")

    def _greenhouse_flutterwave(self):
        return self._greenhouse("flutterwave", "Flutterwave")

    def _greenhouse(self, board_token, company):
        jobs = []
        url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
        data = _get_json(url)
        if not data or "jobs" not in data:
            return jobs
        for item in data["jobs"][:20]:
            title = _clean(item.get("title", ""))
            location = _clean(item.get("location", {}).get("name", "Nigeria"))
            link = item.get("absolute_url", "")
            if not title:
                continue
            if not _is_intern(title):
                continue
            jobs.append(Job(
                title=title, company=company, location=location,
                stipend="Competitive", application_link=link,
                source=f"Careers ({company})", job_type="Internship",
                remote="remote" in location.lower(),
                hash=_fp(title, company, location),
            ))
        logger.info("%s Greenhouse: %d jobs", company, len(jobs))
        return jobs

    def _lever_andela(self):
        jobs = []
        url = "https://api.lever.co/v0/postings/andela?mode=json"
        data = _get_json(url)
        if not data:
            return jobs
        for item in data[:20]:
            title = _clean(item.get("text", ""))
            location = _clean(item.get("categories", {}).get("location", "Remote"))
            link = item.get("hostedUrl", "")
            if not title:
                continue
            if not _is_intern(title):
                continue
            jobs.append(Job(
                title=title, company="Andela", location=location,
                stipend="Competitive", application_link=link,
                source="Careers (Andela)", job_type="Internship",
                remote=True, hash=_fp(title, "andela", location),
            ))
        logger.info("Andela Lever: %d jobs", len(jobs))
        return jobs

    def _google_jobs_rss(self):
        jobs = []
        queries = [
            "SIWES+internship+Nigeria+2026",
            "industrial+training+Nigeria+tech+2026",
            "graduate+trainee+Nigeria+fintech+2026",
        ]
        for q in queries:
            url = f"https://news.google.com/rss/search?q={q}&hl=en-NG&gl=NG&ceid=NG:en"
            soup = _get_html(url)
            if not soup:
                continue
            for item in soup.select("item")[:8]:
                title_el = item.find("title")
                link_el = item.find("link")
                title = _clean(title_el.text) if title_el else ""
                link = link_el.text if link_el else ""
                if not title or not _is_intern(title):
                    continue
                jobs.append(Job(
                    title=title, company="See article",
                    location="Nigeria", stipend="See listing",
                    application_link=link,
                    source="Google News", job_type="Internship",
                    remote=False, hash=_fp(title, "googlenews", q),
                ))
            time.sleep(1)
        logger.info("Google News: %d jobs", len(jobs))
        return jobs
