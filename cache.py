from .remote import call_github_repo
from .config import get_config

from datetime import datetime, timedelta
from dateutil.parser import parse
import sqlite3


REFRESH_TIME_HOURS = 1

DATA_TABLE_NAME = "tracker_table"
LAST_REFRESHED_TABLE_NAME = "refreshed_table"

class CacheAdapter():
	def read_from_cache(self, reponame):
		# we have to store last time we accessed the remote githubrepo
		result = self.get_by_name(reponame)
		last_time_refreshed = self.get_last_time_refreshed(reponame)
		current_datetime = datetime.now()

		if result is None or last_time_refreshed is None:
			result = self.refresh_data_for_repo(reponame)
		elif current_datetime - last_time_refreshed <= timedelta(hours=REFRESH_TIME_HOURS):
			result = self.refresh_data_for_repo(reponame)			
		return result

	def refresh_data_for_repo(self, reponame):
		config = get_config()
		username, reponame = config.get(reponame)
		all_events_data = call_github_repo(username, reponame)
		time = datetime.now()
		self.add_to_cache(reponame, time, all_events_data)
		return all_events_data
	


class SQLAdapter(CacheAdapter):
	def __init__(self):
		self.con = sqlite3.connect("tracker.db")
		self.create_tables()

	def create_tables(self):
		cur = self.con.cursor()
		res = cur.execute("SELECT name FROM sqlite_master")
		table_names = res.fetchall()
		unpack = lambda i: i[0]
		table_names = [unpack(i) for i in table_names]
		print(f"{table_names = }")
		
		if LAST_REFRESHED_TABLE_NAME not in table_names:
			cur.execute(f"CREATE TABLE {LAST_REFRESHED_TABLE_NAME}(refreshed_datetime, owner, reponame)")
		if DATA_TABLE_NAME not in table_names:
			# cur.execute(f"CREATE TABLE {DATA_TABLE_NAME}(id, type, actor, repo, payload, created_at, reponame)")
			cur.execute(f"CREATE TABLE {DATA_TABLE_NAME}(id, type, created_at, reponame)")

	def get_by_name(self, reponame):
		print("Fetching from cache!!")
		return self.con.cursor().execute(f"SELECT * FROM {DATA_TABLE_NAME} WHERE reponame='{reponame}'")

	def get_last_time_refreshed(self, reponame):
		res = self.con.cursor().execute(f"SELECT refreshed_datetime FROM {LAST_REFRESHED_TABLE_NAME} WHERE reponame = '{reponame}'").fetchone()
		if res is None:
			return res
		else:
			return res[0]

	def remove_from_cache(self, user, repo):
		# TODO remove when we stop tracking
		pass

	def get_latest_saved_time_for_reponame(self, reponame):
		cur = self.con.cursor()
		res = cur.execute(f"SELECT MAX(created_at) FROM {DATA_TABLE_NAME} WHERE reponame = '{reponame}'")
		res = res.fetchone()
		return res[0]

	def add_to_cache(self, reponame, time, data):
		# retrieve latest datetime for saved event for this combination
		# iterate all 
		latest_saved_datetime = self.get_latest_saved_time_for_reponame(reponame)
		# add only those that are later
		if latest_saved_datetime is None:
			data_to_save = data

		else:
			data_to_save = []
			# print(data)
			for row in data:
				# print(row)
				if parse(row['created_at']) > parse(latest_saved_datetime):
					data_to_save.append(row)

		for row in data_to_save:
			row['reponame'] = reponame

		self.add_rows_to_table(data_to_save)

	def add_rows_to_table(self, data):
		cur = self.con.cursor()
		cur.executemany(f"INSERT INTO {DATA_TABLE_NAME} VALUES(:id, :type, :created_at, :reponame)", data)
		self.con.commit()  

		

def get_current_adapter():
	return SQLAdapter()