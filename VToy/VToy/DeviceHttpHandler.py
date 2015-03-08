import logging
devicelogger = logging.getLogger('consolelogger')

class DeviceHttpHandler:
    
    @staticmethod
    def handleQueryNewMsg(request):
    	devicelogger.debug("on queryNewMsg")
    	return HttpResponse("implementing...")

    @staticmethod
    def handleGetVoice(request):
    	devicelogger.debug("on getVoice")
    	return HttpResponse("implementing...")

    @staticmethod
    def handleSendMsg(request):
    	devicelogger.debug("on handleSendMsg")
    	return HttpResponse("implementing...")