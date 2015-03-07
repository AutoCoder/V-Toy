import hashlib
import time
import xml.etree.ElementTree as ET
from django.template import Template, Context
from settings import TEMPLATE_DIR
import requests
import logging
import json

#the below code is for verifing the syntax 
if __name__ == "__main__":
    import os,sys
    SYSPATH = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(SYSPATH)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "VToy.settings")
    
from chat.serializer import DBWrapper
logger = logging.getLogger('consolelogger')

class WeiXinHandler:
    #test account
    appid = "wxe10a58cb12e36d7d"
    appsecret = "8643cc7ba2214bfd2b1447601e0078e2"

    #kidscare accout
    #appid = "wxdb5af81164a69efc"
    #appsecret = "2904773a8df1bbc22e995a42c4ae917f"
    accesstoken = ""
    accesstoken_timestamp = None
    expire = 7200
    
    @staticmethod
    def checkSignature(request):
        """
        This method is for wx api, which will return a signature to make sure this site is for a specified weixin Subscribe-Service
        """
        token = "v-toy"  # TOKEN setted in weixin
        signature = request.GET.get('signature', None)
        timestamp = request.GET.get('timestamp', None)
        nonce = request.GET.get('nonce', None)
        echostr = request.GET.get('echostr', None)
        tmpList = [token, timestamp, nonce]
        tmpList.sort()
        tmpstr = "%s%s%s" % tuple(tmpList)
        hashstr = hashlib.sha1(tmpstr).hexdigest()
        if hashstr == signature:
            return echostr
        else:
            return None   
        
    @staticmethod
    def response_msg(request):
        """
        This method is for wx api, which is the auto-response entry api, for now this method only support 'Brand', 'naifen' input.
        """
        recvmsg = request.body # 
        root = ET.fromstring(recvmsg)
        msg = {}
        for child in root:
            msg[child.tag] = child.text
        try:    
            if msg["MsgType"] == "event":
                c = Context({
                    'ToUserName' : msg['FromUserName'],
                    'FromUserName': msg['ToUserName'],
                    'createTime': str(int(time.time())),
                    'content' : 'testing vtoy',
                    'msgType' : 'text'
                    })
        
                fp = open(TEMPLATE_DIR + '/text_templ')
                t = Template(fp.read())
                fp.close()
        
                xmlReply = t.render(c)
                return xmlReply

            elif msg["MsgType"] == "voice":
                logger.debug("begin voice path")
                logger.debug(str(msg))

                if msg.has_key('MediaId') and msg.has_key('FromUserName') and msg.has_key('ToUserName'):
                    open_id = msg["FromUserName"]

                    #1.download the media
                    logger.debug("1.download the media")
                    vocice_data = WeiXinHandler.DownloadMedia('MediaId')

                    #2.query the device binded with
                    logger.debug("1.query the device binded with")
                    devicelist = WeiXinHandler.queryDeviceInfoByOpenID(open_id)

                    if devicelist:
                        device_id = devicelist[0]['device_id']
                        device_type = devicelist[0]['device_type']
                        DBWrapper.receiveWxVoice(fromuser=open_id, createtime=msg["CreateTime"], \
                            deviceid=device_id, devicetype=device_type, msgid=msg["MsgId"], vdata=vocice_data)
                    else:
                        raise ValueError("This open_id have not binded with any devices.")

                else:
                    raise KeyError("Can't not found key %s or %s or %s" % ('MediaId', 'FromUserName', 'ToUserName'))
                
                logger.debug("After receiveVoice")
                c = Context({
                    'ToUserName' : msg['FromUserName'],
                    'FromUserName': msg['ToUserName'],
                    'CreateTime': str(int(time.time())),
                    'Media_ID' : msg['MediaId'],
                    })
        
                fp = open(TEMPLATE_DIR + '/voice_reply_templ')
                t = Template(fp.read())
                fp.close()
    
                xmlReply = t.render(c)
                return xmlReply
            elif msg["MsgType"] == "text":
                c = Context({
                    'ToUserName' : msg['FromUserName'],
                    'FromUserName': msg['ToUserName'],
                    'createTime': str(int(time.time())),
                    'content' : '[Test Reply] %s' % msg['Content'],
                    'msgType' : 'text'
                    })
        
                fp = open(TEMPLATE_DIR + '/text_templ')
                t = Template(fp.read())
                fp.close()
    
                xmlReply = t.render(c)
                return xmlReply
            else:
                c = Context({
                    'ToUserName' : msg['FromUserName'],
                    'FromUserName': msg['ToUserName'],
                    'createTime': str(int(time.time())),
                    'content' : 'testing vtoy',
                    'msgType' : 'text'
                    })
        
                fp = open(TEMPLATE_DIR + '/text_templ')
                t = Template(fp.read())
                fp.close()
    
                xmlReply = t.render(c)
                return xmlReply
        except Exception, debuginfo:
            return WeiXinHandler.replydebugforwx(debuginfo, msg)
     
    @staticmethod 
    def replydebugforwx(exception, msg):
        c = Context({
                 'ToUserName' : msg['FromUserName'],
                 'FromUserName': msg['ToUserName'],
                 'createTime': str(int(time.time())),
                 'content' : str(exception),
                 'msgType' : 'text'
                 })
        
        fp = open(TEMPLATE_DIR + '/text_templ')
        t = Template(fp.read())
        fp.close()
        
        xmlReply = t.render(c)
        return xmlReply
        
    @staticmethod
    def getaccesstoken():
        cur_timestamp = int(time.time())
        if WeiXinHandler.accesstoken_timestamp and (cur_timestamp - WeiXinHandler.accesstoken_timestamp) < WeiXinHandler.expire and WeiXinHandler.accesstoken:
            return WeiXinHandler.accesstoken
        url_params = {
            "grant_type" : "client_credential",
            "appid" : WeiXinHandler.appid,
            "secret" : WeiXinHandler.appsecret,
            }
        r = requests.get("https://api.weixin.qq.com/cgi-bin/token", params=url_params)
        #print(r.url)
        response_json = r.json()
        return response_json["access_token"]

    @staticmethod
    def DownloadMedia(mediaId):
        url_params = {
            "access_token" : WeiXinHandler.getaccesstoken(),
            "media_id" : mediaId,
            }        
        r = requests.get("http://file.api.weixin.qq.com/cgi-bin/media/get", params=url_params)

        if r.headers["content-type"] == "audio/amr":
            filename = "voice_%d.amr" % int(time.time())
            with open(filename, "wb") as voice:
                 voice.write(r.content)
            return r.content
        else:
            print "restore voice failed with error msg : %s" % r.json()["errmsg"]

    @staticmethod
    def UploadMedia(mediaType="voice", filename=""):
        mediaId = ""
        url_params = {
            "access_token" : WeiXinHandler.getaccesstoken(),
            "type" : mediaType,
            "media" : filename,
            }      
        r = requests.get("http://file.api.weixin.qq.com/cgi-bin/media/upload", params=url_params)
        response_json = r.json()
        if response_json.has_key("media_id"):
            return mediaId
        else:
            print "upload media failed with error msg : %s" % r.json()["errmsg"]

    @staticmethod
    def receivefromDeviceMsg(msg):
        """restore this msg to db, then send this msg(voice) to weixin user
           msg = {
            'to_user':'xxx',
            'create_time': 'xxx',
            'device_id' : 'xxx',
            'session_id' : 'xxx',
            'content' : 'xxx',
            'msg_type' : 'xxx',
            'from_user' : 'xxx',
            'device_type' : 'xxx'
           }
        """

        DBWrapper.restoreDeviceVoice(toUser=msg['to_user'], createTime=msg['create_time'], deviceId=msg['device_id'], \
            sessionId=msg['session_id'], content=msg['content'], msgType=msg['msg_type'], formUser=msg['from_user'], \
            deviceType=msg['device_type']) 

        #send content back to weixin user
        fp = open(TEMPLATE_DIR + '/from_device_templ')
        t = Template(fp.read())
        fp.close()

        c = Context({
            'ToUserName' : msg['to_user'],
            'FromUserName': 'vtoy', #weixin gong zhong zhang hao
            'CreateTime': str(int(time.time())),
            'MsgType' : 'device_voice',
            'DeviceType' : 'vtoy', # gongzhong zhanghao yuanshi ID
            'DeviceID' : msg['device_id'],
            'SessionID' : msg['session_id'],
            'Content' : msg['content'],
            })

        xmlReply = t.render(c)
        return xmlReply


    @staticmethod
    def sendMsgToDevice(deviceId, deviceType, openId, content):
        url_params = {
            "access_token" : WeiXinHandler.getaccesstoken(),
            }
        data_json = {
                "device_type": deviceType,
                "device_id": deviceId,
                "open_id": openId,
                "content": content
            }

        r = requests.post("https://api.weixin.qq.com/device/transmsg", params=url_params, data=json.dumps(data_json))
        ret = r.json()
        if ret.has_key('ret') and ret['ret'] == 0:
            return ret['ret_info']
        else:
            return ret['errmsg']

    #For Old Weixin API
    @staticmethod
    def getDeviceQRCode(device_num, deviceid_list):
        """
        Parameters: 1) The count of deviceIds
                    2) The list of deviceIds

        Return: 1) device_num 
                2) ticket_list

        After user get the ticket_list, Tecent(Weixin) suggest us use qrencode library (QR version = 5, error correction level = Q, mistake tolerate precent > 20%) to generate the point-mat image.
        
        """

        url_params = {
            "access_token" : WeiXinHandler.getaccesstoken(),
            }
        data = {
            "device_num": str(device_num),
            "device_id_list": deviceid_list
        }
        r = requests.post("https://api.weixin.qq.com/device/create_qrcode", params=url_params, data=json.dumps(data))
        ret = r.json()
        if ret.has_key('code_list'):
            return ret['device_num'], ret['code_list']
        else:
            return 0,[]

    #For Old Weixin API(only use to update DeviceAttributes for New Weixin API)
    @staticmethod
    def authorizeDevice(Devicelist):
        import json
        """
        [Return json]
        {"resp":[
            {
                 "base_info":
                 {
                    "device_type":"your_devcie_type",
                    "device_id":"id"
                 },
                 "errcode":0,
                 "errmsg":"ok"
            }
        ]}
        """
        url_params = {
            "access_token" : WeiXinHandler.getaccesstoken(),
            }
        
        r = requests.post("https://api.weixin.qq.com/device/authorize_device", params=url_params, data=json.dumps(Devicelist))
        resp_json = r.json()
        if resp_json.has_key("resp"):
            return resp_json
            #authorized_devicelist = resp_json["resp"]
            #return [ (item['base_info']['device_id'],item['base_info']['device_type']) for item in authorized_devicelist]
        else:
            return resp_json

    #For new Weixin API
    @staticmethod
    def genDeviceIdAndQRTicket():
        url_params = {
            "access_token" : WeiXinHandler.getaccesstoken(),
            }
        r = requests.post("https://api.weixin.qq.com/device/getqrcode", params=url_params)
        resp_json = r.json()
        if resp_json.has_key("deviceid") and resp_json.has_key("qrticket"):
            return resp_json["deviceid"],resp_json["qrticket"]

    @staticmethod
    def bindDeivceWithUser(deviceId, openId, unbind=False):
        """
        deviceId: the Unique identity for device
        openId: the Unique identity for Weixin user

        return errcode, "0" - success; "-1" - failed 
        """
        url_params = {
            "access_token" : WeiXinHandler.getaccesstoken(),
            }
        data = {
            "device_id": deviceId, 
            "openid": openId
        }
        if unbind:
            operator = 'compel_unbind'
        else:
            operator = 'compel_bind'
        url = "https://api.weixin.qq.com/device/%s" % operator 
        r = requests.post(url, params=url_params, data=json.dumps(data))

        resp_json = r.json()
        return resp_json['base_resp']['errcode']

    @staticmethod
    def queryDeviceStatus(deviceId):
        """
        return the status of device, for example "status":2 equal "status_info":"bind"
        """
        url_params = {
            "access_token" : WeiXinHandler.getaccesstoken(),
            "device_id" : deviceId
            }
        r = requests.get("https://api.weixin.qq.com/device/get_stat", params=url_params)
        resp_json = r.json()
        if resp_json.has_key("status") and resp_json.has_key("status_info"):
            return resp_json['status'],resp_json['status_info']
        else:
            return resp_json

    @staticmethod
    def queryOpenIDByDeviceInfo(deviceId, deviceType):
        """
        return openid of device's owner, maybe return a list
        """
        url_params = {
            "access_token" : WeiXinHandler.getaccesstoken(),
            "device_type" : deviceType,
            "device_id" : deviceId
        }
        r = requests.post("https://api.weixin.qq.com/device/get_openid", params=url_params)
        resp_json = r.json()
        if resp_json.has_key('open_id'):
            return resp_json['open_id']

    @staticmethod
    def queryDeviceInfoByOpenID(openId):
        """
        return the device info list binded with openID
        """

        url_params = {
            "access_token" : WeiXinHandler.getaccesstoken(),
            "openid" : openId
        }

        r = requests.post("https://api.weixin.qq.com/device/get_bind_device", params=url_params)
        resp_json = r.json()
        if resp_json.has_key('device_list'):
            return resp_json['device_list']
        else:
            return []


def test_authorizedevice():  
    Devicelist = dict()
    Devicelist["device_num"] = '1'
    from WeiXinUtils import WeiXinUtils

    Devicelist["device_list"] = []
    Devicelist["device_list"].append(WeiXinUtils.DeviceInfo(devId='gh_2fb6f6563f31_e16733450c242d9315327c185d9150ca',mac='1234567890AB'))
    Devicelist['op_type'] = '1'
    print json.dumps(Devicelist)
    print WeiXinHandler.authorizeDevice(Devicelist)

# Create your tests here.
# test_authorizedevice()
# print WeiXinHandler.queryDeviceStatus('gh_2fb6f6563f31_e16733450c242d9315327c185d9150ca')