"""
llm.py
------
Writes a real code review + a 0-100 score for a repo.

Two modes, chosen automatically:
  * GEMINI_API_KEY set (in .env)  -> Google Gemini (cloud, best quality, hostable)
  * otherwise                     -> local Ollama model (offline, free, no key)

Gemini calls auto-retry on 429 (rate limit) and fall back across models.
"""

import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Tried in order; first that works wins. Flash-lite has the highest free limit.
GEMINI_MODELS = [GEMINI_MODEL, "gemini-2.5-flash-lite", "gemini-1.5-flash"]

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"


def _build_prompt(repo_meta, checks, readme_text, files, languages):
    file_sample = "\n".join(files[:60])
    langs = ", ".join(languages.keys()) if languages else "unknown"
    return f"""You are a senior software engineer AND a technical recruiter reviewing a
student's GitHub project for their portfolio. Judge it FAIRLY: reward projects
that actually work and are well organised, even if they are frontend-only or
small. Do NOT demand enterprise features from a student project, but DO give
honest, specific, actionable feedback.

Repository: {repo_meta.get('full_name')}
Description: {repo_meta.get('description')}
Primary languages: {langs}
Stars: {repo_meta.get('stargazers_count')}  Forks: {repo_meta.get('forks_count')}

File list (up to 60 files):
{file_sample}

Automated checks:
{json.dumps(checks, indent=2)}

README excerpt (first 2000 chars):
{readme_text[:2000]}

Return ONLY valid JSON in EXACTLY this shape (no extra text):
{{
  "ai_score": <integer 0-100, overall quality for a student portfolio>,
  "project_type": "e.g. Frontend website / Full-stack app / ML project / CLI tool",
  "summary": "2-3 sentence honest overall impression",
  "estimated_developer_level": "Beginner | Intermediate | Advanced",
  "strengths": ["specific point about THIS project", "another specific point"],
  "improvements": ["specific actionable tip", "another", "another"]
}}
"""


def _sanitize(data):
    try:
        data["ai_score"] = max(0, min(100, int(data.get("ai_score"))))
    except Exception:
        data["ai_score"] = None
    return data


def _fallback(msg):
    return {
        "ai_score": None,
        "project_type": "Unknown",
        "summary": msg,
        "estimated_developer_level": "Unknown",
        "strengths": [],
        "improvements": [],
    }


def _gemini_review(prompt):
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "response_mime_type": "application/json"},
    }
    last = "unknown error"
    for model in dict.fromkeys(GEMINI_MODELS):  # de-duplicated, order preserved
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={GEMINI_API_KEY}"
        )
        for attempt in range(2):  # one retry per model on 429
            resp = requests.post(url, json=body, timeout=60)
            if resp.status_code == 429:
                last = f"429 rate/quota on {model}"
                time.sleep(4)
                continue
            resp.raise_for_status()
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            return _sanitize(json.loads(text))
    raise RuntimeError(last)


def _ollama_review(prompt):
    resp = requests.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False,
              "format": "json", "options": {"temperature": 0.3}},
        timeout=240,
    )
    resp.raise_for_status()
    return _sanitize(json.loads(resp.json().get("response", "{}")))


def get_llm_review(repo_meta, checks, readme_text, files, languages):
    prompt = _build_prompt(repo_meta, checks, readme_text, files, languages)
    try:
        if GEMINI_API_KEY:
            return _gemini_review(prompt)
        return _ollama_review(prompt)
    except Exception as e:
        where = "Gemini" if GEMINI_API_KEY else "Ollama"
        return _fallback(f"AI review unavailable via {where} ({e}). Rule-based score still valid.")
