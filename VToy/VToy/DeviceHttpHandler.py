import logging
import json
from WeiXinUtils import WeiXinUtils
from chat.serializer import DBWrapper

devicelogger = logging.getLogger('consolelogger')

class DeviceHttpHandler:
    
    @staticmethod
    def handleQueryNewMsg(request):
        devicelogger.debug("on queryNewMsg")
        if request.method is not "GET":
            ret = {}
            ret["errcode"] = 1
            ret["errmsg"] = "please use httpmethod - 'GET'."
            return HttpResponse(json.dumps(ret))
        else:
            post_json = json.load(request.raw_post_data)
            return HttpResponse("[Test] : %s" % json.dumps(post_json))

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
