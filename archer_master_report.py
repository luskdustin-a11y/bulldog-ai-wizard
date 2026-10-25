"""Generate a versioned ARCHER master PDF from GitHub workflow outcomes.

Runs offline from a GitHub Actions checkout; no secrets or personal memory exported.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from archer_platform import http_response

API = "https://api.github.com"
REPO = os.environ.get("GITHUB_REPOSITORY", "luskdustin-a11y/bulldog-ai-wizard")
BRANCH = os.environ.get("ARCHER_REPORT_BRANCH", "archer-stage4-integration-hardening")

def get_json(path):
    if not path.startswith('/repos/') or any(c in path for c in ('\\', '\r', '\n', '#')):
        raise ValueError('Invalid GitHub API path')
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "archer-report"}
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = "Bearer " + token
    with http_response(API + path, headers=headers, timeout=20,
                       allowed_hosts={'api.github.com'}) as response:
        raw = response.read(2_000_001)
    if len(raw) > 2_000_000:
        raise ValueError('GitHub response exceeds limit')
    return json.loads(raw)

def gather():
    data = get_json(f"/repos/{quote(REPO, safe='/')}/actions/runs?branch={quote(BRANCH, safe='')}&per_page=100")
    runs = data.get("workflow_runs", [])
    return [{"name": r["name"], "commit": r["head_sha"][:12],
             "status": r["status"], "result": r.get("conclusion") or "pending",
             "url": r["html_url"], "created": r["created_at"]}
            for r in runs]

def write_report(runs, destination):
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether
    from xml.sax.saxutils import escape
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    story = [Paragraph("ARCHER / Bulldawg AI — Master Test and Repair Report", styles["Title"]),
             Paragraph("Generated " + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), styles["Normal"]),
             Paragraph("Repository: " + escape(REPO) + " | Branch: " + escape(BRANCH), styles["Normal"]),
             Spacer(1, 16)]
    for run in runs:
        heading = escape(run["name"] + " — " + run["result"].upper())
        details = "Commit: " + escape(run["commit"]) + " | " + escape(run["created"])
        url = escape(run["url"], {'"': '&quot;'})
        story.append(KeepTogether([Paragraph(heading, styles["Heading3"]),
            Paragraph(details, styles["Normal"]),
            Paragraph('<link href="' + url + '">View logs and repair history on GitHub</link>', styles["Normal"]),
            Spacer(1, 8)]))
    if not runs:
        story.append(Paragraph("No matching workflow runs found.", styles["Normal"]))
    SimpleDocTemplate(str(path), pagesize=letter).build(story)
    return path

if __name__ == "__main__":
    write_report(gather(), os.environ.get("ARCHER_REPORT_OUTPUT", "reports/archer-master-latest.pdf"))
