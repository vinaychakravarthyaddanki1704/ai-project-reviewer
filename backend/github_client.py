"""
github_client.py
----------------
Talks to the public GitHub API and pulls repo metadata, the file list,
languages, and the README text. No login needed for public repos.
"""

import base64
import requests

GITHUB_API = "https://api.github.com"


def parse_repo_url(url: str):
    """Turn a GitHub URL into (owner, repo).

    Accepts:
      - https://github.com/owner/repo
      - github.com/owner/repo  or  owner/repo
      - https://owner.github.io/repo  (a GitHub Pages site -> its repo)
      - https://owner.github.io       (user page -> owner/owner.github.io)
    """
    url = url.strip().rstrip("/")

    # --- GitHub Pages URL (the live website, not the repo) ---
    if ".github.io" in url:
        cleaned = url.replace("https://", "").replace("http://", "")
        parts = cleaned.split("/")
        host = parts[0]                       # e.g. vinay.github.io
        owner = host.split(".github.io")[0]   # -> vinay
        if len(parts) >= 2 and parts[1]:
            repo = parts[1]                   # project page -> that repo name
        else:
            repo = host                       # user page -> owner/owner.github.io
        if not owner or not repo:
            raise ValueError("Could not read owner/repo from that Pages URL.")
        return owner, repo

    # --- Standard github.com URL or plain 'owner/repo' ---
    url = url.replace("https://github.com/", "").replace("http://github.com/", "")
    url = url.replace("www.github.com/", "").replace("github.com/", "")
    parts = url.split("/")
    if len(parts) < 2 or not parts[0] or not parts[1]:
        raise ValueError("Invalid GitHub URL. Use https://github.com/owner/repo")
    owner = parts[0]
    repo = parts[1].replace(".git", "")
    return owner, repo


def _headers(token=None):
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_repo_data(owner, repo, token=None):
    """Fetch metadata, file tree, languages and README for one repo."""
    h = _headers(token)

    r = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}", headers=h, timeout=20)
    if r.status_code == 404:
        raise ValueError("Repository not found (wrong URL, or it's private).")
    if r.status_code == 403:
        raise ValueError("GitHub rate limit hit. Add a token or wait a bit.")
    r.raise_for_status()
    meta = r.json()

    default_branch = meta.get("default_branch", "main")

    tree_resp = requests.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1",
        headers=h,
        timeout=20,
    )
    files = []
    if tree_resp.status_code == 200:
        files = [
            item["path"]
            for item in tree_resp.json().get("tree", [])
            if item.get("type") == "blob"
        ]

    lang_resp = requests.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/languages", headers=h, timeout=20
    )
    languages = lang_resp.json() if lang_resp.status_code == 200 else {}

    readme_text = ""
    readme_resp = requests.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/readme", headers=h, timeout=20
    )
    if readme_resp.status_code == 200:
        content = readme_resp.json().get("content", "")
        try:
            readme_text = base64.b64decode(content).decode("utf-8", errors="ignore")
        except Exception:
            readme_text = ""

    return {
        "meta": meta,
        "default_branch": default_branch,
        "files": files,
        "languages": languages,
        "readme_text": readme_text,
    }
