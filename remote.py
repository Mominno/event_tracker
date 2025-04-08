import requests
import dotenv
import json

def get_github_token_from_env(path='./datamole_assignment_token'):
	with open(path) as f:
		TOKEN = f.read()
	return TOKEN

TOKEN = get_github_token_from_env()

def call_github_repo(owner, repo):
	params = {
		"Accept": "application/vnd.github+json",
		"Authorization": f"Bearer {TOKEN}",
		"X-GitHub-Api-Version": "2022-11-28",
	}
	url = f"https://api.github.com/repos/{owner}/{repo}/events"
	print("Fetching from remote!!")
	str_data = requests.get(url, params=params).content.decode("utf-8")
	return json.loads(str_data)

# token should be read from environment
data = call_github_repo('mominno', 'coursera')
# print(data)