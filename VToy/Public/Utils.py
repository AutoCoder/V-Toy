from datetime import datetime
import calendar
import os

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
	filepath += '.png'
	cmd = 'qrencode -o %s -v 5 -l Q "%s"' % (filepath, qrTicket)
	return os.system(cmd), filepath

def wav2amr(wavfile, amrfile):
	"""
	convert wav to amr by ffmpeg
	1rd parameter is inpute file
	2rd parameter is output file
	"""
	if os.path.exists(wavfile):
		cmd = "ffmpeg -i %s -ab 12.2k -ar 8000 -ac 1 %s" % (wavfile, amrfile)
		return (os.system(cmd) == 0), amrfile
	else:
		return False, "wav file is not existed, please check the file path"

def amr2wav(amrfile, wavfile):
	"""
	convert amr to wav by ffmpeg
	1rd parameter is inpute file
	2rd parameter is output file
	"""
	if os.path.exists(amrfile):
		cmd = "ffmpeg -i %s %s" % (amrfile, wavfile)
		return (os.system(cmd) == 0), wavfile
	else:
		return False, "amr file is not existed, please check the file path"