import logging
import json
from django.http import HttpResponse
from WeiXinUtils import WeiXinUtils
from chat.serializer import DBWrapper

devicelogger = logging.getLogger('consolelogger')

class DeviceHttpHandler:
    
    @staticmethod
    def handleQueryNewMsg(request):
        devicelogger.debug("on queryNewMsg")
        devicelogger.debug(request.method)
        if request.method != "POST":
            ret = {}
            ret["errcode"] = 1
            ret["errmsg"] = "please use httpmethod - 'POST'"
            return HttpResponse(json.dumps(ret))
        else:
            devicelogger.debug(request.body)
            post_json = json.loads(request.body)

            #check the sync_mark is 
            if post_json.has_key("mac") and post_json.has_key("sync_mark"):
                noexception, response = DBWrapper.getUnSyncedMsgs(post_json["mac"], post_json["sync_mark"])
                devicelogger.debug(response)
                if noexception:
                    return HttpResponse(json.dumps(response))
                else:
                    return HttpResponse(content=json.dumps(response), status=400)
            else:
                ret = {}
                ret["errcode"] = 2
                ret["errmsg"] = "The post json need contain both keys %s and %s" % ("mac", "sync_mark")
                return HttpResponse(json.dumps(ret))

    @staticmethod
    def handleGetVoice(request, voiceId):
        devicelogger.debug("on getVoice")
        #may need convert amr to wav before sending to device
        devicelogger.debug("voice id is %d" % int(voiceId))
        issuccess, resp = DBWrapper.getVoice(voiceId) # before format converting
        if issuccess:
            return HttpResponse(content=resp,content_type="application/octet-stream")
        else:
            return HttpResponse(status=400, content=json.dumps(resp))

    @staticmethod
    def handleSendMsg(request):
        devicelogger.debug("on handleSendMsg")
        return HttpResponse("implementing...")

    @staticmethod
    def handleRegisterDevice(request):
        """
        This request should post [macaddress], then apply deviceId & qrticket from Wx. finally restore all the device info into db
        """
        devicelogger.debug("on handleRegisterDevice")
        if request.method != "POST":
            ret = {}
            ret["errcode"] = 1
            ret["errmsg"] = "please use httpmethod - 'POST'"
            return HttpResponse(json.dumps(ret))

        if not request.POST.has_key("mac"):
            ret = {}
            ret["errcode"] = 2
            ret["errmsg"] = "please use pass mac address by POST"
            return HttpResponse(json.dumps(ret))

        deviceId, qrTicket = WeiXinUtils.genDeviceIdAndQRTicket()
        macaddress = request.POST["mac"]

        Devicelist = dict()
        Devicelist["device_num"] = '1'

        Devicelist["device_list"] = []
        deviceinfo = WeiXinUtils.DeviceInfo(devId=deviceId,mac=macaddress)
        Devicelist["device_list"].append(deviceinfo)
        Devicelist['op_type'] = '0'
        devicelogger.debug(Devicelist)

        issuccess, authorizeInfo = WeiXinUtils.authorizeDevice(Devicelist)
        db_related_info=""
        if issuccess:
            # if authorizeDevice success, then store the DeviceInfo to db
            issuccess, db_related_info = DBWrapper.registerDevice(deviceId=deviceinfo['id'], macAddress=deviceinfo['mac'])

        if issuccess:
            from Public.Utils import genQRImage
            ret, filepath = genQRImage(macaddress, qrTicket)
            if ret == 0:
                #success
                f = open(filepath, 'rb')
                data = f.read()
                response = HttpResponse(data, content_type='image/png')
                response['Content-Disposition'] = 'attachment; filename=%s.png' % macaddress 
                f.close()
		import os
		os.remove(filepath)
                return response
            else:
                resp = {}
                resp["errcode"] = 6
                resp["errmsg"] = "[authorize] %s; [db] %s; [qrencode] errcode:%d" % (authorizeInfo, db_related_info, ret)
                return HttpResponse(content=json.dumps(resp), status=500)
            
        else:
            ret = dict()
            ret["errcode"] = 123;
            ret["errmsg"] = "[authorizeDevice]: %s; [db_related]: %s" % (authorizeInfo, db_related_info)
            return HttpResponse(json.dumps(ret))
