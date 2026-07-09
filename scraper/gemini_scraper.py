"""
SIWES Hunter NG - Gemini AI Scraper
Optimized: Only 1 API request per run to stay within free limits.
Free tier: 15 requests/minute, 1,500/day — we use only 3/day
"""
import logging
import time
import hashlib
import requests
import json
import re
from datetime import datetime
from database.models import Job
from config.settings import settings

logger = logging.getLogger(__name__)

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)

# Rotate prompts based on time of day
# 8AM = SIWES focus, 2PM = Tech focus, 8PM = Banking/Oil focus
def _get_prompt():
    hour = datetime.utcnow().hour
    if hour < 12:
        return """
List 15 current SIWES, Industrial Training and Internship
opportunities for Nigerian Computer Science students in 2026.
Include opportunities from MTN, Airtel, GTBank, Access Bank,
Zenith Bank, UBA, First Bank, Paystack, Flutterwave, Shell,
TotalEnergies, Chevron, Dangote, Nestle, NITDA, NCC, Kuda.
For each include real application website URL.
Format as JSON array with fields:
title, company, location, stipend, apply_url, deadline
Return ONLY the JSON array. No markdown. No explanation.
"""
    elif hour < 18:
        return """
List 15 Software Engineering, Cybersecurity, Data Analysis,
Networking and IT internship opportunities for Nigerian
students in 2026. Include both remote and on-site roles.
Include opportunities from tech companies, startups and
multinational companies operating in Nigeria.
For each include real application website URL.
Format as JSON array with fields:
title, company, location, stipend, apply_url, deadline
Return ONLY the JSON array. No markdown. No explanation.
"""
    else:
        return """
List 15 Graduate Trainee and Internship programs currently
open in Nigeria for 2026. Focus on Banking, Oil and Gas,
Telecom and Government agencies. Include GTBank, Zenith Bank,
UBA, Access Bank, First Bank, Shell, TotalEnergies, Chevron,
NNPC, MTN, Airtel, NITDA, NCC, Dangote, Nestle programs.
Include real stipend amounts in Naira where known.
For each include real application website URL.
Format as JSON array with fields:
title, company, location, stipend, apply_url, deadline
Return ONLY the JSON array. No markdown. No explanation.
"""


def _fp(title, company, location=""):
    raw = f"{title.lower()}{company.lower()}{location.lower()}gemini"
    return hashlib.md5(raw.encode()).hexdigest()


def _clean(text):
    return " ".join(str(text).split()).strip() if text else ""


def _ask_gemini(prompt: str) -> list:
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return []

    try:
        response = requests.post(
            f"{GEMINI_URL}?key={api_key}",
            json={
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 2048,
                }
            },
            timeout=30,
        )

        if not response.ok:
            logger.error(
                f"Gemini error: {response.status_code} "
                f"{response.text[:300]}"
            )
            return []

        data = response.json()
        text = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )

        # Clean response
        text = text.strip()
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        text = text.strip()

        # Extract JSON array
        start = text.find('[')
        end = text.rfind(']') + 1
        if start == -1 or end == 0:
            logger.warning("No JSON in Gemini response")
            return []

        return json.loads(text[start:end])

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        return []
    except Exception as e:
        logger.error(f"Gemini request failed: {e}")
        return []


def scrape_gemini() -> list:
    if not settings.GEMINI_API_KEY:
        logger.info("Gemini API key not set — skipping")
        return []

    if not settings.ENABLE_GEMINI:
        logger.info("Gemini disabled — skipping")
        return []

    jobs = []
    seen = set()

    # Only 1 request per run — stays well within free limits
    prompt = _get_prompt()
    logger.info("Gemini AI: sending 1 request...")
    results = _ask_gemini(prompt)

    for item in results:
        try:
            title = _clean(item.get("title", ""))
            company = _clean(item.get("company", "N/A"))
            location = _clean(item.get("location", "Nigeria"))
            stipend = _clean(item.get("stipend", "See listing"))
            apply_url = _clean(item.get("apply_url", ""))
            deadline = _clean(item.get("deadline", ""))

            if not title or not company:
                continue

            fp = _fp(title, company, location)
            if fp in seen:
                continue
            seen.add(fp)

            display_title = title
            if deadline:
                display_title = f"{title} — Deadline: {deadline}"

            # Fix empty URLs
            if not apply_url or apply_url in ["N/A", "TBD", ""]:
                apply_url = (
                    f"https://www.google.com/search?q="
                    f"{company.replace(' ', '+')}+"
                    f"internship+Nigeria+2026"
                )

            jobs.append(Job(
                title=display_title,
                company=company,
                location=location,
                stipend=stipend or "See listing",
                application_link=apply_url,
                source="🤖 Gemini AI",
                job_type="SIWES/Internship",
                remote="remote" in location.lower(),
                hash=fp,
            ))

        except Exception as e:
            logger.error(f"Gemini result error: {e}")
            continue

    logger.info(f"Gemini AI: {len(jobs)} jobs found")
    return jobs
