from datetime import datetime
import calendar

def utcdatatime2utctimestamp(date_time):
	return calendar.timegm(date_time.utctimetuple())

def utctimestamp2utcdatatime(timestamp):
	return datetime.utcfromtimestamp(timestamp)