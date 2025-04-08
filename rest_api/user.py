# user blueprint

from flask import Flask, Blueprint, jsonify
from .. import cache
from ..config import get_config

blueprint = Blueprint('user', __name__)



@blueprint.route('/<reponame>', methods=['GET'])
def get_results_for_repo(reponame):
	# get repos
	# return result from cache if available
	# return repo not tracked if not there
	config = get_config()
	reponames = config.get_repo_names()
	if reponame not in reponames:
		# return not tracked
		return jsonify('Not tracked')

	adapter = cache.get_current_adapter()
	result = adapter.read_from_cache(reponame)
	return jsonify(result)

@blueprint.route('/get_tracked_repos', methods=['GET'])
def get_tracked_repos():
	return get_config().get_repo_names()