"""
This file is for generating error struct for http response.
"""

DBError = {
	"NoNewMsg" : {
		"errcode" : 1,
		"errmsg" : "There is no new msgs received."
	},
	"DeviceInfoMissing" : {
		"errcode" : 2,
		"errmsg" : "This device have not been registed to wx mp."
	},	
	"DeviceStatusMissing" : {
		"errcode" : 3,
		"errmsg" : "DeviceStatus table doesn't contain this deviceId."
	},
	"VToyUserMissing" : {
		"errcode" : 4,
		"errmsg" : "This user have not been communicated with our wx mp."
	},
	"Other" : {
		"errcode" : 5,
		"errmsg" : "Unknown"
	}
}

class ExternalToolError:

	@staticmethod
	def ffmpegError(from_format, to_format):
    	ret = {}
        ret["errcode"] = 11
        ret["errmsg"] = "convert %s to %s format failed" % (from_format, to_format)
        return ret		

    @staticmethod
    def qrencodeError(errcode):
    	ret = {}
        ret["errcode"] = 12
        ret["errmsg"] = "qrencode work failed with error code %d" % errcode
        return ret		    	


class HttpRequestError:

	@staticmethod
    def HttpMethodWrong(rightHttpMethod):
    	ret = {}
        ret["errcode"] = 21
        ret["errmsg"] = "please use httpmethod - '%s'" % rightHttpMethod
        return ret

	@staticmethod
    def PostJsonKeyMissing(key1="", key2=""):
    	ret = {}
        ret["errcode"] = 22
        ret["errmsg"] = "The post json need contain both keys %s and %s" % (key1, key2)
        return ret

	@staticmethod
    def PostFormKeyMissing(key1="", key2=""):
    	ret = {}
        ret["errcode"] = 23
        ret["errmsg"] = "please pass key-'%s' and key-'%s' by POST FORM" % (key1, key2)
        return ret
