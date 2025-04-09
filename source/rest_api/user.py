# user blueprint

from flask import Flask, Blueprint, jsonify


from .. import cache
from ..logic import get_types_from_data
from ..config import get_config


blueprint = Blueprint('user', __name__)



@blueprint.route('/<reponame>/<_type>', methods=['GET'])
def get_mean_event_time_for_repo_event_type(reponame, _type):
	config = get_config()
	reponames = config.get_repo_names()
	if reponame not in reponames:
		# return not tracked
		return jsonify({'status': 'fail', 'code': 500, 'msg': 'Not tracked'})

	adapter = cache.get_current_adapter()
	mean = adapter.read_mean_from_cache(reponame, _type)
	result = {'status': 'success', 'code': 200, 'data': mean}
	return jsonify(result)

@blueprint.route('/get_tracked_repos', methods=['GET'])
def get_tracked_repos():
	result = {'status': 'success', 'code': 200, 'data': get_config().get_repo_names()}
	return result

@blueprint.route('/<reponame>/get_event_types', methods=['GET'])
def get_types_for_repo(reponame):
	adapter = cache.get_current_adapter()
	repo_data = adapter.read_data_from_cache(reponame)
	types = get_types_from_data(repo_data)
	return jsonify({'status': 'success', 'code': 200, 'data': types})


