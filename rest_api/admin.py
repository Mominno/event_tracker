# admin blueprint
from ..config import get_config

from flask import Flask, Blueprint, jsonify

blueprint = Blueprint('admin', __name__, url_prefix='/admin')
# print(f"{__name__ = }")

@blueprint.route('/add_repo/<owner>/<reponame>', methods=['POST'])
def add_repo_to_track(owner, reponame):
	config = get_config()
	flag = config.add_repo(owner, reponame)
	print(flag)
	if flag:
		return jsonify("Repo added Successfully.")
	else:
		return jsonify("Repo already tracked or max repos tracked reached.")

@blueprint.route('/remove_repo/<reponame>', methods=['POST'])
def remove_repo_to_track(reponame):
	config = get_config()
	repo_names = config.get_repo_names()
	if reponame in repo_names:
		config.remove_repo(reponame)
		return jsonify(f"Successfully removed repo {reponame}.")
	else:
		return jsonify("Can't remove, repo currently not tracked.")


	
