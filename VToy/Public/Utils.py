from datetime import datetime
import calendar

def utcdatatime2utctimestamp(date_time):
	return calendar.timegm(d.utctimetuple())