import os
import time
import requests
from WeixinSettings import APP_ID, APP_SECRET, ACCESSTOKEN_EXPIRE, JSTICKET_EXPIRE, CUSTOM_MENU
import json
import logging
logger = logging.getLogger('consolelogger')

class WeiXinUtils:
    """
    This class is the wrapper for wx mp HTTP API
    """
    accesstoken = ""
    accesstoken_timestamp = None
    jsticket = ""
    jsticket_timestamp = None


    @staticmethod
    def getaccesstoken():
        cur_timestamp = int(time.time())
        if WeiXinUtils.accesstoken_timestamp and (cur_timestamp - WeiXinUtils.accesstoken_timestamp) < ACCESSTOKEN_EXPIRE and WeiXinUtils.accesstoken:
            logger.debug("Use cached accesstoken")
            return WeiXinUtils.accesstoken
        url_params = {
            "grant_type" : "client_credential",
            "appid" : APP_ID,
            "secret" : APP_SECRET,
            }
        r = requests.get("https://api.weixin.qq.com/cgi-bin/token", params=url_params)
        #print(r.url)
        response_json = r.json()
        return response_json["access_token"]

    @staticmethod
    def getJsTicket():
        cur_timestamp = int(time.time())
        if WeiXinUtils.jsticket_timestamp and (cur_timestamp - WeiXinUtils.jsticket_timestamp) < JSTICKET_EXPIRE and WeiXinUtils.jsticket:
            logger.debug("Use cached jsticket")
            return WeiXinUtils.jsticket

        url_params = {
            "access_token" : WeiXinUtils.getaccesstoken(),
            "type" : "jsapi"
            }  
        
        r = requests.get("https://api.weixin.qq.com/cgi-bin/ticket/getticket", params=url_params)
        
        response_json = r.json()
        return response_json["ticket"]

    @staticmethod
    def DownloadMedia(mediaId):
        url_params = {
            "access_token" : WeiXinUtils.getaccesstoken(),
            "media_id" : mediaId,
            }        

        r = requests.get("http://file.api.weixin.qq.com/cgi-bin/media/get", params=url_params)
        
        if r.headers["content-type"] == "audio/amr" :
            #filename = "voice_%d.amr" % int(time.time())
            #with open(filename, "wb") as voice:
            #     voice.write(r.content)
            return True, r.content
        else:
            resp_json = r.json()
            print False, ("restore voice failed with error msg : %s" % resp_json["errmsg"])

    @staticmethod
    def UploadMedia(filename, mediaType="voice"):
        mediaId = ""
        url_params = {
            "access_token" : WeiXinUtils.getaccesstoken(),
            "type" : mediaType,
            }

        mediafp = open(filename, 'rb')
        mediafile = {'media': mediafp}

        r = requests.post("http://file.api.weixin.qq.com/cgi-bin/media/upload", params=url_params, files=mediafile) 

        response_json = r.json()
        if response_json.has_key("media_id"):
            return response_json['media_id'],"Successfully"
        else:
            return None, "upload media failed with error msg : %s" % response_json["errmsg"]

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
            "access_token" : WeiXinUtils.getaccesstoken(),
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
            "access_token" : WeiXinUtils.getaccesstoken(),
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
            "access_token" : WeiXinUtils.getaccesstoken(),
            }
        
        r = requests.post("https://api.weixin.qq.com/device/authorize_device", params=url_params, data=json.dumps(Devicelist))
        resp_json = r.json()
        if resp_json.has_key("resp"):
            return True,resp_json
            #authorized_devicelist = resp_json["resp"]
            #return [ (item['base_info']['device_id'],item['base_info']['device_type']) for item in authorized_devicelist]
        else:
            return False,resp_json

    #For new Weixin API
    @staticmethod
    def genDeviceIdAndQRTicket():
        url_params = {
            "access_token" : WeiXinUtils.getaccesstoken(),
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
            "access_token" : WeiXinUtils.getaccesstoken(),
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
            "access_token" : WeiXinUtils.getaccesstoken(),
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
            "access_token" : WeiXinUtils.getaccesstoken(),
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
            "access_token" : WeiXinUtils.getaccesstoken(),
            "openid" : openId
        }

        r = requests.post("https://api.weixin.qq.com/device/get_bind_device", params=url_params)
        resp_json = r.json()
        if resp_json.has_key('device_list'):
            return resp_json['device_list']
        else:
            return []

    @staticmethod
    def sendCSVoiceMsg(mediaId, openId):
        postData = {
            "touser" : openId,
            "msgtype" : "voice",
            "voice" : {
                "media_id" : mediaId
            }
        }
        try:
            url_params = {
                "access_token" : WeiXinUtils.getaccesstoken(),
            }
            logger.debug(postData)
            r = requests.post("https://api.weixin.qq.com/cgi-bin/message/custom/send", params=url_params, data=json.dumps(postData))
            resp_json = r.json()
            logger.debug(resp_json)
            return (resp_json["errcode"] == 0), resp_json["errmsg"]
        except Exception,info:
            return False, info

    def getWxUserDetailInfo(openId):
        url_params = {
            "access_token" : WeiXinUtils.getaccesstoken(),
            "openid" : openId
        }

        r = requests.get("https://api.weixin.qq.com/cgi-bin/user/info", params=url_params)
        return r.json()

    @staticmethod
    def createCustomMenu():
        import json
        url_params = {
            "access_token" : WeiXinUtils.getaccesstoken(),
        }

        r = requests.post("https://api.weixin.qq.com/cgi-bin/menu/create", params=url_params, data=json.dumps(CUSTOM_MENU))
        return r.json()

    @staticmethod
    def deleteCustomMenu():
        import json
        url_params = {
            "access_token" : WeiXinUtils.getaccesstoken(),
        }

        r = requests.get("https://api.weixin.qq.com/cgi-bin/menu/delete", params=url_params)
        return r.json()

    @staticmethod
    def queryCustomMenu():
        import json
        url_params = {
            "access_token" : WeiXinUtils.getaccesstoken(),
        }

        r = requests.get("https://api.weixin.qq.com/cgi-bin/menu/get", params=url_params)
        return r.json()

    @staticmethod
    def updateDeviceStatus(openId, deviceId, wxMpId, deviceStatus, msgType=2):
        try:
            postData = {
                "device_type" : wxMpId,
                "device_id" : deviceId,
                "open_id" : openId,
                "msg_type" : msgType,
                "device_status" : (1 if deviceStatus else 0),
            } 
            url_params = {
                "access_token" : WeiXinUtils.getaccesstoken(),
            }
            r = requests.post("https://api.weixin.qq.com/device/transmsg", params=url_params, data=json.dumps(postData))
            resp_json = r.json()
            return (resp_json["ret"] == 0), resp_json["ret_info"]
        except Exception,info:
            return False, info

    @staticmethod
    def DeviceInfo(devId="001",mac="123456789ABC",connect_protocol="4", \
        auth_key='',close_strategy='1',conn_strategy='1', \
        crypt_method='0', auth_ver='0',manu_mac_pos='-1',ser_mac_pos='-2'):
        """  DeviceInfo list   
        {
            "device_num":"2",
            "device_list":[
                {
                    "id":"dev1",
                    "mac":"123456789ABC",
                    "connect_protocol":"1|2",
                    "auth_key":"",
                    "close_strategy":"1",
                    "conn_strategy":"1",
                    "crypt_method":"0",
                    "auth_ver":"1",
                    "manu_mac_pos":"-1",
                    "ser_mac_pos":"-2"
                }
            ],
            "op_type":"0"
        }
        """
        DeviceInfo = dict()
        DeviceInfo['id'] = devId
        DeviceInfo['mac'] = mac
        DeviceInfo['connect_protocol'] = connect_protocol
        DeviceInfo['auth_key'] = auth_key
        DeviceInfo['close_strategy'] = close_strategy
        DeviceInfo['conn_strategy'] = conn_strategy
        DeviceInfo['crypt_method'] = crypt_method
        DeviceInfo['auth_ver'] = auth_ver
        DeviceInfo['manu_mac_pos'] = manu_mac_pos
        DeviceInfo['ser_mac_pos'] = ser_mac_pos

        return DeviceInfo


#print WeiXinUtils.deleteCustomMenu()
#print WeiXinUtils.createCustomMenu()
#print WeiXinUtils.queryCustomMenu()
#print WeiXinUtils.getWxUserDetailInfo("o2lw_t7-SnZTALxfBY-Q4JLskikc")
