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
    "ChatVoiceMissing" : {
        "errcode" : 5,
        "errmsg" : "This Voice Id doesn't exist in table ChatVoices."
    },
    "Other" : {
        "errcode" : 9,
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
    def PostJsonKeyMissing(*keys):
        keysstr = ("[%s] " * len(keys)) % keys
        ret = {}
        ret["errcode"] = 22
        ret["errmsg"] = "The post json need contain both keys %s" % keysstr
        return ret

    @staticmethod
    def PostFormKeyMissing(*keys):
        keysstr = ("[%s] " * len(keys)) % keys
        ret = {}
        ret["errcode"] = 23
        ret["errmsg"] = "please pass keys '%s' by POST FORM" % keysstr
        return ret

# print HttpRequestError.PostJsonKeyMissing("weq","fes","fsdf")
# print HttpRequestError.PostFormKeyMissing("weq","fes","fsdf")

def CompositeError(errstr):
    ret = {}
    ret["errcode"] = 100
    ret["errmsg"] = errstr
    return ret