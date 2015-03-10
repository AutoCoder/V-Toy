from datetime import datetime
import calendar

def utcdatetime2utctimestamp(date_time):
	return calendar.timegm(date_time.utctimetuple())

def utctimestamp2utcdatetime(timestamp):
	return datetime.utcfromtimestamp(timestamp)

def genQRImage(macAddress, qrTicket, path=''):
	"""
	Make sure that it has already authrized the device with macAddress successfuly
	"""
	if path:
		filepath = path + '/' + macAddress
	else:
		filepath = './' + macAddress
	cmd = 'qrencode -o %s.png -v 5 -l Q "%s"' % (filepath, qrTicket)
	return os.system(cmd), filepath