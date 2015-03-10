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
            ret["errmsg"] = "please use httpmethod - 'POST'."
            return HttpResponse(json.dumps(ret))
        else:
            devicelogger.debug(request.body)
            post_json = json.loads(request.body)

            #check the sync_mark is 
            if post_json.has_key("mac") and post_json.has_key("sync_mark"):
                noexception, response = DBWrapper.getUnSyncedMsgs(post_json["mac"], post_json["sync_mark"])
                if noexception:
                    return HttpResponse(json.dumps(response))
                else:
                    return HttpRespnse(content=json.dumps(response), status=400)
            else:
                ret = {}
                ret["errcode"] = 2
                ret["errmsg"] = "The post json need contain both keys %s and %s" % ("mac", "sync_mark")
                return HttpResponse(json.dumps(ret))

    @staticmethod
    def handleGetVoice(request, voiceId):
        devicelogger.debug("on getVoice")
        return HttpResponse("implementing...")

    @staticmethod
    def handleSendMsg(request):
        devicelogger.debug("on handleSendMsg")
        return HttpResponse("implementing...")

    @staticmethod
    def handleRegisterDevice(request):
        """
        This request should post [macaddress], then apply deviceId & qrticket from Wx. finally restore all the device info into db
        """
        devicelogger.debug("on handleAuthorizeDeviceRequest")

        deviceId = 'gh_2fb6f6563f31_e16733450c242d9315327c185d9150ca'
        qrticket = "xxx"
        macaddress = '1234567890AB'
        Devicelist = dict()
        Devicelist["device_num"] = '1'

        Devicelist["device_list"] = []
        deviceinfo = WeiXinUtils.DeviceInfo(devId=deviceId,mac=macaddress)
        Devicelist["device_list"].append(deviceinfo)
        Devicelist['op_type'] = '1'
        print json.dumps(Devicelist)
        issuccess, authorizeInfo = WeiXinUtils.authorizeDevice(Devicelist)
        db_related_info = ""
        if issuccess:
            # if authorizeDevice success, then store the DeviceInfo to db
            issuccess, db_related_info = DBWrapper.registerDevice(deviceId=DeviceInfo['id'], macAddress=DeviceInfo['mac'])

        if issuccess:
            # return the deviceId to device side
            ret = dict()
            relationship = dict()
            relationship["device_id"] = deviceId
            relationship["qrticket"] = qrticket
            relationship["mac"] = macaddress
            ret["errorcode"] = 0
            ret["info"] = relationship
            
        else:
            ret = dict()
            ret["errcode"] = 123;
            ret["errmsg"] = "[authorizeDevice]: %s; [db_related]: %s" % (authorizeInfo, db_related_info)

        #Todo: return the device id, qrticket and macaddress.
        return HttpResponse(json.dumps(ret))
