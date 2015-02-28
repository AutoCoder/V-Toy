import hashlib
import time
import xml.etree.ElementTree as ET
from django.template import Template, Context
from settings import TEMPLATE_DIR
import requests

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
                WeiXinHandler.receiveVoice(msg["MediaId "])
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
    def receiveVoice(mediaId):
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
            print "receive voice failed with error msg : %s" % r.json()["errmsg"]