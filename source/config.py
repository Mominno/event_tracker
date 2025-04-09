import json
import os


CONFIG_NAME = 'config.json'
MAX_TRACKABLE_REPOS = 5

class ConfigurationJson():
	"""interface for configuration of app"""
	# this shall be a wrapper around json config stored in root
	def __init__(self):
		self.load()

	def load(self):
		if os.path.exists(CONFIG_NAME):
			with open(CONFIG_NAME, 'r') as f:
				self.content = json.load(f)
		else:
			with open(CONFIG_NAME, mode='w') as f:
				f.write("{}")
			self.content = {}	 

	def save_to_file(self):
		with open(CONFIG_NAME, 'w') as f:
			config_json = json.dumps(self.content)
			f.write(config_json)

	def add_repo(self, owner, reponame):
		self.load()
		repo_names = self.get_repo_names()
		if len(repo_names) < MAX_TRACKABLE_REPOS and reponame not in repo_names:
			self.content[reponame] = owner
			self.save_to_file()
			return True
		else:
			return False

	def get(self, reponame):
		return self.content[reponame], reponame

	def remove_repo(self, reponame):
		self.load()
		if reponame in self.content:
			del self.content[reponame]
		self.save_to_file()
	
	def get_repo_names(self):
		self.load()
		return list(self.content.keys())

# example
"""
{reponame1: [github_username, github_reponame]}
"""
CONFIG = None

def get_config():
	global CONFIG
	if CONFIG is None:
		CONFIG = ConfigurationJson()
	
	return CONFIG