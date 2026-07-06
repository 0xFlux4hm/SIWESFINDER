"""
SIWES Hunter NG - Complete Nigerian Job Scraper
Sources: Remotive, Arbeitnow, Google News RSS, 
Nigerian company career pages, Government portals
"""
import logging
import time
import hashlib
import requests
import re
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

NIGERIA_KW = [
    "nigeria", "lagos", "abuja", "kaduna", "kano", "ibadan",
    "port harcourt", "nigerian", "enugu", "benin", "warri",
]

INTERN_KW = [
    "intern", "siwes", "industrial training", "trainee",
    "attachment", "graduate trainee", "nysc", "it student",
    "student", "undergraduate", "it intern",
]

CYBER_KW = [
    "cyber", "security", "pentest", "soc", "network",
    "information security", "infosec",
]

SOFTWARE_KW = [
    "software", "developer", "engineer", "python", "java",
    "react", "backend", "frontend", "fullstack", "mobile",
    "flutter", "kotlin", "nodejs", "django",
]

DATA_KW = [
    "data analyst", "data science", "machine learning",
    "ai", "artificial intelligence", "business analyst",
]


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
    return " ".join(str(text).split()).strip() if text else ""


def _fp(title, company, location=""):
    raw = f"{title.lower()}{company.lower()}{location.lower()}"
    return hashlib.md5(raw.encode()).hexdigest()


def _is_nigeria(text):
    t = text.lower()
    return any(k in t for k in NIGERIA_KW)


def _is_intern(text):
    t = text.lower()
    return any(k in t for k in INTERN_KW)


def _get_category(text):
    t = text.lower()
    if any(k in t for k in CYBER_KW):
        return "Cybersecurity"
    if any(k in t for k in SOFTWARE_KW):
        return "Software Engineering"
    if any(k in t for k in DATA_KW):
        return "Data/AI"
    return "General IT"


def _extract_stipend(text):
    if not text:
        return "See listing"
    patterns = [
        r'₦[\d,]+(?:\s*[-–]\s*₦[\d,]+)?(?:\s*/\s*month)?',
        r'N[\d,]+(?:\s*[-–]\s*N[\d,]+)?(?:\s*/\s*month)?',
        r'\$[\d,]+(?:\s*[-–]\s*\$[\d,]+)?(?:\s*/\s*month)?',
        r'[\d,]+\s*(?:naira|NGN)(?:\s*/\s*month)?',
    ]
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            return m.group(0).strip()
    if any(w in text.lower() for w in ["paid", "stipend", "allowance"]):
        return "Paid (see listing)"
    return "See listing"


class LinkedInScraper(BaseScraper):

    def __init__(self):
        super().__init__('MultiSource')

    def scrape(self) -> List[Job]:
        jobs = []
        start_time = time.time()
        seen = set()

        sources = [
            self._remotive,
            self._arbeitnow,
            self._google_news_siwes,
            self._google_news_internship,
            self._google_news_companies,
            self._mtn_careers,
            self._gtbank_careers,
            self._dangote_careers,
            self._nairaland_jobs,
            self._scholarshipregion,
        ]

        for fn in sources:
            try:
                results = fn()
                for job in results:
                    if job.hash not in seen:
                        seen.add(job.hash)
                        jobs.append(job)
                time.sleep(1.5)
            except Exception as e:
                logger.error("%s failed: %s", fn.__name__, e)

        duration = time.time() - start_time
        self.log_scrape('success', len(jobs), len(jobs), duration=duration)
        return jobs

    # ── REMOTIVE ──────────────────────────────────────────────────────────

    def _remotive(self):
        jobs = []
        searches = [
            "https://remotive.com/api/remote-jobs?search=intern+nigeria&limit=20",
            "https://remotive.com/api/remote-jobs?search=SIWES&limit=10",
            "https://remotive.com/api/remote-jobs?category=software-dev&search=intern&limit=15",
            "https://remotive.com/api/remote-jobs?category=cybersecurity&limit=15",
            "https://remotive.com/api/remote-jobs?category=data&search=intern&limit=10",
        ]
        for url in searches:
            data = _get_json(url)
            if not data or "jobs" not in data:
                continue
            for item in data["jobs"][:10]:
                title = _clean(item.get("title", ""))
                company = _clean(item.get("company_name", "N/A"))
                location = _clean(
                    item.get("candidate_required_location", "Remote")
                )
                link = item.get("url", "")
                desc = item.get("description", "")
                tags = " ".join(item.get("tags", []))
                pub_date = item.get("publication_date", "")[:10]

                if not title:
                    continue
                if not _is_intern(f"{title} {tags} {desc[:200]}"):
                    continue

                stipend = _extract_stipend(desc[:500])
                category = _get_category(f"{title} {tags}")

                jobs.append(Job(
                    title=title,
                    company=company,
                    location=f"{location} 🌐 Remote",
                    stipend=stipend,
                    application_link=link,
                    source=f"Remotive ({category})",
                    job_type="Remote Internship",
                    remote=True,
                    hash=_fp(title, company, location),
                ))
            time.sleep(1)
        logger.info("Remotive: %d jobs", len(jobs))
        return jobs

    # ── ARBEITNOW ─────────────────────────────────────────────────────────

    def _arbeitnow(self):
        jobs = []
        searches = [
            "https://www.arbeitnow.com/api/job-board-api?search=intern+nigeria",
            "https://www.arbeitnow.com/api/job-board-api?search=graduate+trainee+nigeria",
            "https://www.arbeitnow.com/api/job-board-api?search=SIWES+nigeria",
            "https://www.arbeitnow.com/api/job-board-api?search=cybersecurity+intern",
            "https://www.arbeitnow.com/api/job-board-api?search=software+intern+nigeria",
        ]
        for url in searches:
            data = _get_json(url)
            if not data or "data" not in data:
                continue
            for item in data["data"][:8]:
                title = _clean(item.get("title", ""))
                company = _clean(item.get("company_name", "N/A"))
                location = _clean(item.get("location", "Remote"))
                link = item.get("url", "")
                tags = " ".join(item.get("tags", []))
                desc = item.get("description", "")

                if not title:
                    continue
                if not (
                    _is_nigeria(f"{title} {company} {location} {tags} {desc}") or
                    _is_intern(f"{title} {tags}")
                ):
                    continue

                stipend = _extract_stipend(desc[:500])
                category = _get_category(f"{title} {tags}")

                jobs.append(Job(
                    title=title,
                    company=company,
                    location=location,
                    stipend=stipend,
                    application_link=link,
                    source=f"Arbeitnow ({category})",
                    job_type="Internship",
                    remote="remote" in location.lower(),
                    hash=_fp(title, company, location),
                ))
            time.sleep(1)
        logger.info("Arbeitnow: %d jobs", len(jobs))
        return jobs

    # ── GOOGLE NEWS — SIWES ───────────────────────────────────────────────

    def _google_news_siwes(self):
        jobs = []
        queries = [
            "SIWES+internship+Nigeria+2026",
            "SIWES+placement+Nigeria+2026",
            "industrial+training+Nigeria+2026",
            "SIWES+stipend+Nigeria+2026",
        ]
        for q in queries:
            url = (
                f"https://news.google.com/rss/search?q={q}"
                f"&hl=en-NG&gl=NG&ceid=NG:en"
            )
            soup = _get_html(url)
            if not soup:
                continue
            for item in soup.select("item")[:6]:
                title_el = item.find("title")
                link_el = item.find("link")
                desc_el = item.find("description")
                pub_el = item.find("pubdate")

                title = _clean(title_el.text) if title_el else ""
                link = link_el.text if link_el else ""
                desc = _clean(desc_el.text) if desc_el else ""
                pub = _clean(pub_el.text)[:16] if pub_el else ""

                if not title or not _is_intern(title):
                    continue

                stipend = _extract_stipend(f"{title} {desc}")

                jobs.append(Job(
                    title=title,
                    company="See article",
                    location="Nigeria",
                    stipend=stipend,
                    application_link=link,
                    source="Google News (SIWES)",
                    job_type="SIWES",
                    remote=False,
                    hash=_fp(title, "googlenews-siwes", q),
                ))
            time.sleep(1)
        logger.info("Google News SIWES: %d jobs", len(jobs))
        return jobs

    # ── GOOGLE NEWS — INTERNSHIP ──────────────────────────────────────────

    def _google_news_internship(self):
        jobs = []
        queries = [
            "internship+Nigeria+technology+2026",
            "graduate+trainee+Nigeria+fintech+2026",
            "IT+internship+Nigeria+2026",
            "cybersecurity+internship+Nigeria+2026",
            "software+engineering+intern+Nigeria+2026",
            "data+analyst+intern+Nigeria+2026",
        ]
        for q in queries:
            url = (
                f"https://news.google.com/rss/search?q={q}"
                f"&hl=en-NG&gl=NG&ceid=NG:en"
            )
            soup = _get_html(url)
            if not soup:
                continue
            for item in soup.select("item")[:5]:
                title_el = item.find("title")
                link_el = item.find("link")
                desc_el = item.find("description")

                title = _clean(title_el.text) if title_el else ""
                link = link_el.text if link_el else ""
                desc = _clean(desc_el.text) if desc_el else ""

                if not title or not _is_intern(title):
                    continue

                category = _get_category(title)
                stipend = _extract_stipend(f"{title} {desc}")

                jobs.append(Job(
                    title=title,
                    company="See article",
                    location="Nigeria",
                    stipend=stipend,
                    application_link=link,
                    source=f"Google News ({category})",
                    job_type="Internship",
                    remote=False,
                    hash=_fp(title, "googlenews-intern", q),
                ))
            time.sleep(1)
        logger.info("Google News Internship: %d jobs", len(jobs))
        return jobs

    # ── GOOGLE NEWS — TOP COMPANIES ───────────────────────────────────────

    def _google_news_companies(self):
        jobs = []
        companies = [
            "MTN+Nigeria+internship+2026",
            "Airtel+Nigeria+internship+2026",
            "GTBank+internship+2026",
            "Access+Bank+internship+2026",
            "Zenith+Bank+internship+2026",
            "UBA+internship+2026",
            "Dangote+internship+2026",
            "Shell+Nigeria+SIWES+2026",
            "TotalEnergies+Nigeria+internship+2026",
            "Chevron+Nigeria+internship+2026",
            "Flutterwave+internship+2026",
            "Paystack+internship+2026",
            "Interswitch+internship+2026",
            "NITDA+internship+2026",
            "NCC+internship+2026",
            "First+Bank+Nigeria+internship+2026",
            "Nestlé+Nigeria+SIWES+2026",
            "Unilever+Nigeria+internship+2026",
        ]
        for q in companies:
            url = (
                f"https://news.google.com/rss/search?q={q}"
                f"&hl=en-NG&gl=NG&ceid=NG:en"
            )
            soup = _get_html(url)
            if not soup:
                continue
            for item in soup.select("item")[:3]:
                title_el = item.find("title")
                link_el = item.find("link")
                desc_el = item.find("description")

                title = _clean(title_el.text) if title_el else ""
                link = link_el.text if link_el else ""
                desc = _clean(desc_el.text) if desc_el else ""

                if not title or not _is_intern(title):
                    continue

                company_name = q.split("+")[0]
                stipend = _extract_stipend(f"{title} {desc}")

                jobs.append(Job(
                    title=title,
                    company=company_name,
                    location="Nigeria",
                    stipend=stipend,
                    application_link=link,
                    source=f"Google News ({company_name})",
                    job_type="Internship",
                    remote=False,
                    hash=_fp(title, company_name, "nigeria"),
                ))
            time.sleep(0.5)
        logger.info("Google News Companies: %d jobs", len(jobs))
        return jobs

    # ── MTN CAREERS ───────────────────────────────────────────────────────

    def _mtn_careers(self):
        jobs = []
        url = "https://www.mtnonline.com/careers/"
        soup = _get_html(url)
        if not soup:
            return jobs
        for card in soup.select("article, .job, .career-item, .vacancy")[:10]:
            title_el = card.select_one("h2 a, h3 a, .title a")
            title = _clean(title_el.text) if title_el else ""
            link = title_el.get("href", url) if title_el else url
            if not title or not _is_intern(title):
                continue
            jobs.append(Job(
                title=title,
                company="MTN Nigeria",
                location="Lagos, Nigeria",
                stipend="Competitive",
                application_link=link,
                source="MTN Careers",
                job_type="Internship",
                remote=False,
                hash=_fp(title, "mtn", "lagos"),
            ))
        logger.info("MTN Careers: %d jobs", len(jobs))
        return jobs

    # ── GTBANK CAREERS ────────────────────────────────────────────────────

    def _gtbank_careers(self):
        jobs = []
        url = "https://www.gtbank.com/about-us/careers"
        soup = _get_html(url)
        if not soup:
            return jobs
        for card in soup.select(".job, .career, article, .vacancy")[:10]:
            title_el = card.select_one("h2 a, h3 a, .title")
            title = _clean(title_el.text) if title_el else ""
            if not title or not _is_intern(title):
                continue
            jobs.append(Job(
                title=title,
                company="GTBank",
                location="Lagos, Nigeria",
                stipend="Competitive",
                application_link=url,
                source="GTBank Careers",
                job_type="Internship",
                remote=False,
                hash=_fp(title, "gtbank", "lagos"),
            ))
        logger.info("GTBank Careers: %d jobs", len(jobs))
        return jobs

    # ── DANGOTE CAREERS ───────────────────────────────────────────────────

    def _dangote_careers(self):
        jobs = []
        url = "https://www.dangote.com/careers/"
        soup = _get_html(url)
        if not soup:
            return jobs
        for card in soup.select(".job, .career, article, .vacancy")[:10]:
            title_el = card.select_one("h2 a, h3 a, .title a")
            title = _clean(title_el.text) if title_el else ""
            if not title or not _is_intern(title):
                continue
            jobs.append(Job(
                title=title,
                company="Dangote Group",
                location="Nigeria",
                stipend="Competitive",
                application_link=url,
                source="Dangote Careers",
                job_type="Internship",
                remote=False,
                hash=_fp(title, "dangote", "nigeria"),
            ))
        logger.info("Dangote Careers: %d jobs", len(jobs))
        return jobs

    # ── NAIRALAND JOBS ────────────────────────────────────────────────────

    def _nairaland_jobs(self):
        jobs = []
        searches = [
            "https://www.nairaland.com/jobs/search?q=SIWES",
            "https://www.nairaland.com/jobs/search?q=internship",
            "https://www.nairaland.com/jobs/search?q=industrial+training",
        ]
        for url in searches:
            soup = _get_html(url)
            if not soup:
                continue
            for row in soup.select("td.subject a, .subject a")[:8]:
                title = _clean(row.text)
                link = row.get("href", "")
                if link.startswith("/"):
                    link = "https://www.nairaland.com" + link
                if not title or not _is_intern(title):
                    continue
                jobs.append(Job(
                    title=title,
                    company="See post",
                    location="Nigeria",
                    stipend="See listing",
                    application_link=link,
                    source="Nairaland Jobs",
                    job_type="Internship",
                    remote=False,
                    hash=_fp(title, "nairaland", url),
                ))
            time.sleep(2)
        logger.info("Nairaland: %d jobs", len(jobs))
        return jobs

    # ── SCHOLARSHIP REGION ────────────────────────────────────────────────

    def _scholarshipregion(self):
        jobs = []
        searches = [
            "https://scholarshipregion.com/?s=SIWES+Nigeria",
            "https://scholarshipregion.com/?s=internship+Nigeria+2026",
            "https://scholarshipregion.com/?s=industrial+training+Nigeria",
        ]
        for url in searches:
            soup = _get_html(url)
            if not soup:
                continue
            for card in soup.select("article, .post")[:6]:
                title_el = card.select_one("h2 a, h3 a, .entry-title a")
                title = _clean(title_el.text) if title_el else ""
                link = title_el.get("href", url) if title_el else url
                if not title or not _is_intern(title):
                    continue
                jobs.append(Job(
                    title=title,
                    company="See article",
                    location="Nigeria",
                    stipend="See listing",
                    application_link=link,
                    source="ScholarshipRegion",
                    job_type="SIWES/Internship",
                    remote=False,
                    hash=_fp(title, "scholarshipregion", url),
                ))
            time.sleep(1)
        logger.info("ScholarshipRegion: %d jobs", len(jobs))
        return jobs
