# 🔍 AI Project Reviewer

> Paste any GitHub repository URL and get an instant **quality score (0–100)** plus an **AI-generated code review** — README quality, structure, tests, CI/CD, license, and concrete suggestions to improve.

Think of it as an automated technical reviewer for student & developer projects. It combines objective checks with a local AI model's judgment, so the score is both fair and explainable.

---

## ✨ Features
- **One-click analysis** — paste a repo URL, get a full report.
- **Blended score** — 50% objective checks + 50% AI judgment (both shown, so you know *why*).
- **Fair to every project type** — frontend, backend, ML, CLI (not just Python-heavy repos).
- **Actionable feedback** — specific strengths and improvements, not generic advice.
- **Auto-handles GitHub Pages links** — converts `user.github.io/repo` to the real repo.
- **100% local & free** — runs on Ollama, no API key, no data leaves your machine.

## 🧠 How it works
```
Browser (index.html)
   │  POST /analyze { url }
   ▼
FastAPI (main.py)
   ├── github_client.py → fetches repo data via the GitHub API
   ├── checks.py        → objective rule-based checks + score
   └── llm.py           → local AI (Ollama) writes a review + its own score
```

## 🛠 Tech stack
`Python` · `FastAPI` · `GitHub REST API` · `Ollama (local LLM)` · `HTML/CSS/JS`

## 🚀 Getting started

**Prerequisites:** [Python 3.10+](https://www.python.org/downloads/) and [Ollama](https://ollama.com/download).

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/ai-project-reviewer.git
cd ai-project-reviewer

# 2. Download the AI model (one time)
ollama pull llama3.2

# 3. Install backend dependencies
cd backend
pip install -r requirements.txt

# 4. Run the server
uvicorn main:app --reload
```

Then open **http://localhost:8000** and paste a repository URL.

> 💡 For much better reviews, run `ollama pull qwen2.5-coder:7b` and set `MODEL = "qwen2.5-coder:7b"` in `backend/llm.py`.

## 📊 What it checks
Source code · README (presence + depth) · Tests · CI/CD · License · `.gitignore` · Dockerfile · Docs · Dependency file

## 🗺 Roadmap
- [ ] Cloud AI option (Gemini) for a hosted live demo
- [ ] Code-complexity analysis (radon)
- [ ] Security scan (bandit)
- [ ] Radar chart of scores
- [ ] React frontend

## 📄 License
MIT — see [LICENSE](LICENSE).
