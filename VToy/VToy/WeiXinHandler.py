import hashlib
import time
import xml.etree.ElementTree as ET
from django.template import Template, Context
from settings import TEMPLATE_DIR

class WeiXinHandler:
    
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
        
 