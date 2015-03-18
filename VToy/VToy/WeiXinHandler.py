import json
import hashlib
import logging
import xml.etree.ElementTree as ET
from django.template import Template, Context
from settings import TEMPLATE_DIR
from WeiXinUtils import *

#the below code is for verifing the syntax 
if __name__ == "__main__":
    import os,sys
    SYSPATH = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(SYSPATH)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "VToy.settings")
    
from chat.serializer import DBWrapper
logger = logging.getLogger('consolelogger')

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
                return WeiXinHandler.replyTextForMsg(msg, 'testing vtoy...')
            elif msg["MsgType"] == "voice":
                return WeiXinHandler.handleVoiceMsg(msg)
            elif msg["MsgType"] == "text":
                text = u'[Test Reply] %s' % msg['Content'] # use unicode for chinese input/output
                return WeiXinHandler.replyTextForMsg(msg, text)
            elif msg["MsgType"] == "device_event":
                if msg["Event"] == 'bind':
                    pass
                elif msg["Event"] == 'subscribe_status':
                    pass
                elif msg["Event"] == 'unsubscribe_status':
                    pass
                elif msg["Event"] == 'unbind':
                    pass
            else:
                return WeiXinHandler.replyTextForMsg(msg, 'testing vtoy for other MsgType...')
        except Exception, debuginfo:
            return WeiXinHandler.replyTextForMsg(msg, debuginfo)
   
    @staticmethod
    def handleVoiceMsg(msg):
        #logger.debug("begin voice path")
        #logger.debug(str(msg))

        if msg.has_key('MediaId') and msg.has_key('FromUserName') and msg.has_key('ToUserName'):
            open_id = msg["FromUserName"]

            #1.download the media
            logger.debug("1.download the media")
            voice_data = None
            # try three times for download media
            for i in range(3):
                is_success, voice_data = WeiXinUtils.DownloadMedia(msg['MediaId'])
                if is_success:
                    logger.debug("try download for %d times." % (i+1))
                    break
                else:
                    continue
            if voice_data == None:
                raise ValueError("Download voice_data with mediaID - %s failed (retry 3 times)" % msg['MediaId'])

            with open("12345.mp3", "wb") as vfile:
                vfile.write()
            #2.query the device binded with
            logger.debug("2.query the device binded with")
            devicelist = WeiXinUtils.queryDeviceInfoByOpenID(open_id)

            if devicelist:
                device_id = devicelist[0]['device_id']
                device_type = devicelist[0]['device_type']
                from datetime import datetime
                time_now = datetime.fromtimestamp(int(msg["CreateTime"]))
                logger.debug(str(time_now))

                # receiveWxVoice will also update the DeviceStatus [attr : latest_msg_receive_time]
                issuccess, info = DBWrapper.receiveWxVoice(fromuser=open_id, createtime=time_now, \
                    deviceid=device_id, devicetype=device_type, msgid=msg["MsgId"], vdata=voice_data)
                if issuccess:
                    logger.debug("DBWrapper.receiveWxVoice success!")
                else:
                    logger.debug("DBWrapper.receiveWxVoice failed, Reason[%s]." % info)
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
        logger.debug(xmlReply)
        return xmlReply        

    @staticmethod
    def replyTextForMsg(msg, text):
        c = Context({
            'ToUserName' : msg['FromUserName'],
            'FromUserName': msg['ToUserName'],
            'createTime': str(int(time.time())),
            'content' : text,#'[Test Reply] %s' % msg['Content'],
            'msgType' : 'text'
            })

        fp = open(TEMPLATE_DIR + '/text_templ')
        t = Template(fp.read())
        fp.close()

        xmlReply = t.render(c)
        return xmlReply

    @staticmethod
    def handleBindMsg(msg):

        logger.debug("handleBindMsg success")
            
def test_authorizedevice():  
    Devicelist = dict()
    Devicelist["device_num"] = '1'

    Devicelist["device_list"] = []
    Devicelist["device_list"].append(WeiXinUtils.DeviceInfo(devId='gh_2fb6f6563f31_e16733450c242d9315327c185d9150ca',mac='1234567890AB'))
    Devicelist['op_type'] = '1'
    print json.dumps(Devicelist)
    print WeiXinUtils.authorizeDevice(Devicelist)

# Create your tests here.
test_authorizedevice()
# print WeiXinHandler.queryDeviceStatus('gh_2fb6f6563f31_e16733450c242d9315327c185d9150ca')
