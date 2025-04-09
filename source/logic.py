from dateutil.parser import parse
from statistics import mean, StatisticsError
from itertools import pairwise


def calculate_mean_time_for_data(data):
	datetimes = sorted([parse(row['created_at']) for row in data])
	diffs = []
	for datetime1, datetime2 in pairwise(datetimes):
		diffs.append((datetime2 - datetime1).total_seconds())
	try:
		res = mean(diffs)
		return res
	except StatisticsError as e:
		return 0


def get_types_from_data(data):
	types = []
	for row in data:
		types.append(row['type'])
	return list(set(types))
