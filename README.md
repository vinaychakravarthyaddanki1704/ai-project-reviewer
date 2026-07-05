# AI Project Reviewer

Paste any GitHub repository URL and get an instant quality score (0–100) plus an AI-generated code review — README quality, structure, tests, CI/CD, license, and concrete suggestions to improve. It combines objective checks with an AI model's judgment, so the score is both fair and explainable.

🔗 **Live demo:** https://ai-project-reviewer-vlxy.onrender.com

> Note: the demo runs on a free server that sleeps after inactivity, so the first load may take ~50 seconds to wake up, then it's fast.

## Features

- One-click analysis — paste a repo URL, get a full report.
- Blended score — 50% objective checks + 50% AI judgment (both shown, so you know why).
- Fair to every project type — frontend, backend, ML, or CLI, not just Python-heavy repos.
- Actionable feedback — specific strengths and improvements, not generic advice.
- Auto-handles GitHub Pages links — converts `user.github.io/repo` to the real repo.
- Flexible AI — Google Gemini in the cloud, or a local Ollama model with no API key.

## How it works

```
Browser (index.html)
   |  POST /analyze { url }
   v
FastAPI (main.py)
   |-- github_client.py  ->  fetches repo data via the GitHub API
   |-- checks.py         ->  objective rule-based checks + score
   |-- llm.py            ->  Gemini / Ollama writes a review + its own score
```

## Tech stack

Python, FastAPI, GitHub REST API, Google Gemini API, Ollama (local LLM), HTML/CSS/JS.

## Getting started (run locally)

Prerequisites: Python 3.10+ and either a free [Gemini API key](https://aistudio.google.com/apikey) or [Ollama](https://ollama.com/download).

```bash
# 1. Clone the repo
git clone https://github.com/vinaychakravarthyaddanki1704/ai-project-reviewer.git
cd ai-project-reviewer/backend

# 2. Install dependencies
pip install -r requirements.txt

# 3a. To use Gemini: create a .env file with your key
#     GEMINI_API_KEY=your_key_here
#     GEMINI_MODEL=gemini-2.5-flash
#
# 3b. Or to use a local model instead: leave .env out and run
#     ollama pull llama3.2

# 4. Start the server
uvicorn main:app --reload
```

Then open http://localhost:8000 and paste a repository URL.

## What it checks

Source code, README (presence and depth), tests, CI/CD, license, `.gitignore`, Dockerfile, docs folder, and dependency file.

## Roadmap

- Code-complexity analysis (radon)
- Security scan (bandit)
- Radar chart of scores
- React frontend

## License

MIT — see [LICENSE](LICENSE).

---

Built by Vinay Chakravarthy Addanki.
