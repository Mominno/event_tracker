from .remote import call_github_repo
from .config import get_config
from .logic import calculate_mean_time_for_data

from datetime import datetime, timedelta, timezone
from dateutil.parser import parse
import sqlite3


REFRESH_TIME_HOURS = 1

DATA_TABLE_NAME = "tracker_table"
LAST_REFRESHED_TABLE_NAME = "refreshed_table"
MEAN_TABLE_NAME = "mean_event_table"

class CacheAdapter():
	"""Base adapter implementing reading data and mean values and refreshing from remote api."""
	def read_data_from_cache(self, reponame, _type=None):
		# we have to store last time we accessed the remote githubrepo
		result = self.get_by_name(reponame, _type=_type)
		last_time_refreshed = self.get_latest_saved_time_for_reponame(reponame)
		current_datetime = datetime.now(tz=timezone.utc)
		print(current_datetime)

		if last_time_refreshed is None:
			self._refresh_data_for_repo(reponame)
			result = self.get_by_name(reponame, _type=_type)
		elif abs(current_datetime - last_time_refreshed) >= timedelta(hours=REFRESH_TIME_HOURS):
			self._refresh_data_for_repo(reponame)
			result = self.get_by_name(reponame, _type=_type)
		return result

	def read_mean_from_cache(self, reponame, _type):
		current_datetime = datetime.now()

		mean_value_tuple = self.get_mean_by_name_and_type(reponame, _type)

		if mean_value_tuple is None:
			self.refresh_mean_for_repo_type(reponame, _type)
			mean_value_tuple = self.get_mean_by_name_and_type(reponame, _type)
		else:
			# its not none, check how old
			print(mean_value_tuple)
			_type, created_at, reponame, mean = mean_value_tuple

			if abs(current_datetime - parse(created_at)) >= timedelta(hours=REFRESH_TIME_HOURS):
				self.refresh_mean_for_repo_type(reponame, _type)
				mean_value_tuple = self.get_mean_by_name_and_type(reponame, _type)

		return mean_value_tuple[3]

	def _refresh_data_for_repo(self, reponame):
		config = get_config()
		username, reponame = config.get(reponame)
		all_events_data = call_github_repo(username, reponame)
		time = datetime.now()
		self.add_to_cache(reponame, time, all_events_data)
		# return all_events_data
	


class SQLAdapter(CacheAdapter):
	"""Implements simple sqlite db that stores necessary data and metadata."""
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
		if MEAN_TABLE_NAME not in table_names:
			# cur.execute(f"CREATE TABLE {DATA_TABLE_NAME}(id, type, actor, repo, payload, created_at, reponame)")
			cur.execute(f"CREATE TABLE {MEAN_TABLE_NAME}(type, created_at, reponame, mean)")

	def get_by_name(self, reponame, _type=None):
		print("Fetching from cache!!")
		column_names = ['id', 'type', 'created_at', 'reponame']
		last_week_datetime = datetime.now() - timedelta(days=1)
		if _type is None:
			data =  self.con.cursor().execute(f"SELECT * FROM {DATA_TABLE_NAME} WHERE reponame='{reponame}' and created_at >= '{last_week_datetime}'")
		else:
			data = self.con.cursor().execute(f"SELECT * FROM {DATA_TABLE_NAME} WHERE reponame='{reponame}' and type='{_type}' and created_at >= '{last_week_datetime}'")
		data_with_headers = []
		for row in data:
			row_with_headers = dict(zip(column_names, row))
			data_with_headers.append(row_with_headers)
		return data_with_headers

	def get_time_data_last_refreshed(self, reponame):
		res = self.con.cursor().execute(f"SELECT refreshed_datetime FROM {LAST_REFRESHED_TABLE_NAME} WHERE reponame = '{reponame}'").fetchone()
		if res is None:
			return res
		else:
			return res[0]

	def get_mean_by_name_and_type(self, reponame, _type):
		res = self.con.cursor().execute(f"SELECT * FROM {MEAN_TABLE_NAME} WHERE reponame='{reponame}' and type='{_type}'").fetchone()
		# if res is None:
		# 	return res
		# else:
		return res

	def refresh_mean_for_repo_type(self, reponame, _type):
		data = self.read_data_from_cache(reponame, _type)
		print("refreshing mean!")
		print(data)
		resulting_mean = calculate_mean_time_for_data(data)
		print(f"{resulting_mean = }")
		row_to_insert = {'mean': resulting_mean, 'type': _type, 'reponame': reponame, 'created_at': datetime.now()}
		# here also delete old mean and replace with new one TODO
		self.con.cursor().execute(f"DELETE FROM {MEAN_TABLE_NAME} WHERE reponame='{reponame}' and type='{_type}'")
		self.con.commit()
		self.con.cursor().execute(f"INSERT INTO {MEAN_TABLE_NAME} VALUES(:type, :created_at, :reponame, :mean)", row_to_insert)
		self.con.commit()
		# return resulting_mean

	def remove_from_cache(self, reponame):
		self.con.cursor().execute(f"DELETE FROM {LAST_REFRESHED_TABLE_NAME} WHERE reponame='{reponame}'")
		self.con.cursor().execute(f"DELETE FROM {MEAN_TABLE_NAME} WHERE reponame='{reponame}'")
		self.con.cursor().execute(f"DELETE FROM {DATA_TABLE_NAME} WHERE reponame='{reponame}'")
		self.con.commit()

	def get_latest_saved_time_for_reponame(self, reponame):
		cur = self.con.cursor()
		res = cur.execute(f"SELECT MAX(created_at) FROM {DATA_TABLE_NAME} WHERE reponame = '{reponame}'")
		res = res.fetchone()
		# print(res)
		if res[0] is None:
			return res[0]
		return parse(res[0])

	def add_to_cache(self, reponame, time, data):
		# retrieve latest datetime for saved event for this combination
		# iterate all 
		latest_saved_datetime = self.get_latest_saved_time_for_reponame(reponame)
		# add only those that are later
		if latest_saved_datetime is None:
			data_to_save = data

		else:
			data_to_save = []
			for row in data:
				if parse(row['created_at']) > latest_saved_datetime:
					data_to_save.append(row)

		for row in data_to_save:
			row['reponame'] = reponame

		self.add_rows_to_table(data_to_save)

	def add_rows_to_table(self, data):
		cur = self.con.cursor()
		cur.executemany(f"INSERT INTO {DATA_TABLE_NAME} VALUES(:id, :type, :created_at, :reponame)", data)
		self.con.commit()  

		

def get_current_adapter() -> CacheAdapter:
	"""Getter for currently used adapter class object."""
	return SQLAdapter()