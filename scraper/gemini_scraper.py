"""
SIWES Hunter NG - Gemini AI Scraper
Uses Google Gemini free API to find SIWES/internship opportunities.
Free tier: 15 requests/minute, 1M tokens/day
"""
import logging
import time
import hashlib
import requests
import json
import re
from database.models import Job
from config.settings import settings

logger = logging.getLogger(__name__)

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent"
)

PROMPTS = [
    """
List 10 current SIWES and Industrial Training opportunities
for Nigerian Computer Science students in 2026.
Focus on: Paystack, Flutterwave, MTN, Airtel, GTBank,
Access Bank, Zenith Bank, Shell, TotalEnergies, Chevron,
NITDA, NCC, Dangote, Nestlé, Unilever, Kuda, Interswitch.
Format as JSON array with these exact fields:
title, company, location, stipend, apply_url, deadline
Return ONLY the JSON array. No explanation. No markdown.
""",

    """
List 10 Internship and Graduate Trainee programs open to
Nigerian university students in technology and finance in 2026.
Include both Lagos and Abuja opportunities.
Include stipend amounts where known in Nigerian Naira.
Format as JSON array with these exact fields:
title, company, location, stipend, apply_url, deadline
Return ONLY the JSON array. No explanation. No markdown.
""",

    """
List 10 Cybersecurity, Software Engineering, Data Analysis,
and Networking internship roles available for Nigerian
students in 2026. Include remote opportunities.
Format as JSON array with these exact fields:
title, company, location, stipend, apply_url, deadline
Return ONLY the JSON array. No explanation. No markdown.
""",

    """
List 10 Oil and Gas, Telecom, and Banking student
internship and SIWES attachment programs in Nigeria 2026.
Include Shell, TotalEnergies, Chevron, NNPC, MTN, Airtel,
GTBank, UBA, First Bank, Zenith Bank programs.
Format as JSON array with these exact fields:
title, company, location, stipend, apply_url, deadline
Return ONLY the JSON array. No explanation. No markdown.
""",
]


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
                f"{response.text[:200]}"
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

    for i, prompt in enumerate(PROMPTS):
        logger.info(f"Gemini prompt {i+1}/{len(PROMPTS)}...")
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

        # Respect free tier rate limit
        time.sleep(5)

    logger.info(f"Gemini AI: {len(jobs)} jobs found")
    return jobs
