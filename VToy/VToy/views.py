from django.http import HttpResponse
from datetime import datetime
from WeiXinHandler import WeiXinHandler
import os

def hello(request):
    return HttpResponse("Hello world")

def rtthreadaudio(request):
	filename = os.path.join(os.path.dirname(__file__),'winlogoff.wav')
	f = open(filename, 'rb')
	data = f.read()
	response = HttpResponse(data, content_type='audio/x-wav')
	response['Content-Disposition'] = 'attachment; filename=winlogoff.wav' 
	f.close()
	return response

def rtthreadaudiostream(request):
    filename = os.path.join(os.path.dirname(__file__),'winlogoff.wav')
    f = open(filename, 'rb')
    data = f.read()
    f.close()
    return HttpResponse(data, content_type='audio/x-wav')

def rtthreadtext(request):  
	ret_msg = {}
	ret_msg['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	return HttpResponse(str(ret_msg), content_type='application/json')

def handleWXHttpRequest(request):
    if request.method == 'GET':
        return HttpResponse(WeiXinHandler.checkSignature(request))
    elif request.method == 'POST':
        return HttpResponse(WeiXinHandler.response_msg(request))

def airkissplaceholder(request):
	return HttpResponse("welcome to airkiss")