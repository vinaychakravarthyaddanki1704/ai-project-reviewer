"""
checks.py
---------
Fast, objective checks on the file list + README, and a 0-100 rule-based score.
Now credits ANY real project (including frontend-only) so good non-Python
projects aren't unfairly scored 0.
"""

CODE_EXTS = (
    ".py", ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".java",
    ".cpp", ".c", ".cs", ".go", ".rb", ".php", ".rs", ".kt", ".swift",
    ".dart", ".vue", ".ipynb", ".sql", ".sh",
)


def run_checks(repo_data):
    files = repo_data["files"]
    readme = repo_data["readme_text"]
    meta = repo_data["meta"]
    lower_files = [f.lower() for f in files]

    def any_match(keywords):
        return any(any(k in f for k in keywords) for f in lower_files)

    has_readme = bool(readme.strip())
    readme_words = len(readme.split())

    has_tests = any(
        f.startswith("test") or "/test" in f or "test_" in f or "_test" in f
        or ".test." in f or ".spec." in f
        for f in lower_files
    )
    has_ci_cd = any(".github/workflows" in f for f in lower_files) or any_match(
        [".gitlab-ci", "travis", "circleci", "azure-pipelines", "jenkinsfile", "netlify.toml", "vercel.json"]
    )
    has_license = bool(meta.get("license")) or any_match(["license", "licence"])
    has_gitignore = any(f.endswith(".gitignore") for f in lower_files)
    has_dockerfile = any_match(["dockerfile", "docker-compose"])
    has_docs_folder = any_match(["docs/", "documentation"])
    has_dependency_file = any_match(
        ["requirements.txt", "pyproject.toml", "package.json", "pom.xml", "go.mod", "cargo.toml", "gemfile"]
    )
    has_source_code = any(f.endswith(CODE_EXTS) for f in lower_files)

    return {
        "has_readme": has_readme,
        "readme_word_count": readme_words,
        "has_source_code": has_source_code,
        "has_tests": has_tests,
        "has_ci_cd": has_ci_cd,
        "has_license": has_license,
        "has_gitignore": has_gitignore,
        "has_dockerfile": has_dockerfile,
        "has_docs_folder": has_docs_folder,
        "has_dependency_file": has_dependency_file,
        "num_files": len(files),
    }


def rule_based_score(checks):
    """0-100 score. Any real project starts with credit for having code."""
    score = 0
    score += 15 if checks["has_source_code"] else 0
    score += 15 if checks["has_readme"] else 0
    if checks["readme_word_count"] > 150:
        score += 10
    elif checks["readme_word_count"] > 30:
        score += 5
    score += 15 if checks["has_tests"] else 0
    score += 10 if checks["has_ci_cd"] else 0
    score += 10 if checks["has_license"] else 0
    score += 5 if checks["has_gitignore"] else 0
    score += 5 if checks["has_dockerfile"] else 0
    score += 5 if checks["has_docs_folder"] else 0
    score += 10 if checks["has_dependency_file"] else 0
    return min(score, 100)
