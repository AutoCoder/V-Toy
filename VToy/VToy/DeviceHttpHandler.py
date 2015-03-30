import logging
import json
from django.http import HttpResponse
from WeiXinUtils import WeiXinUtils
from chat.serializer import DBWrapper
from WeixinSettings import MP_ID
from Public.Utils import wav2amr
from Public.Error import HttpRequestError, ExternalToolError, CompositeError

devicelogger = logging.getLogger('consolelogger')

class DeviceHttpHandler:
    
    @staticmethod
    def handleQueryNewMsg(request):
        devicelogger.debug("on queryNewMsg")
        devicelogger.debug(request.method)
        if request.method != "POST":
            return HttpResponse(json.dumps(HttpRequestError.HttpMethodWrong("POST")))
        else:
            devicelogger.debug(request.body)
            post_json = json.loads(request.body)

            #check the sync_mark is 
            if post_json.has_key("mac") and post_json.has_key("sync_mark"):
                noexception, response = DBWrapper.getUnSyncedMsgs(post_json["mac"], post_json["sync_mark"])
                devicelogger.debug(response)
                if noexception:
                    # heartbeat : update the device status = alive
                    DBWrapper.heartBeat(mac)
                    # Implemtation:
                    # 1) query devicestatus, update update_time and status
                    # 2) if no devicestatus object found, query deviceInfo by mac, and then create an new devicestatus 
                    return HttpResponse(json.dumps(response))
                else:
                    return HttpResponse(content=json.dumps(response), status=400)
            else:
                return HttpResponse(json.dumps(HttpRequestError.PostJsonKeyMissing("mac","sync_mark")))

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
        if request.method != "POST":
            return HttpResponse(json.dumps(HttpRequestError.HttpMethodWrong("POST")))
        else:
            from datetime import datetime
            now_time = datetime.utcnow()
	    print request.META
            mac = request.META['HTTP_MAC']
            user_name = request.META['HTTP_USERNAME']
            weixin_id = request.META['HTTP_WEIXINID']
            vformat = request.META['HTTP_FORMAT']
            isImmediateReply = DBWrapper.IsReplyIn48Hours(now_time, mac)

            isSuccess, dberrInfo = DBWrapper.receiveDeviceVoice(macAddress=mac, userName=user_name, weixinId=weixin_id, \
                format=vformat, deviceType=MP_ID, rawdata=request.body, isPosted=isImmediateReply)
            devicelogger.debug("dberrInfo:%s" % dberrInfo)

            if isImmediateReply:
                # convert wav to amr 
                import time, os
                tempwavfilepath = "%d.wav" % int(time.time())
                with open(tempwavfilepath, "wb") as fp:
                    fp.write(request.body)
                    fp.close()

                import time
                issuccess, amrfilepath = wav2amr(tempwavfilepath, "%d.amr" % int(time.time()))
                if not issuccess:
                    return HttpResponse(json.dumps(ExternalToolError.ffmpegError("wav", "amr")))
                
                os.remove(tempwavfilepath) #clean wav temp file             
                # upload media to wx 
                media_id, uploaderrInfo = WeiXinUtils.UploadMedia(filename=amrfilepath)

                os.remove(amrfilepath) #clean amr

                devicelogger.debug("uploaderrInfo:%s" % uploaderrInfo)

                if media_id: #upload media success
                    isSuccess, errInfo = WeiXinUtils.sendCSVoiceMsg(mediaId=media_id, openId=weixin_id)
                    devicelogger.debug("errInfo:%s" % errInfo)

                    if isSuccess:
                        ret = { "is_posted" : 1 }
                        return HttpResponse(json.dumps(ret))
                else: # upload media fail
                    errmsg = "[dberrInfo] %s ; [uploaderrInfo] %s " % (dberrInfo, uploaderrInfo)
                    return HttpResponse(json.dumps(CompositeError(errmsg)))
            else:
                ret = { "is_posted" : 0 }
                return HttpResponse(json.dumps(ret))

    @staticmethod
    def handleRegisterDevice(request):
        """
        This request should post [macaddress], then apply deviceId & qrticket from Wx. finally restore all the device info into db
        """
        devicelogger.debug("on handleRegisterDevice")
        if request.method != "POST":
            return HttpResponse(json.dumps(HttpRequestError.HttpMethodWrong("POST")))

        if not request.POST.has_key("mac"):
            return HttpResponse(json.dumps(HttpRequestError.PostFormKeyMissing("mac")))

        macaddress = request.POST["mac"]
        #check the passed mac is registed to WX (already existed in db)
        qrTicket = DBWrapper.getQRTicket(macaddress)

        if qrTicket:
            devicelogger.debug("This mac is already registed to WX and restored into db")
        else:
            deviceId, qrTicket = WeiXinUtils.genDeviceIdAndQRTicket()

            Devicelist = dict()
            Devicelist["device_num"] = '1'

            Devicelist["device_list"] = []
            deviceinfo = WeiXinUtils.DeviceInfo(devId=deviceId,mac=macaddress)
            Devicelist["device_list"].append(deviceinfo)
            Devicelist['op_type'] = '1'
            devicelogger.debug(Devicelist)

            issuccess, authorizeInfo = WeiXinUtils.authorizeDevice(Devicelist)
            devicelogger.debug(authorizeInfo)
            if issuccess:
                # if authorizeDevice success, then store the DeviceInfo to db
                issuccess, db_related_info = DBWrapper.registerDevice(deviceId=deviceinfo['id'], macAddress=deviceinfo['mac'], qrticket=qrTicket)
                devicelogger.debug(db_related_info)
                if not issuccess:
                    errstr = "[db] %s" % db_related_info
                    return HttpResponse(content=json.dumps(CompositeError(errstr)), status=500)
                devicelogger.debug("qrticket is %s" % qrTicket)
            else:
                errstr = "[authorizeDevice] %s" % authorizeInfo
                return HttpResponse(content=json.dumps(CompositeError(errstr)), status=500)


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
            return HttpResponse(content=json.dumps(ExternalToolError.qrencodeError(ret)), status=500)
