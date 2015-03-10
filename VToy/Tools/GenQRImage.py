"""
Input - MacAddress

for example : "DFASF-FSGA-GSDFGS-GSDGSD"

Output file: DFASF-FSGA-GSDFGS-GSDGSD.png

Usage: GenQRImage.py "DFASF-FSGA-GSDFGS-GSDGSD"

"""

from VToy.WeiXinUtils import WeiXinUtils
import os

def GenQRImage(MacAddress):
	#1） apply deviceId and qrticket
	deviceId,qrTicket = WeiXinUtils.genDeviceIdAndQRTicket()

	#2） Authrize the applyed deviceId, in this step it need pass macaddress
    Devicelist = dict()
    Devicelist["device_num"] = '1'

    Devicelist["device_list"] = []
    Devicelist["device_list"].append(WeiXinUtils.DeviceInfo(devId=deviceId,mac=MacAddress))
    Devicelist['op_type'] = '0'

    issuccess, resp =  WeiXinUtils.authorizeDevice(Devicelist)
    if issuccess:
    	#3) call qrencode to generate QRImage with png format, and then save MacAddress.png
		cmd = 'qrencode -o %s.png -v 5 -l Q "%s"' % (MacAddress,MacAddress)
		return os.system(cmd)
    else:
    	print "Authrize to Wx server failed, please try again."
    	return 1

if __name__ == "__main__":
	GenQRImage(sys.argv[1])


