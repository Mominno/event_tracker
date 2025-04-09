import requests
import dotenv
import json
from pathlib import Path

TOKEN_NAME = 'token'
DEFAULT_TOKEN_PATH = Path(__file__).parent.parent / TOKEN_NAME
MAX_REQUESTS_PER_PAGE = 500

def get_github_token_from_env(path=DEFAULT_TOKEN_PATH):
	with open(path) as f:
		TOKEN = f.read()
	return TOKEN

TOKEN = get_github_token_from_env()

def call_github_repo(owner: str, repo: str) -> dict:
	"""Simple call to remote API using request lib."""
	params = {
		"Accept": "application/vnd.github+json",
		"Authorization": f"Bearer {TOKEN}",
		"X-GitHub-Api-Version": "2022-11-28",
		"per_page": MAX_REQUESTS_PER_PAGE,
		"page": 1,
	}
	url = f"https://api.github.com/repos/{owner}/{repo}/events"
	print("Fetching from remote!!")
	str_data = requests.get(url, params=params).content.decode("utf-8")
	return json.loads(str_data)
