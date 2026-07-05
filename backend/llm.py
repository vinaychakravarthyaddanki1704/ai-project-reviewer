"""
llm.py
------
Sends the repo (file list + languages + README + checks) to a local Ollama
model and asks for a REAL review AND a 0-100 score. Runs locally, no API key.

Default model is small/fast. For much better reviews, pull a code model:
    ollama pull qwen2.5-coder:7b
then change MODEL below to "qwen2.5-coder:7b".
"""

import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"  # better: "qwen2.5-coder:7b" or "llama3.1:8b" (need more RAM)


def get_llm_review(repo_meta, checks, readme_text, files, languages):
    file_sample = "\n".join(files[:60])
    langs = ", ".join(languages.keys()) if languages else "unknown"

    prompt = f"""You are a senior software engineer AND a technical recruiter reviewing a
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
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.3},
            },
            timeout=240,
        )
        resp.raise_for_status()
        data = json.loads(resp.json().get("response", "{}"))
        try:
            data["ai_score"] = max(0, min(100, int(data.get("ai_score"))))
        except Exception:
            data["ai_score"] = None
        return data
    except Exception as e:
        return {
            "ai_score": None,
            "project_type": "Unknown",
            "summary": f"AI review unavailable ({e}). Is Ollama running? Showing rule-based score only.",
            "estimated_developer_level": "Unknown",
            "strengths": [],
            "improvements": [],
        }
