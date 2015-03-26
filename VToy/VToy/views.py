from django.http import HttpResponse
from datetime import datetime
from WeiXinHandler import WeiXinHandler
from WeiXinJs import getJsLogOnInfo
from WeixinSettings import APP_ID
import os


def hello(request):
    return HttpResponse("Hello world")

def rtthreadaudio(request):
	filename = os.path.join(os.path.dirname(__file__),'123.wav')
	f = open(filename, 'rb')
	data = f.read()
	response = HttpResponse(data, content_type='audio/x-wav')
	response['Content-Disposition'] = 'attachment; filename=123.wav' 
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
    signdict = getJsLogOnInfo()
    c = Context({
    'AppId' : APP_ID,
    'timestamp': signdict["timestamp"],
    'nonce': signdict["nonceStr"],
    'signature' : signdict["signature"],
    })

    fp = open(TEMPLATE_DIR + '/airkiss_templ')
    t = Template(fp.read())
    fp.close()

    reply = t.render(c)
    return HttpResponse(reply)

