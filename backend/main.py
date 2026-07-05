"""
main.py
-------
FastAPI app. Combines objective checks + a local-AI review into one score.
Run:  uvicorn main:app --reload   then open http://localhost:8000
"""

import os
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from github_client import parse_repo_url, fetch_repo_data
from checks import run_checks, rule_based_score
from llm import get_llm_review

app = FastAPI(title="AI Project Reviewer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    url: str
    github_token: Optional[str] = None


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    try:
        owner, repo = parse_repo_url(req.url)
    except ValueError as e:
        return {"error": str(e)}

    try:
        repo_data = fetch_repo_data(owner, repo, req.github_token)
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Failed to fetch repo: {e}"}

    checks = run_checks(repo_data)
    rule_score = rule_based_score(checks)

    review = get_llm_review(
        repo_data["meta"], checks, repo_data["readme_text"],
        repo_data["files"], repo_data["languages"],
    )

    # Blend: 50% objective checks, 50% AI judgment (if the AI answered).
    ai_score = review.get("ai_score")
    if ai_score is not None:
        final_score = round(0.5 * rule_score + 0.5 * ai_score)
    else:
        final_score = rule_score

    return {
        "repo": f"{owner}/{repo}",
        "score": final_score,
        "rule_score": rule_score,
        "ai_score": ai_score,
        "languages": list(repo_data["languages"].keys()),
        "checks": checks,
        "review": review,
    }


FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")


@app.get("/")
def home():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
