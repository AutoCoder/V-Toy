import hashlib
import time
import xml.etree.ElementTree as ET
from django.template import Template, Context
from settings import TEMPLATE_DIR
import requests
import logging

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
                logger.debug("In Voice")
                logger.debug(str(msg))
                WeiXinHandler.receiveVoice(msg["MediaId"])
                logger.debug("After receiveVoice")
                c = Context({
                    'ToUserName' : msg['FromUserName'],
                    'FromUserName': msg['ToUserName'],
                    'createTime': str(int(time.time())),
                    'content' : 'testing receive voice',
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
    def handleVoiceMsg(msg):
        mediaId = "12343546"
        msgId = "12423425235"
        format = 'mp3'
        c = Context({
            'ToUserName' : msg['FromUserName'],
            'FromUserName': msg['ToUserName'],
            'createTime': str(int(time.time())),
            'mediaId' : mediaId,
            'msgType' : 'voice',
            'msgId' : msgId,
            'format' : format,
            })

        fp = open(TEMPLATE_DIR + '/voice_templ')
        t = Template(fp.read())
        fp.close()

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

    @staticmethod
    def getDeviceQRCode(device_num, deviceid_list):
        """
        Parameters: 1) The count of deviceIds
                    2) The list of deviceIds

        Return: 1) device_num 
                2) ticket_list

        After user get the ticket_list, Tecent(Weixin) suggest us use qrencode library (QR version = 5，error correction level = Q ， mistake tolerate precent > 20%) to generate the point-mat image.
        
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