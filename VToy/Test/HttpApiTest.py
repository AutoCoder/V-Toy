import requests
import json


def downloadQRImage():
	post_data = {
		"mac" : "201504109AAA",
	}
	r = requests.post("http://121.40.99.4/vtoy/qrimage/", data=post_data)

	print "HTTP API status code : %d" % r.status_code
	pngfilename = "%s.png" % post_data["mac"]
	with open(pngfilename, "wb") as code:
		code.write(r.content)

def downloadvoice():
	r = requests.get("http://121.40.99.4/vtoy/voice/1")
	print "HTTP API status code : %d" % r.status_code
	with open("voice.amr", "wb") as code:
		code.write(r.content)

def getUnsyncedMessage():
	post_data = {
		"mac" : "3332553390AB",
		"sync_mark" : 0,
	}	
	r = requests.post("http://121.40.99.4/vtoy/messages/", data=json.dumps(post_data))
	print "HTTP API status code : %d" % r.status_code
	with open("messages.json", "w") as code:
		code.write(r.content)

def sendMsgFromDevice():
	headers = {
		'MAC': '201504109AAA',
		'USERNAME' : 'o2lw_t7-SnZTALxfBY-Q4JLskikc',
		'WEIXINID' : 'o2lw_t7-SnZTALxfBY-Q4JLskikc',
		'FORMAT' : 'wav'
	}
	
	r = requests.post("http://121.40.99.4/vtoy/message/", headers=headers, data=open("winlogoff.wav", "rb"))
	print r.content


# downloadQRImage()
# downloadvoice()
# getUnsyncedMessage()
sendMsgFromDevice()