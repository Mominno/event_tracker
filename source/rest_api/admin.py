# admin blueprint
from ..config import get_config
from ..cache import get_current_adapter

from flask import Flask, Blueprint, jsonify

blueprint = Blueprint('admin', __name__, url_prefix='/admin')
# print(f"{__name__ = }")

@blueprint.route('/add_repo/<owner>/<reponame>', methods=['POST'])
def add_repo_to_track(owner: str, reponame: str) -> dict:
	config = get_config()
	flag = config.add_repo(owner, reponame)
	print(flag)
	if flag:
		return jsonify({'msg': "Repo added Successfully.", 'status': 'success', 'code': 200})
	else:
		return jsonify({'msg': "Repo already tracked or max repos tracked reached.", 'status': 'fail', 'code': 500})

@blueprint.route('/remove_repo/<reponame>', methods=['POST'])
def remove_repo_to_track(reponame: str) -> dict:
	config = get_config()
	repo_names = config.get_repo_names()
	if reponame in repo_names:
		config.remove_repo(reponame)
		adapter = get_current_adapter()
		adapter.remove_from_cache(reponame)
		return jsonify({'msg': f"Successfully removed repo {reponame}.", 'status': 'success', 'code': 200})
	else:
		return jsonify({'msg': "Can't remove, repo currently not tracked.", 'status': 'fail',  'code': 200})


	
