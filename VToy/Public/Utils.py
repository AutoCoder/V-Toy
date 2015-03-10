from datetime import datetime
import calendar

def utcdatetime2utctimestamp(date_time):
	return calendar.timegm(date_time.utctimetuple())

def utctimestamp2utcdatetime(timestamp):
	return datetime.utcfromtimestamp(timestamp)
