# EVENT TRACKER
=============

Simple caching utility for viewing mean time between events for GitHub repositories.

## How to run:

1] Get GitHub token, save it as `token` root directory. (Next to this file.)
2a] Create virtual env or install into root python install from requirements.txt
2b]
```
pip install -r requirements.txt
```
3] DEBUG: for debug mode run from root dir 
```
python -m source.main
```
4] For production use 
```
gunicorn 'source.main:get_app()'
```



## Documentation:

User API:

1) Get mean time between event of select type for repo
endpoint: /<reponame>/<_type>
type: GET
example curl:
```
curl localhost:5000/<reponame>/<event_type>
```

2) Get tracked repo's list
endpoint: /get_tracked_repos
type: GET
example curl: curl localhost:5000/get_tracked_repos

3) Get event types for single repo
endpoint: /<reponame>/get_event_types
type: GET
example curl:
```
curl localhost:5000/<reponame>/get_event_types
```



Admin API:
Admin API has /admin prefix for all endpoints

1) Add repo for tracking
endpoint: admin/add_repo/<owner>/<reponame>
type: POST
example curl:
```
curl -X POST localhost:5000/admin/add_repo/<reponame>
```
2 Remove tracked repo
endpoint: admin/remove_repo/<owner>/<reponame>
type: POST
example curl:
```
curl -X POST localhost:5000/admin/remove_repo/<reponame>
```
Admin api responses have the same format
{
'msg': str,
'status': str,
'code': int,
}

