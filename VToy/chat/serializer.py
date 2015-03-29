from models import ChatWxToDevice, ChatDeviceToWx, VToyUser, ChatVoices, DeviceStatus, DeviceInfo
from Public.Utils import utcdatetime2utctimestamp, utctimestamp2utcdatetime
from Public.Error import DBError
from Public.DeviceSettins import VOICE_COUNT_ONEQUERY
import logging

logger = logging.getLogger('consolelogger')

class DBWrapper:
	"""
	This class don't throw out the exception, but only return reason with json format
	"""
	from datetime import datetime
	utc_begin_datetime = datetime.utcfromtimestamp(0)

	@staticmethod
	def receiveWxVoice(fromuser,createtime,deviceid,devicetype,msgid, vdata):
		"""
		1) restore the voice data into ChatWxToDevice, ChatVoices 
		2) if user doesn't exist, add user into VToyUser 
		3) if DeviceStatus doesn't exist, create DeviceStatus instance into DeviceStatus table. if exist, update the latest_msg_receive_time of DeviceStatu.
		"""
		try:
			try:
				userobj = VToyUser.objects.get(weixin_id=fromuser)
			except VToyUser.DoesNotExist:
				userobj = VToyUser(username=fromuser, weixin_id=fromuser)
				userobj.save()
			
			chatobj = ChatWxToDevice(from_user=userobj, create_time=createtime, message_type='0', device_id=deviceid, \
				device_type=devicetype, msg_id=msgid)
			
			voice = ChatVoices(voice_data=vdata)
			voice.save()

			chatobj.voice_id = voice.id
			chatobj.save()

			#update device status
			try:
				logger.debug("begin to update devicestatus")
				devicestatus = DeviceStatus.objects.get(device_id=deviceid)
				devicestatus.latest_msg_receive_time = createtime
				devicestatus.save()
				logger.debug("end update devicestatus")

			except DeviceStatus.DoesNotExist:
				logger.debug("begin to create devicestatus")
				macAddress = None
				try:
					macAddress = DeviceInfo.objects.get(device_id=deviceid).mac
				except DeviceInfo.DoesNotExist:
					debuginfo = "DeviceStatus table doesn't contain this deviceId; " + "DeviceInfo table also doesn't contain this deviceId, so that this device seems have not authrized successfully."
					logger.debug(debuginfo)
					return False, debuginfo
				devicestat = DeviceStatus(device_id=deviceid, mac=macAddress, latest_msg_receive_time=createtime, \
					lastest_syncfromdevice_time=DBWrapper.utc_begin_datetime)
				devicestat.save()
				logger.debug("end to create devicestatus")

			return True,None
		except Exception,info:
			return False,info
	
	@staticmethod
	def receiveDeviceVoice(macAddress, userName, weixinId, format, deviceType, rawdata, isPosted):
		try:
			deviceInfo = DeviceInfo.objects.get(mac=macAddress)
			userobj = VToyUser.objects.get(weixin_id=weixinId, username=userName)

			audio = ChatVoices(voice_data=rawdata, voice_format=format)
			audio.save()

			chatobj = ChatDeviceToWx(to_user=userobj, message_type='0', device_id=deviceInfo.device_id, device_type=deviceType, \
				voice_id=audio.id, is_posted=isPosted)
			chatobj.save()
			return True, "Successfully"
		except DeviceInfo.DoesNotExist:
			logger.debug("device info doesn't exist")
			return False, "This device have not been registed to wx mp"
		except VToyUser.DoesNotExist:
			logger.debug("user doesn't exist")
			return False, "This user have not been communicated with our wx mp"


	@staticmethod
	def registerDevice(deviceId, macAddress, qrticket="", connectProtocol='4',authKey='', connStrategy='1', closeStrategy='1', cryptMethod='0', authVer='0', manuMacPos='-1', serMacPos='-2'):
		"""
		store the device info
		"""
		try:
			queryset = DeviceInfo.objects.filter(mac=macAddress)
			if queryset:
				return False, "This mac is already registed"
			else:
				deviceInfo = DeviceInfo(device_id=deviceId, mac=macAddress, qr_ticket=qrticket, connect_protocol=connectProtocol, auth_key=authKey, conn_strategy=connStrategy, \
				 close_strategy=closeStrategy, crypt_method=cryptMethod, auth_ver=authVer, manu_mac_pos=manuMacPos, ser_mac_pos=serMacPos)
				deviceInfo.save()

			return True, "Regist successfully"
		except Exception,info: 
			return False,info

	@staticmethod
	def getQRTicket(macAddress):
		"""
		return qrticket
		"""
		try:
			return DeviceInfo.objects.get(mac=macAddress).qr_ticket
		except DeviceInfo.DoesNotExist:
			return None

	@staticmethod
	def getUnSyncedMsgs(macaddress, sync_mark):
		"""
		This function will return all unsynced msgs received from wx user. By the way, it will update the sync_mark. finally return tuple (True, JsonResult)
		if the DeviceStatus is not existed, it will create it automatically with 1970.1.1 00:00:00 utc time, finally return tuple (True, {}})
		If the DeviceInfo is not existed, that means the deviceId have not authrized before, it's ridiculous. this fuction will return tuple (False, ErrorReason)

		JsonResult Example:
			{
			 "senders_weixin" : [weixinId1, weixinId2, weixinId3, weixinId4, weixinId5],
			 "senders_userId" : [userId1, userId2, userId3, userId4, userId5],
			 "create_time" : [1421388427, 1421388428, 1421388429, 1421388430, 1421388433],
			 "voice_id" : [123, 124, 125 ,126 ,137],
			 "latest_create_time" : 1421388433,
			}
		"""

		try:
			status = DeviceStatus.objects.get(mac=macaddress)
			latest_msg_receive_timestamp = utcdatetime2utctimestamp(status.latest_msg_receive_time)
			lastest_syncfromdevice_timestamp = utcdatetime2utctimestamp(status.lastest_syncfromdevice_time)

			logger.debug("sync_mark is %d" % sync_mark)
			if sync_mark < latest_msg_receive_timestamp:
				#sync_mark is before latest_msg_receive_time, so that need to query recent received msgs
				logger.debug('sync_mark is before latest_msg_receive_time, so that need to query recent received msgs')
				sync_datetime = utctimestamp2utcdatetime(sync_mark)
				queryset = ChatWxToDevice.objects.filter(create_time__gt=sync_datetime, device_id=status.device_id, message_type='0').order_by("create_time")[:VOICE_COUNT_ONEQUERY]#message_type = Voice
				logger.debug("query count is %d" % queryset.count())
				ret_dict = {}
				ret_dict["senders_weixin"]=[]
				ret_dict["senders_userId"]=[]
				ret_dict["create_time"]=[]
				ret_dict["voice_id"]=[]
				if queryset:
					for item in queryset:
						ret_dict["senders_weixin"].append(item.from_user.weixin_id)
						ret_dict["senders_userId"].append(item.from_user.username)
						ret_dict["create_time"].append(utcdatetime2utctimestamp(item.create_time))
						ret_dict["voice_id"].append(item.voice_id)
					ret_dict["latest_create_time"] = utcdatetime2utctimestamp(queryset.last().create_time)
					return True, ret_dict
				else:
					return True, DBError["NoNewMsg"]
			else:
				#sync_mark is after latest_msg_receive_time, no new msgs received, so that only need to update lastest_syncfromdevice_time
				logger.debug('sync_mark is after latest_msg_receive_time, no new msgs received, so that only need to update lastest_syncfromdevice_time')
				status.lastest_syncfromdevice_time = utctimestamp2utcdatetime(sync_mark)
				status.save()
				return True, DBError["NoNewMsg"]
				
		except DeviceStatus.DoesNotExist:
			# this case may caused by "Nobody have send msg to this device"
			# so we will create DeviceStatus instance here
			logger.debug("the macaddress doesn't exist in DeviceStatus Table.")
			deviceId=None
			try:
				deviceId = DeviceInfo.objects.get(mac=macaddress).device_id
				deviceInfo = DeviceStatus(device_id=deviceId, mac=macaddress, \
					lastest_syncfromdevice_time=DBWrapper.utc_begin_datetime, \
					latest_msg_receive_time=DBWrapper.utc_begin_datetime)
				deviceInfo.save()
				return True, DBError["NoNewMsg"]

			except DeviceInfo.DoesNotExist:
				debuginfo = "DeviceStatus table doesn't contain this deviceId; " + "DeviceInfo table also doesn't contain this deviceId, so that this device seems have not authrized successfully."
				logger.debug(debuginfo)
				return False, DBError["DeviceInfoMissing"]

	@staticmethod
	def getVoice(voiceId):
		try:
			vdata = ChatVoices.objects.get(id=voiceId).voice_data
			return True, vdata
		except ChatVoices.DoesNotExist:
			return False, DBError["ChatVoiceMissing"]

	@staticmethod
	def IsReplyIn48Hours(nowTime, macAddress):
		try:
			statusInfo = DeviceStatus.objects.get(mac=macAddress)
			timedelta = nowTime - statusInfo.latest_msg_receive_time
			return timedelta.total_seconds() < 48 * 3600 , None
		except DeviceStatus.DoesNotExist:
			return False, "No device status for %s existed." % macAddress

