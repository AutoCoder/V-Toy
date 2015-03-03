from models import ChatWxToDevice, ChatDeviceToWx, VToyUser, ChatVoices, MessageType
import base64

class DBWrapper:

	@staticmethod
	def restoreWxVoice(fromUser, sessionId, createTime, content, msgId, openId, deviceId, toUser='wxgzzh', msgType='device_voice', deviceType=''):
		"""Note: the cotent parameter is encoded by base64, this function will decode and then store to db."""

		chatobj = ChatWxToDevice(from_user=fromUser, session_id=sessionId, create_time=createTime, device_id=deviceId, device_type=deviceType, msg_id=msgId, open_id=openId)

		if msgType == 'device_voice':
			chatobj.message_type = 0
		elif msgType == 'device_text':
			chatobj.message_type = 1
		elif msgType == 'device_image':
			chatobj.message_type = 2

		voice = ChatVoices(voice_data=base64.b64decode(content))
		voice.save()

		chatobj.voice_id = voice.id
		chatobj.save()

	@staticmethod
	def restoreDeviceVoice(toUser, createTime, deviceId, sessionId, content, msgType='device_voice', formUser='wxgzzh', deviceType=''):
		"""Note: the content parameter should be binrary. this function will store to db directly."""

		chatobj = ChatDeviceToWx(to_user=toUser, session_id=sessionId, create_time=createTime, device_id=deviceId, device_type=deviceType)
		if msgType == 'device_voice':
			chatobj.message_type = 0
		elif msgType == 'device_text':
			chatobj.message_type = 1
		elif msgType == 'device_image':
			chatobj.message_type = 2

		voice = ChatVoices(voice_data=content)
		voice.save()

		chatobj.voice_id = voice.id
		chatobj.save()