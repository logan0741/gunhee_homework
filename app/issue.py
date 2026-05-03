import json
import os
import urllib.error
import urllib.request


def create_github_issue(title: str, body: str, logger) -> None:
	repo = os.getenv("GH_REPO")
	token = os.getenv("GH_TOKEN")

	if not repo or not token:
		logger.warning("GH_REPO/GH_TOKEN not set; skipping GitHub issue creation.")
		return

	url = f"https://api.github.com/repos/{repo}/issues"
	payload = json.dumps({"title": title, "body": body}).encode("utf-8")
	request = urllib.request.Request(
		url,
		data=payload,
		headers={
			"Authorization": f"Bearer {token}",
			"Accept": "application/vnd.github+json",
			"Content-Type": "application/json",
			"User-Agent": "spamcheck-logging-assignment",
		},
		method="POST",
	)

	try:
		with urllib.request.urlopen(request, timeout=10) as response:
			if response.status >= 300:
				logger.warning("Failed to create issue: HTTP %s", response.status)
	except urllib.error.HTTPError as exc:
		detail = exc.read(200).decode("utf-8", errors="replace")
		logger.warning("Failed to create issue: HTTP %s %s", exc.code, detail)
	except urllib.error.URLError as exc:
		logger.warning("Failed to create issue: %s", exc.reason)
